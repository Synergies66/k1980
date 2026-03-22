#!/usr/bin/env python3
"""
k1980.app · 【生活】模块
海外华人社区、健康、购物、生活资讯
独立运行，故障不影响其他模块
"""
from core_engine import run_module

SOURCES = [
    {
        "name": "Google News 华人社区",
        "url": "https://news.google.com/rss/search?q=Chinese+American+community+news&hl=en-US&gl=US&ceid=US:en",
        "category": "生活",
        "language": "en",
    },
    {
        "name": "Google News 北美生活",
        "url": "https://news.google.com/rss/search?q=%E6%B5%B7%E5%A4%96%E5%8D%8E%E4%BA%BA+%E7%94%9F%E6%B4%BB+%E7%A4%BE%E5%8C%BA&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "category": "生活",
        "language": "zh",
    },
    {
        "name": "Google News 美国医疗",
        "url": "https://news.google.com/rss/search?q=US+healthcare+insurance+cost&hl=en-US&gl=US&ceid=US:en",
        "category": "生活",
        "language": "en",
    },
    {
        "name": "Google News 消费物价",
        "url": "https://news.google.com/rss/search?q=inflation+consumer+price+cost+of+living+US&hl=en-US&gl=US&ceid=US:en",
        "category": "生活",
        "language": "en",
    },
]

INSTRUCTIONS = """
- 贴近海外华人日常生活：医疗保险、超市物价、驾照、换证、税务常识
- 社区安全事件（涉及亚裔/华人的）要报道但措辞谨慎，不渲染恐慌
- 通货膨胀/生活成本内容联系具体物价（食品、油价、房租）
- 健康类信息要注明「建议咨询医生」，不做医疗建议
- 语气轻松，贴近生活，适当使用「咱们」「大家」等亲切称谓

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
        category="生活",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
