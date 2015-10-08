# -*- coding: utf-8 -*-
import scrapy
import IceBreak.IceBreakTools as ibt
from IceBreak.items import IcebreakItem


class PickaxeSpider(scrapy.Spider):
    name = "pickAxe"
    allowed_domains = ['http://ora.ox.ac.uk','http://www.imdb.com','http://www3.imperial.ac.uk']
    start_urls = [
        'http://ora.ox.ac.uk/search/detailed?q=%2A%3A%2A&truncate=450&rows=500&sort=timestamp%20desc',
        'http://www.imdb.com/chart/top',
        'http://www3.imperial.ac.uk/cmbi/researchgroups/publications/?respub-action=search.html&id=288&limit=100&keywords=&iminyear=2011&imaxyear=2015&itypes=BOOK+CHAPTER%2CCONFERENCE+PAPER%2CJOURNAL+ARTICLE&_type=on&type=BOOK+CHAPTER&type=CONFERENCE+PAPER&type=JOURNAL+ARTICLE&minyear=2011&maxyear=2015&page=1'
    ]
    thresholds = {
        "similarity_threshold": 0.6,
        "node_threshold": 50,
        "average_similarity_threshold":0.7,
        "proportion_threshold":0.7
    }

    
    def __init__(self, st=0.55,nt=50,pt=0.7,ast=0.7, *args,**kwargs):
        super(PickaxeSpider, self).__init__(*args, **kwargs)
        self.thresholds["similarity_threshold"] = float(st)
        self.thresholds["node_threshold"] = float(nt)
        self.thresholds["proportion_threshold"] = float(pt)
        self.thresholds["ave_similarity_threshold"] = float(ast)

    def parse(self, response):
        r = response
        (layer,sims) = ibt.layer_report(r,self.thresholds)
        while not layer:
            r = ibt.select_cube(r)
            (layer,sims) = ibt.layer_report(r,self.thresholds)
        #ibt.serve_drink(r,sims,self.thresholds)
        [(yield a) for a in self.serve_drink(r,sims)]

    def serve_drink(self,r,sims):
        '''
        consume the children of r, processing only those with high enough similarity in "sims"
        '''
        items = []
        print("i made it")
        cubes = r.xpath("*")
        for ind in range(len(cubes)):
            if sims[ind]>=self.thresholds["similarity_threshold"]:
    	        print("*"*10+"Recording Record number: "+str(ind)+"*"*10)
    	        item = IcebreakItem()
    	        item["links"] = cubes[ind].xpath(".//@href").extract()
    	        item["title"] = "NOT IMPLEMENTED"
    	        item["authors"] = "NOT IMPLEMENTED"
    	        #item["free_text"] = "".join(cubes[ind].xpath("descendant::text()").extract())
    	        item["free_text"] = cubes[ind].xpath("string(.)").extract()
    	        items.append(item)
    	return items