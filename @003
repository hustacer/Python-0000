#-*- coding:utf-8 -*-
#get a movie-list of douban.com
import requests
from lxml import etree
import time


url1 = 'https://movie.douban.com/chart'
data = requests.get(url1).text
s=etree.HTML(data)

film_name=s.xpath('//*[@id="content"]/h1/text()')
print(film_name)
mmmms=s.xpath('//*[@id="content"]/div/div[1]/div/div/table')
for div in mmmms:
	list_name=div.xpath('./tr/td[2]/div/a/text()')[0].strip().strip(' ').strip('/').strip()
	score=div.xpath('./tr/td[2]/div/div/span[2]/text()')[0]
	comment=div.xpath('./tr/td[2]/div/div/span[3]/text()')[0].strip('(').strip(')')
	aurl=div.xpath('./tr/td[2]/div/a/@href')[0]
	print("电影：{}--->{}分--->{}--->{}".format(list_name,score,comment,aurl))
