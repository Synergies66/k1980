#!/usr/bin/env python3
"""
K1980 双语内容批量生成工具
---------------------------------
功能：
  从 Supabase 读取缺少英文版的文章，
  调用 Claude 翻译 title / summary / content，
  写回 title_en / summary_en / content_en 字段。

运行：
  python generate_bilingual.py --dry-run --limit 5   # 预览
  python generate_bilingual.py --limit 50            # 处理50篇
  python generate_bilingual.py                       # 全量
"""

import os, re, json, time, argparse, requests
from collections import defaultdict

SUPABASE_URL  = "https://wioqkcrtkesntqnuzfkd.supabase.co"
SUPABASE_KEY  = os.environ.get("SUPABASE_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "")
SUPABASE_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indpb3FrY3J0a2VzbnRxbnV6ZmtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwNjE5MTEsImV4cCI6MjA4OTYzNzkxMX0.V7RNM0XkkZt2k02v_ssZkChZBjat7emP4RrMtfsS0hY"
BATCH_SIZE    = 5    # 每批5篇（翻译内容多，每篇较慢）
SLEEP_BETWEEN = 2.0


def sb_headers():
    if SUPABASE_KEY.startswith("sb_"):
        return {
            "apikey": SUPABASE_ANON,
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }
    return {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=minimal",
    }


def fetch_articles(limit=None):
    """拉取缺少 title_en 的文章"""
    params = {
        "select": "id,title,summary,content",
        "title_en": "is.null",
        "order":  "id.asc",
    }
    if limit:
        params["limit"] = limit
    resp = requests.get(
        f"{SUPABASE_URL}/rest/v1/news_articles",
        headers=sb_headers(), params=params
    )
    resp.raise_for_status()
    return resp.json()


def translate_batch(articles):
    """
    批量翻译，返回 [{title_en, summary_en, content_en}, ...]
    """
    items = []
    for i, a in enumerate(articles):
        items.append(f"""--- Article {i+1} ---
Title: {a.get('title','')}
Summary: {a.get('summary','')[:300]}
Content: {(a.get('content') or '')[:800]}""")

    prompt = f"""You are a professional translator for K1980, a global news platform.
Translate the following {len(articles)} Chinese news articles into natural, fluent English.

For each article return:
- title_en: translated headline (concise, under 15 words)
- summary_en: translated summary (80-120 words)  
- content_en: translated full content (keep paragraph structure, translate ### headings too)

Return ONLY a JSON array with {len(articles)} objects, no explanation:
[{{"title_en":"...","summary_en":"...","content_en":"..."}}, ...]

Articles to translate:
{''.join(items)}"""

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 4000,
            "messages": [{"role": "user", "content": prompt}],
        },
        timeout=60,
    )
    resp.raise_for_status()
    raw = resp.json()["content"][0]["text"].strip()

    # 提取 JSON
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        raise ValueError(f"无法解析返回：{raw[:300]}")
    results = json.loads(match.group())
    if len(results) != len(articles):
        raise ValueError(f"数量不匹配：期望{len(articles)}，得到{len(results)}")
    return results


def update_article(article_id, data, dry_run=False):
    if dry_run:
        print(f"  [预览] id={article_id}")
        print(f"    title_en:   {data.get('title_en','')[:60]}")
        print(f"    summary_en: {data.get('summary_en','')[:80]}...")
        return True

    resp = requests.patch(
        f"{SUPABASE_URL}/rest/v1/news_articles?id=eq.{article_id}",
        headers=sb_headers(),
        json={
            "title_en":   data.get("title_en", ""),
            "summary_en": data.get("summary_en", ""),
            "content_en": data.get("content_en", ""),
        }
    )
    if resp.status_code in (200, 204):
        print(f"  ✅  id={article_id} → {data.get('title_en','')[:50]}")
        return True
    else:
        print(f"  ⚠️  id={article_id} 更新失败: {resp.text[:100]}")
        return False


def main():
    parser = argparse.ArgumentParser(description="K1980 双语内容生成")
    parser.add_argument("--dry-run", action="store_true", help="预览模式，不写入")
    parser.add_argument("--limit", type=int, default=None, help="限制处理数量")
    args = parser.parse_args()

    if not SUPABASE_KEY:
        print("❌ 请设置 SUPABASE_KEY 环境变量"); return
    if not ANTHROPIC_KEY:
        print("❌ 请设置 ANTHROPIC_KEY 环境变量"); return

    print("📡 读取待翻译文章...")
    articles = fetch_articles(limit=args.limit)
    print(f"   需要翻译：{len(articles)} 篇\n")

    if not articles:
        print("✅ 所有文章已有英文内容。"); return

    success = 0
    for i in range(0, len(articles), BATCH_SIZE):
        batch = articles[i:i+BATCH_SIZE]
        print(f"🌐 翻译第 {i+1}–{i+len(batch)} 篇...")
        try:
            translations = translate_batch(batch)
        except Exception as e:
            print(f"  ❌ 翻译失败，跳过本批：{e}"); continue

        for article, trans in zip(batch, translations):
            if update_article(article["id"], trans, dry_run=args.dry_run):
                success += 1

        time.sleep(SLEEP_BETWEEN)

    print(f"\n🎉 完成！共翻译 {success} 篇文章。")
    if args.dry_run:
        print("   （预览模式，数据库未修改）")


if __name__ == "__main__":
    main()
