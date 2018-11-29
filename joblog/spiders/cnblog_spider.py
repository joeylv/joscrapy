import scrapy
from scrapy import Selector, Request

from joblog.items import JoblogItem


class CnblogSpider(scrapy.Spider):
    name = "cnblog"
    allowed_domains = ["cnblogs.com"]

    # https://www.cnblogs.com/leesf456/p/5338951.html  JVM目录

    # https://www.cnblogs.com/leesf456/p/5345493.html 集合框架目录

    # https://www.cnblogs.com/leesf456/p/5550043.html JUC集合框架目录

    # https://www.cnblogs.com/leesf456/p/5628300.html  操作系统目录
    start_urls = [
        # https://www.cnblogs.com/leesf456/default.html?page=8
        "https://www.cnblogs.com/chenssy/category/525010.html",
        "https://www.cnblogs.com/chenssy/category/482229.html",
    ]
    count = 0

    def start_requests(self):
        print(self.name)
        # print("start_requests")
        for url in self.start_urls:
            yield Request(url=url, callback=self.parse)  # 去爬博客
        for i in range(1, 9):
            url = "https://www.cnblogs.com/leesf456/default.html?page={}".format(i)
            yield Request(url=url, callback=self.parse_pape)  # 去爬博客

    def parse(self, response):
        # class ="entrylistPosttitle"
        sel = Selector(text=response.body)
        # print(sel.xpath('//div[@class="entrylistPosttitle"]'))
        for context in sel.xpath('//div[@class="entrylistPosttitle"]//a/@href').extract():
            yield Request(url=context, callback=self.topic)

    def parse_pape(self, response):
        # class ="entrylistPosttitle"
        sel = Selector(text=response.body)
        # print(sel.xpath('//div[@class="entrylistPosttitle"]'))
        for context in sel.xpath('//div[@class="postTitle"]//a/@href').extract():
            yield Request(url=context, callback=self.topic)

    def topic(self, response):
        url = str(response.url)
        print(url[url.rindex('/') + 1:url.rindex('.')])
        if response.status == 200:
            self.count += 1
        print(self.count)
        sel = Selector(text=response.body)
        # print(sel.xpath('//div[@id="topic"]'))
        item = JoblogItem()
        item['url'] = url
        item['title'] = sel.xpath('//a[@id="cb_post_title_url"]/text()').extract()[0]
        item['body'] = sel.xpath('//div[@id="cnblogs_post_body"]').extract()[0]
        item['image_urls'] = sel.xpath('//div[@id="cnblogs_post_body"]//img/@src').extract()
        # print(sel.xpath('//div[@id="cnblogs_post_body"]//img/@src').extract())
        # print(item['topic'])
        # print(item.title)
        # for context in sel.xpath('//div[@class="entrylistPosttitle"]//a/@href').extract():
        #     print(context)
        # if list_imgs:
        #     item = DoubanImgsItem()
        #     item['image_urls'] = list_imgs
        # yield item
        return item
