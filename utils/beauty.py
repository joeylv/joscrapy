# -*-coding:utf-8-*-
import sqlite3
import threading
import time
from multiprocessing import Pool, cpu_count
from urllib import parse

import requests
from lxml import etree

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
    "referer": "https://www.bevol.cn/",
    # 'Content-Type': 'text/html; charset=utf-8'
}


def create_tb():
    conn = sqlite3.connect('beauty.db')
    print("Opened database successfully")
    c = conn.cursor()
    sql = "create table product (id varchar(20) primary key, title varchar(30), mid varchar(30))"
    c.execute(sql)
    c.close()
    # 提交事物
    conn.commit()
    # 关闭连接
    conn.close()


def get_urls():
    category = [6, 7, 8, 9, 10, ]  # 11, 12, 13, 15, 20, 47, 30, 38
    urls = []
    # url = 'https://api.bevol.cn/search/goods/index3?p=1&keywords=&category=8&callback=jQuery191034222494301842543_1559113449039&_=1559113449040'
    for cate in category:
        for x in range(30):
            urls.append('https://api.bevol.cn/search/goods/index3?p={}&category={}'.format(x, cate))
    return set(urls)


lock = threading.Lock()  # 全局资源锁


def get_jsons(url):
    conn = sqlite3.connect('beauty.db')
    # print("Opened database successfully")
    c = conn.cursor()
    # url = 'https://api.bevol.cn/search/goods/index3?p={}&category={}'.format(x, cate)
    # req = requests.get(url, headers=HEADERS, timeout=100, ).content
    try:
        with lock:
            time.sleep(1)
            for x in range(1, 251):
                # print(x)
                iurl = url + '&p=' + str(x)
                res = dict(parse.parse_qsl(url[str(url).index('?') + 1:]))
                # print(res)
                # print(res['category'])
                req_t = requests.get(iurl, headers=HEADERS, timeout=100, )
                # print(iurl)
                # print(req_t.status_code)
                # print(req)
                req_t = req_t.json()
                # print(req_t)
                if 'data' not in req_t:
                    # print(len(req_t['data']['items']))
                    return
                if 0 == len(req_t['data']['items']):
                    print(iurl)
                if 0 < len(req_t['data']['items']) < 20:
                    print(iurl)
                    # if len(req_t['data']) > 0:
                    #
                    #     print(len(req_t['data']))
                    #     print(req_t)
                    #     print(req_t['data'])
                # print(len(req_t['data']['items']))
                # print('=' * 100)
                # for i in json.loads(req_t[req_t.index('(') + 1:len(req_t) - 2])['data']['items']:

                for i in req_t['data']['items']:
                    # print('id::' + i['id'])
                    # print('mid::' + i['mid'])
                    # print('imageSrc::' + i['imageSrc'])
                    # print('title::' + i['title'])
                    # print('capacity::' + i['capacity'])
                    # print('alias::' + i['alias'])
                    # print('alias_2::' + i['alias_2'])
                    # print('approval::' + i['approval'])
                    # print('remark2::' + i['remark2'])
                    # print('remark3::' + i['remark3'])
                    # ,imageSrc,title,capacity,alias,alias2,,remark2,remark3,price
                    sql = "INSERT INTO beauty (pid,mid,title,imageSrc,capacity,alias,alias2,approval,remark3,price,category) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                        i['id'], i['mid'], i['title'], i['imageSrc'], i['capacity'], i['alias'], i['alias_2'],
                        i['approval'], i['remark3'], i['price'], res['category'])
                    # i['approval'], i['remark2'], i['remark3'], i['price'])

                    # print(sql)
                    try:
                        c.execute(sql)
                    except Exception as e:
                        # print(e)
                        continue
                conn.commit()
        conn.close()

    except Exception as e:
        # print(e)
        pass


def mainloop(offset):
    conn = sqlite3.connect('beauty.db')
    print("Opened database successfully")
    c = conn.cursor()
    sql = "select mid from beauty limit 20 offset {}".format(offset)
    c.execute(sql)
    # sql = "select * from login where id=?"
    # cursor.execute(sql, ("2",))
    # 获取查询结果：
    values = c.fetchall()
    # print(values)
    # 通过rowcount获得插入的行数:
    # print(c.rowcount())
    # with lock:
    mids = []
    for v in values:
        mids.append(v[0])
        # up_info(v[0])
        print(v[0])
    pool = Pool(processes=cpu_count())
    try:
        # delete_empty_dir(DIR_PATH)
        pool.map(up_info, mids)
    except Exception as e:
        # time.sleep(30)
        print(e)
    conn.close()
    mainloop(offset + 20)


def up_info(mid):
    conn = sqlite3.connect('beauty.db')
    print("Opened database successfully")
    c = conn.cursor()
    url = 'https://www.bevol.cn/product/{}.html'.format(mid)
    req_t = requests.get(url, headers=HEADERS, timeout=10, )
    html = etree.HTML(req_t.content.decode("utf-8"))
    # print(html)
    html_data = html.xpath('/html/body//div[@class="cosmetics-info-box"]//a')
    sql = "Update beauty SET essence = '{}',aseptic ='{}',risk='{}',gravida='{}',major='{}',clean='{}',cistine='{}',sls='{}'  where mid ='{}'".format(
        html_data[0].text if len(html_data) >= 1 else '', html_data[1].text if len(html_data) >= 2 else '',
        html_data[2].text if len(html_data) >= 3 else '', html_data[3].text if len(html_data) >= 4 else '',
        html_data[4].text if len(html_data) >= 5 else '',
        html_data[5].text if len(html_data) >= 6 else '', html_data[6].text if len(html_data) >= 7 else '',
        html_data[7].text if len(html_data) >= 8 else '', mid)
    # print(sql)
    try:
        c.execute(sql)
    except Exception as e:
        print(e)
    conn.commit()
    pass
    conn.close()


def midloop():
    conn = sqlite3.connect('beauty.db')
    print("Opened database successfully")
    c = conn.cursor()
    sql = "select mid from beauty"
    c.execute(sql)
    # sql = "select * from login where id=?"
    # cursor.execute(sql, ("2",))
    # 获取查询结果：
    values = c.fetchall()
    # print(values)
    # 通过rowcount获得插入的行数:
    # print(c.rowcount())
    # with lock:
    for v in values:
        # print(v[0])
        url = 'https://www.bevol.cn/product/{}.html'.format(v[0])
        req_t = requests.get(url, headers=HEADERS, timeout=10, )
        # with open("../file/" + v[0] + ".txt", "w", encoding="utf-8") as r:
        #     r.write(req_t.content.decode("utf-8"))
        # # print(req_t.content.decode('utf-8'))
        # with open("../file/ed5b9975f24100e98b1ed7760898441c.txt", "r", encoding="utf-8") as r:
        html = etree.HTML(req_t.content.decode("utf-8"))
        # print(html)
        html_data = html.xpath('/html/body//div[@class="cosmetics-info-box"]//a')
        # print(html_data)
        # for item in html_data:
        #     print(item.text)
        # print(len(html_data))
        # print(html_data[0].text)
        # print(html_data[1].text)
        # print(html_data[2].text)
        # print(html_data[3].text)
        # print(html_data[4].text)
        # print(html_data[5].text)
        # print(html_data[6].text)
        # print(html_data[7].text)
        sql = "Update beauty SET essence = '{}',aseptic ='{}',risk='{}',gravida='{}',major='{}',clean='{}',cistine='{}',sls='{}'  where mid ='{}'".format(
            html_data[0].text if len(html_data) >= 1 else '', html_data[1].text if len(html_data) >= 2 else '',
            html_data[2].text if len(html_data) >= 3 else '', html_data[3].text if len(html_data) >= 4 else '',
            html_data[4].text if len(html_data) >= 5 else '',
            html_data[5].text if len(html_data) >= 6 else '', html_data[6].text if len(html_data) >= 7 else '',
            html_data[7].text if len(html_data) >= 8 else '', v[0])
        # print(sql)
        try:
            c.execute(sql)
        except Exception as e:
            print(e)
        conn.commit()
        pass
    conn.close()


def ch_test():
    conn = sqlite3.connect('beauty.db')
    print("Opened database successfully")
    c = conn.cursor()
    sql = "select essence,aseptic,risk,gravida,major,clean,cistine,sls from beauty limit 1000 offset 2000"
    c.execute(sql)
    # sql = "select * from login where id=?"
    # cursor.execute(sql, ("2",))
    # 获取查询结果：
    values = c.fetchall()
    # print(values)
    # 通过rowcount获得插入的行数:
    # print(c.rowcount())
    # with lock:
    tit = []
    for v in values:
        es = str(v[6]).lstrip().rstrip().replace(' ', '')  # v[0] ->v[7] 不同类型成分名称

        if '（' in es and len(es) > 10:
            name = es[es.index('（') + 1:es.rindex('）')]
            t = name.lstrip().rstrip().replace('\n', '').replace('\r', '').replace('（', '(').replace('）', ')').replace(
                '.', '')
            if '、' in t:
                for i in t.split('、'):
                    if i not in tit and len(i) > 0:
                        tit.append(i)
    print(tit)
    for w in tit:
        composition(w)

    # str.index(v[0],'（',len(v[0]))
    # print(es.index('（'))
    # print(str(v[0])[str(v[0]).index('（'):str(v[0]).rindex('）')])
    # print(v[1])
    # print(v[2])
    # print(v[3])
    # print(v[4])
    # print(v[5])
    # print(v[6])
    # print(v[7])
    conn.close()


def composition(w):
    url = 'https://api.bevol.cn/search/composition/index?keywords={}'.format(w)
    req_t = requests.get(url, headers=HEADERS, timeout=10, )
    conn = sqlite3.connect('beauty.db')
    # print("Opened database successfully")
    c = conn.cursor()
    if 'data' in req_t.json():
        for item in req_t.json()['data']['items']:
            # print(item['mid'])
            # print(item['usedtitle'])
            # print(item['name'])
            # print(item['english'])
            # print(item['other_title'])
            # print(item['namejp'])
            # print(item['remark'])
            # print(item)
            sql = "INSERT INTO composition (mid,usedtitle,remark,english,namejp,name,other_title) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}' )".format(
                item['mid'], item['usedtitle'], item['remark'], item['english'], item['namejp'], item['name'],
                item['other_title'])
            # i['approval'], i['remark2'], i['remark3'], i['price'])

            # print(sql)
            try:
                c.execute(sql)
            except Exception as e:
                print(e)
                continue
        conn.commit()
    conn.close()


def url_loop():
    category = [6, 7, 8, 9, 10, 11, 12, 13, 15, 20, 47, 30, 38]
    urls = []
    # url = 'https://api.bevol.cn/search/goods/index3?p=1&keywords=&category=8&callback=jQuery191034222494301842543_1559113449039&_=1559113449040'
    for cate in category:
        urls.append('https://api.bevol.cn/search/goods/index3?category={}'.format(cate))

    # urls = get_urls()
    urls = set(urls)
    # print(urls)
    pool = Pool(processes=cpu_count())
    try:
        # delete_empty_dir(DIR_PATH)
        pool.map(get_jsons, urls)
    except Exception as e:
        # time.sleep(30)
        print(e)
        # print(sys.exc_info()[0])
        # pool.map(get_jsons, urls)


if __name__ == "__main__":
    mainloop(0)
    # for i in range(10):
    # url_loop()

    # midloop()  # 获取化妆品
    # ch_test()  # 获取成分信息
    # composition('苧烯')

    # url = 'https://api.bevol.cn/search/composition/index?keywords=苯甲酸钠'
    # req_t = requests.get(url, headers=HEADERS, timeout=10, )
    # for item in req_t.json()['data']['items']:
    #     print(item['mid'])
    #     print(item['usedtitle'])
    #     print(item['name'])
    #     print(item['english'])
    #     print(item['other_title'])
    #     print(item['namejp'])
    #     print(item['remark'])
    #     print(item)
