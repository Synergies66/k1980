#!/usr/bin/env python3
"""
k1980.app · 【时事】模块
国际要闻、政治外交、社会事件
独立运行，故障不影响其他模块
"""
from core_engine import run_module

SOURCES = [
    {
        "name": "BBC 中文",
        "url": "https://feeds.bbci.co.uk/zhongwen/simp/rss.xml",
        "category": "时事",
        "language": "zh",
    },
    {
        "name": "Reuters 国际头条",
        "url": "https://feeds.reuters.com/reuters/topNews",
        "category": "时事",
        "language": "en",
    },
    {
        "name": "Reuters 世界新闻",
        "url": "https://feeds.reuters.com/Reuters/worldNews",
        "category": "时事",
        "language": "en",
    },
    {
        "name": "Google News 国际",
        "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlBQVAB?hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "category": "时事",
        "language": "zh",
    },
]

INSTRUCTIONS = """
- 重点关注：中美关系、台海动态、国际政治对海外华人的直接影响
- 涉及政策变化时，说明对持有中国护照或美国绿卡人士的实际影响
- 避免政治立场鲜明的表述，保持客观中立
- 如有突发事件，在摘要中标注「突发」二字

内容过滤规则（以下类型文章直接跳过，不改写不发布）：
- 朝鲜军事动态：导弹试射、核武器、军事演习、朝鲜领导人军事相关活动
- 伊朗军事动态：核计划、导弹项目、军事对抗、制裁相关军事内容
- 任何涉及武装冲突的详细战术报道
- 恐怖主义袭击的详细描述
- 上述话题如有必要报道，只能从"对海外华人出行/签证/安全"的实用角度切入，且必须极度简短

编辑原则（所有内容必须遵守）：
- 严格保持政治中立，不对任何政治人物、政党或政府发表个人评价或立场
- 地区主权争议、领土争端（包括但不限于：台海、南海、克什米尔、巴以冲突等）仅客观陈述各方立场，不表达倾向
- 不使用带有政治倾向的形容词或修辞，如"非法"、"正义"、"邪恶"等价值判断词汇
- 涉及政治敏感事件只报道事实：发生了什么、影响是什么，不作原因归咎或道德评判
- 如原文观点鲜明，改写时只保留事实部分，删除立场表达
"""

if __name__ == "__main__":
    run_module(
        category="时事",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
