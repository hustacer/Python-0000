#-*- coding:utf-8 -*-
#获取淘宝网上前100页关于耳机的信息并将其绘制成图表
import re
import time
import requests
import pandas as pd
from retrying import retry
from concurrent.futures import ThreadPoolExecutor
 
start = time.clock()     #计时-开始
 
#plist 为1-100页的URL的编号num 
plist = []           
for i in range(1,101):   
	#淘宝的页数都是以下面这种形式来结束的，所以使用44
	#https://s.taobao.com/search?q=耳机&xxx&s=44
    #https://s.taobao.com/search?q=耳机&xxx&s=88
    j = 44*(i-1)
    plist.append(j)
 
listno = plist
datatmsp = pd.DataFrame(columns=[])
 
while True: 
   @retry(stop_max_attempt_number = 8)     #设置最大重试次数
   def network_programming(num):   
   	  #将耳机转换为汉字编码%E8%80%B3%E6%9C%BA
      url='https://s.taobao.com/search?q=%E8%80%B3%E6%9C%BA&ssid=s5-e \
      &search_type=item&sourceId=tb.index&spm=a21bo.2017.201856-taobao-item.1 \
      &ie=utf8&initiative_id=tbindexz_20170306&fs=1&filter_tianmao=tmall \
      &sort=sale-desc&filter=reserve_price%5B50%2C%5D&bcoffset=0 \
      &p4ppushleft=%2C44&s=' + str(num)  
      web = requests.get(url, headers=headers)     
      web.encoding = 'utf-8'
      return web   
 
   #多线程       
   def multithreading():     
      number = listno        #每次爬取未爬取成功的页
      event = []
    
      with ThreadPoolExecutor(max_workers=10) as executor:
         for result in executor.map(network_programming,
                                    number, chunksize=10):
             event.append(result)   
      return event
    
   #隐藏：修改headers参数
   #因为淘宝可能会出现反爬虫，所以使用cookie，构建head是很有必要的。尽量把自己伪装成一个浏览器。  
   headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) \
            AppleWebKit/537.36(KHTML, like Gecko)  \
            Chrome/55.0.2883.87 Safari/537.36'}
    
   #多线程从json获取数据
   listpg = []
   event = multithreading()
   for i in event:
      json = re.findall('"auctions":(.*?),"recommendAuctions"', i.text)
      if len(json):
         table = pd.read_json(json[0])      
         datatmsp = pd.concat([datatmsp,table],axis=0,ignore_index=True)  
          
         pg = re.findall('"pageNum":(.*?),"p4pbottom_up"',i.text)[0]
         listpg.append(pg)      #记入每一次爬取成功的页码
    
   lists = []
   for a in listpg:   
       b = 44*(int(a)-1)
       lists.append(b)     #将爬取成功的页码转为url中的num值
    
   listn = listno
 
   #每次循环将爬取失败的数组清空
   listno = []       #将本次爬取失败的页记入列表中 用于循环爬取
   for p in listn:
       if p not in lists:
           listno.append(p)
            
   if len(listno) == 0:     #当未爬取页数为0时 终止循环！
      break
       
datatmsp.to_excel('datatmsp1.xls', index=False)    #导出数据为Excel
 
end = time.clock()    #计时-结束
print ("爬取完成 用时：", end - start,'s')


'''
二、数据清洗、处理： (此步骤也可以在Excel中完成 再读入数据)
'''
datatmsp = pd.read_excel('datatmsp1.xls')     #读取爬取的数据 
#datatmsp.shape   
  
# 数据缺失值分析：
# 安装模块：pip3 install missingno
import missingno as msno
msno.bar(datatmsp.sample(len(datatmsp)),figsize=(10,4))   
 
# 删除缺失值过半的列
half_count = len(datatmsp)/2
datatmsp = datatmsp.dropna(thresh = half_count, axis=1)
 
# 删除重复行：
datatmsp = datatmsp.drop_duplicates()   

'''
说明：只取了 item_loc, raw_title, view_price, view_sales 这4列数据，
上面的item_loc, raw_title, view_price, view_sales 都是从网页源代码中获取的标签信息
主要对 标题、区域、价格、销量 进行分析，代码如下: 
'''
# 取出这4列数据：
data = datatmsp[['item_loc','raw_title','view_price','view_sales']]   
data.head()    #默认查看前5行数据
 
# 对 item_loc 列的省份和城市 进行拆分 得出 province 和 city 两列:
# 生成province列：
# lambda表达式类似于一个没有声明的函数
data['province'] = data.item_loc.apply(lambda x: x.split()[0])
 
# 注：因直辖市的省份和城市相同 这里根据字符长度进行判断： 
data['city'] = data.item_loc.apply(lambda x: x.split()[0]   \
                                if len(x) < 4 else x.split()[1])
 
# 提取 view_sales 列中的数字，得到 sales 列：                                                
#data['sales'] = data.view_sales.apply(lambda x: x.split('人')[0])  
 
# 查看各列数据类型
data.dtypes   
 
# 将数据类型进行转换                                             
#data['sales'] = data.sales.astype('int') 

list_col = ['province','city']
for i in  list_col:
    data[i] = data[i].astype('category') 
 
# 删除不用的列：
data = data.drop(['item_loc','view_sales'], axis=1) 
 

'''
三、数据挖掘与分析：
 
【1】. 对 raw_title 列标题进行文本分析：
   使用结巴分词器，安装模块pip3 install jieba
'''                 
title = data.raw_title.values.tolist()    #转为list
 
# 对每个标题进行分词：  使用lcut函数
import jieba
title_s = []
for line in title:     
   title_cut = jieba.lcut(line)    
   title_s.append(title_cut)

'''
对 title_s（list of list 格式）中的每个list的元素（str）进行过滤 剔除不需要的词语，
即 把停用词表stopwords中有的词语都剔除掉：
'''
 
# 导入停用词表：
stopwords = pd.read_excel('stopwords.xlsx')        
stopwords = stopwords.stopword.values.tolist()      
 
# 剔除停用词：
title_clean = []
for line in title_s:
   line_clean = []
   for word in line:
      if word not in stopwords:
         line_clean.append(word)
   title_clean.append(line_clean)
 
'''
因为下面要统计每个词语的个数，所以 为了准确性 这里对过滤后的数据 title_clean 中的每个list的元素进行去重，
即 每个标题被分割后的词语唯一。 
'''
title_clean_dist = []  
for line in title_clean:   
   line_dist = []
   for word in line:
      if word not in line_dist:
         line_dist.append(word)
   title_clean_dist.append(line_dist)
 
 # 将 title_clean_dist 转化为一个list: allwords_clean_dist 
allwords_clean_dist = []
for line in title_clean_dist:
   for word in line:
      allwords_clean_dist.append(word)
 
 
# 把列表 allwords_clean_dist 转为数据框： 
df_allwords_clean_dist = pd.DataFrame({'allwords': allwords_clean_dist})
 
 
# 对过滤_去重的词语 进行分类汇总：
word_count = df_allwords_clean_dist.allwords.value_counts().reset_index()    
word_count.columns = ['word','count']      #添加列名 
 
 
'''
观察 word_count 表中的词语，发现jieba默认的词典 无法满足需求： 
有的词语（如 可拆洗、不可拆洗等）却被cut，这里根据需求对词典加入新词
（也可以直接在词典dict.txt里面增删，然后载入修改过的dict.txt）
'''
add_words = pd.read_excel('add_words.xlsx')     #导入整理好的待添加词语
 
# 添加词语： 
for w in add_words.word:
   jieba.add_word(w , freq=1000)  
   
    
#=======================================================================
# 注：再将上面的 分词_过滤_去重_汇总 等代码执行一遍，得到新的 word_count表
#=======================================================================
    
#word_count.to_excel('word_count.xlsx', index=False)    #导出数据
 
'''
词云可视化： 见下<图2>
安装模块 wordcloud  
方法：pip3 install wordcloud  
'''
from wordcloud import WordCloud
import matplotlib.pyplot as plt
from scipy.misc import imread    
plt.figure(figsize=(20,10))   
 
pic = imread("shafa.png")   #读取图片,自定义‘沙发’形状
w_c = WordCloud(font_path="semplice.ttf",background_color="white", 
                mask=pic, max_font_size=60, margin=1)
wc = w_c.fit_words({x[0]:x[1] for x in word_count.head(100).values})    
 
plt.imshow(wc, interpolation='bilinear') 
plt.axis("off")
plt.show()
 
'''
以上注释：
shafa.png 是透明背景图 将该图放在Python的项目路径下！
"./data/simhei.ttf"   设置字体
background_color   默认是黑色 这里设置成白色
head(100)   取前100个词进行可视化！ 
max_font_size　 字体最大字号 
interpolation='bilinear'  图优化   
"off"   去除边框
'''

'''
不同省份的商品数量分布：
''' 
plt.figure(figsize=(8,4))
data.province.value_counts().plot(kind='bar',color='purple')
plt.xticks(rotation= 0)       
plt.xlabel('省份')
plt.ylabel('数量')
plt.title('不同省份的商品数量分布')
plt.show()
