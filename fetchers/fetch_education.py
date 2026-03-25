#!/usr/bin/env python3
"""k1980.app 教育模块"""
from core_engine import run_module

SOURCES = [
    {"name":"Google News 美国留学","url":"https://news.google.com/rss/search?q=US+university+international+students+admission&hl=en-US&gl=US&ceid=US:en","category":"教育","language":"en"},
    {"name":"Google News 大学申请","url":"https://news.google.com/rss/search?q=college+application+SAT+ACT+ivy+league&hl=en-US&gl=US&ceid=US:en","category":"教育","language":"en"},
    {"name":"Google News 学生签证","url":"https://news.google.com/rss/search?q=F1+student+visa+OPT+STEM&hl=en-US&gl=US&ceid=US:en","category":"教育","language":"en"},
    {"name":"Google News 华人子女教育","url":"https://news.google.com/rss/search?q=%E6%B5%B7%E5%A4%96%E5%8D%8E%E4%BA%BA+%E5%AD%90%E5%A5%B3+%E6%95%99%E8%82%B2+%E7%94%B3%E8%AF%B7&hl=zh-CN&gl=CN&ceid=CN:zh-Hans","category":"教育","language":"zh"},
]

if __name__ == "__main__":
    run_module(SOURCES, category="教育")
