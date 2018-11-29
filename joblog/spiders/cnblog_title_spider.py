import re
import time

import scrapy
from scrapy import Selector, Request

from joblog.items import JoblogItem, TitleItem


class CnblogSpider(scrapy.Spider):
    name = "blog_title"
    allowed_domains = ["cnblogs.com"]

    start_urls = [
        # "https://www.cnblogs.com/AllBloggers.aspx",
        "https://www.cnblogs.com/aggsite/UserStats",
    ]

    def start_requests(self):
        print(self.name)
        # print("start_requests")
        # for url in self.start_urls:
        #     yield Request(url=url, callback=self.parse)  # 去爬微博
        url = "http://www.cnblogs.com/chenssy/"
        yield Request(url=url, callback=self.title_parse)  # 去爬微博

    def parse(self, response):
        # class ="entrylistPosttitle"
        sel = Selector(text=response.body)
        # print(response.body)
        for context in sel.xpath('//div[@id="blogger_list"]//a/@href').extract():
            yield Request(url='https:' + context, callback=self.blogger)

    def blogger(self, response):
        sel = Selector(text=response.body)
        # for context in sel.xpath('//div[@class="postTitle"]//a/@href').extract():
        #     print(context)
        for context in sel.xpath('//div[@id="nav_next_page"]//a/@href').extract():
            # print(context)
            yield Request(url=context, callback=self.blogger)
        pager = sel.xpath('//div[@id="homepage_top_pager"]//a/@href').extract()
        if pager:
            url = str(response.url)
            pager = str(pager[len(pager) - 1])
            # int(pager[pager.rindex('=') + 1:])
            for i in range(int(pager[pager.rindex('=') + 1:])):
                url = url[:url.rindex('/') + 1] + 'default.html?page={}'.format(i + 1)
                yield Request(url=url, callback=self.title_parse, dont_filter=True)

    def title_parse(self, response):
        sel = Selector(text=response.body)
        # print(response.url)
        # url = str(response.url)
        # print(':::::::::{}::::::::::::::{}'.format(response.url, len(sel.xpath('//div[@class="postTitle"]//a/text()'))))
        for t in sel.xpath('//div[@class="day"]/*'):
        # for t in sel.xpath('//div[@class="dayTitle"]/*'):
            print(t.xpath('//div[@class="dayTitle"]//a').extract())
            # print(t.xpath('//div[@class="dayTitle"]'))
            print(t.xpath('//div[@class="postTitle"]'))
            print(t.xpath('//div[@class="postDesc"]'))
            # i = t.css('//div[@class="dayTitle"]')
            # print(i)

        # for t in sel.xpath('//a[@class="postTitle2"]'):
        #     item = TitleItem()
        #     item['url'] = t.xpath('@href').extract()[0]
        #     item['name'] = url[url.rindex('com/') + 4:url.rindex('/')]
        #     # item['day'] = context.xpath('//div[@class="dayTitle"]//a/text()').extract()
        #     item['title'] = t.xpath('text()').extract()[0]
        #     # item['title'] = context.extract()
        #     # for context in sel.xpath('//div[@class="dayTitle"]//a/@href').extract():
        #     # for context in sel.xpath('//div[@class="postTitle"]//a/@href').extract():
        #     # print(item)
        #     yield item
