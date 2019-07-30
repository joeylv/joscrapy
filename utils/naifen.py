# -*-coding:utf-8-*-
import sqlite3

import requests
from bs4 import BeautifulSoup
from lxml import etree

HEADERS = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.110 Safari/537.36",
    "referer": "https://www.bevol.cn/",
    # 'Content-Type': 'text/html; charset=utf-8'
}


def get_type():
    'https://www.naifenzhiku.com/powder?sort_id=294&chan=8&page=2'
    url = 'https://www.naifenzhiku.com/powder?sort_id=294'
    req = requests.get(url, headers=HEADERS, timeout=10, )
    bs = BeautifulSoup(
        req.text,
        'lxml').find('div', id="pinpai")
    print(len(bs.find_all('a')))
    for x in bs.find_all('a'):
        if int(x['data-type']) > 0:
            # print(x.get_text())
            # midloop(x['data-type'])
            composition(x['data-type'])
            # print(x['data-type'])


def midloop(type):
    conn = sqlite3.connect('beauty.db')
    print("Opened database successfully")
    c = conn.cursor()
    url = 'https://www.naifenzhiku.com/powder?sort_id=294&pin={}&chan=0&lei=0&duan=0&shi=0'.format(type)
    req = requests.get(url, headers=HEADERS, timeout=10, )
    html = etree.HTML(req.content.decode("utf-8"))
    list = []
    html_data = html.xpath('/html/body//div[@class="cp_item"]//a/@href')
    for d in html_data:
        try:
            if d not in list:
                list.append(d)
        except:
            pass

    for l in list:
        req = requests.get('https://www.naifenzhiku.com' + l, headers=HEADERS, timeout=10, )
        # html = etree.HTML(req.content.decode("utf-8"))
        # html_data = html.xpath('/html/body//div[@class="all_guige"]//p/span/node()')
        # html_data = html.xpath('/html/body//div[@class="pp_yycf"]')

        bs = BeautifulSoup(req.text, 'lxml').find('div', id="cpgk")
        i = bs.find('img')
        # print(i['src'])
        t = bs.find_all('p')
        # print(len(t))
        # for b in bs.find_all('p'):
        #     txt = str(b.get_text())
        #     if '：' in txt:
        #         print(txt[txt.index('：') + 1:])
        #     else:
        #         print(txt)
        sql = "INSERT INTO naifen VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
            t[0].get_text("|"), t[1].span.get_text(), t[3].span.get_text(), t[4].span.get_text(),
            t[5].span.get_text(), t[6].span.get_text(), t[7].span.get_text(), t[8].span.get_text(),
            t[9].span.get_text(), t[10].span.get_text(), t[11].span.get_text(), t[12].span.get_text(),
            t[13].span.get_text(), t[2].span.get_text(), i['src'])
        # print(sql)

        # cf = BeautifulSoup(req.text, 'lxml').find('div', class_="pp_yycf").find_all('div', class_="cf_tbody")
        # for c in cf:
        #     print(str(c.get_text()).lstrip().rstrip())
        #     for p in c.find_all('p'):
        #         print(p.get_text())

        # if b:
        #     print(b)
        #     for link in b.find_all('span'):
        #         print(link.get_text())
        # bs = BeautifulSoup(req.text, 'lxml').find('div', class_="pp_yycf")
        # print(bs)
        # for da in html_data:
        #     print(da)
        try:
            c.execute(sql)
        except Exception as e:
            print(e)
            continue
    conn.commit()
    conn.close()


def ch_test():
    conn = sqlite3.connect('beauty.db')
    print("Opened database successfully")
    c = conn.cursor()
    for i in range(1, 58):
        url = 'https://www.naifenzhiku.com/powder?sort_id=294&page={}'.format(i)
        print(i)
        print(url)
        req = requests.get(url, headers=HEADERS, timeout=10, )
        html = etree.HTML(req.content.decode("utf-8"))
        list = []
        print(len(html.xpath('/html/body//div[@class="cp_item"]//a')))
        html_data = html.xpath('/html/body//div[@class="cp_item"]//a/@href')
        for d in html_data:
            try:
                if d not in list:
                    list.append(d)
            except:
                pass
        for l in list:
            req = requests.get('https://www.naifenzhiku.com' + l, headers=HEADERS, timeout=10, )
            # html = etree.HTML(req.content.decode("utf-8"))
            # html_data = html.xpath('/html/body//div[@class="all_guige"]//p/span/node()')
            # html_data = html.xpath('/html/body//div[@class="pp_yycf"]')

            bs = BeautifulSoup(req.text, 'lxml').find('div', id="cpgk")
            i = bs.find('img')
            # print(i['src'])
            t = bs.find_all('p')
            # print(len(t))
            # for b in bs.find_all('p'):
            #     txt = str(b.get_text())
            #     if '：' in txt:
            #         print(txt[txt.index('：') + 1:])
            #     else:
            #         print(txt)
            sql = "INSERT INTO naifen VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(
                t[0].get_text("|"), t[1].span.get_text(), t[3].span.get_text(), t[4].span.get_text(),
                t[5].span.get_text(), t[6].span.get_text(), t[7].span.get_text(), t[8].span.get_text(),
                t[9].span.get_text(), t[10].span.get_text(), t[11].span.get_text(), t[12].span.get_text(),
                t[13].span.get_text(), t[2].span.get_text(), i['src'])
            # print(sql)

            # cf = BeautifulSoup(req.text, 'lxml').find('div', class_="pp_yycf").find_all('div', class_="cf_tbody")
            # for c in cf:
            #     print(str(c.get_text()).lstrip().rstrip())
            #     for p in c.find_all('p'):
            #         print(p.get_text())

            # if b:
            #     print(b)
            #     for link in b.find_all('span'):
            #         print(link.get_text())
            # bs = BeautifulSoup(req.text, 'lxml').find('div', class_="pp_yycf")
            # print(bs)
            # for da in html_data:
            #     print(da)
            try:
                c.execute(sql)
            except Exception as e:
                print(e)
                continue
            conn.commit()
    conn.close()


def composition(type):
    conn = sqlite3.connect('beauty.db')
    print("Opened database successfully")
    c = conn.cursor()
    url = 'https://www.naifenzhiku.com/powder?sort_id=294&pin={}&chan=0&lei=0&duan=0&shi=0'.format(type)
    req = requests.get(url, headers=HEADERS, timeout=10, )
    html = etree.HTML(req.content.decode("utf-8"))
    list = []
    print(len(html.xpath('/html/body//div[@class="cp_item"]//a')))
    html_data = html.xpath('/html/body//div[@class="cp_item"]//a/@href')
    for d in html_data:
        try:
            if d not in list:
                list.append(d)
        except:
            pass
    has = []
    for l in list:
        req = requests.get('https://www.naifenzhiku.com' + l, headers=HEADERS, timeout=10, )
        # html = etree.HTML(req.content.decode("utf-8"))
        # html_data = html.xpath('/html/body//div[@class="all_guige"]//p/span/node()')
        # html_data = html.xpath('/html/body//div[@class="pp_yycf"]')

        bs = BeautifulSoup(req.text, 'lxml').find('div', class_="pp_yycf").find_all('div', class_="cf_tbody")
        # print(cf[3].get_text())
        for b in bs:
            # print(len(c))
            # print(c.get_text())
            # print('*' * 100)
            t = str(b.get_text("|")).replace('\n', '')
            cf = []

            for s in t.split('|'):
                if len(s) > 0:
                    cf.append(s.lstrip().rstrip())
            print(has)
            if cf[0] not in has:
                print(cf)
                sql = "INSERT INTO chengfen VALUES ('{}', '{}', '{}', '{}', '{}')".format(
                    cf[0], cf[2], cf[3], cf[4], cf[5])
                print(sql)
                has.append(cf[0])
                try:
                    c.execute(sql)
                except Exception as e:
                    print(e)
                    continue
                conn.commit()

    conn.close()


if __name__ == "__main__":
    # get_type()
    # midloop()  # 获取奶粉
    ch_test()  # 获取成分信息
    # composition('苧烯')
