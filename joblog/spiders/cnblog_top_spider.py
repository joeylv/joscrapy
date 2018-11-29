import re

import scrapy
from scrapy import Selector, Request

from joblog.items import JoblogItem


class CnblogSpider(scrapy.Spider):
    name = "topblog"
    allowed_domains = ["cnblogs.com"]

    start_urls = [
        # "https://www.cnblogs.com/AllBloggers.aspx",
        "https://www.cnblogs.com/aggsite/UserStats"
        # "https://www.cnblogs.com/artech/",
        # "https://www.cnblogs.com/huangxincheng/",
        # "https://www.cnblogs.com/chenxizhang/",
    ]

    def start_requests(self):
        print(self.name)
        # print("start_requests")
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)  # 去爬微博
        # url = "https://www.cnblogs.com/aggsite/UserStats"
        # yield Request(url=url, callback=self.parse)  # 去爬微博

    def parse(self, response):
        # class ="entrylistPosttitle"
        sel = Selector(text=response.body)
        for context in sel.xpath('//div[@id="blogger_list"]//a/@href').extract():
            userid = context.replace('//www.cnblogs.com', '')
            yield Request(url='https://www.cnblogs.com' + userid + 'mvc/blog/sidecolumn.aspx?blogApp=' + userid,
                          callback=self.blogger)

    def blogger(self, response):
        sel = Selector(text=response.body)
        size = count = 0

        print(response.url)
        if sel.xpath('//div[@id="sidebar_toptags"]'):
            print(sel.xpath('//div[@id="sidebar_toptags"]').extract())
            # print(sel.xpath('//div[@id="sidebar_toptags"]').extract())

        if sel.xpath('//div[@id="sidebar_postarchive"]'):
            print(sel.xpath('//div[@id="sidebar_postarchive"]').extract())
            docs = sel.xpath('//div[@id="sidebar_postarchive"]//h3//span/text()').extract()
            size = self.couseint(docs)

        if sel.xpath('//div[@id="sidebar_categories"]'):
            print(sel.xpath('//div[@id="sidebar_categories"]').extract())
            docs = sel.xpath('//div[@id="sidebar_categories"]//h3//span/text()').extract()
            print(type(docs))
            print(len(docs))
            print(docs)
            if len(docs) > 0:
                count = self.couseint(docs)
                print(count)
            else:
                docs = sel.xpath('//div[@id="sidebar_categories"]//li//a/text()').extract()
                count = self.couseint(docs, True)
                print(count)
        print(size)
        print(count)

    def topic(self, response):
        print(response.url)
        if response.status == 200:
            self.count += 1
        print(self.count)
        sel = Selector(text=response.body)
        # print(sel.xpath('//div[@id="topic"]'))
        item = JoblogItem()
        item['title'] = sel.xpath('//a[@id="cb_post_title_url"]/text()').extract()[0]
        item['body'] = sel.xpath('//div[@id="cnblogs_post_body"]').extract()[0]
        item['image_urls'] = sel.xpath('//div[@id="cnblogs_post_body"]//img/@src').extract()

    def couseint(self, docs, p=False):
        count = 0
        if isinstance(docs, list) and len(docs) > 0:
            # docs = docs[0]
            print('108:::::::::::::')
            for doc in docs:
                print(doc)
                doc = str(doc)
                print('112:::::::::::::' + doc)
                print(doc.__contains__('('))
                print(doc.find('('))
                if doc.__contains__('('):
                    doc = doc[doc.index('(') + 1:doc.rindex(')')]
                    doc = int(doc.replace('(', '').replace(')', ''))

                    print(doc)
                    if p:
                        count += doc
                    else:
                        if doc > count:
                            count = doc
        return count
