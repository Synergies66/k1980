#!/usr/bin/env python3
import os,json,re,time,hashlib,feedparser,httpx
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
    {"url":"https://news.google.com/rss/search?q=federal+reserve+interest+rate&hl=en-US&gl=US&ceid=US:en","cat":"财经"},
    {"url":"https://news.google.com/rss/search?q=stock+market+wall+street&hl=en-US&gl=US&ceid=US:en","cat":"财经"},
    {"url":"https://news.google.com/rss/search?q=china+yuan+economy+trade&hl=en-US&gl=US&ceid=US:en","cat":"财经"},
    {"url":"https://news.google.com/rss/search?q=immigration+visa+h1b+policy&hl=en-US&gl=US&ceid=US:en","cat":"移民"},
    {"url":"https://news.google.com/rss/search?q=housing+market+mortgage+rate&hl=en-US&gl=US&ceid=US:en","cat":"财经"},
]

PROMPT="""你是 K1980 资深编辑，为全球海外华人写深度分析文章。

读者关心：这对我的工作/投资/签证/生活有什么影响？

严格按以下JSON格式输出，不要任何多余文字：
{"title":"15字以内标题","summary":"100字摘要","content":"800-1200字正文，小节标题用**粗体**","tags":["标签1","标签2","标签3"],"category":"科技或财经或移民或时事"}"""

PRIORITY_KW=["chinese","china","immigrant","visa","fed","rate","ai","nvidia","openai","layoff","housing","inflation","australia","new zealand","canada","uk","tariff"]

def fetch_headlines():
    headlines=[]
    for src in SOURCES:
        try:
            feed=feedparser.parse(src["url"],agent="Mozilla/5.0")
            for e in feed.entries[:4]:
                t=e.get("title","").strip()
                if not t:continue
                headlines.append({"title":t,"summary":e.get("summary","")[:300],"category":src["cat"],"link":e.get("link","")})
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

def extract_json(text):
    text=text.strip()
    # 移除markdown代码块
    text=re.sub(r"^```(?:json)?\s*","",text)
    text=re.sub(r"\s*```$","",text)
    text=text.strip()
    # 找到第一个{到最后一个}
    start=text.find("{")
    end=text.rfind("}")
    if start>=0 and end>start:
        text=text[start:end+1]
    return json.loads(text)

def write(h):
    try:
        msg=client.messages.create(
            model="claude-sonnet-4-20250514",max_tokens=2500,
            messages=[{"role":"user","content":f"新闻标题：{h['title']}
新闻摘要：{h['summary'][:200]}
建议分类：{h['category']}

{PROMPT}"}]
        )
        raw=msg.content[0].text
        return extract_json(raw)
    except Exception as e:
        print(f"  ⚠️ {e}");return None

def publish(article,link):
    guid=hashlib.md5((article["title"]+datetime.now().strftime("%Y-%m-%d")).encode()).hexdigest()
    payload={
        "guid":guid,
        "title":article["title"],
        "summary":article["summary"],
        "content":article["content"],
        "category":article.get("category","科技"),
        "tags":article.get("tags",[]),
        "source_name":"K1980 深度",
        "original_url":link or "#",
        "is_published":True,
        "is_jingwei":False,
        "view_count":100,
        "created_at":datetime.now(timezone.utc).isoformat()
    }
    hdrs={"apikey":SUPABASE_KEY,"Authorization":f"Bearer {SUPABASE_KEY}","Content-Type":"application/json","Prefer":"return=minimal"}
    try:
        r=httpx.post(f"{SUPABASE_URL}/rest/v1/news_articles",json=payload,headers=hdrs,timeout=15)
        if r.status_code in(200,201):return True
        elif r.status_code==409:print("  ⏭ 已存在");return False
        else:print(f"  ❌ {r.status_code}: {r.text[:300]}");return False
    except Exception as e:print(f"  ❌ {e}");return False

def main():
    print(f"
🖊 K1980 深度稿件生成器
⏰ {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
")
    headlines=fetch_headlines()
    headlines.sort(key=score,reverse=True)
    selected=headlines[:ARTICLES_PER_RUN]
    print(f"📋 选定 {len(selected)} 个选题：")
    for i,h in enumerate(selected,1):print(f"  {i}. [{h['category']}] {h['title'][:60]}")
    published=0
    for i,h in enumerate(selected,1):
        print(f"
── [{i}/{len(selected)}] {h['title'][:50]}...")
        art=write(h)
        if not art:print("  ⚠️ 跳过");continue
        print(f"  📝 {art.get('title','')}")
        if publish(art,h["link"]):
            published+=1
            print(f"  ✅ 已发布")
        time.sleep(2)
    print(f"
🎉 完成！发布 {published}/{len(selected)} 篇")

if __name__=="__main__":main()
