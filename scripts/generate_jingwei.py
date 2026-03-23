#!/usr/bin/env python3
"""
K1980 经纬专栏每日生成器
每天早上生成3篇深度报道，存入 data/jingwei.json
网站直接读取，稳定不变
"""

import json, os, time, requests, hashlib
from datetime import datetime, timezone, date

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
OUTPUT_DIR = 'data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

TODAY = date.today().isoformat()

SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_KEY = os.environ.get('SUPABASE_SERVICE_KEY', '')

TOPICS = [
    {
        'tag':   '宏观经济',
        'color': '#c2410c',
        'bg':    'rgba(194,65,12,.08)',
        'prompt': f"""今天是{TODAY}。你是一位服务于海外华人高净值群体的首席经济学家，请写一篇今日深度报道。

主题：当前全球宏观经济形势与海外华人的资产配置策略

要求：
- 标题要有冲击力，让人想点击（20字内）
- 导语50字内，一句话抓住读者
- 正文600字，用###分3-4个小节
- 要有具体数据、真实逻辑、可操作建议
- 风格像《经济学人》：冷静、精准、有观点
- 结合今日最新市场动态

严格只返回JSON：{{"title":"","summary":"","body":"","tag":"宏观经济","date":"{TODAY}"}}"""
    },
    {
        'tag':   '产业洞察',
        'color': '#7c3aed',
        'bg':    'rgba(124,58,237,.08)',
        'prompt': f"""今天是{TODAY}。你是一位专注科技和产业的深度记者，请写一篇今日产业深度报道。

主题：当前最值得关注的科技或产业趋势，对海外华人从业者和投资者的影响

要求：
- 选一个今天最热的产业话题（AI/芯片/新能源/生物科技/任选）
- 标题要有冲击力（20字内）
- 导语50字内
- 正文600字，用###分3-4个小节
- 要有具体公司案例、数据支撑、前瞻判断
- 风格像《哈佛商业评论》特稿

严格只返回JSON：{{"title":"","summary":"","body":"","tag":"产业洞察","date":"{TODAY}"}}"""
    },
    {
        'tag':   '移民经济',
        'color': '#0891b2',
        'bg':    'rgba(8,145,178,.08)',
        'prompt': f"""今天是{TODAY}。你是一位专注海外华人生活与财富的专栏作家，请写一篇今日深度报道。

主题：新西兰/澳洲/加拿大/英国移民政策或本地经济动态，对华人社区的实际影响

要求：
- 选一个最新、最实用的话题
- 标题要让目标读者（海外华人）立刻感到相关（20字内）
- 导语50字内
- 正文600字，用###分3-4个小节
- 要有政策细节、真实案例、具体建议
- 风格犀利务实，不说废话

严格只返回JSON：{{"title":"","summary":"","body":"","tag":"移民经济","date":"{TODAY}"}}"""
    },
]

def generate_article(topic: dict) -> dict | None:
    try:
        resp = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key':         ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'content-type':      'application/json',
            },
            json={
                'model':    'claude-sonnet-4-20250514',
                'max_tokens': 1500,
                'messages': [{'role': 'user', 'content': topic['prompt']}],
            },
            timeout=60,
        )
        raw   = resp.json()['content'][0]['text']
        start = raw.find('{')
        end   = raw.rfind('}') + 1
        art   = json.loads(raw[start:end])
        art['color'] = topic['color']
        art['bg']    = topic['bg']
        print(f'  ✅ {topic["tag"]}: {art.get("title","?")}')
        return art
    except Exception as e:
        print(f'  ❌ {topic["tag"]}: {e}')
        return None

def publish_to_supabase(art):
    if not SUPABASE_URL or not SUPABASE_KEY:
        print("  ⚠️ 未配置 Supabase，跳过发布")
        return False
    guid = hashlib.md5((art["title"] + TODAY).encode()).hexdigest()
    payload = {
        "guid":         guid,
        "title":        art["title"],
        "summary":      art.get("summary", ""),
        "content":      art.get("body", ""),
        "category":     art.get("tag", "时事"),
        "tags":         [art.get("tag", "经纬")],
        "source_name":  "K1980经纬",
        "original_url": "#",
        "is_published": True,
        "is_jingwei":   True,
        "view_count":   100,
        "created_at":   datetime.now(timezone.utc).isoformat(),
    }
    hdrs = {
        "apikey":        SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type":  "application/json",
        "Prefer":        "return=minimal",
    }
    try:
        r = requests.post(f"{SUPABASE_URL}/rest/v1/news_articles", json=payload, headers=hdrs, timeout=15)
        if r.status_code in (200, 201):
            print(f"  ☁️ 已发布到 Supabase")
            return True
        elif r.status_code == 409:
            print(f"  ⏭ Supabase 已存在")
            return False
        else:
            print(f"  ❌ Supabase 错误 {r.status_code}: {r.text[:200]}")
            return False
    except Exception as e:
        print(f"  ❌ Supabase 异常: {e}")
        return False

if __name__ == '__main__':
    print(f'🚀 经纬专栏生成器')
    print(f'📅 {TODAY}')

    if not ANTHROPIC_API_KEY:
        print('❌ 未设置 ANTHROPIC_API_KEY')
        exit(1)

    articles = []
    for topic in TOPICS:
        print(f'\n📝 生成「{topic["tag"]}」...')
        art = generate_article(topic)
        if art:
            articles.append(art)
            publish_to_supabase(art)
        time.sleep(2)

    output = {
        'date':       TODAY,
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'articles':   articles,
    }

    path = os.path.join(OUTPUT_DIR, 'jingwei.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f'\n✅ 完成！{len(articles)} 篇文章保存至 {path}')
