#!/usr/bin/env python3
"""
K1980 本地新闻抓取器 — 新西兰/澳洲/美国/英国/加拿大/日本/韩国/新加坡/马来西亚/印尼
全部使用官方 RSS Feed，合法合规

合规说明：
- 只使用各媒体官方提供的 RSS Feed
- 抓取前检查 robots.txt
- 只显示标题+摘要，点击跳原文
- 注明来源，礼貌间隔
- 与 Google News 同等做法
"""

import json, os, time, hashlib, feedparser
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from datetime import datetime, timezone
from bs4 import BeautifulSoup

BOT_UA = 'K1980Bot/1.0 (+https://www.k1980.app/bot; news aggregator for Chinese communities)'
OUTPUT_DIR = 'data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ── 各地区官方 RSS 数据源 ──────────────────────────────────────────────
# 全部为媒体官方提供，专为聚合设计
NEWS_SOURCES = {

    'nz': [
        # 新西兰先驱报 — 新西兰最大英文报
        {'name': 'NZ Herald',       'url': 'https://www.nzherald.co.nz/arc/outboundfeeds/rss/section/nz/?outputType=xml', 'lang': 'en'},
        {'name': 'NZ Herald 头条',   'url': 'https://www.nzherald.co.nz/arc/outboundfeeds/rss/?outputType=xml',           'lang': 'en'},
        # Stuff — 新西兰第二大新闻网
        {'name': 'Stuff NZ',        'url': 'https://www.stuff.co.nz/rss',                                                 'lang': 'en'},
        {'name': 'Stuff 本地',       'url': 'https://www.stuff.co.nz/national/rss',                                       'lang': 'en'},
        # RNZ — 新西兰国家广播（公共媒体）
        {'name': 'RNZ News',        'url': 'https://www.rnz.co.nz/rss/news.xml',                                          'lang': 'en'},
        {'name': 'RNZ 政治',         'url': 'https://www.rnz.co.nz/rss/political.xml',                                    'lang': 'en'},
        # 1News — TVNZ 官方新闻
        {'name': '1News TVNZ',      'url': 'https://www.1news.co.nz/rss',                                                 'lang': 'en'},
    ],

    'au': [
        # ABC News — 澳大利亚广播公司（公共媒体）
        {'name': 'ABC News AU',     'url': 'https://www.abc.net.au/news/feed/51120/rss.xml',                              'lang': 'en'},
        {'name': 'ABC 澳洲本地',     'url': 'https://www.abc.net.au/news/feed/2942460/rss.xml',                           'lang': 'en'},
        # SBS Chinese — 专门面向华人
        {'name': 'SBS 中文',         'url': 'https://www.sbs.com.au/language/chinese/rss',                                'lang': 'zh'},
        {'name': 'SBS News',        'url': 'https://www.sbs.com.au/news/feed',                                            'lang': 'en'},
        # The Guardian Australia
        {'name': 'Guardian AU',     'url': 'https://www.theguardian.com/australia-news/rss',                              'lang': 'en'},
        # Sydney Morning Herald
        {'name': 'SMH',             'url': 'https://www.smh.com.au/rss/feed.xml',                                         'lang': 'en'},
        # The Age — 墨尔本
        {'name': 'The Age',         'url': 'https://www.theage.com.au/rss/feed.xml',                                      'lang': 'en'},
    ],

    'us': [
        # AP News — 美联社（全球最权威通讯社）
        {'name': 'AP News',         'url': 'https://rsshub.app/apnews/topics/apf-topnews',                                'lang': 'en'},
        # NPR — 美国国家公共广播
        {'name': 'NPR News',        'url': 'https://feeds.npr.org/1001/rss.xml',                                          'lang': 'en'},
        {'name': 'NPR 世界',         'url': 'https://feeds.npr.org/1004/rss.xml',                                         'lang': 'en'},
        # VOA 中文 — 专为华人
        {'name': 'VOA 中文',         'url': 'https://www.voachinese.com/api/zmgqiipuqt',                                  'lang': 'zh'},
        # CNN RSS
        {'name': 'CNN 头条',         'url': 'http://rss.cnn.com/rss/cnn_topstories.rss',                                  'lang': 'en'},
        # The New York Times
        {'name': 'NYT 头条',         'url': 'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',                  'lang': 'en'},
    ],

    'uk': [
        # BBC News — 全球最知名公共媒体
        {'name': 'BBC 头条',         'url': 'http://feeds.bbci.co.uk/news/rss.xml',                                       'lang': 'en'},
        {'name': 'BBC 英国',         'url': 'http://feeds.bbci.co.uk/news/uk/rss.xml',                                    'lang': 'en'},
        {'name': 'BBC 中文',         'url': 'https://feeds.bbci.co.uk/zhongwen/simp/rss.xml',                             'lang': 'zh'},
        # The Guardian
        {'name': 'The Guardian',    'url': 'https://www.theguardian.com/uk/rss',                                          'lang': 'en'},
        # Reuters
        {'name': 'Reuters',         'url': 'https://feeds.reuters.com/reuters/UKTopNews',                                  'lang': 'en'},
    ],

    'ca': [
        # CBC News — 加拿大广播公司（公共媒体）
        {'name': 'CBC 头条',         'url': 'https://www.cbc.ca/cmlink/rss-topstories',                                   'lang': 'en'},
        {'name': 'CBC 加拿大',       'url': 'https://www.cbc.ca/cmlink/rss-canada',                                       'lang': 'en'},
        {'name': 'CBC 温哥华',       'url': 'https://www.cbc.ca/cmlink/rss-canada-britishcolumbia',                       'lang': 'en'},
        {'name': 'CBC 多伦多',       'url': 'https://www.cbc.ca/cmlink/rss-canada-toronto',                               'lang': 'en'},
        # Globe and Mail
        {'name': 'Globe and Mail',  'url': 'https://www.theglobeandmail.com/arc/outboundfeeds/rss/',                      'lang': 'en'},
        # 明报加西版
        {'name': '明报加西',         'url': 'https://www.mingpaocanada.com/rss/van/rss.xml',                              'lang': 'zh'},
    ],

    'jp': [
        # NHK World 中文
        {'name': 'NHK 中文',         'url': 'https://www3.nhk.or.jp/rss/news/cat0.xml',                                   'lang': 'ja'},
        {'name': 'NHK World',       'url': 'https://www3.nhk.or.jp/nhkworld/en/news/feeds/',                              'lang': 'en'},
        # Japan Times
        {'name': 'Japan Times',     'url': 'https://www.japantimes.co.jp/feed/',                                          'lang': 'en'},
    ],

    'kr': [
        # Korea Herald
        {'name': 'Korea Herald',    'url': 'http://www.koreaherald.com/common/rss_xml.php?ct=102',                        'lang': 'en'},
        # Yonhap English
        {'name': 'Yonhap News',     'url': 'https://en.yna.co.kr/RSS/news.xml',                                           'lang': 'en'},
    ],

    'sg': [
        # CNA — Channel NewsAsia
        {'name': 'CNA Singapore',   'url': 'https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml',        'lang': 'en'},
        {'name': 'CNA 东南亚',       'url': 'https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml&category=6511',  'lang': 'en'},
        # Straits Times
        {'name': 'Straits Times',   'url': 'https://www.straitstimes.com/news/singapore/rss.xml',                         'lang': 'en'},
        # 联合早报 — 新加坡华文报
        {'name': '联合早报',         'url': 'https://www.zaobao.com.sg/rss/singapore',                                    'lang': 'zh'},
    ],

    'my': [
        # The Star
        {'name': 'The Star MY',     'url': 'https://www.thestar.com.my/rss/News/Nation/',                                 'lang': 'en'},
        # Malaysiakini
        {'name': 'Malaysiakini',    'url': 'https://www.malaysiakini.com/rss',                                            'lang': 'en'},
        # 中国报 — 马来西亚华文报
        {'name': '中国报',           'url': 'https://www.chinadaily.com.my/rss',                                          'lang': 'zh'},
        # 星洲日报
        {'name': '星洲日报',         'url': 'https://www.sinchew.com.my/rss',                                             'lang': 'zh'},
    ],

    'id': [
        # Kompas
        {'name': 'Kompas',          'url': 'https://rss.kompas.com/data/xml/channel/KOMPAS_TERKINI.xml',                  'lang': 'id'},
        # Jakarta Post
        {'name': 'Jakarta Post',    'url': 'https://www.thejakartapost.com/feed',                                         'lang': 'en'},
        # Detik
        {'name': 'Detik News',      'url': 'https://rss.detik.com/index.php/detikcom',                                    'lang': 'id'},
    ],
}

# ── 分类关键词（自动打标签） ───────────────────────────────────────────
CATEGORY_KEYWORDS = {
    '移民':   ['visa', 'immigration', 'migration', 'residency', 'citizenship', '签证', '移民', '居留', '入籍', 'pr ', 'permanent resident'],
    '政治':   ['government', 'minister', 'parliament', 'election', 'policy', 'political', '政府', '选举', '议会', '政策'],
    '经济':   ['economy', 'inflation', 'interest rate', 'gdp', 'housing', 'mortgage', 'tax', '经济', '利率', '房价', '通胀'],
    '华人':   ['chinese', 'china', 'mandarin', '华人', '中国', '中文', '华裔', 'chinatown'],
    '天气':   ['weather', 'storm', 'flood', 'earthquake', 'cyclone', 'rain', '天气', '洪水', '地震', '台风'],
    '教育':   ['school', 'university', 'student', 'education', 'tuition', '学校', '大学', '教育', '学费'],
    '科技':   ['tech', 'ai', 'digital', 'cyber', 'startup', '科技', '人工智能', '数字'],
}

# ── robots.txt 检查 ────────────────────────────────────────────────────
_robots_cache = {}

def can_fetch(url: str) -> bool:
    parsed = urlparse(url)
    base = f'{parsed.scheme}://{parsed.netloc}'
    if base not in _robots_cache:
        rp = RobotFileParser()
        try:
            rp.set_url(f'{base}/robots.txt')
            rp.read()
            _robots_cache[base] = rp
        except Exception:
            _robots_cache[base] = None
    rp = _robots_cache[base]
    if rp is None:
        return True
    allowed = rp.can_fetch(BOT_UA, url)
    if not allowed:
        print(f'  🚫 robots.txt 禁止: {url[:55]}')
    return allowed

# ── 自动打分 ───────────────────────────────────────────────────────────
def compute_score(entry, lang: str) -> int:
    score = 55
    text = (entry.get('title','') + ' ' + entry.get('summary','')).lower()
    
    # 华人相关加分
    if any(k in text for k in ['chinese','china','华人','中国','mandarin','华裔']):
        score += 12
    # 移民/签证加分（华人最关心）
    if any(k in text for k in ['visa','immigration','移民','签证','residency']):
        score += 10
    # 中文内容加分
    if lang == 'zh':
        score += 8
    # 新鲜度
    pub = entry.get('published_parsed')
    if pub:
        age_h = (time.time() - time.mktime(pub)) / 3600
        if age_h < 2:    score += 15
        elif age_h < 6:  score += 10
        elif age_h < 24: score += 5
    # 有媒体图片
    if entry.get('media_content') or entry.get('enclosures'):
        score += 3
    return min(score, 99)

def get_categories(title: str, summary: str) -> list:
    text = (title + ' ' + summary).lower()
    cats = [cat for cat, kws in CATEGORY_KEYWORDS.items() if any(k in text for k in kws)]
    return cats[:3] if cats else ['本地']

def time_ago(pub_parsed) -> str:
    if not pub_parsed:
        return '今日'
    age_h = (time.time() - time.mktime(pub_parsed)) / 3600
    if age_h < 1:    return f'{int(age_h*60)}分前'
    if age_h < 24:   return f'{int(age_h)}小时前'
    if age_h < 48:   return '昨日'
    return f'{int(age_h/24)}天前'

# ── 抓取单个 RSS ───────────────────────────────────────────────────────
def fetch_source(source: dict, region: str) -> list:
    url  = source['url']
    name = source['name']
    lang = source['lang']
    
    if not can_fetch(url):
        return []
    
    results = []
    try:
        feed = feedparser.parse(url, agent=BOT_UA, request_headers={'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8'})
        if not feed.entries:
            print(f'  ⚠️  无条目: {name}')
            return []
        
        for entry in feed.entries[:8]:
            summary_raw = entry.get('summary', entry.get('description', ''))
            summary = BeautifulSoup(summary_raw, 'html.parser').get_text()[:200].strip()
            title   = entry.get('title', '').strip()[:100]
            if not title:
                continue
            
            pub = entry.get('published_parsed') or entry.get('updated_parsed')
            card_id = hashlib.md5((entry.get('link','') + title).encode()).hexdigest()[:10]
            
            # 封面图
            image = None
            if entry.get('media_content'):
                image = entry['media_content'][0].get('url')
            elif entry.get('media_thumbnail'):
                image = entry['media_thumbnail'][0].get('url')
            elif entry.get('enclosures'):
                for enc in entry['enclosures']:
                    if 'image' in enc.get('type',''):
                        image = enc.get('href') or enc.get('url')
                        break
            
            results.append({
                'id':         card_id,
                'region':     region,
                'source':     name,
                'source_url': url,
                'lang':       lang,
                'title':      title,
                'summary':    summary,
                'link':       entry.get('link', ''),
                'image':      image,
                'categories': get_categories(title, summary),
                'score':      compute_score(entry, lang),
                'ago':        time_ago(pub),
                'pub_ts':     time.mktime(pub) if pub else 0,
                'hot':        any(k in title.lower() for k in ['urgent','breaking','alert','重大','突发','紧急']),
            })
        
        print(f'  ✅ {name}: {len(results)}条')
    except Exception as e:
        print(f'  ❌ {name}: {e}')
    
    return results

# ── 抓取整个地区 ───────────────────────────────────────────────────────
def scrape_region(region: str) -> dict:
    region_names = {
        'nz':'新西兰','au':'澳洲','us':'美国','uk':'英国',
        'ca':'加拿大','jp':'日本','kr':'韩国','sg':'新加坡',
        'my':'马来西亚','id':'印尼'
    }
    print(f'\n🌏 抓取 {region_names.get(region, region)}...')
    
    all_articles = []
    for source in NEWS_SOURCES.get(region, []):
        articles = fetch_source(source, region)
        all_articles.extend(articles)
        time.sleep(1.5)  # 礼貌间隔
    
    # 去重（同标题前20字）
    seen, unique = set(), []
    for a in all_articles:
        key = a['title'][:20]
        if key not in seen:
            seen.add(key)
            unique.append(a)
    
    # 按分数排序，取前30条
    unique.sort(key=lambda x: (x['score'], x['pub_ts']), reverse=True)
    top = unique[:30]
    
    # 统计各分类
    cat_counts = {}
    for a in top:
        for c in a['categories']:
            cat_counts[c] = cat_counts.get(c, 0) + 1
    
    print(f'  📊 共 {len(top)} 条 | 分类: {cat_counts}')
    
    return {
        'region':     region,
        'name':       region_names.get(region, region),
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'total':      len(top),
        'cat_counts': cat_counts,
        'articles':   top,
    }

# ── 保存 ──────────────────────────────────────────────────────────────
def save(region: str, data: dict):
    path = os.path.join(OUTPUT_DIR, f'news_{region}.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'  💾 {path}')

def save_meta(all_data: dict):
    meta = {
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'regions': {r: {'total': d['total'], 'updated_at': d['updated_at']} for r, d in all_data.items()}
    }
    with open(os.path.join(OUTPUT_DIR, 'news_meta.json'), 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)

# ── 入口 ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print('🚀 K1980 本地新闻抓取器')
    print(f'⏰ {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}')
    print(f'📡 覆盖地区: {", ".join(NEWS_SOURCES.keys())}')
    
    all_data = {}
    for region in NEWS_SOURCES:
        try:
            data = scrape_region(region)
            save(region, data)
            all_data[region] = data
        except Exception as e:
            print(f'❌ {region} 失败: {e}')
    
    save_meta(all_data)
    total = sum(d['total'] for d in all_data.values())
    print(f'\n✅ 完成！共抓取 {total} 条新闻')
