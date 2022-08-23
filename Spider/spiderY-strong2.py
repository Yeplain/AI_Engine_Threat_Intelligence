# coding=utf-8
import threading
import time

import requests
from bs4 import BeautifulSoup
from lxml import etree
import logging
import pandas as pd
import xlrd
import xlwt

# row = 1

def craw_url(url):
    # global row
    title_str = ''
    try:
        resp = s.get('https://'+url, verify=False, timeout=2)
    except:
        try:
            resp = s.get('http://' + url, verify=False, timeout=2)
        except:
            # print('%s url get error happened' % url)
            return -1
    resp.encoding = "utf-8"
    if resp.status_code != 200:
        # print('%s url 不可正常访问' % url)
        return -1
    html = resp.text
    bes = BeautifulSoup(html, 'lxml')
    a_list = bes.find_all('a')
    title = bes.find('title')

    if title is not None:
        if title.string == "江苏反诈公益宣传":
            return -1
        title_str = title.string
        print(title_str)

    link_info = []
    for a in a_list:
        if a.string is None:
            continue
        link_info.append(a.string)

    if (title is not None) or (len(link_info) > 0):
        print(url)
        a = {'url': [url], 'title': [title_str], 'feature_ori': [str(link_info)]}
        df = pd.DataFrame(a)
        df.to_csv('feature_ori_9.csv', mode='a', index=False, header=False, encoding='utf_8_sig', sep='|')
        # print('--------------This is significantly url--------------')
        #
        # lock.acquire()
        # row += 1
        # lock.release()
        return 1
    else:
        # print('no info in this url')
        return -1


if __name__ == '__main__':
    start = time.perf_counter()
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
    col = ('url', 'title', 'features_ori')

    # anti-anti-spider
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)z \
                Chrome/103.0.0.0 Safari/537.36",
        'Cookie': "buvid3=0C3F9901-0B4A-20F7-B743-F39956A904E533362infoc; innersign=0'"}
    s.headers = headers
    logging.captureWarnings(True)

    # 多线程
    lock = threading.Lock()
    max_connections = 60
    pool_sema = threading.BoundedSemaphore(max_connections)
    thread_list = []

    for url in urls:
        # if row >= 10000:
        #     break
        pool_sema.acquire()

        thread = threading.Thread(target=craw_url, args=[url])
        thread.start()
        pool_sema.release()
        thread_list.append(thread)

    for t in thread_list:
        t.join()

    print("+++++++++++++++Original Features Mining Finished+++++++++++++++")