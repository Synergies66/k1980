import httpx, json, time

SUPABASE_URL = 'https://wioqkcrtkesntqnuzfkd.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indpb3FrY3J0a2VzbnRxbnV6ZmtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwNjE5MTEsImV4cCI6MjA4OTYzNzkxMX0.V7RNM0XkkZt2k02v_ssZkChZBjat7emP4RrMtfsS0hY'
ANTHROPIC_KEY = os.environ.get('ANTHROPIC_API_KEY', '')

HEADERS = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}', 'Content-Type': 'application/json'}

def fetch_untranslated(offset=0, limit=20):
    url = f"{SUPABASE_URL}/rest/v1/news_articles?is_published=eq.true&title_en=is.null&select=id,title,summary&order=id.asc&limit={limit}&offset={offset}"
    r = httpx.get(url, headers=HEADERS)
    return r.json() if r.is_success else []

def translate_batch(articles):
    titles = '\n'.join([f"{a['id']}|||{a['title']}|||{a['summary'] or ''}" for a in articles])
    prompt = f"""Translate the following Chinese news article titles and summaries to English.
Each line format: ID|||title|||summary
Return ONLY a JSON array, no other text:
[{{"id": 123, "title_en": "...", "summary_en": "..."}}]

Articles:
{titles}"""

    r = httpx.post(
        'https://api.anthropic.com/v1/messages',
        headers={'x-api-key': ANTHROPIC_KEY, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'},
        json={'model': 'claude-haiku-4-5-20251001', 'max_tokens': 4000, 'messages': [{'role': 'user', 'content': prompt}]},
        timeout=60
    )
    text = r.json()['content'][0]['text'].strip()
    # 清理可能的markdown
    if text.startswith('```'):
        text = text.split('```')[1]
        if text.startswith('json'):
            text = text[4:]
    return json.loads(text.strip())

def update_article(id, title_en, summary_en):
    url = f"{SUPABASE_URL}/rest/v1/news_articles?id=eq.{id}"
    r = httpx.patch(url, headers=HEADERS, json={'title_en': title_en, 'summary_en': summary_en})
    return r.is_success

total = 0
offset = 0
batch_size = 15

while True:
    articles = fetch_untranslated(offset, batch_size)
    if not articles:
        print(f"✅ 完成！共翻译 {total} 篇")
        break
    
    print(f"翻译第 {offset+1}-{offset+len(articles)} 篇...")
    try:
        translated = translate_batch(articles)
        for t in translated:
            if update_article(t['id'], t['title_en'], t['summary_en']):
                total += 1
        print(f"  ✓ 成功 {len(translated)} 篇")
    except Exception as e:
        print(f"  ✗ 错误: {e}")
    
    offset += batch_size
    time.sleep(1)  # 避免限流
