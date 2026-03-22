#!/usr/bin/env python3
"""
K1980 单地区抓取器
用法: python scripts/scrape_region.py nz
支持: nz au us uk ca jp kr sg my id hk mo
"""

import json, os, sys, time, hashlib, feedparser
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
    'my':'马来西亚','id':'印尼','hk':'香港','mo':'澳门'
}

# ════════════════════════════════════════════════════
# 新闻数据源
# ════════════════════════════════════════════════════
NEWS_SOURCES = {
    'nz': [
        {'name':'NZ Herald',    'url':'https://www.nzherald.co.nz/arc/outboundfeeds/rss/section/nz/?outputType=xml','lang':'en'},
        {'name':'NZ Herald 头条','url':'https://www.nzherald.co.nz/arc/outboundfeeds/rss/?outputType=xml',          'lang':'en'},
        {'name':'Stuff NZ',     'url':'https://www.stuff.co.nz/rss',                                                'lang':'en'},
        {'name':'RNZ News',     'url':'https://www.rnz.co.nz/rss/news.xml',                                         'lang':'en'},
        {'name':'RNZ 政治',     'url':'https://www.rnz.co.nz/rss/political.xml',                                    'lang':'en'},
        {'name':'1News TVNZ',   'url':'https://www.1news.co.nz/rss',                                                'lang':'en'},
    ],
    'au': [
        {'name':'ABC News AU',  'url':'https://www.abc.net.au/news/feed/51120/rss.xml',                             'lang':'en'},
        {'name':'SBS 中文',     'url':'https://www.sbs.com.au/language/chinese/rss',                               'lang':'zh'},
        {'name':'SBS News',     'url':'https://www.sbs.com.au/news/feed',                                           'lang':'en'},
        {'name':'Guardian AU',  'url':'https://www.theguardian.com/australia-news/rss',                             'lang':'en'},
        {'name':'SMH',          'url':'https://www.smh.com.au/rss/feed.xml',                                        'lang':'en'},
        {'name':'The Age',      'url':'https://www.theage.com.au/rss/feed.xml',                                     'lang':'en'},
    ],
    'us': [
        {'name':'NPR News',     'url':'https://feeds.npr.org/1001/rss.xml',                                         'lang':'en'},
        {'name':'NPR 世界',     'url':'https://feeds.npr.org/1004/rss.xml',                                         'lang':'en'},
        {'name':'VOA 中文',     'url':'https://www.voachinese.com/api/zmgqiipuqt',                                  'lang':'zh'},
        {'name':'CNN 头条',     'url':'http://rss.cnn.com/rss/cnn_topstories.rss',                                  'lang':'en'},
        {'name':'NYT 头条',     'url':'https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml',                  'lang':'en'},
    ],
    'uk': [
        {'name':'BBC 头条',     'url':'http://feeds.bbci.co.uk/news/rss.xml',                                       'lang':'en'},
        {'name':'BBC 英国',     'url':'http://feeds.bbci.co.uk/news/uk/rss.xml',                                    'lang':'en'},
        {'name':'BBC 中文',     'url':'https://feeds.bbci.co.uk/zhongwen/simp/rss.xml',                             'lang':'zh'},
        {'name':'The Guardian', 'url':'https://www.theguardian.com/uk/rss',                                         'lang':'en'},
        {'name':'Reuters',      'url':'https://feeds.reuters.com/reuters/UKTopNews',                                 'lang':'en'},
    ],
    'ca': [
        {'name':'CBC 头条',     'url':'https://www.cbc.ca/cmlink/rss-topstories',                                   'lang':'en'},
        {'name':'CBC 温哥华',   'url':'https://www.cbc.ca/cmlink/rss-canada-britishcolumbia',                       'lang':'en'},
        {'name':'CBC 多伦多',   'url':'https://www.cbc.ca/cmlink/rss-canada-toronto',                               'lang':'en'},
        {'name':'明报加西',     'url':'https://www.mingpaocanada.com/rss/van/rss.xml',                              'lang':'zh'},
    ],
    'jp': [
        {'name':'NHK 日本',     'url':'https://www3.nhk.or.jp/rss/news/cat0.xml',                                   'lang':'ja'},
        {'name':'Japan Times',  'url':'https://www.japantimes.co.jp/feed/',                                         'lang':'en'},
    ],
    'kr': [
        {'name':'Korea Herald', 'url':'http://www.koreaherald.com/common/rss_xml.php?ct=102',                       'lang':'en'},
        {'name':'Yonhap News',  'url':'https://en.yna.co.kr/RSS/news.xml',                                          'lang':'en'},
    ],
    'sg': [
        {'name':'CNA Singapore','url':'https://www.channelnewsasia.com/api/v1/rss-outbound-feed?_format=xml',       'lang':'en'},
        {'name':'联合早报',     'url':'https://www.zaobao.com.sg/rss/singapore',                                   'lang':'zh'},
        {'name':'Straits Times','url':'https://www.straitstimes.com/news/singapore/rss.xml',                        'lang':'en'},
    ],
    'my': [
        {'name':'The Star MY',  'url':'https://www.thestar.com.my/rss/News/Nation/',                                'lang':'en'},
        {'name':'星洲日报',     'url':'https://www.sinchew.com.my/rss',                                            'lang':'zh'},
        {'name':'Malaysiakini', 'url':'https://www.malaysiakini.com/rss',                                           'lang':'en'},
    ],
    'id': [
        {'name':'Jakarta Post', 'url':'https://www.thejakartapost.com/feed',                                        'lang':'en'},
        {'name':'Kompas',       'url':'https://rss.kompas.com/data/xml/channel/KOMPAS_TERKINI.xml',                 'lang':'id'},
        {'name':'Detik News',   'url':'https://rss.detik.com/index.php/detikcom',                                   'lang':'id'},
    ],
    # ── 香港 ──────────────────────────────────────────────────
    'hk': [
        {'name':'RTHK 香港電台', 'url':'https://rthk.hk/rss/rthknews.xml',                                         'lang':'zh'},
        {'name':'RTHK English',  'url':'https://rthk.hk/rss/rthknews_en.xml',                                      'lang':'en'},
        {'name':'SCMP 南华早报', 'url':'https://www.scmp.com/rss/91/feed',                                         'lang':'en'},
        {'name':'SCMP 香港',     'url':'https://www.scmp.com/rss/2/feed',                                          'lang':'en'},
        {'name':'香港01',        'url':'https://www.hk01.com/rss/index.xml',                                       'lang':'zh'},
        {'name':'明报新闻',      'url':'https://news.mingpao.com/rss/pns/s00001.xml',                              'lang':'zh'},
        {'name':'星岛日报',      'url':'https://std.stheadline.com/rss/realtime/news.xml',                         'lang':'zh'},
    ],
    # ── 澳门 ──────────────────────────────────────────────────
    'mo': [
        {'name':'澳门日报',      'url':'https://www.macaodaily.com/rss.xml',                                       'lang':'zh'},
        {'name':'TDM澳广视',     'url':'https://www.tdm.com.mo/rss/news.xml',                                      'lang':'zh'},
        {'name':'澳门电台',      'url':'https://www.tdmradio.com/rss/news.xml',                                    'lang':'zh'},
        {'name':'Macau News',    'url':'https://macaunews.mo/feed/',                                               'lang':'en'},
        {'name':'Macau Business','url':'https://macaubusiness.com/feed/',                                          'lang':'en'},
        {'name':'力报',          'url':'https://www.exmoo.com/rss.xml',                                           'lang':'zh'},
    ],
}

# ════════════════════════════════════════════════════
# 服务数据源
# ════════════════════════════════════════════════════
SERVICE_SOURCES = {
    'nz': [
        {'name':'Seek NZ',        'url':'https://www.seek.co.nz/jobs/rss',                                  'type':'job'},
        {'name':'TradeMe Jobs',   'url':'https://www.trademe.co.nz/jobs/rss',                               'type':'job'},
        {'name':'TradeMe 出租',   'url':'https://www.trademe.co.nz/property/residential-property-for-rent/rss','type':'house'},
        {'name':'1-Day Deals',    'url':'https://www.1-day.co.nz/rss/deals.xml',                            'type':'deal'},
        {'name':'Eventfinda NZ',  'url':'https://www.eventfinda.co.nz/feed/events/new-zealand',             'type':'event'},
    ],
    'au': [
        {'name':'Seek AU',        'url':'https://www.seek.com.au/jobs/rss',                                 'type':'job'},
        {'name':'Domain 出租',    'url':'https://www.domain.com.au/rss/rent/',                              'type':'house'},
        {'name':'OzBargain',      'url':'https://www.ozbargain.com.au/deals/feed',                          'type':'deal'},
        {'name':'Eventbrite AU',  'url':'https://www.eventbrite.com.au/d/australia/events/rss/',            'type':'event'},
    ],
    'us': [
        {'name':'Indeed US',      'url':'https://www.indeed.com/rss?q=chinese+speaker',                    'type':'job'},
        {'name':'SlickDeals',     'url':'https://slickdeals.net/newsearch.php?mode=frontpage&rss=1',        'type':'deal'},
        {'name':'Eventbrite US',  'url':'https://www.eventbrite.com/d/united-states/events/rss/',          'type':'event'},
    ],
    'uk': [
        {'name':'Reed UK',        'url':'https://www.reed.co.uk/jobs/rss',                                 'type':'job'},
        {'name':'HotUKDeals',     'url':'https://www.hotukdeals.com/rss/hottest',                          'type':'deal'},
        {'name':'Eventbrite UK',  'url':'https://www.eventbrite.co.uk/d/united-kingdom/events/rss/',       'type':'event'},
    ],
    'ca': [
        {'name':'Indeed CA',      'url':'https://ca.indeed.com/rss?q=&l=Vancouver',                        'type':'job'},
        {'name':'RedflagDeals',   'url':'https://www.redflagdeals.com/feed/',                              'type':'deal'},
        {'name':'Eventbrite CA',  'url':'https://www.eventbrite.ca/d/canada/events/rss/',                  'type':'event'},
    ],
    'jp': [
        {'name':'GaijinPot Jobs', 'url':'https://jobs.gaijinpot.com/index/index/rss',                     'type':'job'},
    ],
    'kr': [
        {'name':'Eventbrite KR',  'url':'https://www.eventbrite.com/d/south-korea/events/rss/',            'type':'event'},
    ],
    'sg': [
        {'name':'MyCareersFuture','url':'https://www.mycareersfuture.gov.sg/api/jobs?rss=true',             'type':'job'},
        {'name':'SGDeals',        'url':'https://sgdeals.com/feed',                                        'type':'deal'},
        {'name':'Eventbrite SG',  'url':'https://www.eventbrite.sg/d/singapore/events/rss/',               'type':'event'},
    ],
    'my': [
        {'name':'JobStreet MY',   'url':'https://www.jobstreet.com.my/en/job-search/jobs-in-malaysia/rss/','type':'job'},
        {'name':'Eventbrite MY',  'url':'https://www.eventbrite.my/d/malaysia/events/rss/',                'type':'event'},
    ],
    'id': [
        {'name':'JobStreet ID',   'url':'https://www.jobstreet.co.id/id/job-search/jobs-in-indonesia/rss/','type':'job'},
    ],
    # ── 香港服务 ──────────────────────────────────────────────
    'hk': [
        {'name':'JobsDB 香港',    'url':'https://hk.jobsdb.com/hk/search-jobs/rss',                       'type':'job'},
        {'name':'CTgoodjobs',     'url':'https://www.ctgoodjobs.hk/rss.aspx',                             'type':'job'},
        {'name':'Recruit.com.hk', 'url':'https://www.recruit.com.hk/rss/joblist.xml',                    'type':'job'},
        {'name':'28Landlord 租盘','url':'https://www.28hse.com/en/rent/rss',                              'type':'house'},
        {'name':'Eventbrite HK',  'url':'https://www.eventbrite.hk/d/hong-kong/events/rss/',              'type':'event'},
        {'name':'HKTicketing',    'url':'https://www.hkticketing.com/rss/events.xml',                     'type':'event'},
    ],
    # ── 澳门服务 ──────────────────────────────────────────────
    'mo': [
        {'name':'澳门人才网',     'url':'https://www.jobsmacao.com/rss/jobs.xml',                         'type':'job'},
        {'name':'Eventbrite MO',  'url':'https://www.eventbrite.com/d/macao/events/rss/',                 'type':'event'},
    ],
}

# ════════════════════════════════════════════════════
# 关键词
# ════════════════════════════════════════════════════
CATEGORY_KW = {
    '移民': ['visa','immigration','migration','签证','移民','居留','入籍','permanent resident'],
    '政治': ['government','minister','parliament','election','政府','选举','议会','政策'],
    '经济': ['economy','inflation','interest rate','housing','mortgage','tax','经济','利率','房价','通胀'],
    '华人': ['chinese','china','mandarin','华人','中国','中文','华裔','chinatown'],
    '天气': ['weather','storm','flood','earthquake','cyclone','rain','天气','洪水','地震'],
    '教育': ['school','university','student','education','学校','大学','教育'],
    '科技': ['tech','ai','digital','cyber','科技','人工智能','数字'],
}
CHINESE_KW = ['chinese','china','mandarin','华人','中国','中文','华裔','普通话']
VISA_KW    = ['visa','immigration','移民','签证','residency','work permit']

# ════════════════════════════════════════════════════
# 工具函数
# ════════════════════════════════════════════════════
_robots_cache = {}

def can_fetch(url):
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
    if rp is None: return True
    ok = rp.can_fetch(BOT_UA, url)
    if not ok: print(f'  🚫 robots.txt禁止: {url[:55]}')
    return ok

def time_ago(pub):
    if not pub: return '今日'
    age_h = (time.time() - time.mktime(pub)) / 3600
    if age_h < 1:   return f'{int(age_h*60)}分前'
    if age_h < 24:  return f'{int(age_h)}小时前'
    if age_h < 48:  return '昨日'
    return f'{int(age_h/24)}天前'

def is_within_3days(pub):
    """只保留3天内的内容"""
    if not pub: return True  # 没有时间戳的保留
    age_h = (time.time() - time.mktime(pub)) / 3600
    return age_h <= 72

def extract_image(entry):
    if entry.get('media_content'):    return entry['media_content'][0].get('url')
    if entry.get('media_thumbnail'):  return entry['media_thumbnail'][0].get('url')
    for enc in entry.get('enclosures', []):
        if 'image' in enc.get('type', ''): return enc.get('href') or enc.get('url')
    return None

def news_score(entry, lang):
    score = 55
    text  = (entry.get('title','') + ' ' + entry.get('summary','')).lower()
    if any(k in text for k in CHINESE_KW): score += 12
    if any(k in text for k in VISA_KW):   score += 10
    if lang == 'zh':                        score += 8
    pub = entry.get('published_parsed')
    if pub:
        age_h = (time.time() - time.mktime(pub)) / 3600
        if age_h < 2:   score += 15
        elif age_h < 6: score += 10
        elif age_h < 24:score += 5
    return min(score, 99)

def svc_score(entry):
    score = 60
    text  = (entry.get('title','') + ' ' + entry.get('summary','')).lower()
    if any(k in text for k in CHINESE_KW): score += 10
    if any(k in text for k in ['urgent','急招','限时','hot','热门']): score += 8
    pub = entry.get('published_parsed')
    if pub:
        age_h = (time.time() - time.mktime(pub)) / 3600
        if age_h < 2:   score += 15
        elif age_h < 6: score += 10
        elif age_h < 24:score += 5
    return min(score, 99)

def get_categories(title, summary):
    text = (title + ' ' + summary).lower()
    cats = [c for c, kws in CATEGORY_KW.items() if any(k in text for k in kws)]
    return cats[:3] if cats else ['本地']

def fetch_rss(url, name, limit=8):
    if not can_fetch(url): return []
    try:
        feed    = feedparser.parse(url, agent=BOT_UA,
                    request_headers={'Accept-Language':'zh-CN,zh;q=0.9,en;q=0.8'},
                    handlers=[])
        entries = feed.entries[:limit]
        if entries: print(f'  ✅ {name}: {len(entries)}条')
        else:       print(f'  ⚠️  {name}: 无数据')
        return entries
    except Exception as e:
        print(f'  ❌ {name}: {e}')
        return []

def dedupe(cards):
    seen, out = set(), []
    for c in cards:
        k = c['title'][:20]
        if k not in seen:
            seen.add(k); out.append(c)
    return out

# ════════════════════════════════════════════════════
# 主逻辑
# ════════════════════════════════════════════════════
def scrape(region):
    name = REGION_NAMES.get(region, region)
    print(f'\n{"="*50}\n🌏 {name} ({region})\n{"="*50}')

    # 新闻
    news = []
    for src in NEWS_SOURCES.get(region, []):
        for e in fetch_rss(src['url'], src['name']):
            title   = e.get('title','').strip()[:100]
            if not title: continue
            summary = BeautifulSoup(e.get('summary', e.get('description','')), 'html.parser').get_text()[:200].strip()
            pub     = e.get('published_parsed') or e.get('updated_parsed')
            # 只保留3天内的新闻
            if not is_within_3days(pub):
                continue
            news.append({
                'id':         hashlib.md5((e.get('link','') + title).encode()).hexdigest()[:10],
                'type':       'news',
                'region':     region,
                'source':     src['name'],
                'lang':       src['lang'],
                'title':      title,
                'summary':    summary,
                'link':       e.get('link',''),
                'image':      extract_image(e),
                'categories': get_categories(title, summary),
                'score':      news_score(e, src['lang']),
                'ago':        time_ago(pub),
                'pub_ts':     time.mktime(pub) if pub else 0,
                'hot':        any(k in title.lower() for k in ['breaking','alert','重大','突发','紧急']),
            })
        time.sleep(0.8)

    news = dedupe(news)
    news.sort(key=lambda x: (x['score'], x['pub_ts']), reverse=True)
    news = news[:30]

    # 服务
    svcs = []
    for src in SERVICE_SOURCES.get(region, []):
        for e in fetch_rss(src['url'], src['name']):
            title   = e.get('title','').strip()[:100]
            if not title: continue
            summary = BeautifulSoup(e.get('summary', e.get('description','')), 'html.parser').get_text()[:150].strip()
            pub     = e.get('published_parsed') or e.get('updated_parsed')
            # 只保留3天内的服务信息
            if not is_within_3days(pub):
                continue
            type_label = {'job':'招聘','house':'房产','deal':'优惠','event':'活动'}.get(src['type'], src['type'])
            svcs.append({
                'id':          hashlib.md5((e.get('link','') + title).encode()).hexdigest()[:10],
                'type':        src['type'],
                'type_label':  type_label,
                'region':      region,
                'source':      src['name'],
                'title':       title,
                'summary':     summary,
                'link':        e.get('link',''),
                'tags':        [],
                'score':       svc_score(e),
                'ago':         time_ago(pub),
                'pub_ts':      time.mktime(pub) if pub else 0,
                'hot':         any(k in title.lower() for k in ['urgent','急招','限时','hot']),
            })
        time.sleep(0.8)

    svcs = dedupe(svcs)
    svcs.sort(key=lambda x: (x['score'], x['pub_ts']), reverse=True)
    svcs = svcs[:20]

    now = datetime.now(timezone.utc).isoformat()

    # 保存新闻
    with open(f'{OUTPUT_DIR}/news_{region}.json', 'w', encoding='utf-8') as f:
        json.dump({'region':region,'name':name,'updated_at':now,
                   'total':len(news),'articles':news}, f, ensure_ascii=False, indent=2)

    # 保存服务
    with open(f'{OUTPUT_DIR}/services_{region}.json', 'w', encoding='utf-8') as f:
        json.dump({'region':region,'name':name,'updated_at':now,
                   'total':len(svcs),'services':svcs}, f, ensure_ascii=False, indent=2)

    print(f'  💾 news_{region}.json ({len(news)}条) + services_{region}.json ({len(svcs)}条)')

# ════════════════════════════════════════════════════
# 入口
# ════════════════════════════════════════════════════
if __name__ == '__main__':
    region = sys.argv[1] if len(sys.argv) > 1 else 'nz'
    if region not in REGION_NAMES:
        print(f'❌ 不支持的地区: {region}')
        print(f'支持: {", ".join(REGION_NAMES.keys())}')
        sys.exit(1)
    print(f'🚀 K1980 单地区抓取器')
    print(f'⏰ {datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}')
    scrape(region)
    print('\n✅ 完成！')
