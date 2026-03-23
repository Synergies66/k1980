#!/usr/bin/env python3
"""
k1980.app · 【移民】模块
签证政策、绿卡排期、入籍、移民局动态
独立运行，故障不影响其他模块
"""
from fetchers.core_engine import run_module

SOURCES = [
    {
        "name": "Google News 美国移民",
        "url": "https://news.google.com/rss/search?q=US+immigration+visa+policy&hl=en-US&gl=US&ceid=US:en",
        "category": "移民",
        "language": "en",
    },
    {
        "name": "Google News 绿卡H1B",
        "url": "https://news.google.com/rss/search?q=green+card+H1B+USCIS&hl=en-US&gl=US&ceid=US:en",
        "category": "移民",
        "language": "en",
    },
    {
        "name": "Google News 加拿大移民",
        "url": "https://news.google.com/rss/search?q=Canada+immigration+Express+Entry+PR&hl=en-US&gl=US&ceid=US:en",
        "category": "移民",
        "language": "en",
    },
    {
        "name": "Google News 澳洲移民",
        "url": "https://news.google.com/rss/search?q=Australia+immigration+visa+skilled+migration&hl=en-US&gl=US&ceid=US:en",
        "category": "移民",
        "language": "en",
    },
    {
        "name": "Google News 华人移民",
        "url": "https://news.google.com/rss/search?q=%E5%8D%8E%E4%BA%BA+%E7%A7%BB%E6%B0%91+%E7%AD%BE%E8%AF%81&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "category": "移民",
        "language": "zh",
    },
]

INSTRUCTIONS = """
- 这是本站最核心的板块，读者高度关注，准确性要求最高
- 涉及政策数字（排期日期、配额数量、费用金额）必须从原文准确引用
- 明确区分：美国/加拿大/澳洲/英国/新西兰 不同国家政策，不要混淆
- 常用词汇保留英文：H1B, OPT, STEM OPT, EAD, I-485, I-140, EB-1/2/3, Express Entry, EOI
- 如有移民局公告或排期变化，在标题中标注国家和签证类别
- 政策解读要中立，避免夸大利好或利空，建议读者查阅官方网站确认

编辑原则（所有内容必须遵守）：
- 严格保持政治中立，不对任何政治人物、政党或政府发表个人评价或立场
- 地区主权争议、领土争端（包括但不限于：台海、南海、克什米尔、巴以冲突等）仅客观陈述各方立场，不表达倾向
- 不使用带有政治倾向的形容词或修辞，如"非法"、"正义"、"邪恶"等价值判断词汇
- 涉及政治敏感事件只报道事实：发生了什么、影响是什么，不作原因归咎或道德评判
- 如原文观点鲜明，改写时只保留事实部分，删除立场表达
"""

if __name__ == "__main__":
    run_module(
        category="移民",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
