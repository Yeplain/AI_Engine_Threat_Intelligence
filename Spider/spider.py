#coding=utf-8
import requests
from bs4 import BeautifulSoup
from lxml import etree
import logging
import pandas as pd
import xlrd

#data = xlrd.open_workbook('D:\\shixi\\model\\traffic_target_1-1.xlsx')
data = xlrd.open_workbook(r'D:\shixi\model\traffic_target_1-1.xlsx')
table = data.sheets()[0]
urls = table.col_values(0)
for url in urls:
    print(url)
    print('http://'+ url)
    logging.captureWarnings(True)
    resp = requests.get('http://'+ url, verify=False)
    resp.encoding = "utf-8"
    # print(resp) #打印请求结果的状态码
    # print(resp.content) #打印请求到的网页源码
    # html = etree.HTML(resp.text)
    # results = html.xpath('//ul/li[contains(@class,"left left-main")]')
    html = resp.text
    # print(html)
    bes = BeautifulSoup(html,'lxml') #将网页源码构造成BeautifulSoup对象，方便操作
    #texts = bes.find("div", id = "content")
    a_list = bes.find_all('a') #获取网页中的所有a标签对象
    for a in a_list:
        if a.string is None:
            continue
        print(a.string)