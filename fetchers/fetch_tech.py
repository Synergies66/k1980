#!/usr/bin/env python3
"""
k1980.app Â· ãç§æãæ¨¡å
AIãè¯çãå¤§åå¨æãç§ææ¿ç­
ç¬ç«è¿è¡ï¼æéä¸å½±åå¶ä»æ¨¡å
"""
from fetchers.core_engine import run_module

SOURCES = [
    {
        "name": "Reuters ç§æ",
        "url": "https://feeds.reuters.com/reuters/technologyNews",
        "category": "ç§æ",
        "language": "en",
    },
    {
        "name": "Google News ç§æ",
        "url": "https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGdqTlhZU0FtVnVHZ0pWVXlBQVAB?hl=en-US&gl=US&ceid=US:en",
        "category": "ç§æ",
        "language": "en",
    },
    {
        "name": "Google News AI",
        "url": "https://news.google.com/rss/search?q=artificial+intelligence+AI&hl=en-US&gl=US&ceid=US:en",
        "category": "ç§æ",
        "language": "en",
    },
    {
        "name": "Google News è¯çåå¯¼ä½",
        "url": "https://news.google.com/rss/search?q=semiconductor+chip+nvidia&hl=en-US&gl=US&ceid=US:en",
        "category": "ç§æ",
        "language": "en",
    },
]

INSTRUCTIONS = """
- éç¹å³æ³¨ï¼AIè¡ä¸å¨æãè¯çåºå£ç®¡å¶ï¼å¯¹åè£å·¥ç¨å¸å·¥ä½çå½±åï¼ãå¤§åè£å/æè
- çªåºå¯¹å¨åç¾ä»äºIT/å·¥ç¨è¡ä¸åäººçèä¸å½±å
- æ¶åç­¾è¯/å·¥ä½è®¸å¯çç§ææ¿ç­ååè¦éç¹è¯´æ
- H1BãOPTãSTEMç¸å³æ¿ç­æ¯éç¹è¯é¢
- ææ¯åè¯ä¿çè±æååï¼å æ¬å·è¯´æä¸­æå«ä¹

ç¼è¾ååï¼ææåå®¹å¿é¡»éµå®ï¼ï¼
- ä¸¥æ ¼ä¿ææ¿æ²»ä¸­ç«ï¼ä¸å¯¹ä»»ä½æ¿æ²»äººç©ãæ¿åææ¿åºåè¡¨ä¸ªäººè¯ä»·æç«åº
- å°åºä¸»æäºè®®ãé¢åäºç«¯ï¼åæ¬ä½ä¸éäºï¼å°æµ·ãåæµ·ãåä»ç±³å°ãå·´ä»¥å²çªç­ï¼ä»å®¢è§éè¿°åæ¹ç«åºï¼ä¸è¡¨è¾¾å¾å
- ä¸ä½¿ç¨å¸¦ææ¿æ²»å¾åçå½¢å®¹è¯æä¿®è¾ï¼å¦"éæ³"ã"æ­£ä¹"ã"éªæ¶"ç­ä»·å¼å¤æ­è¯æ±
- æ¶åæ¿æ²»ææäºä»¶åªæ¥éäºå®ï¼åçäºä»ä¹ãå½±åæ¯ä»ä¹ï¼ä¸ä½åå å½åæéå¾·è¯å¤
- å¦åæè§ç¹é²æï¼æ¹åæ¶åªä¿çäºå®é¨åï¼å é¤ç«åºè¡¨è¾¾
"""

if __name__ == "__main__":
    run_module(
        category="ç§æ",
        sources=SOURCES,
        custom_instructions=INSTRUCTIONS,
        max_items_per_source=5,
        sleep_between_calls=1.5,
    )
