#!/usr/bin/env python3
"""
K1980 经纬专栏每日生成器
每天早上生成3篇深度报道，存入 data/jingwei.json
网站直接读取，稳定不变
"""

import json, os, time, requests
from datetime import datetime, timezone, date

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
OUTPUT_DIR = 'data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

TODAY = date.today().isoformat()

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
