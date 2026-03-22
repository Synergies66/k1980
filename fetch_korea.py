#!/usr/bin/env python3
"""
k1980.app · 【韩国本地】模块
覆盖：韩国本地资讯
独立运行，故障不影响其他模块
"""
from core_engine import run_module

SOURCES = [
    {"name":"Google News 在韩华人","url":"https://news.google.com/rss/search?q=%E5%9C%A8%E9%9F%A9%E5%8D%8E%E4%BA%BA+%E4%B8%AD%E6%96%87&hl=zh-CN&gl=KR&ceid=KR:zh-Hans","category":"韩国本地","language":"zh"},
    {"name":"Google News Korea Chinese","url":"https://news.google.com/rss/search?q=Korea+Chinese+community+Seoul&hl=en-US&gl=KR&ceid=KR:en","category":"韩国本地","language":"en"},
    {"name":"Google News 韩国签证政策","url":"https://news.google.com/rss/search?q=%E9%9F%A9%E5%9B%BD+%E7%AD%BE%E8%AF%81+%E5%B7%A5%E4%BD%9C%E8%AE%B8%E5%8F%AF&hl=zh-CN&gl=CN&ceid=CN:zh-Hans","category":"韩国本地","language":"zh"},
    {"name":"Google News Korean visa","url":"https://news.google.com/rss/search?q=Korea+visa+Chinese+E7+work+permit&hl=en-US&gl=KR&ceid=KR:en","category":"韩国本地","language":"en"}
]

INSTRUCTIONS = """
- 读者主要是在韩国的华人（留学生、IT工程师、K-pop/韩流文化爱好者）
- 重点关注：E-7技术签证、韩国永居政策、中韩文化交流、首尔华人聚居区（大林洞等）
- 韩元汇率对华人消费的影响、在韩华人创业环境
- 中韩关系政策变化对在韩华人的实际影响
- 保持客观，避免政治敏感表述

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
        category="韩国本地",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
