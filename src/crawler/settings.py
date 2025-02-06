#!/usr/bin/env python3
# ~*~ coding: utf-8 ~*~
"""Scrapy settings for crawler."""
BOT_NAME = "src.crawler"

SPIDER_MODULES = ["src.crawler.spiders"]
NEWSPIDER_MODULE = "src.crawler.spiders"

ROBOTSTXT_OBEY = True

DEFAULT_REQUEST_HEADERS = {
    "Accept": "application/json",
}

# Set settings whose default value is deprecated to a future-proof value
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
