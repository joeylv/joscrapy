# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy import Item, Field


class JoblogItem(scrapy.Item):
    # define the fields for your item here like:
    url = Field()
    title = Field()
    body = Field()
    image_urls = Field()
    images = Field()
    image_paths = Field()
    # pass


class TitleItem(scrapy.Item):
    # define the fields for your item here like:
    name = Field()
    url = Field()
    day = Field()
    title = Field()


class BloggerItem(scrapy.Item):
    # define the fields for your item here like:
    name = Field()
    age = Field()
    fans = Field()
    focus = Field()
    tags = Field()
    category = Field()
