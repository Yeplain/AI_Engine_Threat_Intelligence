# 威胁情报库AI引擎使用指南

## 所需环境及软件

1. **Pycharm**：用于运行python代码 （[官网下载](https://www.jetbrains.com/pycharm/download/#section=windows)）Community版本即可

2. **Emeditor**：便于打开大的csv、txt文件 （[官网下载](https://www.emeditor.com/download/)）免费版本即可

3. **Python3.7.3** ：python初始环境  （[官网下载](https://www.python.org/downloads/release/python-373/)）对应系统版本

4. **Anaconda**: 深度学习相关库，以及环境隔离和管理  （[官网下载](https://www.anaconda.com/)）对应系统版本

5. 下载好Anaconda后，打开命令行

```shell
conda create -n QABX python=3.7.3   # 创建一个叫QABX的环境
```

6. 在命令行中：`conda activate QABX  # 启动环境`

7. 更改国内下载源：

```shell
conda config --set show_channel_urls yes

conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/msys2/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/pytorch/
conda config --show
```

8. 安装所需库和依赖：

​	所需环境见 **requirements.txt**

```shell
conda install --yes --file ../requirements.txt
```

按如上方式即可生成所有依赖。若如上方式出现错误，可采用如下方式安装依赖（**推荐**）：

```shell
conda install beautifulsoup4==4.11.1
conda install numpy==1.16.4
conda install pandas==0.24.2
conda install requests==2.22.0
conda install scikit-learn==0.21.2
conda install tensorboardX==2.5.1
conda install tqdm==4.32.1
conda install lxml
conda install pytorch torchvision torchaudio cpuonly
# (若有GPU，可以不用增添cpuonly选项；若只使用模型，cpuonly即可)
```



## 文件目录

文件主要可分为三个部分：

1. **AI_Engine_Threat_Intelligence**：**端到端的威胁情报库AI引擎**

2. **Spider**：爬取urls等域名信息的爬虫代码（使用时不需要，仅作为存档）

3. **url_list**: 两个url源文件 (使用时不需要)

​			black_gray_list.csv：从数据库中拷贝的灰黑告警域名（使用时不需要，仅用于爬取）

​			white_list.csv: 从数据库中拷贝的白告警域名（使用时不需要，仅用于爬取）



## AI引擎使用方法

实现了**端到端**的AI引擎使用，即只需输入所需的url文件，即可输出经过AI引擎分析后的结果。

1. **将需要分析的url写入urls文件夹下的urls.csv；**
2. **根据自己的代理软件修改craw_url函数下的代理端口**（若不使用代理，则将代码中该部分注释）**；**
3. **运行Application.py文件；**
4. **打开results文件夹下的 results.txt，即为最终结果；**

```python
# 使用http代理
    proxies = {
        'https': 'https://127.0.0.1:7890',  7890 ---> your port
        'http': 'http://127.0.0.1:7890'   7890 ---> your port
    }
```

数据文件见**data文件夹**下：

1. urls文件夹：将需要分析的url写入urls.csv，以换行分隔，放置该目录下；
2. features文件夹：对urls爬虫后，每一步数据清洗、数据预处理后生成的特征文件；
3. results文件夹：results.txt 为最终分类结果，url与label以￥分隔；

具体在Application.py中可见定义：

```python
source_urls_file = './data/urls/urls.csv'  # 原始urls
features_file = './data/features/original.csv'  # 爬虫后的原始特征数据
features_file_1 = './data/features/features1.csv'  # 初步预处理后的数据
features_file_2 = './data/features/features2.csv'  # 数据清洗后的数据
features_en_file = './data/features/features_en.csv'  # 英文数据
features_ch_file = './data/features/features_ch.csv'  # 中文数据
model_analysis_file = './data/results/data_ori.csv'  # 需要使用AI模型分析的数据
model_final_file = './data/results/data_final.txt'  # 送入AI模型分析的数据
result_file = './data/results/results.txt'  # 最终分类结果
```

标签及对应分类结果为：**-3**: 爬取内容为空  **-2**: 数据待处理  **-1**：访问出错 

​									       **0**：白名单  **1**：灰黑名单  **2**：诈骗网站  **3**：域名失效



## AI模型构建流程

威胁情报库AI引擎开发流程如下：

#### 1. 数据集建立

1. 从本地库获取到灰黑产告警和白告警的域名 ，即**black_gray_list.csv**和**white_list.csv**；

2. 使用全局代理多线程爬虫脚本并发爬取对应网站的标题、跳转超链接名等信息；

3. 存入csv文件中，作为情报库原始语料库；

#### 2. 数据预处理/数据清洗

1. 由于原始数据中含有大量的非法字符及无效符号等信息（有些网站title与超链接均为图片，则提取出的是乱码），如’抱歉，站点已暂停‘ ’���‘’404 Not Found‘等对其中的这些数据进行清洗；
2. 有些网站超链接中含有大量\t，\n等符号，需要进一步去除噪声；

#### 3. 分词模型分词

1. 通过pre-trained基于HanLP的中文分词模型，对原始数据集进一步分词处理；
2. 由于情报库中网站大部分为中文和英文，先筛选中文序列，使用分词模型对其进行分词处理；
3. 使用分词模型，提取其中的中文词语；进一步根据词性，去除了其中的介词、连词、助词、虚词等，避免噪声的干扰；

#### 4. 数据集划分和标签化

1. 对灰黑域名的内容打标签1，白域名打标签0，数据与标签用￥分隔；
2. 进一步，以98:1:1划分训练集、测试集和验证集，以词向量的形式作为原始的输入（后改为字向量）；

#### 5. 搭建深度神经网络模型

1. 基于成熟的NLP模型框架，针对我们的任务，搭建了基于**FastText、DPCNN、TextRNN、TextCNN、TextRCNN、TextRNN_Att、Transformer**的七种模型结构，并对其中的一些超参数进行了初始化；

2. 具体模型结构见 **AI_Engine_Threat_Intelligence** 中的 **models**:

<img src=".\models.png" alt="image-20220823181522187"  />

#### 6. 训练并优化模型参数

经过比较，选取了效果最好的**FastText**模型，通过处理好的数据集对其进行训练，对训练好的参数进行保存，用于后续使用。



## AI引擎解析流程

各个函数的作用均在Application.py的注释中予以详细解释说明。

#### 1. 数据挖掘阶段

​	**data_mining(urls_ori)**：

​	在全局代理模式下，使用多线程爬虫并发爬取url中所有需要的信息，对于无法访问的网站，分类为-1

#### 2. 数据清洗阶段

​	**data_cleaning_1(features_ori)：**

​	数据初步清洗，并进行前置分类

​	**data_cleaning_2()：**

​	清洗掉一些脏符号

​	**data_cleaning_3():**

​	将网站分为英文和中文，分别进行处理

#### 3. 预分析阶段

​	**pre_analysis_en(features)：**

​	对英文网站进行预先分析，若有一些脏词汇，则直接分类

​	**pre_analysis_ch(features):**

​	对中文网站进行预先分析，若有一些脏词汇，则直接分类

​	**pre_process2final_file():**

​	生成最终送入模型的文件

#### 4. AI模型分析阶段

​	**model_analysis()：**

​	使用训练好的AI引擎对数据清洗后的原始特征进行分类，并将结果写入result_file