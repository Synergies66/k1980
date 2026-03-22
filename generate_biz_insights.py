#!/usr/bin/env python3
"""
K1980 商业洞察每日生成器
每天自动调用 Claude API 生成 8-10 家企业深度分析
覆盖：500强、热点企业、小而精的技术隐形冠军
"""

import json, os, random, time, datetime, requests

ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
OUTPUT_DIR = 'data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 企业候选池 ────────────────────────────────────────────────
# 每天从各类别各选若干家，保证多样性

COMPANIES = {

    # 全球500强 / 科技巨头
    'mega_tech': [
        'Apple 苹果', 'Microsoft 微软', 'NVIDIA 英伟达', 'Google Alphabet',
        'Amazon 亚马逊', 'Meta', 'Tesla 特斯拉', 'Samsung 三星',
        'TSMC 台积电', 'ASML', 'Intel 英特尔', 'Qualcomm 高通',
        'Broadcom 博通', 'AMD', 'SAP', 'Oracle 甲骨文',
    ],

    # 中国头部企业
    'china_major': [
        '腾讯 Tencent', '阿里巴巴 Alibaba', '华为 Huawei', '比亚迪 BYD',
        '字节跳动 ByteDance', '小米 Xiaomi', '美团 Meituan', '拼多多 PDD',
        '宁德时代 CATL', '大疆 DJI', '百度 Baidu', '京东 JD.com',
        '中芯国际 SMIC', '商汤科技 SenseTime',
    ],

    # 新兴热点企业
    'hot_startups': [
        'OpenAI', 'Anthropic', 'xAI（马斯克）', 'Mistral AI',
        'Perplexity AI', 'Scale AI', 'Cohere', 'Stability AI',
        'Stripe', 'Databricks', 'Snowflake', 'Palantir',
        'SpaceX', 'Rivian', 'Lucid Motors', 'QuantumScape',
        'DeepMind', 'Figure AI（人形机器人）', '1X Technologies',
    ],

    # 小而精的技术隐形冠军（这是亮点！）
    'hidden_champions': [
        # 半导体/材料
        'ASML（光刻机垄断者）', 'Entegris（半导体材料）', 'Axcelis Technologies',
        'Onto Innovation', 'Cohu（半导体测试）', 'Veeco Instruments',
        # 工业软件
        'PTC Inc（工业软件）', 'Ansys（仿真软件）', 'Altair Engineering',
        'Hexagon AB（精密测量）', 'FARO Technologies',
        # 医疗科技
        'Intuitive Surgical（手术机器人）', 'Insulet（胰岛素泵）',
        'Penumbra（神经介入）', 'Invacare', 'Natus Medical',
        # 网络安全
        'Cloudflare', 'Zscaler', 'CrowdStrike', 'SentinelOne',
        'Varonis Systems', 'Qualys', 'Rapid7',
        # 垂直SaaS
        'Veeva Systems（医药SaaS）', 'Procore（建筑SaaS）',
        'Samsara（物联网）', 'Clio（法律SaaS）', 'Toast（餐饮SaaS）',
        # 新材料/新能源
        'Wolfspeed（碳化硅）', 'Enovis（医疗器械）',
        'Array Technologies（太阳能追踪）', 'Bloom Energy（固态燃料电池）',
        # 亚太隐形冠军
        'Keyence（传感器）', 'SMC Corporation（气动元件）',
        'Shimano（自行车零件）', 'Advantest（芯片测试）',
        '信越化学 Shin-Etsu（硅片）', '迪思科 Disco（晶圆切割）',
        # 新西兰/澳洲本地
        'Xero（会计SaaS）', 'WiseTech Global（物流科技）',
        'Appen（AI数据标注）', 'Pushpay（教会支付）',
        'Fisher & Paykel Healthcare（呼吸器械）',
    ],

    # 传统行业转型
    'transformation': [
        'John Deere（农业科技化）', 'Caterpillar（工程机械数字化）',
        'Siemens（工业数字化）', 'Honeywell（智能楼宇）',
        'Rolls-Royce（发动机即服务）', 'Michelin（轮胎即服务）',
        'Maersk（航运数字化）', 'Hitachi（社会创新）',
    ],
}

# ── 每日精选逻辑 ──────────────────────────────────────────────
def pick_daily_companies() -> list:
    """每天根据日期种子选取不同企业，保证多样性"""
    today = datetime.date.today()
    seed  = today.toordinal()
    rng   = random.Random(seed)

    selected = []
    # 每类别各取若干
    quotas = {
        'mega_tech':       2,
        'china_major':     2,
        'hot_startups':    2,
        'hidden_champions': 3,  # 重点推隐形冠军
        'transformation':  1,
    }
    for cat, n in quotas.items():
        pool = COMPANIES[cat]
        picks = rng.sample(pool, min(n, len(pool)))
        selected.extend(picks)

    rng.shuffle(selected)
    return selected

# ── Claude API 调用 ────────────────────────────────────────────
def analyze_company(company: str) -> dict | None:
    prompt = f"""你是顶级商业分析师。请对「{company}」进行深度分析，严格只返回JSON，不要有任何其他文字：

{{
  "company": "企业标准名称",
  "company_en": "英文名",
  "emoji": "最代表该企业的单个emoji",
  "tagline": "一句话定位（15字内）",
  "industry": "所属行业",
  "sub_industry": "细分赛道",
  "founded": "创立年份",
  "market_cap": "当前市值或估值",
  "employees": "员工规模",
  "hq": "总部城市,国家",
  "revenue": "年营收（估算）",
  "type": "mega_tech/china/startup/hidden_champion/transformation 之一",
  "scores": {{
    "innovation": 85,
    "growth": 78,
    "moat": 90,
    "global_reach": 75
  }},
  "tech_highlights": [
    "核心技术亮点1（35字内，具体有数据更好）",
    "核心技术亮点2（35字内）",
    "核心技术亮点3（35字内）"
  ],
  "industry_position": "行业地位（100字内，市场份额、竞争壁垒、护城河、与竞争对手对比）",
  "growth_story": "成长历程（120字内，创始背景、关键转折点、重要里程碑、如何成为今天的规模）",
  "biz_opportunities": [
    "商业机会或投资逻辑1（35字内）",
    "商业机会或投资逻辑2（35字内）",
    "商业机会或投资逻辑3（35字内）"
  ],
  "research_insights": "产业研究洞察（120字内，行业趋势、产业链地位、上下游关系、未来3-5年展望、对华人投资者/从业者的意义）",
  "why_matters_chinese": "与海外华人的关联（60字内，就业机会/投资价值/生活影响）",
  "risks": ["主要风险1（25字内）", "主要风险2（25字内）"],
  "competitors": ["竞争对手1", "竞争对手2", "竞争对手3"],
  "tags": ["标签1", "标签2", "标签3", "标签4", "标签5"]
}}"""

    try:
        resp = requests.post(
            'https://api.anthropic.com/v1/messages',
            headers={
                'x-api-key':         ANTHROPIC_API_KEY,
                'anthropic-version': '2023-06-01',
                'content-type':      'application/json',
            },
            json={
                'model':      'claude-sonnet-4-20250514',
                'max_tokens': 1500,
                'messages':   [{'role': 'user', 'content': prompt}],
            },
            timeout=60,
        )
        raw  = resp.json()['content'][0]['text']
        # 提取 JSON
        start = raw.find('{')
        end   = raw.rfind('}') + 1
        data  = json.loads(raw[start:end])
        data['generated_at'] = datetime.datetime.utcnow().isoformat()
        data['source_query'] = company
        print(f'  ✅ {company}: {data.get("company","?")}')
        return data
    except Exception as e:
        print(f'  ❌ {company}: {e}')
        return None

# ── 主流程 ────────────────────────────────────────────────────
if __name__ == '__main__':
    today = datetime.date.today().isoformat()
    print(f'🚀 K1980 商业洞察生成器')
    print(f'📅 {today}')

    if not ANTHROPIC_API_KEY:
        print('❌ 未设置 ANTHROPIC_API_KEY，请在 GitHub Secrets 中添加')
        exit(1)

    companies = pick_daily_companies()
    print(f'📋 今日企业（{len(companies)}家）: {", ".join(companies)}')

    results = []
    for i, company in enumerate(companies):
        print(f'\n[{i+1}/{len(companies)}] 分析 {company}...')
        data = analyze_company(company)
        if data:
            results.append(data)
        time.sleep(2)  # 避免超限

    output = {
        'date':       today,
        'updated_at': datetime.datetime.utcnow().isoformat(),
        'total':      len(results),
        'companies':  results,
    }

    path = os.path.join(OUTPUT_DIR, 'biz_insights.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f'\n✅ 完成！共生成 {len(results)} 家企业洞察')
    print(f'💾 保存至 {path}')
