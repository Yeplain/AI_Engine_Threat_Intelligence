import pandas as pd
import string

data = pd.read_csv('./dataset/bga2.csv', delimiter='|', encoding='utf_8_sig', error_bad_lines=False)
del_list = []
for index in data.index:
    if str(data['title'][index]).find('�') != -1 or str(data['features_ori'][index]).find('�') != -1:
        print('delete %s content' % data['url'][index])
        del_list.append(index)
data_new = data.drop(del_list, axis=0)
data_new.to_csv('./dataset/bga3.csv', index=False, header=False, encoding='utf_8_sig', sep='|')
print("++++++++++++++++++delete � finished+++++++++++++++")
