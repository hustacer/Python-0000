#-*- coding:utf-8 -*-
# get the movie^s information  
import requests
from lxml import etree
import time


url1 = 'https://movie.douban.com/subject/26942674/'
data = requests.get(url1).text
s=etree.HTML(data)

film_name=s.xpath('//*[@id="content"]/h1/span[1]/text()')#电影名
director=s.xpath('//*[@id="info"]/span[1]/span[2]/a/text()')#编剧

actor=s.xpath('//*[@id="info"]/span[3]/span[2]/a/text()')#主演
movie_time=s.xpath('//*[@id="info"]/span[13]/text()')#片长

#由于导演有时候不止一个人，所以我这里以列表的形式输出
ds = []
for d in director:
    ds.append(d)

#由于演员不止一个人，所以我这里以列表的形式输出
acs = []
for a in actor:
    acs.append(a)

print ('电影名:',film_name)
print ('导演:',ds)
print ('主演:',acs)
print ('片长:',movie_time)
