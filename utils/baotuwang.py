# -*- coding: utf-8 -*-
import lxml.html
import requests

etree = lxml.html.etree
# 1. 请求包图网拿到整体数据
response = requests.get("https://ibaotu.com/shipin/")

# 2. 抽取 视频标题、视频链接
html = etree.HTML(response.text)
tit_list = html.xpath('//span[@class="video-title"]/text()')
src_list = html.xpath('//div[@class="video-play"]/video/@src')
for tit, src in zip(tit_list, src_list):  # 数据一一对应
    # 3. 下载视频
    response = requests.get("http:" + src)

    # 4. 保存视频
    fileName = "E:/photo/" + tit + ".mp4"
    print("正在保存视频文件：" + fileName)
    with open(fileName, "wb") as f:
        f.write(response.content)
