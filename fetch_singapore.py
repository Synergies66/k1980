#!/usr/bin/env python3
"""
k1980.app · 【新加坡本地】模块
覆盖：新加坡本地资讯
独立运行，故障不影响其他模块
"""
from core_engine import run_module

SOURCES = [
    {"name":"联合早报","url":"https://www.zaobao.com.sg/rss/singapore","category":"新加坡本地","language":"zh"},
    {"name":"Google News 新加坡华人","url":"https://news.google.com/rss/search?q=%E6%96%B0%E5%8A%A0%E5%9D%A1+%E5%8D%8E%E4%BA%BA+%E7%A4%BE%E5%8C%BA&hl=zh-CN&gl=SG&ceid=SG:zh-Hans","category":"新加坡本地","language":"zh"},
    {"name":"Google News Singapore Chinese","url":"https://news.google.com/rss/search?q=Singapore+Chinese+community+employment+pass&hl=en-US&gl=SG&ceid=SG:en","category":"新加坡本地","language":"en"},
    {"name":"Google News 新加坡移民政策","url":"https://news.google.com/rss/search?q=Singapore+Employment+Pass+PR+citizenship+Chinese&hl=en-US&gl=SG&ceid=SG:en","category":"新加坡本地","language":"en"}
]

INSTRUCTIONS = """
- 读者主要是在新加坡工作生活的华人（EP/SP/WP持有者、PR申请者、公民）
- 新加坡华族占74%，语言用简体中文，可加入少量英语词汇（符合新加坡华人用语习惯）
- 重点关注：EP/SP/WP政策变化、PR/公民身份申请、新加坡本地就业市场、组屋（HDB）政策
- 新加坡特有话题：PSLE/O-level/A-level考试、华文教育、牛车水等华人文化活动
- 中国大陆新移民与本地华人的融合话题也很受关注

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
        category="新加坡本地",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
