import html2text as ht
import os
import re
import requests
import sqlite3
import traceback
import urllib


class coverMd(object):
    def __init__(self):
        self.con = sqlite3.connect('../topic.db')
        self.cur = self.con.cursor()

    def search(self):
        sql = "SELECT * FROM topic "
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
                # print(md.markdown(body))
                an = url.replace('https://www.cnblogs.com/', '')
                us = an[:str.index(an, '/')] if url.replace('https://www.cnblogs.com/', '') else 'cmsblogs'
                print(us)

                for img in image.split(','):
                    # default_headers['referer'] = img
                    if img.__contains__('http'):
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

                                if img_path.__contains__('ContractedBlock') or img_path.__contains__(
                                        'ExpandedBlockStart'):
                                    body = body.replace(img, '')
                                else:
                                    body = body.replace(img, img_path)
                                    if os.path.exists(img_path) is False:
                                        print('存图片' + img_path)
                                        file = open(img_path, 'wb')
                                        file.write(html.content)
                                        file.close()
                        except Exception:
                            print("Error: {}".format(traceback.print_exc()))
                            continue

                md_path = '../md/' + re.sub(r'[\\\\/:*?\"<>|]', '', str(title).replace(' ', '')) + '.md'
                # print(body.find(img))
                if os.path.exists(md_path) is False:
                    with open(md_path, 'w', encoding='utf8') as f:
                        text_maker = ht.HTML2Text()
                        text_maker.ignore_links = False
                        text_maker.bypass_tables = True
                        text_maker.default_image_alt = 'Image_Here'
                        text = text_maker.handle(body)
                        # print(text)
                        # md = text.split('#')  # split post content
                        # print(md)
                        # open("1.md", "w", encoding='utf8').write(text)
                        f.write(text)

        except Exception:
            print("Error: {}".format(traceback.print_exc()))


if __name__ == '__main__':
    coverMd().search()

    # for root, dirs, files in os.walk("../md", topdown=False):
    #     for name in files:
    #         if root.__contains__('img') is False:
    # print(os.path.join(root, name))
    # print(name)
    # md = open('../README.md', 'a', encoding='utf8')
    # md.writelines('[' + name + '](' + os.path.join('https://github.com/joeylv/joscrapy/blob/master/md/', name) + ') \r\n')

    # line = line.rstrip()
    # if m.readline()
    # url = 'https://user-gold-cdn.xitu.io/2018/2/2/16153f4f595b39f2?w=474&h=451&f=png&s=73536'
    # n = url[str.rindex(url, '/') + 1:str.rindex(url, '?')]
    # params = urllib.parse.parse_qs(url)
    # print(n + '.' + params['f'][0])
    #
    # print(params)
    # print()
    # html = requests.get('https://gitee.com/chenssy/blog-home/raw/master/image/201811/201811271001.png')
    # # html = requests.get('https://images0.cnblogs.com/blog/381060/201308/25000933-8fbd7ad38250442294ef87d433ab49b0.jpg')
    # if html.status_code == 200:
    #     print(html.content)
    #     file = open('test.png', 'wb')
    #     file.write(html.content)
    #     file.close()
