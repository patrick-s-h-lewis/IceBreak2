# -*- coding: utf-8 -*-
import scrapy
import IceBreak.IceBreakTools as ibt
from IceBreak.items import IcebreakItem
import IceBreak.Cubes as cubes 


class PickaxeSpider(scrapy.Spider):
    name = "pickAxe"
    allowed_domains = []
    start_urls = []
    thresholds = {
        "similarity_threshold": 0.6,
        "node_threshold": 50,
        "average_similarity_threshold":0.7,
        "proportion_threshold":0.7
    }
    xp = ''
    
    def __init__(self, web_record,*args,**kwargs):
        super(PickaxeSpider, self).__init__(*args, **kwargs)
        self.thresholds = web_record['thresholds']
        self.allowed_domains = web_record['domain']
        self.start_urls = web_record['url']
        self.xp = cubes.main(web_record['url'])

    def parse(self, r):
        (_,sims) = cubes.layer_report(r,self.thresholds)
        recs = r.xpath(self.xp)
        for ind in len(recs):
	    if sims(ind):
	        print("*"*10+"Recording Record number: "+str(ind)+"*"*10)
    	        item = IcebreakItem()
    	        item["links"] = recs[ind].xpath(".//@href").extract()
    	        item["title"] = "NOT IMPLEMENTED"
    	        item["authors"] = "NOT IMPLEMENTED"
    	        item["free_text"] = recs[ind].xpath("string(.)").extract()
    	        yield item