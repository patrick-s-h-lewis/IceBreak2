# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from datetime import datetime

class IcebreakItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    links = scrapy.Field()
    title = scrapy.Field()
    authors = scrapy.Field()
    date_scraped = scrapy.Field()
    free_text = scrapy.Field() 
    #def __init__(self):
    #    self["date_scraped"] = datetime.now()    