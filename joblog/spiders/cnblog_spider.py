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
        # "https://www.cnblogs.com/chenssy/category/525010.html",  # Java 提高
        # "https://www.cnblogs.com/chenssy/category/482229.html",  # 设计模式
        # 'https://www.cnblogs.com/qiumingcheng/category/867569.html'
        # 'https://www.cnblogs.com/valor-xh/p/6348009.html',
        # 'https://www.cnblogs.com/blogs423524123/p/9495893.html',
        # 'https://www.cnblogs.com/blogs423524123/p/10099162.html',
        # 'https://www.cnblogs.com/blogs423524123/p/10098665.html',
        # 'https://www.cnblogs.com/blogs423524123/p/9515354.html',
        # 'https://www.cnblogs.com/JJJ1990/p/10096722.html',

    ]
    count = 0

    def start_requests(self):
        print(self.name)
        # print("start_requests")
        # for url in self.start_urls: # 系列文章目录
        #     yield Request(url=url, callback=self.parse)

        # for url in self.start_urls:  # 单个文章地址
        #     yield Request(url=url, callback=self.topic)

        # for i in range(1, 16):# 爬博主
        #     url = "https://www.cnblogs.com/chenssy/default.html?page={}".format(i)
        #     yield Request(url=url, callback=self.parse_pape)
        # for i in range(1, 9):# 爬博主
        #     url = "https://www.cnblogs.com/leesf456/default.html?page={}".format(i)
        #     yield Request(url=url, callback=self.parse_pape)
        # for i in range(1, 5):  # 爬博主
        #     url = "https://www.cnblogs.com/ityouknow/default.html?page={}".format(i)
        #     yield Request(url=url, callback=self.parse_pape)

        # for i in range(1, 21):  # 爬博主
        #     url = "https://www.cnblogs.com/sui776265233/default.html?page={}".format(i)
        #     yield Request(url=url, callback=self.parse_pape)

        for i in range(1, 18):  # 爬博主
            url = "https://www.cnblogs.com/ggzhangxiaochao/default.html?page={}".format(i)
            yield Request(url=url, callback=self.parse_pape)

        for i in range(1, 6):  # 爬博主
            url = "https://www.cnblogs.com/youzhibing/default.html?page={}".format(i)
            yield Request(url=url, callback=self.parse_pape)

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
        # print(url[url.rindex('/') + 1:url.rindex('.')])
        # print(response)
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
