#!/usr/bin/env python3
"""
k1980.app 新闻引擎核心库
所有分类模块共用，不直接运行
版本: 2.0 - 模块化架构
"""

import os
import re
import json
import time
import hashlib
import logging
import feedparser
import anthropic
from datetime import datetime, timezone
from supabase import create_client, Client

# ─── 日志配置 ─────────────────────────────────────────────
def setup_logger(module_name: str) -> logging.Logger:
    logging.basicConfig(
        level=logging.INFO,
        format=f"%(asctime)s [{module_name}] %(levelname)s │ %(message)s",
        datefmt="%H:%M:%S",
    )
    return logging.getLogger(module_name)

# ─── 客户端初始化 ──────────────────────────────────────────
def init_clients() -> tuple[Client, anthropic.Anthropic]:
    supabase = create_client(
        os.environ["SUPABASE_URL"],
        os.environ["SUPABASE_SERVICE_KEY"],
    )
    claude = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    return supabase, claude

# ─── 工具函数 ──────────────────────────────────────────────
def make_guid(url: str) -> str:
    return hashlib.sha256(url.encode()).hexdigest()[:32]

def clean_html(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

# ─── RSS 抓取 ──────────────────────────────────────────────
def fetch_feed(source: dict, max_items: int = 5) -> list[dict]:
    log = logging.getLogger(source.get("category", "feed"))
    log.info(f"抓取 → {source['name']}")
    try:
        feed = feedparser.parse(source["url"])
        if feed.bozo and not feed.entries:
            log.warning(f"  RSS 解析警告: {feed.bozo_exception}")
        items = []
        for entry in feed.entries[:max_items]:
            title   = clean_html(getattr(entry, "title", ""))
            summary = clean_html(getattr(entry, "summary", ""))
            link    = getattr(entry, "link", "")
            pub     = getattr(entry, "published", "")
            if not title or not link:
                continue
            items.append({
                "guid":           make_guid(link),
                "source_name":    source["name"],
                "category":       source["category"],
                "original_title": title,
                "original_summary": summary,
                "original_url":   link,
                "published_at":   pub,
                "language":       source.get("language", "en"),
            })
        log.info(f"  └ {len(items)} 条")
        return items
    except Exception as e:
        log.warning(f"  └ 抓取失败: {e}")
        return []

# ─── Claude 改写 ───────────────────────────────────────────
def build_system_prompt(category: str, custom_instructions: str = "") -> str:
    base = f"""你是 k1980.app 的资深华人媒体编辑，专门负责【{category}】板块，目标读者是海外华人（北美、澳洲、欧洲）。

改写规则：
1. 不直接翻译原文，用自己的语言重新表达核心信息
2. 从海外华人视角切入（签证/工作/投资/子女教育/移民政策/社区动态）
3. 标题20字以内，醒目有力，可加数字或疑问
4. 语言风格：专业但亲切，简洁，适合微信/微博传播
5. 正文150-250字，纯文字，不使用markdown格式"""

    if custom_instructions:
        base += f"\n\n【{category}板块特别要求】\n{custom_instructions}"

    base += """

必须严格返回以下JSON格式，不要输出任何其他内容：
{
  "title": "改写后标题（≤20字）",
  "summary": "两句话摘要（≤50字，突出华人关注点）",
  "content": "正文（150-250字，分2-3段，纯文字）",
  "tags": ["标签1", "标签2", "标签3"]
}"""
    return base


def rewrite_with_claude(
    item: dict,
    claude: anthropic.Anthropic,
    system_prompt: str,
    log: logging.Logger,
    retry: int = 2,
) -> dict | None:
    lang_hint = "（原文中文）" if item["language"] == "zh" else "（原文英文，理解后改写，勿直译）"
    user_msg = (
        f"分类：{item['category']} {lang_hint}\n\n"
        f"原标题：{item['original_title']}\n"
        f"原摘要：{item['original_summary'][:600] or '（无摘要）'}\n\n"
        f"请改写为适合海外华人的中文资讯，JSON格式返回。"
    )
    for attempt in range(1, retry + 2):
        try:
            resp = claude.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1000,
                system=system_prompt,
                messages=[{"role": "user", "content": user_msg}],
            )
            raw = resp.content[0].text.strip()
            # 容错：截取第一个 { 到最后一个 }
            m = re.search(r'\{.*\}', raw, re.DOTALL)
            if not m:
                raise ValueError("未找到 JSON 结构")
            try:
                data = json.loads(m.group())
            except json.JSONDecodeError:
                result = {}
                for key in ("title", "summary", "content"):
                    fm = re.search(rf'"{key}"\s*:\s*"(.*?)(?<!\\\\)"', m.group(), re.DOTALL)
                    if fm:
                        result[key] = fm.group(1).replace("\\n", "\n")
                tags = re.search(r'"tags"\s*:\s*\[([^\]]+)\]', m.group())
                result["tags"] = [t.strip().strip('"') for t in tags.group(1).split(",")] if tags else []
                if "title" not in result or "content" not in result:
                    raise
                data = result
            # 验证必要字段
            for field in ("title", "summary", "content", "tags"):
                if field not in data:
                    raise ValueError(f"缺少字段: {field}")
            return data
        except Exception as e:
            log.warning(f"  改写失败 (第{attempt}次): {e}")
            if attempt <= retry:
                time.sleep(2)
    return None

# ─── Supabase 操作 ─────────────────────────────────────────
def get_existing_guids(supabase: Client, category: str, log: logging.Logger) -> set[str]:
    """只拉取本分类的 guid，减少内存占用"""
    try:
        res = (
            supabase.table("news_articles")
            .select("guid")
            .eq("category", category)
            .execute()
        )
        guids = {row["guid"] for row in res.data}
        log.info(f"数据库已有 [{category}] 文章: {len(guids)} 篇")
        return guids
    except Exception as e:
        log.warning(f"获取 guid 失败: {e}")
        return set()

def insert_article(supabase: Client, item: dict, rewritten: dict, log: logging.Logger) -> bool:
    try:
        record = {
            "guid":           item["guid"],
            "title":          rewritten["title"],
            "summary":        rewritten["summary"],
            "content":        rewritten["content"],
            "tags":           rewritten.get("tags", []),
            "category":       item["category"],
            "source_name":    item["source_name"],
            "original_url":   item["original_url"],
            "original_title": item["original_title"],
            "published_at":   item.get("published_at") or datetime.now(timezone.utc).isoformat(),
            "created_at":     datetime.now(timezone.utc).isoformat(),
            "is_published":   True,
        }
        supabase.table("news_articles").insert(record).execute()
        return True
    except Exception as e:
        log.warning(f"  写入失败: {e}")
        return False

# ─── 主运行函数（每个模块调用此函数）──────────────────────
def run_module(
    category: str,
    sources: list[dict],
    custom_instructions: str = "",
    max_items_per_source: int = 5,
    sleep_between_calls: float = 1.5,
) -> dict:
    """
    通用运行入口，每个分类模块调用此函数。
    返回运行统计结果。
    """
    log = setup_logger(category)
    log.info("=" * 55)
    log.info(f"k1980 [{category}] 模块启动")
    log.info("=" * 55)

    supabase, claude = init_clients()
    system_prompt    = build_system_prompt(category, custom_instructions)
    existing_guids   = get_existing_guids(supabase, category, log)

    stats = {"new": 0, "skipped": 0, "failed": 0}

    for source in sources:
        items = fetch_feed(source, max_items=max_items_per_source)
        for item in items:
            if item["guid"] in existing_guids:
                stats["skipped"] += 1
                continue

            log.info(f"改写: {item['original_title'][:65]}…")
            rewritten = rewrite_with_claude(item, claude, system_prompt, log)
            if not rewritten:
                stats["failed"] += 1
                continue

            if insert_article(supabase, item, rewritten, log):
                existing_guids.add(item["guid"])
                stats["new"] += 1
                log.info(f"  ✓ {rewritten['title']}")
            else:
                stats["failed"] += 1

            time.sleep(sleep_between_calls)

    log.info("=" * 55)
    log.info(f"完成 │ 新增: {stats['new']} │ 跳过: {stats['skipped']} │ 失败: {stats['failed']}")
    log.info("=" * 55)
    return stats
