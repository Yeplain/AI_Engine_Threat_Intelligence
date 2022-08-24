# coding: UTF-8
import random
import numpy as np
import torch
from utils_fasttext import build_dataset, build_iterator_1, build_data_data
from importlib import import_module
import threading
import requests
from bs4 import BeautifulSoup
import logging
import pandas as pd

# file paths
source_urls_file = './data/urls/urls.csv'  # 原始urls

features_file = './data/features/original.csv'  # 爬虫后的原始特征数据
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
    将分类结果写入result_file中：
    -3: 爬取内容为空  -2: 数据待处理  -1：访问出错  0：白名单  1：灰黑名单  2：诈骗网站  3：域名失效
    """
    result = {'url': [url], 'label': flag}
    df = pd.DataFrame(result)
    df.to_csv(result_file, mode='a', index=False, header=False, encoding='utf_8', sep='￥')


def craw_url(url):
    """
    Craw title and hyperlink strings from the url, write to features_file
    爬取该url中标题和超链接的string信息，作为原始特征写入features_file
    """
    # url预处理
    urll = str(url).replace("https://", "")
    urll = str(urll).replace("http://", "")

    # 使用http代理
    proxies = {
        'https': 'https://127.0.0.1:7890',
        'http': 'http://127.0.0.1:7890'
    }
    title_str = ''

    # noinspection PyBroadException
    try:
        resp = s.get('https://'+urll, verify=False, proxies=proxies, timeout=10)
    except Exception:
        # noinspection PyBroadException
        try:
            resp = s.get('http://' + urll, verify=False, proxies=proxies, timeout=10)
        except Exception:
            # noinspection PyBroadException
            try:
                resp = s.get('http://' + urll + '/index.php', verify=False, proxies=proxies, timeout=10)
            except Exception:
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
        a = {'url': [url], 'title': [title_str], 'feature_ori': [str(link_info)]}
        df = pd.DataFrame(a)
        df.to_csv(features_file, mode='a', index=False, header=False, encoding='utf_8', sep='|')
        return 1
    else:
        write_result(url, -3)
        return -1


def data_mining(original_urls):
    """
    Multi-threading mining data from source_urls as original features
    从source_urls中多线程爬取所有数据，作为原始特征
    """
    # anti-anti-spider 反反爬虫
    headers = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)z Chrome/103.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36',
        'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14',
        'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)',
        'Mozilla/5.0 (Windows; U; Windows NT 5.1; it; rv:1.8.1.11) Gecko/20071127 Firefox/2.0.0.11',
        'Opera/9.25 (Windows NT 5.1; U; en)',
        'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)',
        'Mozilla/5.0 (compatible; Konqueror/3.5; Linux) KHTML/3.5.5 (like Gecko) (Kubuntu)',
        'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.0.12) Gecko/20070731 Ubuntu/dapper-security Firefox/1.5.0.12',
        'Lynx/2.8.5rel.1 libwww-FM/2.14 SSL-MM/1.4.1 GNUTLS/1.2.9',
        'Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.04 Chromium/16.0.912.77 Chrome/16.0.912.77 Safari/535.7',
        'Mozilla/5.0 (X11; Ubuntu; Linux i686; rv:10.0) Gecko/20100101 Firefox/10.0 ']
    head = random.choice(headers)
    hh = {'User-Agent': head,
          'Cookie': '__SESSION_NAME_ipm5=f1f06c8f8adc9f15a0bf4669126f2683; iqqtv_net_ipm5=f1f06c8f8adc9f15a0bf4669126f2683; iqqtv_net_referer=%2F; '
                    'iqqtv_net=b644ea9b281750052754b580b83005f5; iqqtv_net_is_online=yUOFEtwQNVc3qMBs_%2Bix61AnRp3%2FEndKCniP%3Dqc%2FNVcJqUBqb%2FLn%'
                    '2FcoD%2BRXMD7nwBFYlftK%2F%3DVS6qDBKsv_oq1GmOYiZ6'}
    s.headers = hh
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
            tt = str(original_features['title'][index]).replace('�', "")
            ff = str(original_features['features_ori'][index])
            if is_chinese(tt) is False or len(tt + ff) <= 15:
                print('delete %s content' % original_features['title'][index])
                write_result(str(original_features['url'][index]), -2)
                del_list.append(index)
                continue
        if str(original_features['title'][index]).find('江苏反诈公益宣传') != -1 or \
                    str(original_features['features_ori'][index]).find('江苏反诈公益宣传') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), 2)
            continue
        if str(original_features['title'][index]).find('赌博') != -1 or \
                    str(original_features['features_ori'][index]).find('赌博') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), 2)
            continue
        if str(original_features['title'][index]).find('澳门') != -1 and \
                    str(original_features['title'][index]).find('彩') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), 2)
            continue
        if str(original_features['features_ori'][index]).find('澳门') != -1 and \
                    str(original_features['features_ori'][index]).find('彩') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), 2)
            continue
        if str(original_features['title'][index]).find('没有找到站点') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), 3)
            continue
        if str(original_features['title'][index]).find('站点创建成功') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), 3)
            continue
        if str(original_features['title'][index]).find('404 Not Found') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), 3)
            continue
        if str(original_features['title'][index]).find('抱歉，站点已暂停') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), 3)
            continue
        if str(original_features['title'][index]).find('404页面') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), 3)
            continue
        if str(original_features['title'][index]).find('无法访问此网站') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), 3)
            continue
        if str(original_features['title'][index]).find('Welcome to nginx') != -1:
            del_list.append(index)
            write_result(str(original_features['url'][index]), 3)
            continue
    data_new = original_features.drop(del_list, axis=0)
    data_new.to_csv(features_file_1, index=False, header=False, encoding='utf_8', sep='|')
    write_raw_index(features_file_1)


def data_cleaning_2():
    """
    Clean the dirty characters
    清洗掉一些脏符号
    """
    dirty_char = ['\t', '\n', '\r', '�', '[]']
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
                   'gangbang', 'bdsm', '18+', 'pussy', '3p']
    for index in features.index:
        flag = 0
        for word in dirty_words:
            if (str(features['title'][index]).lower()).find(word) != -1 or \
                    str(features['features_ori'][index]).find(word) != -1:
                flag = 1
                break
        write_result(str(features['url'][index]), flag)


def pre_analysis_ch(features):
    """
    Chinese websites pre-analysis
    对中文网站进行预先分析，若有一些脏词汇，则直接分类
    """
    del_list = []
    dirty_words = ['色情', '强奸', '人妻', '乱伦', '里番', '高潮', '成人', '男同', '女优', '痴汉', '毛片', '牲交',
                   '啪啪', '欧美', '同性', '少妇', '无码', '自慰', '爆乳', '喷潮', '变态', '18禁', '群交', '射精',
                   '色欲', '有码', '日韩', '国产', '性交', '毛片', '约炮', '性爱', '屁股', 'porn', '黄色', '做爱',
                   'fuck', 'sex', 'gay', 'uncensored', 'threesome', 'tits', 'anal', 'gangbang', 'bdsm', '18+',
                   'av', 'AV', '3P', 'SM', 'sm']
    for index in features.index:
        for word in dirty_words:
            if str(features['title'][index]).find(word) != -1 or \
                    str(features['features_ori'][index]).find(word) != -1:
                write_result(str(features['url'][index]), 1)
                del_list.append(index)
                break
    data_new = features.drop(del_list, axis=0)
    data_new.to_csv(model_analysis_file, index=False, header=False, encoding='utf_8', sep='|')
    write_raw_index(model_analysis_file)


def pre_process2final_file():
    """
    Generate the final file which needs to be analysed by AI engine
    生成最终送入模型的文件
    """
    data = pd.read_csv(model_analysis_file, delimiter='|', encoding='utf_8_sig', error_bad_lines=False)
    for index in data.index:
        mm = str(data['title'][index])
        mm2 = str(data['features_ori'][index])
        mm = mm + mm2
        a = {'content': [mm]}
        df = pd.DataFrame(a)
        df.to_csv(model_final_file, mode='a', index=False, header=False, encoding='utf_8')


def model_analysis():
    """
    Classify the cleaned data through our trained AI engine and write the result to result_file
    使用训练好的AI引擎对数据清洗后的原始特征进行分类，并将结果写入result_file
    """
    url_data = pd.read_csv(model_analysis_file, delimiter='|', encoding='utf_8_sig', error_bad_lines=False)
    dataset = 'QABXDatasets'  # 数据集
    embedding = 'random'
    model_name = 'FastText'

    x = import_module('models.' + model_name)
    config = x.Config(dataset, embedding)
    vocab, _, _, _ = build_dataset(config, False)
    data_data = build_data_data(config, model_final_file)
    config.n_vocab = len(vocab)
    config.batch_size = 1
    data_iter = build_iterator_1(data_data, config)

    model = x.Model(config).to(config.device)
    model.load_state_dict(torch.load(config.save_path))
    model.eval()
    predict_all = []
    with torch.no_grad():
        for texts in data_iter:
            outputs = model(texts)
            predict = torch.max(outputs.data, 1)[1].cpu().numpy()
            predict_all = np.append(predict_all, predict)
    for index in url_data.index:
        write_result(str(url_data['url'][index]), int(predict_all[index]))


if __name__ == '__main__':
    # Spider mining stage 数据挖掘阶段
    requests.adapters.DEFAULT_RETRIES = 5
    s = requests.session()
    s.keep_alive = False
    urls_ori = pd.read_csv(source_urls_file, encoding='utf_8', error_bad_lines=False)
    data_mining(urls_ori)
    print("+++++++++++++++Original Features Mining Finished+++++++++++++++")

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
    features_final_ch = pd.read_csv(features_ch_file, delimiter='|', encoding='utf_8', error_bad_lines=False)
    pre_analysis_ch(features_final_ch)
    print("+++++++++++++Chinese websites pre-analysis finished+++++++++++++")

    # AI engine analysis stage AI引擎分析阶段
    pre_process2final_file()
    print("++++++++++++++++AI engine analysis finished+++++++++++++++++")
    model_analysis()
    print("++++++++++++++++All Finished+++++++++++++++++")
