#!/usr/bin/env python3
"""
k1980.app · 【教育】模块
留学申请、子女教育、大学排名、教育政策
独立运行，故障不影响其他模块
"""
from core_engine import run_module

SOURCES = [
    {
        "name": "Google News 美国留学",
        "url": "https://news.google.com/rss/search?q=US+university+international+students+admission&hl=en-US&gl=US&ceid=US:en",
        "category": "教育",
        "language": "en",
    },
    {
        "name": "Google News 大学申请",
        "url": "https://news.google.com/rss/search?q=college+application+SAT+ACT+ivy+league&hl=en-US&gl=US&ceid=US:en",
        "category": "教育",
        "language": "en",
    },
    {
        "name": "Google News 学生签证",
        "url": "https://news.google.com/rss/search?q=F1+student+visa+OPT+STEM&hl=en-US&gl=US&ceid=US:en",
        "category": "教育",
        "language": "en",
    },
    {
        "name": "Google News 华人子女教育",
        "url": "https://news.google.com/rss/search?q=%E6%B5%B7%E5%A4%96%E5%8D%8E%E4%BA%BA+%E5%AD%90%E5%A5%B3+%E6%95%99%E8%82%B2+%E7%94%B3%E8%AF%B7&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "category": "教育",
        "language": "zh",
    },
]

INSTRUCTIONS = """
- 读者主要是在海外有子女的华人父母，或正在申请/在读的留学生
- 重点话题：名校录取率变化、AA平权政策影响华裔、课外活动内卷、费用涨幅
- 涉及华裔学生受到区别对待的话题要客观呈现，不煽情
- 留学费用信息要换算为人民币，帮助国内家长理解
- F1签证政策变化是高优先级话题
- 常用词保留英文：GPA, SAT, AP, IB, Common App, ED/EA/RD

编辑原则（所有内容必须遵守）：
- 严格保持政治中立，不对任何政治人物、政党或政府发表个人评价或立场
- 地区主权争议、领土争端（包括但不限于：台海、南海、克什米尔、巴以冲突等）仅客观陈述各方立场，不表达倾向
- 不使用带有政治倾向的形容词或修辞，如"非法"、"正义"、"邪恶"等价值判断词汇
- 涉及政治敏感事件只报道事实：发生了什么、影响是什么，不作原因归咎或道德评判
- 如原文观点鲜明，改写时只保留事实部分，删除立场表达
"""

if __name__ == "__main__":
    run_module(
        category="教育",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
