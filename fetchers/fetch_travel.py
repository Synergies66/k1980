#!/usr/bin/env python3
"""
k1980.app · 【旅游】模块
海外华人旅行、目的地、签证、航班、酒店资讯
独立运行，故障不影响其他模块
"""
from core_engine import run_module

SOURCES = [
    {
        "name": "Google News 海外旅游",
        "url": "https://news.google.com/rss/search?q=travel+tourism+Asia+Pacific&hl=en-US&gl=US&ceid=US:en",
        "category": "旅游",
        "language": "en",
    },
    {
        "name": "Google News 华人旅游",
        "url": "https://news.google.com/rss/search?q=%E6%B5%B7%E5%A4%96%E6%97%85%E6%B8%B8+%E7%AD%BE%E8%AF%81+%E8%88%AA%E7%8F%AD&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "category": "旅游",
        "language": "zh",
    },
    {
        "name": "Google News 旅行签证",
        "url": "https://news.google.com/rss/search?q=visa+travel+restrictions+tourists&hl=en-US&gl=US&ceid=US:en",
        "category": "旅游",
        "language": "en",
    },
    {
        "name": "Google News 新西兰澳洲旅游",
        "url": "https://news.google.com/rss/search?q=New+Zealand+Australia+tourism+travel&hl=en-US&gl=US&ceid=US:en",
        "category": "旅游",
        "language": "en",
    },
    {
        "name": "Google News 航班机票",
        "url": "https://news.google.com/rss/search?q=airline+flight+ticket+price+Pacific&hl=en-US&gl=US&ceid=US:en",
        "category": "旅游",
        "language": "en",
    },
]

INSTRUCTIONS = """
- 读者是经常在海外与中国之间往返的华人，也包括在海外定居后探索当地旅游的华人
- 重点话题：中国/新西兰/澳洲/加拿大/美国之间的签证政策变化、航班恢复、机票涨跌
- 具体数字要保留：机票价格换算为人民币、当地住宿费用要说清楚
- 热门目的地（北岛/南岛/大堡礁/黄石等）的华人友好信息优先（有中文服务吗？）
- 旅行安全提示、健康须知要简洁列出
- 节假日（中国春节、黄金周、圣诞节）前的旅游资讯是高优先级
- 语气轻松愉快，像朋友分享旅行心得

编辑原则（所有内容必须遵守）：
- 严格保持政治中立，不对任何政治人物、政党或政府发表个人评价或立场
- 地区主权争议、领土争端（包括但不限于：台海、南海、克什米尔、巴以冲突等）仅客观陈述各方立场，不表达倾向
- 不使用带有政治倾向的形容词或修辞，如"非法"、"正义"、"邪恶"等价值判断词汇
- 涉及政治敏感事件只报道事实：发生了什么、影响是什么，不作原因归咎或道德评判
- 如原文观点鲜明，改写时只保留事实部分，删除立场表达
"""

if __name__ == "__main__":
    run_module(
        category="旅游",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
