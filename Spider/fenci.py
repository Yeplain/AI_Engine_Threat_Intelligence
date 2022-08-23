import jieba
import pandas as pd
import jieba.posseg as pseg
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

data = pd.read_csv('feature_ori_9_5.csv', delimiter='|', encoding='utf_8_sig', error_bad_lines=False)
for index in data.index:
    seg_list = pseg.cut(str(data['features_ori'][index]))
    # print(",".join(seg_list))
    add_list = []
    for m, flag in seg_list:
        if not is_chinese(m):
            continue
        elif flag == 'r' or flag == 'p' or flag == 'c' or flag == 'u' or flag == 'xc':
            continue
        else:
            add_list.append(m)
    if len(add_list) > 0:
        print(add_list)
        a = {'word': [str(add_list)]}
        df = pd.DataFrame(a)
        df.to_csv('fenci_featuresori_full_mode.csv', mode='a', index=False, header=False, encoding='utf_8_sig')
print("++++++++++++++++++fenci finished+++++++++++++++")