#!/usr/bin/env python3
"""K1980 英文 Slug 批量生成工具"""

import re, os, time, json, argparse, requests
from collections import defaultdict

SUPABASE_URL  = "https://wioqkcrtkesntqnuzfkd.supabase.co"
SUPABASE_KEY  = os.environ.get("SUPABASE_KEY", "")
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_KEY", "")
SUPABASE_ANON = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indpb3FrY3J0a2VzbnRxbnV6ZmtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwNjE5MTEsImV4cCI6MjA4OTYzNzkxMX0.V7RNM0XkkZt2k02v_ssZkChZBjat7emP4RrMtfsS0hY"
BATCH_SIZE    = 20
SLEEP_BETWEEN = 1.0


def supabase_headers():
    # 新格式 sb_secret_... 用 anon 作 apikey，secret 作 Bearer
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
    url = f"{SUPABASE_URL}/rest/v1/news_articles"
    params = {"select": "id,title,slug_en", "order": "id.asc"}
    if limit:
        params["limit"] = limit
    resp = requests.get(url, headers=supabase_headers(), params=params)
    resp.raise_for_status()
    articles = resp.json()
    return [a for a in articles if not a.get("slug_en")]


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"['\u2019\u2018]", "", text)
    text = re.sub(r"[^a-z0-9\s-]", " ", text)
    text = re.sub(r"[\s_-]+", "-", text)
    text = re.sub(r"^-+|-+$", "", text)
    return text[:80]


def translate_batch(titles):
    numbered = "\n".join(f"{i+1}. {t}" for i, t in enumerate(titles))
    prompt = f"""You are an SEO expert. Convert each Chinese news headline below into a short, 
SEO-friendly English slug (3-7 words, hyphen-separated, lowercase, no stop words).

Return ONLY a JSON array of strings in the same order, no explanation.
Example output: ["us-china-trade-war-tariffs", "tokyo-olympic-athletes-record"]

Headlines:
{numbered}"""

    resp = requests.post(
        "https://api.anthropic.com/v1/messages",
        headers={
            "x-api-key": ANTHROPIC_KEY,
            "anthropic-version": "2023-06-01",
            "content-type": "application/json",
        },
        json={
            "model": "claude-sonnet-4-20250514",
            "max_tokens": 1024,
            "messages": [{"role": "user", "content": prompt}],
        },
    )
    resp.raise_for_status()
    raw = resp.json()["content"][0]["text"].strip()
    match = re.search(r"\[.*\]", raw, re.DOTALL)
    if not match:
        raise ValueError(f"无法解析返回：{raw[:200]}")
    slugs = json.loads(match.group())
    if len(slugs) != len(titles):
        raise ValueError(f"数量不匹配：期望{len(titles)}，得到{len(slugs)}")
    return [slugify(s) for s in slugs]


def deduplicate(slug_map):
    count = defaultdict(int)
    result = {}
    for aid, slug in slug_map.items():
        count[slug] += 1
        result[aid] = slug if count[slug] == 1 else f"{slug}-{count[slug]}"
    return result


def update_slugs(slug_map, dry_run=False):
    for article_id, slug in slug_map.items():
        if dry_run:
            print(f"  [预览] id={article_id}  →  {slug}")
            continue
        url = f"{SUPABASE_URL}/rest/v1/news_articles?id=eq.{article_id}"
        resp = requests.patch(url, headers=supabase_headers(), json={"slug_en": slug})
        if resp.status_code not in (200, 204):
            print(f"  ⚠️  更新失败 id={article_id}: {resp.text}")
        else:
            print(f"  ✅  id={article_id}  →  {slug}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--limit", type=int, default=None)
    args = parser.parse_args()

    if not SUPABASE_KEY:
        print("❌ 请设置 SUPABASE_KEY 环境变量")
        return
    if not ANTHROPIC_KEY:
        print("❌ 请设置 ANTHROPIC_KEY 环境变量")
        return

    print("📡 正在读取 Supabase 文章...")
    articles = fetch_articles(limit=args.limit)
    print(f"   需要处理：{len(articles)} 篇\n")

    if not articles:
        print("✅ 所有文章已有英文 slug。")
        return

    slug_map = {}
    for i in range(0, len(articles), BATCH_SIZE):
        batch = articles[i:i+BATCH_SIZE]
        titles = [a["title"] for a in batch]
        ids    = [a["id"]    for a in batch]
        print(f"🔤 翻译第 {i+1}–{i+len(batch)} 篇...")
        try:
            slugs = translate_batch(titles)
        except Exception as e:
            print(f"  ❌ 失败，跳过：{e}")
            continue
        for aid, slug in zip(ids, slugs):
            slug_map[aid] = slug
        time.sleep(SLEEP_BETWEEN)

    slug_map = deduplicate(slug_map)
    print(f"\n💾 {'[预览]' if args.dry_run else '写入 Supabase'}...")
    update_slugs(slug_map, dry_run=args.dry_run)
    print(f"\n🎉 完成！共处理 {len(slug_map)} 篇。")


if __name__ == "__main__":
    main()
