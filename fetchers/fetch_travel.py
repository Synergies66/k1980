#!/usr/bin/env python3
"""k1980.app 生活模块（原旅游）"""
from core_engine import run_module

SOURCES = [
    {"name":"Google News 海外旅游","url":"https://news.google.com/rss/search?q=travel+tourism+Asia+Pacific&hl=en-US&gl=US&ceid=US:en","category":"生活","language":"en"},
    {"name":"Google News 华人旅游","url":"https://news.google.com/rss/search?q=%E6%B5%B7%E5%A4%96%E6%97%85%E6%B8%B8+%E7%AD%BE%E8%AF%81+%E8%88%AA%E7%8F%AD&hl=zh-CN&gl=CN&ceid=CN:zh-Hans","category":"生活","language":"zh"},
    {"name":"Google News 旅行签证","url":"https://news.google.com/rss/search?q=visa+travel+restrictions+tourists&hl=en-US&gl=US&ceid=US:en","category":"生活","language":"en"},
    {"name":"Google News 新西兰澳洲旅游","url":"https://news.google.com/rss/search?q=New+Zealand+Australia+tourism+travel&hl=en-US&gl=US&ceid=US:en","category":"生活","language":"en"},
    {"name":"Google News 航班机票","url":"https://news.google.com/rss/search?q=airline+flight+ticket+price+Pacific&hl=en-US&gl=US&ceid=US:en","category":"生活","language":"en"},
]

if __name__ == "__main__":
    run_module(SOURCES, category="生活")
