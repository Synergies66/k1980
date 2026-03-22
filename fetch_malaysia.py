#!/usr/bin/env python3
"""
k1980.app · 【马来西亚本地】模块
覆盖：马来西亚本地资讯
独立运行，故障不影响其他模块
"""
from core_engine import run_module

SOURCES = [
    {"name":"Google News 马来西亚华人","url":"https://news.google.com/rss/search?q=%E9%A9%AC%E6%9D%A5%E8%A5%BF%E4%BA%9A+%E5%8D%8E%E4%BA%BA+%E7%A4%BE%E5%8C%BA&hl=zh-CN&gl=MY&ceid=MY:zh-Hans","category":"马来西亚本地","language":"zh"},
    {"name":"Google News 星洲日报","url":"https://news.google.com/rss/search?q=site:sinchew.com.my&hl=zh-CN&gl=MY&ceid=MY:zh-Hans","category":"马来西亚本地","language":"zh"},
    {"name":"Google News Malaysia Chinese","url":"https://news.google.com/rss/search?q=Malaysia+Chinese+community+education+politics&hl=en-US&gl=MY&ceid=MY:en","category":"马来西亚本地","language":"en"},
    {"name":"Google News 马来西亚教育","url":"https://news.google.com/rss/search?q=%E9%A9%AC%E6%9D%A5%E8%A5%BF%E4%BA%9A+%E5%8D%8E%E6%96%87%E6%95%99%E8%82%B2+%E7%8B%AC%E4%B8%AD&hl=zh-CN&gl=MY&ceid=MY:zh-Hans","category":"马来西亚本地","language":"zh"}
]

INSTRUCTIONS = """
- 读者包括马来西亚本地华人和从大陆移居马来西亚的华人
- 马来西亚华人特有议题：独中教育（独立中学）、华团文化活动、茨厂街等华人商业区动态
- 马来西亚特殊政治生态：华人政党（MCA/DAP）、新经济政策对华人的影响
- 实用信息：马币汇率、MM2H移民计划（第二家园）、槟城/吉隆坡/新山华人聚居区资讯
- 语言可使用马来西亚华人特有表达（如"德士"=出租车，"组屋"=公寓等）

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
        category="马来西亚本地",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
