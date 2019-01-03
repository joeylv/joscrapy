# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


import sqlite3
from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline

from joblog.items import TitleItem


def transferContent(content):
    if content is None:
        return None
    else:
        string = ""
        for c in content:
            if c == '"':
                string += '\\\"'
            elif c == "'":
                string += "\\\'"
            elif c == "\\":
                string += "\\\\"
            else:
                string += c
        return string


class JoblogPipeline(object):
    def __init__(self):
        self.con = sqlite3.connect('topic.db')
        self.cur = self.con.cursor()
        self.create_table()
        self.count = 0

    def process_item(self, item, spider):
        # print(item)
        # print(self.select_ex(item))
        # print(self.select_ex(item) is None)
        if self.select_ex(item) is None:
            self.insert_into(item)
            # print('Not exist::::::::::::' + item['title'])
        else:
            print('exist::::::::::::' + item['title'])

        # print('process_item {} {}'.format(item['image_urls'], item.get('image_paths', '')))
        return item

    def select_ex(self, item):
        if isinstance(item, TitleItem):
            sql = "SELECT * from title where url = '%s' or title ='%s'" % (item.get('url', ''), item.get('title', ''))
        else:
            sql = "SELECT * from topic where url = '%s' or title ='%s'" % (
                item.get('url', ''), item.get('title', '').replace('—–', '-----'))

        self.cur.execute(sql)
        return self.cur.fetchone()

    def insert_into(self, item):
        # print(item)
        if isinstance(item, TitleItem):
            self.count += 1
            print(self.count)
            sql = "INSERT INTO title(name,url,title)  VALUES('%s','%s','%s')" \
                  % (item.get('name', ''), item.get('url', ''), item['title'].replace("'", '"'),)
        else:
            image_paths = image_urls = ''
            for x in item.get('image_urls', ''):
                image_urls += x + ','
            for x in item.get('image_paths', ''):
                image_paths += x + ','

            sql = "INSERT INTO topic(url,title, body ,image_urls,images,image_paths)  VALUES('%s','%s','%s','%s','%s','%s')" \
                  % (item.get('url', ''), item['title'], str(item['body'].replace("'", "\"")),
                     image_urls, item.get('images', ''), image_paths)
        # print(sql)
        # print(item.get('image_paths'))
        # print('image_urls:::::::' + image_urls)
        # print('image_paths:::::::' + image_paths)

        try:
            self.cur.execute(sql)
        except Exception as e:
            print("WWWWWWWWW" + e)

        self.con.commit()

    def create_table(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS topic(id INTEGER PRIMARY KEY NOT NULL, \
                                        url varchar, \
                                        title varchar, \
                                        body TEXT, \
                                        image_urls varchar, \
                                        images varchar, \
                                        image_paths varchar )")

        self.cur.execute("CREATE TABLE IF NOT EXISTS title(id INTEGER PRIMARY KEY NOT NULL, \
                                                name varchar, \
                                                url varchar, \
                                                title varchar)")


class JoblogImagePipeline(ImagesPipeline):
    default_headers = {
        'accept': 'image/webp,image/*,*/*;q=0.8',
        'accept-encoding': 'gzip, deflate, sdch, br',
        'accept-language': 'zh-CN,zh;q=0.8,en;q=0.6',
        'cookie': 'bid=yQdC/AzTaCw',
        'referer': 'https://www.cnblogs.com/chenssy/',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Safari/537.36',
    }

    def get_media_requests(self, item, info):
        # print("get_media_requests {}".format(info))
        for image_url in item['image_urls']:
            self.default_headers['referer'] = image_url
            # print("image_url::::::::::::::" + image_url)
            yield Request(image_url, headers=self.default_headers)

    def item_completed(self, results, item, info):
        # print('item_completed {}    {} '.format(results, info))
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        # print('image_paths:::::::::::' + x for x in item['image_paths'])

        return item
