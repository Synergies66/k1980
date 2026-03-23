#!/usr/bin/env python3
"""
k1980.app Â· ãæè²ãæ¨¡å
çå­¦ç³è¯·ãå­å¥³æè²ãå¤§å­¦æåãæè²æ¿ç­
ç¬ç«è¿è¡ï¼æéä¸å½±åå¶ä»æ¨¡å
"""
from fetchers.core_engine import run_module

SOURCES = [
    {
        "name": "Google News ç¾å½çå­¦",
        "url": "https://news.google.com/rss/search?q=US+university+international+students+admission&hl=en-US&gl=US&ceid=US:en",
        "category": "æè²",
        "language": "en",
    },
    {
        "name": "Google News å¤§å­¦ç³è¯·",
        "url": "https://news.google.com/rss/search?q=college+application+SAT+ACT+ivy+league&hl=en-US&gl=US&ceid=US:en",
        "category": "æè²",
        "language": "en",
    },
    {
        "name": "Google News å­¦çç­¾è¯",
        "url": "https://news.google.com/rss/search?q=F1+student+visa+OPT+STEM&hl=en-US&gl=US&ceid=US:en",
        "category": "æè²",
        "language": "en",
    },
    {
        "name": "Google News åäººå­å¥³æè²",
        "url": "https://news.google.com/rss/search?q=%E6%B5%B7%E5%A4%96%E5%8D%8E%E4%BA%BA+%E5%AD%90%E5%A5%B3+%E6%95%99%E8%82%B2+%E7%94%B3%E8%AF%B7&hl=zh-CN&gl=CN&ceid=CN:zh-Hans",
        "category": "æè²",
        "language": "zh",
    },
]

INSTRUCTIONS = """
- è¯»èä¸»è¦æ¯å¨æµ·å¤æå­å¥³çåäººç¶æ¯ï¼ææ­£å¨ç³è¯·/å¨è¯»ççå­¦ç
- éç¹è¯é¢ï¼åæ ¡å½åçååãAAå¹³ææ¿ç­å½±ååè£ãè¯¾å¤æ´»å¨åå·ãè´¹ç¨æ¶¨å¹
- æ¶ååè£å­¦çåå°åºå«å¯¹å¾çè¯é¢è¦å®¢è§åç°ï¼ä¸ç½æ
- çå­¦è´¹ç¨ä¿¡æ¯è¦æ¢ç®ä¸ºäººæ°å¸ï¼å¸®å©å½åå®¶é¿çè§£
- F1ç­¾è¯æ¿ç­ååæ¯é«ä¼åçº§è¯é¢
- å¸¸ç¨è¯ä¿çè±æï¼GPA, SAT, AP, IB, Common App, ED/EA/RD

ç¼è¾ååï¼ææåå®¹å¿é¡»éµå®ï¼ï¼
- ä¸¥æ ¼ä¿ææ¿æ²»ä¸­ç«ï¼ä¸å¯¹ä»»ä½æ¿æ²»äººç©ãæ¿åææ¿åºåè¡¨ä¸ªäººè¯ä»·æç«åº
- å°åºä¸»æäºè®®ãé¢åäºç«¯ï¼åæ¬ä½ä¸éäºï¼å°æµ·ãåæµ·ãåä»ç±³å°ãå·´ä»¥å²çªç­ï¼ä»å®¢è§éè¿°åæ¹ç«åºï¼ä¸è¡¨è¾¾å¾å
- ä¸ä½¿ç¨å¸¦ææ¿æ²»å¾åçå½¢å®¹è¯æä¿®è¾ï¼å¦"éæ³"ã"æ­£ä¹"ã"éªæ¶"ç­ä»·å¼å¤æ­è¯æ±
- æ¶åæ¿æ²»ææäºä»¶åªæ¥éäºå®ï¼åçäºä»ä¹ãå½±åæ¯ä»ä¹ï¼ä¸ä½åå å½åæéå¾·è¯å¤
- å¦åæè§ç¹é²æï¼æ¹åæ¶åªä¿çäºå®é¨åï¼å é¤ç«åºè¡¨è¾¾
"""

if __name__ == "__main__":
    run_module(
        category="æè²",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
