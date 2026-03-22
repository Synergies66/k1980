#!/usr/bin/env python3
"""
k1980.app · 【财经】模块
美股、房市、汇率、宏观经济
独立运行，故障不影响其他模块
"""
from core_engine import run_module

SOURCES = [
    {
        "name": "Reuters 财经",
        "url": "https://feeds.reuters.com/reuters/businessNews",
        "category": "财经",
        "language": "en",
    },
    {
        "name": "Reuters 市场",
        "url": "https://feeds.reuters.com/reuters/financialsNews",
        "category": "财经",
        "language": "en",
    },
    {
        "name": "Google News 美股",
        "url": "https://news.google.com/rss/search?q=stock+market+S%26P500+nasdaq&hl=en-US&gl=US&ceid=US:en",
        "category": "财经",
        "language": "en",
    },
    {
        "name": "Google News 房地产",
        "url": "https://news.google.com/rss/search?q=US+housing+market+mortgage+rate&hl=en-US&gl=US&ceid=US:en",
        "category": "财经",
        "language": "en",
    },
    {
        "name": "Google News 人民币汇率",
        "url": "https://news.google.com/rss/search?q=%E4%BA%BA%E6%B0%91%E5%B8%81+%E6%B1%87%E7%8E%87+%E7%BE%8E%E5%85%83&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "category": "财经",
        "language": "zh",
    },
]

INSTRUCTIONS = """
- 重点关注：影响海外华人储蓄、投资、买房的经济政策
- 汇率波动（人民币/美元/加元/澳元）要具体说明对汇款的影响
- 美联储利率决定：联系抵押贷款、储蓄利率，用数字说话
- 美股大盘波动：与401(k)退休金挂钩，引导读者关注长期投资
- 房市报告：北美/澳洲/加拿大热门华人聚居城市为优先
- 避免具体投资建议，鼓励读者咨询专业人士

编辑原则（所有内容必须遵守）：
- 严格保持政治中立，不对任何政治人物、政党或政府发表个人评价或立场
- 地区主权争议、领土争端（包括但不限于：台海、南海、克什米尔、巴以冲突等）仅客观陈述各方立场，不表达倾向
- 不使用带有政治倾向的形容词或修辞，如"非法"、"正义"、"邪恶"等价值判断词汇
- 涉及政治敏感事件只报道事实：发生了什么、影响是什么，不作原因归咎或道德评判
- 如原文观点鲜明，改写时只保留事实部分，删除立场表达
"""

if __name__ == "__main__":
    run_module(
        category="财经",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
