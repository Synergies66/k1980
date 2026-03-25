import httpx, json, time

SUPABASE_URL = 'https://wioqkcrtkesntqnuzfkd.supabase.co'
SUPABASE_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Indpb3FrY3J0a2VzbnRxbnV6ZmtkIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQwNjE5MTEsImV4cCI6MjA4OTYzNzkxMX0.V7RNM0XkkZt2k02v_ssZkChZBjat7emP4RrMtfsS0hY'
ANTHROPIC_KEY = 'REMOVED_API_KEY'

HEADERS = {'apikey': SUPABASE_KEY, 'Authorization': f'Bearer {SUPABASE_KEY}', 'Content-Type': 'application/json'}

def fetch_untranslated(offset=0):
    url = f"{SUPABASE_URL}/rest/v1/news_articles?is_published=eq.true&content_en=is.null&select=id,content&order=id.asc&limit=5&offset={offset}"
    r = httpx.get(url, headers=HEADERS)
    return r.json() if r.is_success else []

def translate_content(id, content):
    if not content or len(content) < 10:
        return None
    r = httpx.post(
        'https://api.anthropic.com/v1/messages',
        headers={'x-api-key': ANTHROPIC_KEY, 'anthropic-version': '2023-06-01', 'content-type': 'application/json'},
        json={'model': 'claude-haiku-4-5-20251001', 'max_tokens': 2000,
              'messages': [{'role': 'user', 'content': f'Translate this Chinese news article to English. Keep markdown formatting. Return only the translation:\n\n{content[:2000]}'}]},
        timeout=60
    )
    return r.json()['content'][0]['text']

def update(id, content_en):
    url = f"{SUPABASE_URL}/rest/v1/news_articles?id=eq.{id}"
    r = httpx.patch(url, headers=HEADERS, json={'content_en': content_en})
    return r.is_success

total = 0
offset = 0
while True:
    articles = fetch_untranslated(offset)
    if not articles:
        print(f"✅ 完成！共翻译 {total} 篇")
        break
    for a in articles:
        try:
            en = translate_content(a['id'], a['content'])
            if en and update(a['id'], en):
                total += 1
                print(f"✓ {a['id']} ({total}篇)")
        except Exception as e:
            print(f"✗ {a['id']}: {e}")
        time.sleep(0.5)
    offset += 5
