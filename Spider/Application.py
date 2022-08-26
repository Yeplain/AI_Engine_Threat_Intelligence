from importlib import import_module
import threading
import requests
from bs4 import BeautifulSoup
import logging
import pandas as pd

# file paths
source_urls_file = './data/urls/urls.csv'  # 原始urls

features_file = './data/features/black_gray_all.csv'  # 爬虫后的原始特征数据
features_file_1 = './data/features/features1.csv'  # 初步预处理后的数据
features_file_2 = './data/features/features2.csv'  # 数据清洗后的数据
features_en_file = './data/features/features_en.csv'  # 英文数据
features_ch_file = './data/features/features_ch.csv'  # 中文数据

model_analysis_file = './data/results/data_ori.csv'  # 需要使用AI模型分析的数据
model_final_file = './data/results/data_final.txt'  # 送入AI模型分析的数据
result_file = './data/results/results.txt'  # 最终分类结果


def is_chinese(string):
    """
    检查整个字符串是否包含中文
    :param string: 需要检查的字符串
    :return: bool
    """
    for ch in string:
        if u'\u4e00' <= ch <= u'\u9fff':
            return True
    return False


def write_result(url, flag):
    """
    Write label result to the result_file
    将分类结果写入result_file中：-2: 数据待处理  -1：访问出错  0：白名单  1：灰黑名单  2：诈骗网站
    """
    result = {'url': [url], 'label': flag}
    df = pd.DataFrame(result)
    df.to_csv(result_file, mode='a', index=False, header=False, encoding='utf_8', sep='￥')


def craw_url(url):
    """
    Craw title and hyperlink strings from the url, write to features_file
    爬取该url中标题和超链接的string信息，作为原始特征写入features_file
    """
    title_str = ''
    try:
        resp = s.get('https://'+url, verify=False, timeout=2)
    except:
        try:
            resp = s.get('http://' + url, verify=False, timeout=2)
        except:
            write_result(url, -1)
            return -1
    resp.encoding = "utf-8"
    if resp.status_code != 200:
        write_result(url, -1)
        return -1
    html = resp.text
    bes = BeautifulSoup(html, 'lxml')
    a_list = bes.find_all('a')  # hyperlink
    title = bes.find('title')   # title
    if title is not None:
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
        df.to_csv(features_file, mode='a', index=False, header=False, encoding='utf_8', sep='|')
        return 1
    else:
        write_result(url, -1)
        return -1


def data_mining(original_urls):
    """
    Multi-threading mining data from source_urls as original features
    从source_urls中多线程爬取所有数据，作为原始特征
    """
    # anti-anti-spider 反反爬虫
    headers = {
        'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)z \
                    Chrome/103.0.0.0 Safari/537.36",
        'Cookie': "buvid3=0C3F9901-0B4A-20F7-B743-F39956A904E533362infoc; innersign=0'"}
    s.headers = headers
    logging.captureWarnings(True)
    # Multi-threading 多线程
    max_connections = 60
    pool_sema = threading.BoundedSemaphore(max_connections)
    thread_list = []
    for index in original_urls.index:
        url = original_urls['target_key'][index]
        pool_sema.acquire()
        thread = threading.Thread(target=craw_url, args=[url])
        thread.start()
        pool_sema.release()
        thread_list.append(thread)
    for t in thread_list:
        t.join()
    write_raw_index(features_file)


def write_raw_index(path):
    """
    Insert the raw index to files
    向特征文件第一行插入索引
    """
    with open(path, 'r+', encoding='utf-8') as f:
        content = f.read()
        f.seek(0, 0)
        index_text = 'url|title|features_ori'
        f.write(index_text + '\n' + content)


def data_cleaning_1(original_features):
    """
    Clean data
    数据初步清洗，并进行前置分类
    """
    del_list = []
    for index in original_features.index:
        if str(original_features['title'][index]).find('�') != -1:
            print('delete %s content' % original_features['title'][index])
            write_result(str(original_features['url'][index]), -2)
            del_list.append(index)
            continue
        if str(original_features['title'][index]).find('江苏反诈公益宣传') != -1 or \
                    str(original_features['features_ori'][index]).find('江苏反诈公益宣传') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), 2)
            continue
        if str(original_features['title'][index]).find('没有找到站点') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), -1)
            continue
        if str(original_features['title'][index]).find('站点创建成功') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), -1)
            continue
        if str(original_features['title'][index]).find('404 Not Found') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), -1)
            continue
        if str(original_features['title'][index]).find('抱歉，站点已暂停') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), -1)
            continue
    data_new = original_features.drop(del_list, axis=0)
    data_new.to_csv(features_file_1, index=False, header=False, encoding='utf_8', sep='|')
    write_raw_index(features_file_1)


def data_cleaning_2():
    """
    Clean the dirty characters
    清洗掉一些脏符号
    """
    dirty_char = ['\t', '\n', '\r']
    features = pd.read_csv(features_file_1, delimiter='|', encoding='utf_8', error_bad_lines=False)
    for index in features.index:
        tt = str(features['title'][index])
        ff = str(features['features_ori'][index])
        for word in dirty_char:
            tt = tt.replace(word, "")
            ff = ff.replace(word, "")
        result = {'url': [features['url'][index]], 'title': [tt], 'features_ori': [ff]}
        df = pd.DataFrame(result)
        df.to_csv(features_file_2, mode='a', index=False, header=False, encoding='utf_8', sep='|')
    write_raw_index(features_file_2)


def data_cleaning_3():
    """
    English websites and Chinese websites
    将网站分为英文和中文，分别进行处理
    """
    data = pd.read_csv(features_file_2, delimiter='|', encoding='utf_8_sig', error_bad_lines=False)
    english_list = []
    chinese_list = []
    for index in data.index:
        if is_chinese(str(data['title'][index])) is False and is_chinese(str(data['features_ori'][index])) is False:
            english_list.append(index)
        else:
            chinese_list.append(index)
    data_en = data.drop(chinese_list, axis=0)
    data_ch = data.drop(english_list, axis=0)
    data_en.to_csv(features_en_file, index=False, header=False, encoding='utf_8_sig', sep='|')
    data_ch.to_csv(features_ch_file, index=False, header=False, encoding='utf_8_sig', sep='|')
    write_raw_index(features_en_file)
    write_raw_index(features_ch_file)


def pre_analysis_en(features):
    """
    English websites pre-analysis
    对英文网站进行预先分析，若有一些脏词汇，则直接分类
    """
    dirty_words = ['porn', 'fuck', 'sex', 'gay', 'uncensored', 'threesome', 'tits', 'anal',
                   'gangbang', 'bdsm', '18+', 'pussy']
    for index in features.index:
        flag = 3
        for word in dirty_words:
            if (str(features['title'][index]).lower()).find(word) != -1 or \
                    str(features['features_ori'][index]).find(word) != -1:
                flag = 1
                break
        write_result(str(features['url'][index]), flag)


def pre_process2final_file():
    """
    Generate the final file which needs to be analysed by AI engine
    生成最终送入模型的文件
    """
    data = pd.read_csv(features_ch_file, delimiter='|', encoding='utf_8_sig', error_bad_lines=False)
    for index in data.index:
        write_result(str(data['url'][index]), 1)
        mm = str(data['title'][index])
        mm2 = str(data['features_ori'][index])
        mm = mm + mm2
        a = {'content': [mm], 'label': 1}
        df = pd.DataFrame(a)
        df.to_csv(model_final_file, mode='a', index=False, header=False, encoding='utf_8', sep='￥')


if __name__ == '__main__':
    # Spider mining stage 数据挖掘阶段
    # requests.adapters.DEFAULT_RETRIES = 5
    # s = requests.session()
    # s.keep_alive = False
    # urls_ori = pd.read_csv(source_urls_file, encoding='utf_8', error_bad_lines=False)
    # data_mining(urls_ori)
    # print("+++++++++++++++Original Features Mining Finished+++++++++++++++")

    # Data cleaning stage 数据清洗阶段
    features_ori = pd.read_csv(features_file, delimiter='|', encoding='utf_8', error_bad_lines=False)
    data_cleaning_1(features_ori)
    print("++++++++++++++++++++++Delete � finished+++++++++++++++++++++++")
    data_cleaning_2()
    print("+++++++++++++++++++++Data cleaning finished++++++++++++++++++++")
    data_cleaning_3()
    print("++++++++++++English and Chinese classify finished+++++++++++++++")

    # Websites pre-analysis stage 预分析阶段
    features_final_en = pd.read_csv(features_en_file, delimiter='|', encoding='utf_8', error_bad_lines=False)
    pre_analysis_en(features_final_en)
    print("++++++++++++++English websites analysis finished++++++++++++++++")
    # features_final_ch = pd.read_csv(features_ch_file, delimiter='|', encoding='utf_8', error_bad_lines=False)
    # pre_analysis_ch(features_final_ch)
    print("+++++++++++++Chinese websites pre-analysis finished+++++++++++++")
    pre_process2final_file()