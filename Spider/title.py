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
    # feature_ori_9_5.csv  white3
data = pd.read_csv('./dataset/bga_no_url.csv', delimiter='|', encoding='utf_8_sig', error_bad_lines=False)
for index in data.index:
    # seg_list = pseg.cut(str(data['title'][index]))
    # print(",".join(seg_list))
    # add_list = []
    # for m, flag in seg_list:
    #     if not is_chinese(m):
    #         continue
    #     elif flag == 'r' or flag == 'p' or flag == 'c' or flag == 'u' or flag == 'xc':
    #         continue
    #     else:
    #         add_list.append(m)
    mm = str(data['title'][index])
    mm2 = str(data['features_ori'][index])
    mm = mm + mm2
    if not is_chinese(mm):
        continue
    else:
        if len(mm) > 0:
            print(mm)
            a = {'title': [mm], 'label': 1}
            df = pd.DataFrame(a)
            df.to_csv('./dataset/train_bga.txt', mode='a', index=False, header=False, encoding='utf_8', sep='￥')
print("++++++++++++++++++title extract finished+++++++++++++++")