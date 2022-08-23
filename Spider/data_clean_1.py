import pandas as pd
import string

data = pd.read_csv('./dataset/black_gray_all.csv', delimiter='|', encoding='utf_8', error_bad_lines=False)
del_list = []
i = 0
for index in data.index:
    if str(data['title'][index]).find('\n') != -1 :
        i = i + 1
        print('delete %s content' % data['title'][index], i)
        del_list.append(index)
data_new = data.drop(del_list, axis=0)
data_new.to_csv('./dataset/bga1.csv', index=False, header=False, encoding='utf_8', sep='|')
print("++++++++++++++++++delete � finished+++++++++++++++")
