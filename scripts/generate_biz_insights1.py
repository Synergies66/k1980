"""
K1980 自动内容引擎
每次运行做三件事：
1. 从 Google News RSS 抓取最新华人相关新闻
2. AI 主动生成华人视角原创深度报道（每次8篇）
3. 对现有未处理文章补充 ai_title / ai_insight
"""

import os, json, re, time, uuid, hashlib, requests
from datetime import datetime, timezone
from xml.etree import ElementTree as ET

# ── 配置 ──────────────────────────────────────────────────
SUPABASE_URL   = os.environ["SUPABASE_URL"]
SUPABASE_KEY   = os.environ["SUPABASE_KEY"]
ANTHROPIC_KEY  = os.environ.get("ANTHROPIC_API_KEY", "")
CF_WORKER_URL  = "https://k1980-ai.gwkgd6828n.workers.dev"

HEADERS_SB = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "return=minimal",
}

# ── Google News RSS 源（华人相关关键词）─────────────────────
RSS_FEEDS = [
    # 移民/签证
    "https://news.google.com/rss/search?q=华人+移民&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    "https://news.google.com/rss/search?q=Chinese+immigrants+Australia+New+Zealand&hl=en&gl=US&ceid=US:en",
    # 财经
    "https://news.google.com/rss/search?q=海外华人+财经+投资&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    "https://news.google.com/rss/search?q=Chinese+community+property+economy&hl=en&gl=US&ceid=US:en",
    # 科技
    "https://news.google.com/rss/search?q=AI+人工智能+华人&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    # 生活/教育
    "https://news.google.com/rss/search?q=海外华人+教育+留学&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
    # 新西兰/澳洲本地
    "https://news.google.com/rss/search?q=New+Zealand+China+Chinese&hl=en&gl=NZ&ceid=NZ:en",
    "https://news.google.com/rss/search?q=Australia+Chinese+community&hl=en&gl=AU&ceid=AU:en",
]

# ── AI 主动生成的主题提示词 ─────────────────────────────────
DAILY_TOPICS = [
    "新西兰最新移民政策变化对华人申请者的影响与应对策略",
    "澳大利亚华人房产投资：当前市场机会与风险分析",
    "海外华人子女教育：本地学校 vs 华文学校的利弊权衡",
    "北美华人职场：AI时代如何保持竞争力",
    "英国签证政策新变化：华人留学生和工作签证最新动态",
    "新加坡华人创业机遇：东南亚市场的华商新浪潮",
    "海外华人投资回国：当前政策环境与实操指南",
    "华人社区心理健康：异乡生活压力与支持资源",
]

import random


def safe_parse_json(text: str) -> dict:
    text = re.sub(r'```json|```', '', text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{[\s\S]*\}', text)
        if match:
            try:
                return json.loads(match.group())
            except Exception:
                pass
    raise ValueError(f"JSON解析失败: {text[:100]}")


def call_claude(prompt: str, max_tokens: int = 1200) -> str:
    if not ANTHROPIC_KEY:
        raise ValueError("未设置 ANTHROPIC_API_KEY")
    resp = requests.post(
        CF_WORKER_URL,
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": prompt}]
        },
        headers={"Content-Type": "application/json"},
        timeout=45
    )
    resp.raise_for_status()
    data = resp.json()
    return data["content"][0]["text"]


def sb_insert(table: str, rows: list) -> bool:
    resp = requests.post(
        f"{SUPABASE_URL}/rest/v1/{table}",
        headers=HEADERS_SB,
        json=rows,
        timeout=15
    )
    return resp.ok


def sb_patch(table: str, id_val, data: dict) -> bool:
    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/{table}?id=eq.{id_val}",
        headers=HEADERS_SB,
        json=data,
        timeout=15
    )
    return resp.ok


def sb_get(table: str, params: str) -> list:
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/{table}?{params}",
        headers={**HEADERS_SB, "Prefer": "count=exact"},
        timeout=15
    )
    return resp.json() if resp.ok else []


# ══ 步骤1：抓取 RSS 新闻 ══════════════════════════════════
def fetch_rss_news() -> int:
    print("\n── 步骤1：抓取 RSS 新闻 ──")
    added = 0

    # 获取已有 guid，用于去重
    existing = sb_get("news_articles", "select=guid&limit=500&order=created_at.desc")
    existing_guids = {r.get("guid", "") for r in existing if isinstance(r, dict)}

    for feed_url in RSS_FEEDS:
        try:
            resp = requests.get(feed_url, timeout=15,
                                headers={"User-Agent": "Mozilla/5.0"})
            if not resp.ok:
                continue
            root = ET.fromstring(resp.content)
            items = root.findall(".//item")[:8]  # 每个源取8条

            for item in items:
                title   = (item.findtext("title") or "").strip()
                link    = (item.findtext("link") or "").strip()
                pub     = item.findtext("pubDate") or ""
                source  = item.findtext("source") or "Google News"

                if not title or len(title) < 5:
                    continue

                # 用 title+link 生成唯一 guid
                guid = hashlib.md5((title + link).encode()).hexdigest()
                if guid in existing_guids:
                    continue

                # 简单分类
                cat = classify(title)
                summary = title  # RSS 通常没有正文，用标题作摘要

                row = {
                    "guid": guid,
                    "title": title,
                    "summary": summary,
                    "content": summary,
                    "category": cat,
                    "source_name": str(source)[:40],
                    "original_url": link,
                    "is_published": True,
                    "view_count": random.randint(50, 500),
                    "created_at": datetime.now(timezone.utc).isoformat(),
                }
                if sb_insert("news_articles", [row]):
                    existing_guids.add(guid)
                    added += 1
                    print(f"  ✅ [{cat}] {title[:50]}")
                time.sleep(0.3)

        except Exception as e:
            print(f"  ⚠️  RSS抓取失败 {feed_url[:50]}: {e}")
            continue

    print(f"  共新增 {added} 条新闻")
    return added


def classify(text: str) -> str:
    text = text.lower()
    if any(k in text for k in ["移民","签证","visa","immigr","resident","pr","citizenship","入籍"]):
        return "移民"
    if any(k in text for k in ["留学","教育","university","school","student","学生","考试","学费"]):
        return "教育"
    if any(k in text for k in ["房价","房产","property","housing","rent","投资","股票","经济","gdp","finance","wealth","money","tax","贷款"]):
        return "财经"
    if any(k in text for k in ["ai","人工智能","科技","tech","apple","google","microsoft","chip","芯片","openai","chatgpt"]):
        return "科技"
    if any(k in text for k in ["旅游","travel","tourism","签证","flight","航班","酒店"]):
        return "旅游"
    if any(k in text for k in ["生活","社区","community","health","医疗","饮食","文化","华人"]):
        return "生活"
    return "时事"


# ══ 步骤2：AI 主动生成原创深度报道 ══════════════════════════
WRITE_PROMPT = """你是 K1980.app 的主编，专为全球海外华人撰写深度资讯。
请围绕以下主题，生成一篇华人视角的深度报道：

主题：{topic}

要求：
1. 标题：吸引海外华人，突出实际影响，不超过30字
2. 分类：从 时事/移民/教育/财经/科技/生活/旅游 中选一个最合适的
3. 摘要：80-120字，概括核心内容
4. 正文：400-600字，有背景、有数据、有对华人的具体影响和行动建议
5. 标签：3-4个关键词（逗号分隔）
6. 来源：写"K1980深度"

严格按JSON返回，不加任何说明：
{{"title":"...","category":"...","summary":"...","content":"...","tags":"...","source_name":"K1980深度"}}"""


def generate_ai_articles(count: int = 8) -> int:
    if not ANTHROPIC_KEY:
        print("\n── 步骤2：跳过AI生成（未设置 ANTHROPIC_API_KEY）──")
        return 0

    print(f"\n── 步骤2：AI 主动生成 {count} 篇原创报道 ──")
    topics = random.sample(DAILY_TOPICS, min(count, len(DAILY_TOPICS)))
    added = 0

    for topic in topics:
        try:
            print(f"  生成：{topic[:40]}...")
            raw = call_claude(WRITE_PROMPT.format(topic=topic), max_tokens=1500)
            data = safe_parse_json(raw)

            assert "title" in data and "content" in data, "缺少必要字段"

            tags = data.get("tags", "")
            if isinstance(tags, list):
                tags = ",".join(tags)

            row = {
                "guid": str(uuid.uuid4()),
                "title": data["title"],
                "summary": data.get("summary", data["content"][:120]),
                "content": data["content"],
                "category": data.get("category", "时事"),
                "source_name": data.get("source_name", "K1980深度"),
                "tags": [t.strip() for t in tags.split(",") if t.strip()],
                "original_url": "#",
                "is_published": True,
                "view_count": random.randint(200, 1500),
                "created_at": datetime.now(timezone.utc).isoformat(),
            }
            if sb_insert("news_articles", [row]):
                added += 1
                print(f"  ✅ [{row['category']}] {row['title']}")
            time.sleep(2)  # 避免限流

        except Exception as e:
            print(f"  ❌ 生成失败: {e}")
            continue

    print(f"  共生成 {added} 篇原创报道")
    return added


# ══ 步骤3：对现有文章补充 AI 洞察 ════════════════════════════
INSIGHT_PROMPT = """你是 K1980.app 主编。处理以下新闻，转化为华人视角深度短评。

原始新闻：{raw_text}

输出要求：
1. ai_title：去掉官方腔，突出对华人影响，不超过25字
2. ai_insight：HTML格式3个<li>，每条含emoji：发生了什么/对华人影响/行动建议
3. tags：3个逗号分隔标签

严格JSON返回：
{{"ai_title":"...","ai_insight":"<ul><li>...</li><li>...</li><li>...</li></ul>","tags":"标签1,标签2,标签3"}}"""


def process_existing_articles(limit: int = 15) -> int:
    if not ANTHROPIC_KEY:
        print("\n── 步骤3：跳过AI洞察补充（未设置 ANTHROPIC_API_KEY）──")
        return 0

    print(f"\n── 步骤3：补充 AI 洞察（最多{limit}条）──")
    articles = sb_get(
        "news_articles",
        f"ai_title=is.null&is_published=eq.true&order=created_at.desc&limit={limit}&select=id,title,summary,content"
    )

    ok = 0
    for art in articles:
        try:
            raw = (art.get("content") or art.get("summary") or art.get("title", ""))[:2000]
            if not raw.strip():
                continue
            print(f"  处理: {art.get('title','')[:40]}...")
            result = call_claude(INSIGHT_PROMPT.format(raw_text=raw), max_tokens=800)
            data = safe_parse_json(result)
            assert "ai_title" in data
            if sb_patch("news_articles", art["id"], {
                "ai_title":   data["ai_title"],
                "ai_insight": data.get("ai_insight", ""),
                "tags":       [t.strip() for t in data.get("tags","").split(",") if t.strip()],
            }):
                ok += 1
                print(f"  ✅ {data['ai_title']}")
            time.sleep(2)
        except Exception as e:
            print(f"  ❌ {e}")
            continue

    print(f"  共处理 {ok} 篇")
    return ok


# ══ 主函数 ════════════════════════════════════════════════
if __name__ == "__main__":
    print(f"🚀 K1980 内容引擎启动 {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"   ANTHROPIC_KEY: {'已设置' if ANTHROPIC_KEY else '❌ 未设置'}")

    rss_count = fetch_rss_news()
    ai_count  = generate_ai_articles(count=8)
    ins_count = process_existing_articles(limit=10)

    print(f"\n── 完成 ──")
    print(f"  RSS新闻: +{rss_count} 条")
    print(f"  AI原创: +{ai_count} 篇")
    print(f"  洞察补充: {ins_count} 篇")
    print(f"  总计新增内容: {rss_count + ai_count} 条")
