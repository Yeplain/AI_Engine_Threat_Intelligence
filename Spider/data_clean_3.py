import pandas as pd
import string

data = pd.read_csv('./dataset/bga_ch.csv', delimiter='|', encoding='utf_8_sig', error_bad_lines=False)
data_new = data.drop(['url'], axis=1)
data_new.to_csv('./dataset/bga_ch_final.csv', index=False, header=False, encoding='utf_8_sig', sep='|')
print("++++++++++++++++++delete � finished+++++++++++++++")
