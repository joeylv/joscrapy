import os
import re
import sqlite3
import traceback
import urllib

import html2text as ht
import requests
from bs4 import BeautifulSoup


class coverMd(object):
    def __init__(self):
        self.con = sqlite3.connect('../topic.db')
        self.cur = self.con.cursor()

    def search(self):
        sql = "SELECT * FROM topic limit 300 offset 531"
        try:
            # 执行SQL语句
            self.cur.execute(sql)
            # 获取所有记录列表
            results = self.cur.fetchall()
            # print(len(results))
            for row in results:
                fname = row[0]
                url = row[1]
                title = row[2]
                body = row[3]
                image = row[4]
                # print(row)
                print(fname)
                # print(url)
                # print(title)
                # print(fname)
                # print(body)
                # str(url).rindex(img, '/') + 1:

                # an = url.replace('https://www.cnblogs.com/', '')
                # us = an[:str.index(an, '/')]
                us = 'cmsblogs'
                # print(us)
                # 下载图片
                for img in image.split(','):
                    # default_headers['referer'] = img
                    if img.__contains__('http'):

                        # print(img[str.rindex(img, '/') + 1:])
                        try:
                            html = requests.get(img)
                            if html.status_code == 200:
                                # print("image_url::::::::::::::" + img)
                                if img[str.rindex(img, '/') + 1:].__contains__('.') is False:
                                    n = img[str.rindex(img, '/') + 1:str.rindex(img, '?')]
                                    params = urllib.parse.parse_qs(img)
                                    img_path = '../md/img/{}/{}'.format(us, n + '.' + params['f'][0])
                                else:
                                    img_path = '../md/img/{}/{}'.format(us, img[str.rindex(img, '/') + 1:])
                                # print(img_path[:str.rindex(img_path, '/')])
                                if os.path.exists(img_path[:str.rindex(img_path, '/')]) is False:
                                    os.mkdir(img_path[:str.rindex(img_path, '/')])

                                if img_path.__contains__('ContractedBlock') is False or img_path.__contains__(
                                        'ExpandedBlockStart') is False:
                                    body = body.replace(img, '> ![Alt text](' + img_path + ')<')
                                    if os.path.exists(img_path) is False:
                                        print('存图片' + img_path)
                                        file = open(img_path, 'wb')
                                        file.write(html.content)
                                        file.close()
                        except Exception:
                            body = body.replace(img, '> ![Alt text](' + img + ')<')
                            print("Error: {}".format(traceback.print_exc()))
                            continue

                # w = re.findall(, str(title))
                # print(w)
                md_path = '../md/' + re.sub(r'[\\\\/:*?\"<>|]', '', str(title).replace(' ', '')) + '.md'
                # print(body.find(img))
                if os.path.exists(md_path) is False:
                    with open(md_path, 'w', encoding='utf8') as f:
                        # with open(fname + '.md', 'wa') as f:
                        f.write('##' + title)
                        body = body.replace('<p>', '####').replace('<h2>', '##')
                        # dr = re.compile(r'</?\w+[^>]*>', re.S)
                        dr = re.compile(r'<[^>]+>', re.S)
                        dd = dr.sub('', body.replace('<pre>', "\t").replace('}', "\t}")).replace('\n', '')
                        strip = re.compile(r'\xa0', re.S)
                        # print(strip)
                        f.write(
                            strip.sub('', dd.replace('###', '\n###').replace('##', '\n##').replace('&lt;', '<').replace(
                                '&gt;', '>').replace('\n#', '#')))
                        f.flush()
                        f.close()
                        # 打印结果
                        # print(' title {}'.format(title))
                        # with

        except Exception:
            print("Error: {}".format(traceback.print_exc()))


if __name__ == '__main__':
    # coverMd().search()
    req = requests.get('https://blog.csdn.net/u010697681/article/details/79414112')
    if req.status_code == 200:
        # print(req.text)
        soup = BeautifulSoup(req.text, "lxml")
        # print(soup)
        itemBlog = soup.find_all('div', class_='blog-content-box')
        body = itemBlog[0]
        with open('Java-Interview.md', 'w', encoding='utf8') as f:
            text_maker = ht.HTML2Text()
            # text_maker.ignore_links = False
            text_maker.bypass_tables = True
            text_maker.default_image_alt = 'Image_Here'
            text = text_maker.handle(str(body).replace('script', ''))
            # print(text)
            # md = text.split('#')  # split post content
            # print(md)
            # open("java-list-link.md", "w", encoding='utf8').write(text)
            f.write(text)
        # print(itemBlog)
