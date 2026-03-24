#!/usr/bin/env python3
"""
从 Supabase 拉取所有文章，生成独立 HTML 页面 + 更新 sitemap + 生成 _redirects
优先使用 slug_en（英文 SEO slug），不存在时回退到中文 slugify
"""
import os, re, json, httpx
from datetime import datetime, timezone
from pathlib import Path

SUPABASE_URL = os.environ.get("SUPABASE_URL", "https://wioqkcrtkesntqnuzfkd.supabase.co")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_KEY") or os.environ.get("SUPABASE_ANON_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indpb3FrY3J0a2VzbnRxbnV6ZmtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwNjE5MTEsImV4cCI6MjA4OTYzNzkxMX0.V7RNM0XkkZt2k02v_ssZkChZBjat7emP4RrMtfsS0hY")
SITE_URL = "https://k1980.app"

BASE_DIR = Path(__file__).parent.parent
NEWS_DIR = BASE_DIR / "news"
TEMPLATE = (BASE_DIR / "article_template.html").read_text(encoding="utf-8")


def slugify_zh(title: str) -> str:
    """中文标题 → URL-safe slug（兜底用）"""
    title = title.lower()
    title = re.sub(r'[^\w\s-]', '', title)
    title = re.sub(r'[\s_]+', '-', title)
    title = re.sub(r'-+', '-', title).strip('-')
    return title[:80] or "article"


def get_slug(article: dict) -> str:
    """优先用 slug_en，无则用中文 slug"""
    en = (article.get("slug_en") or "").strip()
    if en:
        return en
    return slugify_zh(article.get("title", "article"))


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


def generate_page(article: dict):
    slug     = get_slug(article)
    zh_slug  = slugify_zh(article.get("title", "article"))
    tags_raw = article.get("tags") or []
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

    content_html = format_content(article.get("content") or article.get("summary", ""))
    title   = article.get("title", "")
    summary = article.get("summary", "")
    source  = article.get("source_name", "K1980")
    cat     = article.get("category", "")

    jsonld = json.dumps({
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": title,
        "description": summary,
        "url": f"{SITE_URL}/news/{slug}",
        "datePublished": date_iso,
        "publisher": {
            "@type": "Organization",
            "name": "K1980",
            "url": SITE_URL
        },
        "keywords": tags_csv
    }, ensure_ascii=False)

    html = TEMPLATE
    html = html.replace("{{TITLE}}", title)
    html = html.replace("{{SUMMARY}}", summary)
    html = html.replace("{{CONTENT}}", content_html)
    html = html.replace("{{CATEGORY}}", cat)
    html = html.replace("{{SOURCE}}", source)
    html = html.replace("{{DATE}}", date_str)
    html = html.replace("{{DATE_ISO}}", date_iso)
    html = html.replace("{{TAGS}}", tags_html)
    html = html.replace("{{SLUG}}", slug)
    html = html.replace("{{JSONLD}}", jsonld)

    return slug, zh_slug, html


def main():
    NEWS_DIR.mkdir(exist_ok=True)
    hdrs = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"}

    print("📥 拉取文章（含 slug_en）...")
    r = httpx.get(
        f"{SUPABASE_URL}/rest/v1/news_articles"
        "?is_published=eq.true"
        "&order=created_at.desc"
        "&limit=2000"
        "&select=id,title,summary,content,category,source_name,tags,created_at,slug_en",
        headers=hdrs, timeout=30
    )
    articles = r.json()
    if not isinstance(articles, list):
        print(f"❌ 拉取失败：{articles}")
        return
    print(f"共 {len(articles)} 篇文章")

    slugs          = []
    slug_seen      = {}
    redirect_lines = []

    for a in articles:
        slug, zh_slug, html = generate_page(a)

        # 去重：同名 slug 加 -2, -3 后缀
        if slug in slug_seen:
            slug_seen[slug] += 1
            slug = f"{slug}-{slug_seen[slug]}"
        else:
            slug_seen[slug] = 1

        path = NEWS_DIR / f"{slug}.html"
        path.write_text(html, encoding="utf-8")
        slugs.append((slug, zh_slug, a.get("created_at", "")))

        if slug != zh_slug and zh_slug:
            redirect_lines.append(f"/news/{zh_slug}  /news/{slug}  301")

    print(f"✅ 生成 {len(slugs)} 个页面")

    # ── sitemap ──────────────────────────────────────────────────
    urls = [
        '  <url>\n    <loc>https://k1980.app</loc>\n'
        '    <changefreq>hourly</changefreq>\n    <priority>1.0</priority>\n  </url>'
    ]
    for slug, _, created_at in slugs:
        date = created_at[:10] if created_at else ""
        urls.append(
            f'  <url>\n    <loc>{SITE_URL}/news/{slug}</loc>\n'
            f'    <lastmod>{date}</lastmod>\n'
            f'    <changefreq>weekly</changefreq>\n    <priority>0.8</priority>\n  </url>'
        )
    sitemap = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + '\n'.join(urls)
        + '\n</urlset>'
    )
    (BASE_DIR / "sitemap.xml").write_text(sitemap, encoding="utf-8")
    print(f"✅ sitemap 更新完成，共 {len(slugs)+1} 个 URL")

    # ── _redirects ───────────────────────────────────────────────
    if redirect_lines:
        redirects_path = BASE_DIR / "_redirects"
        existing = ""
        if redirects_path.exists():
            existing_lines = [
                l for l in redirects_path.read_text().splitlines()
                if l.strip() and not l.startswith("/news/")
            ]
            existing = "\n".join(existing_lines) + "\n" if existing_lines else ""

        content = existing + "\n".join(redirect_lines) + "\n"
        content += "\n# 兜底：未匹配路径回首页\n/news/*  /  302\n"
        redirects_path.write_text(content, encoding="utf-8")
        print(f"✅ _redirects 写入 {len(redirect_lines)} 条重定向规则")
    else:
        print("ℹ️  所有文章已有英文 slug，无需生成重定向")


if __name__ == "__main__":
    main()
