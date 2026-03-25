import os, httpx, anthropic
from datetime import datetime, timezone, timedelta

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_KEY = os.environ["SUPABASE_KEY"]
HEADERS = {"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}", "Content-Type": "application/json"}

def fetch_articles():
    since = (datetime.now(timezone.utc) - timedelta(hours=48)).isoformat()
    r = httpx.get(f"{SUPABASE_URL}/rest/v1/news_articles?is_published=eq.true&created_at=gte.{since}&order=view_count.desc&limit=15&select=title,summary,category", headers=HEADERS)
    return r.json() if r.ok else []

def generate(articles):
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    today = datetime.now(timezone(timedelta(hours=8))).strftime("%Y年%m月%d日")
    art_list = "\n".join([f"【{a['category']}】{a['title']}：{(a['summary'] or '')[:80]}" for a in articles[:12]])
    msg = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=3000,
        messages=[{"role": "user", "content": f"""你是K1980全球华人决策信息平台首席编辑。今天{today}。

以下是过去48小时热门文章：
{art_list}

生成「今日必读｜{today} 全球华人关键资讯」，要求：
- 开篇2句话点出今日最重要大势
- 分5个板块（时事/移民/财经/科技/生活），每板块3条要点，每条60-100字
- 结尾「今日决策建议」针对移民申请者/投资者/海外工作者各一句
- 文风专业有温度，1500-2000字，Markdown格式
- 直接输出正文，不要前言"""}]
    )
    return msg.content[0].text

def publish(content):
    today = datetime.now(timezone(timedelta(hours=8)))
    title = f"今日必读｜{today.strftime('%Y年%m月%d日')} 全球华人关键资讯"
    summary_r = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"]).messages.create(
        model="claude-sonnet-4-20250514", max_tokens=150,
        messages=[{"role": "user", "content": f"用60字概括核心内容：{content[:800]}"}]
    )
    summary = summary_r.content[0].text
    r = httpx.post(f"{SUPABASE_URL}/rest/v1/news_articles",
        headers={**HEADERS, "Prefer": "return=minimal"},
        json={"title": title, "summary": summary, "content": content,
              "category": "时事", "source_name": "K1980 AI简报",
              "tags": ["每日简报","今日必读","全球华人"],
              "original_url": "#", "is_published": True, "is_jingwei": True,
              "view_count": 0, "published_at": today.isoformat()})
    print("✅ 发布成功" if r.is_success else f"❌ 失败: {r.text}")

articles = fetch_articles()
print(f"抓取 {len(articles)} 篇文章")
if articles:
    content = generate(articles)
    publish(content)
