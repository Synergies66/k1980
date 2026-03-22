#!/usr/bin/env python3
"""
k1980.app · 【科技】模块
AI、芯片、大厂动态、科技政策
独立运行，故障不影响其他模块
"""
from core_engine import run_module

SOURCES = [
    {
        "name": "Reuters 科技",
        "url": "https://feeds.reuters.com/reuters/technologyNews",
        "category": "科技",
        "language": "en",
    },
    {
        "name": "Google News 科技",
        "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGdqTlhZU0FtVnVHZ0pWVXlBQVAB?hl=en-US&gl=US&ceid=US:en",
        "category": "科技",
        "language": "en",
    },
    {
        "name": "Google News AI",
        "url": "https://news.google.com/rss/search?q=artificial+intelligence+AI&hl=en-US&gl=US&ceid=US:en",
        "category": "科技",
        "language": "en",
    },
    {
        "name": "Google News 芯片半导体",
        "url": "https://news.google.com/rss/search?q=semiconductor+chip+nvidia&hl=en-US&gl=US&ceid=US:en",
        "category": "科技",
        "language": "en",
    },
]

INSTRUCTIONS = """
- 重点关注：AI行业动态、芯片出口管制（对华裔工程师工作的影响）、大厂裁员/招聘
- 突出对在北美从事IT/工程行业华人的职业影响
- 涉及签证/工作许可的科技政策变化要重点说明
- H1B、OPT、STEM相关政策是重点话题
- 技术名词保留英文原名，加括号说明中文含义

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
        category="科技",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
