import os
import re
import sqlite3

import requests


class coverMd(object):
    def __init__(self):
        self.con = sqlite3.connect('../topic.db')
        self.cur = self.con.cursor()

    def search(self):
        sql = "SELECT * FROM topic"
        try:
            # 执行SQL语句
            self.cur.execute(sql)
            # 获取所有记录列表
            results = self.cur.fetchall()
            for row in results:
                fname = row[0]
                title = row[2]
                body = row[3]
                image = row[4]
                # print(row)
                # print(fname)
                # print(title)
                # print(fname)
                # print(body)

                # 下载图片
                for img in image.split(','):
                    # default_headers['referer'] = img
                    if img:
                        # print("image_url::::::::::::::" + img)
                        # print(img[str.rindex(img, '/') + 1:])
                        html = requests.get(img)
                        if html.status_code == 200:
                            img_path = '../md/img/' + img[str.rindex(img, '/') + 1:]
                            if img_path.__contains__('ContractedBlock') is False or img_path.__contains__(
                                    'ExpandedBlockStart') is False:
                                body = body.replace(img, '> ![Alt text](' + img_path + ')<')
                                if os.path.exists(img_path) is False:
                                    # print('存图片')
                                    file = open(img_path, 'wb')
                                    file.write(html.content)
                                    file.close()

                # w = re.findall(, str(title))
                # print(w)
                md_path = '../md/' + re.sub(r'[\\\\/:*?\"<>|]', '', str(title)) + '.md'
                # print(body.find(img))
                with open(md_path, 'a', encoding='utf8') as f:
                    # with open(fname + '.md', 'wa') as f:
                    f.write('##' + title)
                    body = body.replace('<p>', '####').replace('<h2>', '##')
                    # dr = re.compile(r'</?\w+[^>]*>', re.S)
                    dr = re.compile(r'<[^>]+>', re.S)
                    dd = dr.sub('', body.replace('<pre>', "\t").replace('}', "\t}")).replace('\n', '')
                    strip = re.compile(r'\xa0', re.S)
                    # print(strip)
                    f.write(strip.sub('', dd.replace('###', '\n###').replace('##', '\n##').replace('&lt;', '<').replace(
                        '&gt;', '>')))
                    f.flush()

                    f.close()
                    # 打印结果
                    # print(' title {}'.format(title))
                    # with

        except Exception as e:
            print("Error: {}".format(e))


if __name__ == '__main__':
    coverMd().search()
