#!/usr/bin/env python3
"""
k1980.app · 【时事】模块
国际要闻、政治外交、社会事件
独立运行，故障不影响其他模块
"""
from fetchers.core_engine import run_module

SOURCES = [
    {
        "name": "BBC 中文",
        "url": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
        "category": "时事",
        "language": "zh",
    },
    {
        "name": "BBC 国际新闻",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "category": "时事",
        "language": "en",
    },
    {
        "name": "RFI 法广中文",
        "url": "https://www.rfi.fr/cn/rss",
        "category": "时事",
        "language": "zh",
    },
    {
        "name": "Deutsche Welle 德国之声中文",
        "url": "https://rss.dw.com/rdf/rss-chi-all",
        "category": "时事",
        "language": "zh",
    },
    {
        "name": "Google News 国际头条",
        "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlBQVAB?hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "category": "时事",
        "language": "zh",
    },
    {
        "name": "Google News 华人关注",
        "url": "https://news.google.com/rss/search?q=%E5%8D%8E%E4%BA%BA+%E6%B5%B7%E5%A4%96+%E6%96%B0%E9%97%BB&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "category": "时事",
        "language": "zh",
    },
    {
        "name": "Google News 中美关系",
        "url": "https://news.google.com/rss/search?q=%E4%B8%AD%E7%BE%8E%E5%85%B3%E7%B3%BB+%E8%B4%B8%E6%98%93&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "category": "时事",
        "language": "zh",
    },
    {
        "name": "Google News 英文国际",
        "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlBQVAB?hl=en-US&gl=US&ceid=US:en",
        "category": "时事",
        "language": "en",
    },
    {
        "name": "Al Jazeera 英文",
        "url": "https://www.aljazeera.com/xml/rss/all.xml",
        "category": "时事",
        "language": "en",
    },
    {
        "name": "VOA 中文",
        "url": "https://www.voachinese.com/api/zrqeipoe_t",
        "category": "时事",
        "language": "zh",
    },
]

INSTRUCTIONS = """
- 重点关注：中美关系、台海动态、国际政治对海外华人的直接影响
- 涉及政策变化时，说明对持有中国护照或美国绿卡人士的实际影响
- 避免政治立场鲜明的表述，保持客观中立
- 如果突发事件，在摘要中标注「突发」二字
- 优先选择与海外华人生活、工作、投资直接相关的新闻
- 英文新闻翻译成中文，保留关键专有名词的英文原文
- 每条新闻摘要100-150字，清晰说明：发生了什么、在哪里、影响是什么
编辑规范（所有内容必须遵守）：
- 严格保持政治中立，不对任何政治人物、政党或政府表达个人评价或立场
- 地区主权争议、领土之争（包括但不限于：台海、南海、巴以冲突、巴什米尔冲突等），从客观陈述各方立场，不表达倾向
- 不使用带有政治倾向的形容词或修辞，如"非法"、"正义"、"邪恶"等价值判断词汇
- 涉及政治或敏感事件只报道事实，发生了什么、影响是什么，不做价值判断或道德评价
- 如发现观点鲜明，修改时只保留事实部分，删除立场表达
"""

if __name__ == "__main__":
    run_module(
        category="时事",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=8,
        sleep_between_calls=1.5,
    )
