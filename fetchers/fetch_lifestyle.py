#!/usr/bin/env python3
"""
k1980.app · 【商业】模块
企业动态、产品发布、科技公司、商业报道
独立运行，故障不影响其他模块
"""
from fetchers.core_engine import run_module

SOURCES = [
    {
        "name": "Google News 科技企业",
        "url": "https://news.google.com/rss/search?q=tech+company+product+launch+startup&hl=en-US&gl=US&ceid=US:en",
        "category": "商业",
        "language": "en",
    },
    {
        "name": "Google News 华人商业",
        "url": "https://news.google.com/rss/search?q=%E5%8D%8E%E4%BA%BA+%E5%95%86%E4%B8%9A+%E4%BC%81%E4%B8%9A&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "category": "商业",
        "language": "zh",
    },
    {
        "name": "Google News 企业并购",
        "url": "https://news.google.com/rss/search?q=merger+acquisition+corporate+deal+billion&hl=en-US&gl=US&ceid=US:en",
        "category": "商业",
        "language": "en",
    },
    {
        "name": "Google News 产品发布",
        "url": "https://news.google.com/rss/search?q=product+launch+new+release+apple+google+microsoft&hl=en-US&gl=US&ceid=US:en",
        "category": "商业",
        "language": "en",
    },
    {
        "name": "Google News 创业融资",
        "url": "https://news.google.com/rss/search?q=startup+funding+venture+capital+series+round&hl=en-US&gl=US&ceid=US:en",
        "category": "商业",
        "language": "en",
    },
]

INSTRUCTIONS = """
- 专注企业、产品、科技商业报道，读者为海外华人商界人士和从业者
- 涉及具体公司时，说明公司规模、业务范围、与华人社区的关联
- 产品发布类：突出功能亮点、定价、上市时间、对华人用户的影响
- 融资并购类：说明金额、投资方、战略意义
- 语气专业客观，像《福布斯》或《彭博商业周刊》风格

编辑规范（所有内容必须遵守）：
- 严格保持政治中立，不对任何政治人物、政党或政府表个人评价或立场
- 地区主权争议、领土争端（包括但不限于：台海、南海、巴以冲突等），仅客观陈述各方立场，不表达倾向
- 不使用带有政治倾向的形容词或修辞，如"非法"、"正义"、"邪恶"等价值判断词汇
- 涉及政治敏感事件只报道事实，发生了什么、影响是什么，不作道德评判
- 如含观点性内容，删改时只保留事实部分，删除立场表达
"""

if __name__ == "__main__":
    run_module(
        category="商业",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
