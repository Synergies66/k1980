#!/usr/bin/env python3
"""
K1980 全合一抓取器 — 本地新闻 + 本地服务推送
覆盖：新西兰/澳洲/美国/英国/加拿大/日本/韩国/新加坡/马来西亚/印尼

合规说明：
- 全部使用官方 RSS Feed 或公开数据
- 抓取前检查 robots.txt
- 只显示标题+摘要，点击跳原文，注明来源
- 抓取间隔 1.5 秒，诚实声明爬虫身份
- 与 Google News 同等做法，合法合规
"""

import json, os, time, hashlib, feedparser
from urllib.robotparser import RobotFileParser
from urllib.parse import urlparse
from datetime import datetime, timezone
from bs4 import BeautifulSoup

BOT_UA     = 'K1980Bot/1.0 (+https://www.k1980.app/bot; news aggregator for Chinese communities)'
OUTPUT_DIR = 'data'
os.makedirs(OUTPUT_DIR, exist_ok=True)

REGION_NAMES = {
    'nz':'新西兰','au':'澳洲','us':'美国','uk':'英国',
    'ca':'加拿大','jp':'日本','kr':'韩国','sg':'新加坡',
    'my':'马来西亚','id':'印尼'
}

# ════════════════════════════════════════════════════════════════
# 一、本地新闻数据源（官方 RSS）
# ════════════════════════════════════════════════════════════════
NEWS_SOURCES = {
    'nz': [
        {'name':'NZ Herald',      'url':'https://www.nzherald.co.nz/arc/outboundfeeds/rss/section/nz/?outputType=xml','lang':'en'},
        {'name':'NZ Herald 头条',  'url':'https://www.nzherald.co.nz/arc/outboundfeeds/rss/?outputType=xml',           'lang':'en'},
        {'name':'Stuff NZ',       'url':'https://www.stuff.co.nz/rss',                                                 'lang':'en'},
        {'name':'Stuff 本地',      'url':'https://www.stuff.co.nz/national/rss',                                       'lang':'en'},
        {'name':'RNZ News',       'url':'https://www.rnz.co.nz/rss/news.xml',                                          'lang':'en'},
        {'name':'RNZ 政治',        'url':'https://www.rnz.co.nz/rss/political.xml',                                    'lang':'en'},
        {'name':'1News TVNZ',     'url':'https://www.1news.co.nz/rss',                                                 'lang':'en'},
    ],
    'au': [
        {'name':'ABC News AU',    'url':'https://www.abc.net.au/news/feed/51120/rss.xml',                              'lang':'en'},
        {'name':'ABC 澳洲本地',    'url':'https://www.abc.net.au/news/feed/2942460/rss.xml',                           'lang':'en'},
        {'name':'SBS 中文',        'url':'https://www.sbs.com.au/language/chinese/rss',                                'lang':'zh'},
        {'name':'SBS News',       'url':'https://www.sbs.com.au/news/feed',                                            'lang':'en'},
        {'name':'Guardian AU',    'url':'https://www.theguardian.com/australia-news/rss',                              'lang':'en'},
        {'name':'SMH',            'url':'https://www.smh.com.au/rss/feed.xml',                                         'lang':'en'},
        {'name':'The Age',        'url':'https://www.theage.com.au/rss/feed.xml',                                      'lang':'en'},
    ],
    'us': [
        {'name':'AP News',        'url':'https://rsshub.app/apnews/topics/apf-topnews',                                'lang':'en'},
        {'name':'NPR News',       'url':'https://feeds.npr.org/1001/rss.xml',                                          'lang':'en'},
        {'name':'NPR 世界',        'url':'https://feeds.npr.org/1004/rss.xml',                                         'lang':'en'},
        {'name':'VOA 中文',        'url':'https://www.voachinese.com/api/zmgqiipuqt',                                  'lang':'zh'},
        {'name':'CNN 头条',        'url':'http://rss.cnn.com/rss/cnn_topstories.rss',                                  'lang':'en'},
        {'name':'NYT 头条',        'url':'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',                  'lang':'en'},
    ],
    'uk': [
        {'name':'BBC 头条',        'url':'http://feeds.bbci.co.uk/news/rss.xml',                                       'lang':'en'},
        {'name':'BBC 英国',        'url':'http://feeds.bbci.co.uk/news/uk/rss.xml',                                    'lang':'en'},
        {'name':'BBC 中文',        'url':'https://feeds.bbci.co.uk/zhongwen/simp/rss.xml',                             'lang':'zh'},
        {'name':'The Guardian',   'url':'https://www.theguardian.com/uk/rss',                                          'lang':'en'},
        {'name':'Reuters',        'url':'https://feeds.reuters.com/reuters/UKTopNews',                                  'lang':'en'},
    ],
    'ca': [
        {'name':'CBC 头条',        'url':'https://www.cbc.ca/cmlink/rss-topstories',                                   'lang':'en'},
        {'name':'CBC 加拿大',      'url':'https://www.cbc.ca/cmlink/rss-canada',                                       'lang':'en'},
        {'name':'CBC 温哥华',      'url':'https://www.cbc.ca/cmlink/rss-canada-britishcolumbia',                       'lang':'en'},
        {'name':'CBC 多伦多',      'url':'https://www.cbc.ca/cmlink/rss-canada-toronto',                               'lang':'en'},
        {'name':'Globe and Mail', 'url':'https://www.theglobeandmail.com/arc/outboundfeeds/rss/',                      'lang':'en'},
        {'name':'明报加西',        'url':'https://www.mingpaocanada.com/rss/van/rss.xml',                              'lang':'zh'},
    ],
    'jp': [
        {'name':'NHK 日本',        'url':'https://www3.nhk.or.jp/rss/news/cat0.xml',                                   'lang':'ja'},
        {'name':'NHK World',      'url':'https://www3.nhk.or.jp/nhkworld/en/news/feeds/',                              'lang':'en'},
        {'name':'Japan Times',    'url':'https://www.japantimes.co.jp/feed/',                                          'lang':'en'},
    ],
    'kr': [
        {'name':'Korea Herald',   'url':'http://www.koreaherald.com/common/rss_xml.php?ct=102',                        'lang':'en'},
        {'name':'Yonhap News',    'url':'https://en.yna.co.kr/RSS/news.xml',                                           'lang':'en'},
    ],
    'sg': [
        {'name':'CNA Singapore',  'url':'https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml',        'lang':'en'},
        {'name':'Straits Times',  'url':'https://www.straitstimes.com/news/singapore/rss.xml',                         'lang':'en'},
        {'name':'联合早报',        'url':'https://www.zaobao.com.sg/rss/singapore',                                    'lang':'zh'},
    ],
    'my': [
        {'name':'The Star MY',    'url':'https://www.thestar.com.my/rss/News/Nation/',                                 'lang':'en'},
        {'name':'Malaysiakini',   'url':'https://www.malaysiakini.com/rss',                                            'lang':'en'},
        {'name':'星洲日报',        'url':'https://www.sinchew.com.my/rss',                                             'lang':'zh'},
    ],
    'id': [
        {'name':'Jakarta Post',   'url':'https://www.thejakartapost.com/feed',                                         'lang':'en'},
        {'name':'Kompas',         'url':'https://rss.kompas.com/data/xml/channel/KOMPAS_TERKINI.xml',                  'lang':'id'},
        {'name':'Detik News',     'url':'https://rss.detik.com/index.php/detikcom',                                    'lang':'id'},
    ],
}

# ════════════════════════════════════════════════════════════════
# 二、本地服务数据源（招聘/房产/优惠/活动）
# ════════════════════════════════════════════════════════════════
SERVICE_SOURCES = {
    'nz': [
        # 招聘
        {'name':'Seek NZ',           'url':'https://www.seek.co.nz/jobs/rss',                                          'type':'job'},
        {'name':'TradeMe Jobs',      'url':'https://www.trademe.co.nz/jobs/rss',                                       'type':'job'},
        # 房产
        {'name':'TradeMe 出租',       'url':'https://www.trademe.co.nz/property/residential-property-for-rent/rss',    'type':'house'},
        {'name':'RealEstate NZ',     'url':'https://www.realestate.co.nz/residential/rent/rss',                        'type':'house'},
        # 优惠
        {'name':'1-Day Deals',       'url':'https://www.1-day.co.nz/rss/deals.xml',                                    'type':'deal'},
        # 活动
        {'name':'Eventfinda NZ',     'url':'https://www.eventfinda.co.nz/feed/events/new-zealand',                     'type':'event'},
    ],
    'au': [
        {'name':'Seek AU',           'url':'https://www.seek.com.au/jobs/rss',                                         'type':'job'},
        {'name':'Domain 出租',        'url':'https://www.domain.com.au/rss/rent/',                                     'type':'house'},
        {'name':'OzBargain',         'url':'https://www.ozbargain.com.au/deals/feed',                                  'type':'deal'},
        {'name':'Eventbrite AU',     'url':'https://www.eventbrite.com.au/d/australia/events/rss/',                    'type':'event'},
    ],
    'ca': [
        {'name':'Indeed CA',         'url':'https://ca.indeed.com/rss?q=&l=Vancouver',                                 'type':'job'},
        {'name':'Indeed 多伦多',      'url':'https://ca.indeed.com/rss?q=&l=Toronto',                                  'type':'job'},
        {'name':'RedflagDeals',      'url':'https://www.redflagdeals.com/feed/',                                       'type':'deal'},
        {'name':'Eventbrite CA',     'url':'https://www.eventbrite.ca/d/canada/events/rss/',                           'type':'event'},
    ],
    'us': [
        {'name':'Indeed US',         'url':'https://www.indeed.com/rss?q=chinese+speaker',                             'type':'job'},
        {'name':'SlickDeals',        'url':'https://slickdeals.net/newsearch.php?mode=frontpage&rss=1',                 'type':'deal'},
        {'name':'Eventbrite US',     'url':'https://www.eventbrite.com/d/united-states/events/rss/',                   'type':'event'},
    ],
    'uk': [
        {'name':'Reed UK',           'url':'https://www.reed.co.uk/jobs/rss',                                          'type':'job'},
        {'name':'Indeed UK',         'url':'https://uk.indeed.com/rss?q=chinese+speaker&l=London',                     'type':'job'},
        {'name':'HotUKDeals',        'url':'https://www.hotukdeals.com/rss/hottest',                                   'type':'deal'},
        {'name':'Eventbrite UK',     'url':'https://www.eventbrite.co.uk/d/united-kingdom/events/rss/',                'type':'event'},
    ],
    'jp': [
        {'name':'GaijinPot Jobs',    'url':'https://jobs.gaijinpot.com/index/index/rss',                               'type':'job'},
        {'name':'Eventbrite JP',     'url':'https://www.eventbrite.jp/d/japan/events/rss/',                            'type':'event'},
    ],
    'kr': [
        {'name':'Eventbrite KR',     'url':'https://www.eventbrite.com/d/south-korea/events/rss/',                     'type':'event'},
    ],
    'sg': [
        {'name':'MyCareersFuture',   'url':'https://www.mycareersfuture.gov.sg/api/jobs?rss=true',                     'type':'job'},
        {'name':'SGDeals',           'url':'https://sgdeals.com/feed',                                                 'type':'deal'},
        {'name':'Eventbrite SG',     'url':'https://www.eventbrite.sg/d/singapore/events/rss/',                        'type':'event'},
    ],
    'my': [
        {'name':'JobStreet MY',      'url':'https://www.jobstreet.com.my/en/job-search/jobs-in-malaysia/rss/',          'type':'job'},
        {'name':'Eventbrite MY',     'url':'https://www.eventbrite.my/d/malaysia/events/rss/',                         'type':'event'},
    ],
    'id': [
        {'name':'JobStreet ID',      'url':'https://www.jobstreet.co.id/id/job-search/jobs-in-indonesia/rss/',          'type':'job'},
        {'name':'Eventbrite ID',     'url':'https://www.eventbrite.com/d/indonesia/events/rss/',                       'type':'event'},
    ],
}

# ════════════════════════════════════════════════════════════════
# 三、关键词配置
# ════════════════════════════════════════════════════════════════
NEWS_CATEGORY_KW = {
    '移民': ['visa','immigration','migration','residency','citizenship','签证','移民','居留','入籍','permanent resident'],
    '政治': ['government','minister','parliament','election','policy','political','政府','选举','议会','政策'],
    '经济': ['economy','inflation','interest rate','gdp','housing','mortgage','tax','经济','利率','房价','通胀'],
    '华人': ['chinese','china','mandarin','华人','中国','中文','华裔','chinatown'],
    '天气': ['weather','storm','flood','earthquake','cyclone','rain','天气','洪水','地震','台风'],
    '教育': ['school','university','student','education','tuition','学校','大学','教育','学费'],
    '科技': ['tech','ai','digital','cyber','startup','科技','人工智能','数字'],
}
SERVICE_HOT_KW  = ['urgent','immediate','急招','限时','breaking','热门','popular','featured']
CHINESE_KW      = ['chinese','china','mandarin','华人','中国','中文','华裔','普通话','cantonese']
VISA_KW         = ['visa','immigration','移民','签证','residency','pr ','work permit']
SERVICE_TAG_KW  = {
    '全职':  ['full.time','full time','全职'],
    '兼职':  ['part.time','part time','兼职'],
    '远程':  ['remote','work from home','远程','wfh'],
    '签证':  ['visa','sponsorship','签证','work permit'],
    '华人':  CHINESE_KW,
}

# ════════════════════════════════════════════════════════════════
# 四、工具函数
# ════════════════════════════════════════════════════════════════
_robots_cache = {}

def can_fetch(url: str) -> bool:
    parsed = urlparse(url)
    base   = f'{parsed.scheme}://{parsed.netloc}'
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
    ok = rp.can_fetch(BOT_UA, url)
    if not ok:
        print(f'  🚫 robots.txt 禁止: {url[:55]}')
    return ok

def time_ago(pub_parsed) -> str:
    if not pub_parsed:
        return '今日'
    age_h = (time.time() - time.mktime(pub_parsed)) / 3600
    if age_h < 1:   return f'{int(age_h*60)}分前'
    if age_h < 24:  return f'{int(age_h)}小时前'
    if age_h < 48:  return '昨日'
    return f'{int(age_h/24)}天前'

def extract_image(entry) -> str | None:
    if entry.get('media_content'):
        return entry['media_content'][0].get('url')
    if entry.get('media_thumbnail'):
        return entry['media_thumbnail'][0].get('url')
    if entry.get('enclosures'):
        for enc in entry['enclosures']:
            if 'image' in enc.get('type',''):
                return enc.get('href') or enc.get('url')
    return None

def news_score(entry, lang: str) -> int:
    score = 55
    text  = (entry.get('title','') + ' ' + entry.get('summary','')).lower()
    if any(k in text for k in CHINESE_KW):  score += 12
    if any(k in text for k in VISA_KW):     score += 10
    if lang == 'zh':                         score += 8
    pub = entry.get('published_parsed')
    if pub:
        age_h = (time.time() - time.mktime(pub)) / 3600
        if age_h < 2:    score += 15
        elif age_h < 6:  score += 10
        elif age_h < 24: score += 5
    if entry.get('media_content') or entry.get('enclosures'):
        score += 3
    return min(score, 99)

def service_score(entry) -> int:
    score = 60
    text  = (entry.get('title','') + ' ' + entry.get('summary','')).lower()
    if any(k in text for k in CHINESE_KW):       score += 10
    if any(k in text for k in SERVICE_HOT_KW):   score += 8
    if any(k in text for k in VISA_KW):           score += 7
    pub = entry.get('published_parsed')
    if pub:
        age_h = (time.time() - time.mktime(pub)) / 3600
        if age_h < 2:    score += 15
        elif age_h < 6:  score += 10
        elif age_h < 24: score += 5
    return min(score, 99)

def news_categories(title: str, summary: str) -> list:
    text = (title + ' ' + summary).lower()
    cats = [c for c, kws in NEWS_CATEGORY_KW.items() if any(k in text for k in kws)]
    return cats[:3] if cats else ['本地']

def service_tags(title: str, summary: str) -> list:
    text = (title + ' ' + summary).lower()
    tags = [tag for tag, kws in SERVICE_TAG_KW.items() if any(k in text for k in kws)]
    return tags[:3]

# ════════════════════════════════════════════════════════════════
# 五、抓取函数
# ════════════════════════════════════════════════════════════════
def fetch_rss(url: str, name: str, limit: int = 8) -> list:
    """通用 RSS 抓取，返回原始 feedparser entries"""
    if not can_fetch(url):
        return []
    try:
        feed = feedparser.parse(url, agent=BOT_UA,
                                request_headers={'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8'})
        entries = feed.entries[:limit]
        if not entries:
            print(f'  ⚠️  无条目: {name}')
        else:
            print(f'  ✅ {name}: {len(entries)}条')
        return entries
    except Exception as e:
        print(f'  ❌ {name}: {e}')
        return []

def build_news_card(entry, region: str, source_name: str, lang: str) -> dict | None:
    title = entry.get('title','').strip()[:100]
    if not title:
        return None
    summary_raw = entry.get('summary', entry.get('description',''))
    summary     = BeautifulSoup(summary_raw, 'html.parser').get_text()[:200].strip()
    pub         = entry.get('published_parsed') or entry.get('updated_parsed')
    return {
        'id':         hashlib.md5((entry.get('link','') + title).encode()).hexdigest()[:10],
        'type':       'news',
        'region':     region,
        'source':     source_name,
        'lang':       lang,
        'title':      title,
        'summary':    summary,
        'link':       entry.get('link',''),
        'image':      extract_image(entry),
        'categories': news_categories(title, summary),
        'score':      news_score(entry, lang),
        'ago':        time_ago(pub),
        'pub_ts':     time.mktime(pub) if pub else 0,
        'hot':        any(k in title.lower() for k in ['breaking','alert','重大','突发','紧急']),
    }

def build_service_card(entry, region: str, source_name: str, stype: str) -> dict | None:
    title = entry.get('title','').strip()[:100]
    if not title:
        return None
    summary_raw = entry.get('summary', entry.get('description',''))
    summary     = BeautifulSoup(summary_raw, 'html.parser').get_text()[:150].strip()
    pub         = entry.get('published_parsed') or entry.get('updated_parsed')
    type_label  = {'job':'招聘','house':'房产','deal':'优惠','event':'活动'}.get(stype, stype)
    return {
        'id':          hashlib.md5((entry.get('link','') + title).encode()).hexdigest()[:10],
        'type':        stype,
        'type_label':  type_label,
        'region':      region,
        'source':      source_name,
        'source_domain': urlparse(entry.get('link','')).netloc or source_name,
        'title':       title,
        'summary':     summary,
        'link':        entry.get('link',''),
        'image':       extract_image(entry),
        'tags':        service_tags(title, summary),
        'score':       service_score(entry),
        'ago':         time_ago(pub),
        'pub_ts':      time.mktime(pub) if pub else 0,
        'hot':         any(k in title.lower() for k in SERVICE_HOT_KW),
    }

# ════════════════════════════════════════════════════════════════
# 六、地区主抓取
# ════════════════════════════════════════════════════════════════
def scrape_region(region: str) -> dict:
    name = REGION_NAMES.get(region, region)
    print(f'\n{"="*50}')
    print(f'🌏 {name} ({region})')
    print(f'{"="*50}')

    # ── 新闻 ──
    print(f'\n📰 新闻抓取...')
    news_cards = []
    for src in NEWS_SOURCES.get(region, []):
        entries = fetch_rss(src['url'], src['name'])
        for e in entries:
            card = build_news_card(e, region, src['name'], src['lang'])
            if card:
                news_cards.append(card)
        time.sleep(1.5)

    # 去重 + 排序
    news_cards = dedupe(news_cards)
    news_cards.sort(key=lambda x: (x['score'], x['pub_ts']), reverse=True)
    news_cards = news_cards[:30]

    # ── 服务 ──
    print(f'\n🛎️  服务抓取...')
    service_cards = []
    for src in SERVICE_SOURCES.get(region, []):
        entries = fetch_rss(src['url'], src['name'])
        for e in entries:
            card = build_service_card(e, region, src['name'], src['type'])
            if card:
                service_cards.append(card)
        time.sleep(1.5)

    service_cards = dedupe(service_cards)
    service_cards.sort(key=lambda x: (x['score'], x['pub_ts']), reverse=True)
    service_cards = service_cards[:20]

    # ── 统计 ──
    news_cat_counts = {}
    for a in news_cards:
        for c in a['categories']:
            news_cat_counts[c] = news_cat_counts.get(c, 0) + 1

    service_type_counts = {}
    for s in service_cards:
        t = s['type']
        service_type_counts[t] = service_type_counts.get(t, 0) + 1

    print(f'  📊 新闻 {len(news_cards)} 条 | 服务 {len(service_cards)} 条')

    return {
        'region':             region,
        'name':               name,
        'updated_at':         datetime.now(timezone.utc).isoformat(),
        'news_total':         len(news_cards),
        'service_total':      len(service_cards),
        'news_cat_counts':    news_cat_counts,
        'service_type_counts':service_type_counts,
        'news':               news_cards,
        'services':           service_cards,
    }

def dedupe(cards: list) -> list:
    seen, unique = set(), []
    for c in cards:
        key = c['title'][:20]
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique

# ════════════════════════════════════════════════════════════════
# 七、保存
# ════════════════════════════════════════════════════════════════
def save_region(region: str, data: dict):
    # 分开保存新闻和服务，方便前端按需加载
    news_path = os.path.join(OUTPUT_DIR, f'news_{region}.json')
    svc_path  = os.path.join(OUTPUT_DIR, f'services_{region}.json')

    news_payload = {k: v for k, v in data.items() if k != 'services'}
    svc_payload  = {k: v for k, v in data.items() if k != 'news'}
    svc_payload['services'] = data['services']

    with open(news_path, 'w', encoding='utf-8') as f:
        json.dump(news_payload, f, ensure_ascii=False, indent=2)
    with open(svc_path, 'w', encoding='utf-8') as f:
        json.dump(svc_payload, f, ensure_ascii=False, indent=2)

    print(f'  💾 {news_path} + {svc_path}')

def save_meta(all_data: dict):
    meta = {
        'updated_at': datetime.now(timezone.utc).isoformat(),
        'regions': {
            r: {
                'name':          d['name'],
                'news_total':    d['news_total'],
                'service_total': d['service_total'],
                'updated_at':    d['updated_at'],
            }
            for r, d in all_data.items()
        }
    }
    path = os.path.join(OUTPUT_DIR, 'meta.json')
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2)
    print(f'\n📋 元数据: {path}')

# ════════════════════════════════════════════════════════════════
# 八、入口
# ════════════════════════════════════════════════════════════════
if __name__ == '__main__':
    print('🚀 K1980 全合一抓取器启动')
    print(f'⏰ {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}')
    print(f'📡 覆盖: {", ".join(REGION_NAMES.values())}')

    all_data   = {}
    total_news = 0
    total_svc  = 0

    for region in REGION_NAMES:
        try:
            data = scrape_region(region)
            save_region(region, data)
            all_data[region] = data
            total_news += data['news_total']
            total_svc  += data['service_total']
        except Exception as e:
            print(f'❌ {region} 失败: {e}')

    save_meta(all_data)
    print(f'\n✅ 全部完成！')
    print(f'   📰 新闻: {total_news} 条')
    print(f'   🛎️  服务: {total_svc} 条')
    print(f'   🌏 覆盖: {len(all_data)} 个地区')
