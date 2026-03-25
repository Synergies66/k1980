#!/usr/bin/env python3
"""k1980.app 财经模块（原商业）"""
from core_engine import run_module

SOURCES = [
    {"name":"Google News 科技企业","url":"https://news.google.com/rss/search?q=tech+company+product+launch+startup&hl=en-US&gl=US&ceid=US:en","category":"财经","language":"en"},
    {"name":"Google News 华人商业","url":"https://news.google.com/rss/search?q=%E5%8D%8E%E4%BA%BA+%E5%95%86%E4%B8%9A+%E4%BC%81%E4%B8%9A&hl=zh-CN&gl=CN&ceid=CN:zh-Hans","category":"财经","language":"zh"},
    {"name":"Google News 企业并购","url":"https://news.google.com/rss/search?q=merger+acquisition+corporate+deal+billion&hl=en-US&gl=US&ceid=US:en","category":"财经","language":"en"},
    {"name":"Google News 产品发布","url":"https://news.google.com/rss/search?q=product+launch+new+release+apple+google+microsoft&hl=en-US&gl=US&ceid=US:en","category":"财经","language":"en"},
    {"name":"Google News 创业融资","url":"https://news.google.com/rss/search?q=startup+funding+venture+capital+series+round&hl=en-US&gl=US&ceid=US:en","category":"财经","language":"en"},
]

if __name__ == "__main__":
    run_module(SOURCES, category="财经")
