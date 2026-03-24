#!/usr/bin/env python3
"""
从 Supabase 拉取所有文章，生成独立 HTML 页面 + sitemap + _redirects
支持双语：优先用 slug_en 作路径，注入 title_en/summary_en/content_en
"""
import os, re, json, httpx
from datetime import datetime
from pathlib import Path

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://wioqkcrtkesntqnuzfkd.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indpb3FrY3J0a2VzbnRxbnV6ZmtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwNjE5MTEsImV4cCI6MjA4OTYzNzkxMX0.V7RNM0XkkZt2k02v_ssZkChZBjat7emP4RrMtfsS0hY")
SITE_URL = "https://k1980.app"

BASE_DIR  = Path(__file__).parent.parent
NEWS_DIR  = BASE_DIR / "news"
TEMPLATE  = (BASE_DIR / "article_template.html").read_text(encoding="utf-8")


def slugify_zh(title: str) -> str:
    title = title.lower()
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'[\s_]+', '-', title)
    title = re.sub(r'-+', '-', title).strip('-')
    return title[:80] or "article"


def get_slug(article: dict) -> str:
    en = (article.get("slug_en") or "").strip()
    return en if en else slugify_zh(article.get("title", "article"))


def format_content(content: str) -> str:
    if not content:
        return ""
    html = ""
    for p in content.split('\n\n'):
        p = p.strip()
        if not p:
            continue
        p = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', p)
        if p.startswith('###'):
            html += f"<h3>{p[3:].strip()}</h3>\n"
        elif p.startswith('##'):
            html += f"<h2>{p[2:].strip()}</h2>\n"
        else:
            html += f"<p>{p}</p>\n"
    return html


def generate_page(article: dict):
    slug    = get_slug(article)
    zh_slug = slugify_zh(article.get("title", "article"))

    tags_raw  = article.get("tags") or []
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in tags_raw)
    tags_csv  = ", ".join(tags_raw)

    date_str = date_iso = ""
    if article.get("created_at"):
        try:
            dt = datetime.fromisoformat(article["created_at"].replace("Z", "+00:00"))
            date_str = dt.strftime("%Y年%m月%d日")
            date_iso = dt.strftime("%Y-%m-%dT%H:%M:%S+00:00")
        except Exception:
            pass

    title   = article.get("title", "")
    summary = article.get("summary", "")
    source  = article.get("source_name", "K1980")
    cat     = article.get("category", "")

    # 英文内容
    title_en   = article.get("title_en") or ""
    summary_en = article.get("summary_en") or ""
    content_en = format_content(article.get("content_en") or "")
    has_en     = "true" if title_en else "false"

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": title,
        "description": summary,
        "url": f"{SITE_URL}/news/{slug}",
        "datePublished": date_iso,
        "inLanguage": ["zh", "en"] if title_en else ["zh"],
        "publisher": {"@type": "Organization", "name": "K1980", "url": SITE_URL},
        "keywords": tags_csv
    }, ensure_ascii=False)

    html = TEMPLATE
    html = html.replace("{{TITLE}}",      title)
    html = html.replace("{{TITLE_EN}}",   title_en)
    html = html.replace("{{SUMMARY}}",    summary)
    html = html.replace("{{SUMMARY_EN}}", summary_en)
    html = html.replace("{{CONTENT}}",    format_content(article.get("content") or summary))
    html = html.replace("{{CONTENT_EN}}", content_en)
    html = html.replace("{{CATEGORY}}",   cat)
    html = html.replace("{{SOURCE}}",     source)
    html = html.replace("{{DATE}}",       date_str)
    html = html.replace("{{DATE_ISO}}",   date_iso)
    html = html.replace("{{TAGS}}",       tags_html)
    html = html.replace("{{SLUG}}",       slug)
    html = html.replace("{{JSONLD}}",     jsonld)
    html = html.replace("{{HAS_EN}}",     has_en)

    return slug, zh_slug, html


def main():
    NEWS_DIR.mkdir(exist_ok=True)
    hdrs = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

    print("📥 拉取文章（含双语字段）...")
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/news_articles"
        "?is_published=eq.true"
        "&order=created_at.desc"
        "&limit=2000"
        "&select=id,title,title_en,summary,summary_en,content,content_en,"
        "category,source_name,tags,created_at,slug_en",
        headers=hdrs, timeout=30
    )
    articles = r.json()
    if not isinstance(articles, list):
        print(f"❌ 拉取失败：{articles}"); return
    print(f"共 {len(articles)} 篇文章")

    slugs = []
    slug_seen = {}
    redirect_lines = []

    for a in articles:
        slug, zh_slug, html = generate_page(a)
        if slug in slug_seen:
            slug_seen[slug] += 1
            slug = f"{slug}-{slug_seen[slug]}"
        else:
            slug_seen[slug] = 1

        (NEWS_DIR / f"{slug}.html").write_text(html, encoding="utf-8")
        slugs.append((slug, zh_slug, a.get("created_at", "")))
        if slug != zh_slug and zh_slug:
            redirect_lines.append(f"/news/{zh_slug}  /news/{slug}  301")

    print(f"✅ 生成 {len(slugs)} 个页面")

    # sitemap
    urls = ['  <url>\n    <loc>https://k1980.app</loc>\n    <changefreq>hourly</changefreq>\n    <priority>1.0</priority>\n  </url>']
    for slug, _, created_at in slugs:
        date = created_at[:10] if created_at else ""
        urls.append(f'  <url>\n    <loc>{SITE_URL}/news/{slug}</loc>\n    <lastmod>{date}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>')
    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>'
    (BASE_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print(f"✅ sitemap 更新，共 {len(slugs)+1} 个 URL")

    # _redirects
    if redirect_lines:
        redirects_path = BASE_DIR / "_redirects"
        existing = ""
        if redirects_path.exists():
            existing_lines = [l for l in redirects_path.read_text().splitlines() if l.strip() and not l.startswith("/news/")]
            existing = "\n".join(existing_lines) + "\n" if existing_lines else ""
        content = existing + "\n".join(redirect_lines) + "\n/news/*  /  302\n"
        redirects_path.write_text(content, encoding="utf-8")
        print(f"✅ _redirects 写入 {len(redirect_lines)} 条")


if __name__ == "__main__":
    main()
