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
        title_str = title.string
        # if str(title_str).find('�') or str(title_str).find('404 Not Found') or str(title_str).find('无法找到该页'):
        #     return -1
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
        df.to_csv('white_features_ori.csv', mode='a', index=False, header=False, encoding='utf_8', sep='|')
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
    # start = time.perf_counter()
    requests.adapters.DEFAULT_RETRIES = 5
    s = requests.session()
    s.keep_alive = False

    # read urls from the csv file
    data = pd.read_csv('../white_list.csv', encoding='utf_8', error_bad_lines=False)

    # write title to the csv file
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

    for index in data.index:
        # if row >= 10000:
        #     break
        url = data['target_key'][index]
        pool_sema.acquire()

        thread = threading.Thread(target=craw_url, args=[url])
        thread.start()
        pool_sema.release()
        thread_list.append(thread)

    for t in thread_list:
        t.join()

    print("+++++++++++++++Original Features Mining Finished+++++++++++++++")