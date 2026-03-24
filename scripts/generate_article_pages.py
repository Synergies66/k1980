#!/usr/bin/env python3
"""
从 Supabase 拉取所有文章，生成独立 HTML 页面 + 更新 sitemap
"""
import os, re, json, httpx
from datetime import datetime, timezone
from pathlib import Path

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://wioqkcrtkesntqnuzfkd.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indpb3FrY3J0a2VzbnRxbnV6ZmtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwNjE5MTEsImV4cCI6MjA4OTYzNzkxMX0.V7RNM0XkkZt2k02v_ssZkChZBjat7emP4RrMtfsS0hY")

BASE_DIR = Path(__file__).parent.parent
NEWS_DIR = BASE_DIR / "news"
TEMPLATE = (BASE_DIR / "article_template.html").read_text(encoding="utf-8")

def slugify(title: str) -> str:
    title = title.lower()
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'[\s_]+', '-', title)
    title = re.sub(r'-+', '-', title).strip('-')
    return title[:80] or "article"

def format_content(content: str) -> str:
    if not content:
        return ""
    paragraphs = content.split('\n\n')
    html = ""
    for p in paragraphs:
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

def generate_page(article: dict) -> str:
    slug = slugify(article.get("title", "article"))
    tags_html = "".join(f'<span class="tag">{t}</span>' for t in (article.get("tags") or []))
    date_str = ""
    if article.get("created_at"):
        try:
            dt = datetime.fromisoformat(article["created_at"].replace("Z", "+00:00"))
            date_str = dt.strftime("%Y-%m-%d")
        except:
            pass
    content_html = format_content(article.get("content") or article.get("summary", ""))
    html = TEMPLATE
    html = html.replace("{{TITLE}}", article.get("title", ""))
    html = html.replace("{{SUMMARY}}", article.get("summary", ""))
    html = html.replace("{{CONTENT}}", content_html)
    html = html.replace("{{CATEGORY}}", article.get("category", ""))
    html = html.replace("{{SOURCE}}", article.get("source_name", "K1980"))
    html = html.replace("{{DATE}}", date_str)
    html = html.replace("{{TAGS}}", tags_html)
    html = html.replace("{{SLUG}}", slug)
    return slug, html

def main():
    NEWS_DIR.mkdir(exist_ok=True)
    hdrs = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}
    print("📥 拉取文章...")
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/news_articles?is_published=eq.true&order=created_at.desc&limit=1000&select=id,title,summary,content,category,source_name,tags,created_at",
        headers=hdrs, timeout=30
    )
    articles = r.json()
    print(f"共 {len(articles)} 篇文章")

    slugs = []
    for a in articles:
        slug, html = generate_page(a)
        path = NEWS_DIR / f"{slug}.html"
        path.write_text(html, encoding="utf-8")
        slugs.append((slug, a.get("created_at", "")))

    print(f"✅ 生成 {len(slugs)} 个页面")

    # 更新 sitemap
    urls = ['  <url>\n    <loc>https://k1980.app</loc>\n    <changefreq>hourly</changefreq>\n    <priority>1.0</priority>\n  </url>']
    for slug, created_at in slugs:
        date = created_at[:10] if created_at else ""
        urls.append(f'  <url>\n    <loc>https://k1980.app/news/{slug}</loc>\n    <lastmod>{date}</lastmod>\n    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>')

    sitemap = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sitemap += '\n'.join(urls)
    sitemap += '\n</urlset>'
    (BASE_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print(f"✅ sitemap 更新完成，共 {len(slugs)+1} 个 URL")

if __name__ == "__main__":
    main()
