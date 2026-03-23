#!/usr/bin/env python3
"""
k1980.app Â· ãç§»æ°ãæ¨¡å
ç­¾è¯æ¿ç­ãç»¿å¡ææãå¥ç±ãç§»æ°å±å¨æ
ç¬ç«è¿è¡ï¼æéä¸å½±åå¶ä»æ¨¡å
"""
from fetchers.core_engine import run_module

SOURCES = [
    {
        "name": "Google News ç¾å½ç§»æ°",
        "url": "https://news.google.com/rss/search?q=US+immigration+visa+policy&hl=en-US&gl=US&ceid=US:en",
        "category": "ç§»æ°",
        "language": "en",
    },
    {
        "name": "Google News ç»¿å¡H1B",
        "url": "https://news.google.com/rss/search?q=green+card+H1B+USCIS&hl=en-US&gl=US&ceid=US:en",
        "category": "ç§»æ°",
        "language": "en",
    },
    {
        "name": "Google News å æ¿å¤§ç§»æ°",
        "url": "https://news.google.com/rss/search?q=Canada+immigration+Express+Entry+PR&hl=en-US&gl=US&ceid=US:en",
        "category": "ç§»æ°",
        "language": "en",
    },
    {
        "name": "Google News æ¾³æ´²ç§»æ°",
        "url": "https://news.google.com/rss/search?q=Australia+immigration+visa+skilled+migration&hl=en-US&gl=US&ceid=US:en",
        "category": "ç§»æ°",
        "language": "en",
    },
    {
        "name": "Google News åäººç§»æ°",
        "url": "https://news.google.com/rss/search?q=%E5%8D%8E%E4%BA%BA+%E7%A7%BB%E6%B0%91+%E7%AD%BE%E8%AF%81&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "category": "ç§»æ°",
        "language": "zh",
    },
]

INSTRUCTIONS = """
- è¿æ¯æ¬ç«ææ ¸å¿çæ¿åï¼è¯»èé«åº¦å³æ³¨ï¼åç¡®æ§è¦æ±æé«
- æ¶åæ¿ç­æ°å­ï¼æææ¥æãéé¢æ°éãè´¹ç¨éé¢ï¼å¿é¡»ä»åæåç¡®å¼ç¨
- æç¡®åºåï¼ç¾å½/å æ¿å¤§/æ¾³æ´²/è±å½/æ°è¥¿å° ä¸åå½å®¶æ¿ç­ï¼ä¸è¦æ··æ·
- å¸¸ç¨è¯æ±ä¿çè±æï¼H1B, OPT, STEM OPT, EAD, I-485, I-140, EB-1/2/3, Express Entry, EOI
- å¦æç§»æ°å±å¬åæææååï¼å¨æ é¢ä¸­æ æ³¨å½å®¶åç­¾è¯ç±»å«
- æ¿ç­è§£è¯»è¦ä¸­ç«ï¼é¿åå¤¸å¤§å©å¥½æå©ç©ºï¼å»ºè®®è¯»èæ¥éå®æ¹ç½ç«ç¡®è®¤

ç¼è¾ååï¼ææåå®¹å¿é¡»éµå®ï¼ï¼
- ä¸¥æ ¼ä¿ææ¿æ²»ä¸­ç«ï¼ä¸å¯¹ä»»ä½æ¿æ²»äººç©ãæ¿åææ¿åºåè¡¨ä¸ªäººè¯ä»·æç«åº
- å°åºä¸»æäºè®®ãé¢åäºç«¯ï¼åæ¬ä½ä¸éäºï¼å°æµ·ãåæµ·ãåä»ç±³å°ãå·´ä»¥å²çªç­ï¼ä»å®¢è§éè¿°åæ¹ç«åºï¼ä¸è¡¨è¾¾å¾å
- ä¸ä½¿ç¨å¸¦ææ¿æ²»å¾åçå½¢å®¹è¯æä¿®è¾ï¼å¦"éæ³"ã"æ­£ä¹"ã"éªæ¶"ç­ä»·å¼å¤æ­è¯æ±
- æ¶åæ¿æ²»ææäºä»¶åªæ¥éäºå®ï¼åçäºä»ä¹ãå½±åæ¯ä»ä¹ï¼ä¸ä½åå å½åæéå¾·è¯å¤
- å¦åæè§ç¹é²æï¼æ¹åæ¶åªä¿çäºå®é¨åï¼å é¤ç«åºè¡¨è¾¾
"""

if __name__ == "__main__":
    run_module(
        category="ç§»æ°",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
