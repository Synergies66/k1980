#!/usr/bin/env python3
"""
k1980.app · 【印尼本地】模块
覆盖：印尼本地资讯
独立运行，故障不影响其他模块
"""
from core_engine import run_module

SOURCES = [
    {"name":"Google News 印尼华人","url":"https://news.google.com/rss/search?q=%E5%8D%B0%E5%B0%BC%E5%8D%8E%E4%BA%BA+%E5%8D%8E%E4%BA%BA+%E7%A4%BE%E5%8C%BA&hl=zh-CN&gl=ID&ceid=ID:zh-Hans","category":"印尼本地","language":"zh"},
    {"name":"Google News Indonesia Chinese","url":"https://news.google.com/rss/search?q=Indonesia+Chinese+community+Jakarta+overseas+Chinese&hl=en-US&gl=ID&ceid=ID:en","category":"印尼本地","language":"en"},
    {"name":"Google News 印尼签证","url":"https://news.google.com/rss/search?q=Indonesia+KITAS+KITAP+work+permit+Chinese&hl=en-US&gl=ID&ceid=ID:en","category":"印尼本地","language":"en"},
    {"name":"Google News 印华日报","url":"https://news.google.com/rss/search?q=%E5%8D%B0%E5%B0%BC%E5%8D%8E%E4%BA%BA+%E9%9B%85%E5%8A%A0%E8%BE%BE+%E7%94%9F%E6%B4%BB&hl=zh-CN&gl=CN&ceid=CN:zh-Hans","category":"印尼本地","language":"zh"}
]

INSTRUCTIONS = """
- 读者包括在印尼经商、工作的大陆华人，以及印尼本地华裔（华族）
- 印尼华人特有议题：华族春节、KITAS/KITAP工作许可、华人商业（特别是基础设施和矿业投资）
- 雅加达格罗多唐人街、苏拉巴亚华人聚居区动态
- 印尼政治经济环境对华人商业的影响
- 中印尼双边关系、一带一路项目进展对在印尼华人企业的影响
- 保持政治敏感话题的中立立场

编辑原则（所有内容必须遵守）：
- 严格保持政治中立，不对任何政治人物、政党或政府发表个人评价或立场
- 地区主权争议、领土争端（包括但不限于：台海、南海、克什米尔、巴以冲突等）仅客观陈述各方立场，不表达倾向
- 不使用带有政治倾向的形容词或修辞，如"非法"、"正义"、"邪恶"等价值判断词汇
- 涉及政治敏感事件只报道事实：发生了什么、影响是什么，不作原因归咎或道德评判
- 如原文观点鲜明，改写时只保留事实部分，删除立场表达
"""

if __name__ == "__main__":
    run_module(
        category="印尼本地",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
