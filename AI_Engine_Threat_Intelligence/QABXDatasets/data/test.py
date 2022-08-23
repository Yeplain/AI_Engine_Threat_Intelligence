from tqdm import tqdm

with open("9dev.txt", 'r', encoding='UTF-8') as f:
    for line in tqdm(f):
        lin = line.strip()
        if not lin:
            continue
        content, label = lin.split('￥')
        print(content, label)