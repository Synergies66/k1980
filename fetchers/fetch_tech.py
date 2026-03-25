#!/usr/bin/env python3
"""k1980.app 科技模块"""
from core_engine import run_module

SOURCES = [
    {"name":"Reuters 科技","url":"https://feeds.reuters.com/reuters/technologyNews","category":"科技","language":"en"},
    {"name":"Google News 科技","url":"https://news.google.com/rss/topics/CAAqJggKIiBDQkFTRWdvSUwyMHZNRGdqTlhZU0FtVnVHZ0pWVXlBQVAB?hl=en-US&gl=US&ceid=US:en","category":"科技","language":"en"},
    {"name":"Google News AI","url":"https://news.google.com/rss/search?q=artificial+intelligence+AI&hl=en-US&gl=US&ceid=US:en","category":"科技","language":"en"},
    {"name":"Google News 半导体","url":"https://news.google.com/rss/search?q=semiconductor+chip+nvidia&hl=en-US&gl=US&ceid=US:en","category":"科技","language":"en"},
]

if __name__ == "__main__":
    run_module(SOURCES, category="科技")
