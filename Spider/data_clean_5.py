import pandas as pd
import string
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

data = pd.read_csv('feature_ori_9_4.csv', delimiter='|', encoding='utf_8_sig', error_bad_lines=False)
del_list = []
for index in data.index:
    if is_chinese(str(data['title'][index])) == False and is_chinese(str(data['features_ori'][index])) == False:
        print('delete %s content' % data['url'][index])
        del_list.append(index)
data_new = data.drop(del_list, axis=0)
data_new.to_csv('./feature_ori_9_4.csv', index=False, header=False, encoding='utf_8_sig', sep='|')
print("++++++++++++++++++delete � finished+++++++++++++++")
