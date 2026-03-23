#!/usr/bin/env python3
import os,json,time,hashlib,feedparser,httpx
from datetime import datetime,timezone
from anthropic import Anthropic

ANTHROPIC_KEY=os.environ["ANTHROPIC_API_KEY"]
SUPABASE_URL=os.environ["SUPABASE_URL"]
SUPABASE_KEY=os.environ["SUPABASE_SERVICE_KEY"]
ARTICLES_PER_RUN=int(os.environ.get("ARTICLES_PER_RUN","5"))
client=Anthropic(api_key=ANTHROPIC_KEY)

SOURCES=[
    {"url":"https://feeds.reuters.com/reuters/technologyNews","cat":"科技"},
    {"url":"https://news.google.com/rss/search?q=AI+artificial+intelligence&hl=en-US&gl=US&ceid=US:en","cat":"科技"},
    {"url":"https://news.google.com/rss/search?q=semiconductor+nvidia+chip&hl=en-US&gl=US&ceid=US:en","cat":"科技"},
    {"url":"https://news.google.com/rss/search?q=federal+reserve+interest+rate+economy&hl=en-US&gl=US&ceid=US:en","cat":"财经"},
    {"url":"https://news.google.com/rss/search?q=stock+market+wall+street&hl=en-US&gl=US&ceid=US:en","cat":"财经"},
    {"url":"https://news.google.com/rss/search?q=china+yuan+economy+trade&hl=en-US&gl=US&ceid=US:en","cat":"财经"},
    {"url":"https://news.google.com/rss/search?q=immigration+visa+h1b+policy&hl=en-US&gl=US&ceid=US:en","cat":"移民"},
    {"url":"https://news.google.com/rss/search?q=housing+market+mortgage+rate&hl=en-US&gl=US&ceid=US:en","cat":"财经"},
    {"url":"https://news.google.com/rss/search?q=australia+new+zealand+canada+chinese+community&hl=en&gl=US&ceid=US:en","cat":"时事"},
]

PROMPT="""你是 K1980 资深编辑，为全球华人（新西兰/澳洲/美国/英国/加拿大）写深度分析文章。

读者关心：这对我的工作/投资/签证/生活有什么影响？背后原因？我该怎么应对？

要求：
1. 标题15字内，点明华人影响，有冲击力
2. 正文800-1200字，分3-4小节，小节标题用**粗体**
3. 开篇用具体数据或场景（不用"近日"开头）
4. 背景→影响→应对三段递进
5. 语言自然流畅，专业但不晦涩
6. 严格政治中立

输出严格JSON：
{"title":"标题","summary":"100字华人影响摘要","content":"正文含**小节标题**","tags":["标签1","标签2","标签3"],"category":"分类"}

只输出JSON，不要任何前缀。"""

PRIORITY_KW=["chinese","china","immigrant","visa","fed","rate","ai","nvidia","openai","layoff","housing","inflation","australia","new zealand","canada","uk","overseas","tariff","trump"]

def fetch_headlines():
    headlines=[]
    for src in SOURCES:
        try:
            feed=feedparser.parse(src["url"],agent="Mozilla/5.0")
            for e in feed.entries[:4]:
                t=e.get("title","").strip()
                if not t:continue
                headlines.append({"title":t,"summary":e.get("summary","")[:300],"category":src["cat"],"source":src["url"].split("/")[2],"link":e.get("link","")})
        except:pass
        time.sleep(0.5)
    seen,unique=set(),[]
    for h in headlines:
        k=h["title"][:20]
        if k not in seen:seen.add(k);unique.append(h)
    print(f"✅ 抓到 {len(unique)} 条热点")
    return unique

def score(h):
    text=(h["title"]+" "+h["summary"]).lower()
    s=sum(2 for kw in PRIORITY_KW if kw in text)
    if h["category"] in("财经","科技"):s+=3
    return s

def write(h):
    try:
        msg=client.messages.create(model="claude-sonnet-4-20250514",max_tokens=2000,
            messages=[{"role":"user","content":f"新闻：{h['title']}\n摘要：{h['summary']}\n分类：{h['category']}\n\n{PROMPT}"}])
        raw=msg.content[0].text.strip()
        if raw.startswith("```"):raw=raw.split("```")[1];raw=raw[4:] if raw.startswith("json") else raw
        return json.loads(raw.strip().rstrip("`"))
    except Exception as e:
        print(f"  ⚠️ {e}");return None

def publish(article,link):
    guid=hashlib.md5((article["title"]+datetime.now().strftime("%Y-%m-%d")).encode()).hexdigest()
    payload={"guid":guid,"title":article["title"],"summary":article["summary"],"content":article["content"],
        "category":article["category"],"tags":article.get("tags",[]),"source_name":"K1980 深度",
        "original_url":link or "#","is_published":True,"is_jingwei":True,"view_count":100,
        "created_at":datetime.now(timezone.utc).isoformat()}
    hdrs={"apikey":SUPABASE_KEY,"Authorization":f"Bearer {SUPABASE_KEY}","Content-Type":"application/json","Prefer":"return=minimal"}
    try:
        r=httpx.post(f"{SUPABASE_URL}/rest/v1/news_articles",json=payload,headers=hdrs,timeout=15)
        if r.status_code in(200,201):return True
        elif r.status_code==409:print("  ⏭ 已存在");return False
        else:print(f"  ❌ {r.status_code}");return False
    except Exception as e:print(f"  ❌ {e}");return False

def main():
    print(f"\n🖊 K1980 深度稿件生成器\n⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}\n")
    headlines=fetch_headlines()
    headlines.sort(key=score,reverse=True)
    selected=headlines[:ARTICLES_PER_RUN]
    print(f"\n📋 选定 {len(selected)} 个选题：")
    for i,h in enumerate(selected,1):print(f"  {i}. [{h['category']}] {h['title'][:60]}")
    published=0
    for i,h in enumerate(selected,1):
        print(f"\n── [{i}/{len(selected)}] {h['title'][:50]}...")
        art=write(h)
        if not art:continue
        print(f"  📝 {art.get('title','')}")
        if publish(art,h["link"]):published+=1
        time.sleep(2)
    print(f"\n🎉 完成！发布 {published}/{len(selected)} 篇")

if __name__=="__main__":main()
