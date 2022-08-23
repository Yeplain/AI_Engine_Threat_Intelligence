import pandas as pd


# read urls from the csv file
data = pd.read_csv('../white_list.csv', encoding='utf_8', error_bad_lines=False)
for index in data.index:
	print(data['target_key'][index])