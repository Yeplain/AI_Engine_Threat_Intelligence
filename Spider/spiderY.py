# coding=utf-8
import requests
from bs4 import BeautifulSoup
from lxml import etree
import logging
import pandas as pd
import xlrd
import xlwt

requests.adapters.DEFAULT_RETRIES = 5
s = requests.session()
s.keep_alive = False

# read urls from the xlsx file
data = xlrd.open_workbook(r'D:\shixi\model\traffic_target_1-1.xlsx')
table = data.sheets()[0]
urls = table.col_values(0)

# write features_original to the xlsx file
book = xlwt.Workbook(encoding='utf-8', style_compression=0)
sheet = book.add_sheet('features_ori', cell_overwrite_ok=True)
col = ('url', 'title', 'features_ori', 'features_more')

# anti-anti-spider
headers = {
            'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)z \
            Chrome/103.0.0.0 Safari/537.36",
            'Cookie': "buvid3=0C3F9901-0B4A-20F7-B743-F39956A904E533362infoc; innersign=0'"}
s.headers = headers
logging.captureWarnings(True)

i = 1  # 行号
for url in urls:
    try:
        resp = s.get('https://'+url, verify=False, timeout=2)
    except:
        try:
            resp = s.get('http://' + url, verify=False, timeout=2)
        except:
            # print('%s url get error happened' % url)
            continue
    resp.encoding = "utf-8"
    if resp.status_code != 200:
        # print('%s url 不可正常访问' % url)
        continue
    html = resp.text
    bes = BeautifulSoup(html, 'lxml')
    a_list = bes.find_all('a')
    title = bes.find('title')
    # print(url)
    if title is not None:
        if title.string == "江苏反诈公益宣传":
            continue
        print(title.string)
        sheet.write(i, 1, title.string)
    link_info = []
    for a in a_list:
        if a.string is None:
            continue
        link_info.append(a.string)
    if len(link_info) > 0:
        sheet.write(i, 2, str(link_info))
    if (title is not None) | (len(link_info) > 0):
        sheet.write(i, 0, url)
        print(url)
        print('--------------This is No.%d significantly url--------------' %i)
        i += 1
    if i == 20:
        break
book.save('features_ori_new.xls')