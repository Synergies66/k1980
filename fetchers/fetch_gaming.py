#!/usr/bin/env python3
"""
k1980.app · 【游戏】模块
华人玩家、游戏行业、电竞、手游、主机资讯
独立运行，故障不影响其他模块
"""
from core_engine import run_module

SOURCES = [
    {
        "name": "Google News 游戏行业",
        "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGRqTVhZU0FtVnVHZ0pWVXlBQVAB?hl=en-US&gl=US&ceid=US:en",
        "category": "游戏",
        "language": "en",
    },
    {
        "name": "Google News 电竞",
        "url": "https://news.google.com/rss/search?q=esports+gaming+tournament+2025&hl=en-US&gl=US&ceid=US:en",
        "category": "游戏",
        "language": "en",
    },
    {
        "name": "Google News 手机游戏",
        "url": "https://news.google.com/rss/search?q=mobile+game+new+release+2025&hl=en-US&gl=US&ceid=US:en",
        "category": "游戏",
        "language": "en",
    },
    {
        "name": "Google News 华人游戏",
        "url": "https://news.google.com/rss/search?q=%E6%B8%B8%E6%88%8F+%E6%96%B0%E6%B8%B8%E6%88%8F+%E7%94%B5%E7%AB%9E&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "category": "游戏",
        "language": "zh",
    },
    {
        "name": "Google News 主机游戏",
        "url": "https://news.google.com/rss/search?q=PlayStation+Xbox+Nintendo+Switch+game&hl=en-US&gl=US&ceid=US:en",
        "category": "游戏",
        "language": "en",
    },
]

INSTRUCTIONS = """
- 读者是海外华人玩家，年龄跨度大（18-45岁），包括休闲玩家和硬核玩家
- 重点话题：新游戏发布、大厂（腾讯/网易/米哈游）动态、电竞赛事、游戏监管政策
- 中国游戏出海、海外游戏进入中国市场的资讯很受关注
- 涉及游戏名称保留原名（中英文均可），不要强行翻译
- 游戏版号、未成年人保护政策等监管内容要客观说明
- 电竞赛事结果要及时、简洁：谁赢了、奖金多少、下一轮是什么
- 语气活泼，可以用玩家圈的表达方式，但不要过度使用网络梗

编辑原则（所有内容必须遵守）：
- 严格保持政治中立，不对任何政治人物、政党或政府发表个人评价或立场
- 地区主权争议、领土争端（包括但不限于：台海、南海、克什米尔、巴以冲突等）仅客观陈述各方立场，不表达倾向
- 不使用带有政治倾向的形容词或修辞，如"非法"、"正义"、"邪恶"等价值判断词汇
- 涉及政治敏感事件只报道事实：发生了什么、影响是什么，不作原因归咎或道德评判
- 如原文观点鲜明，改写时只保留事实部分，删除立场表达
"""

if __name__ == "__main__":
    run_module(
        category="游戏",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
