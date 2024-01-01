#!/usr/bin/python
# -*- coding: UTF-8 -*-
 
import urllib.request as request
import json
from bs4 import BeautifulSoup


class CommonUtil:
    def getHtml(self, url = '', params = {}):
        pass

    def getResponse(self, url='', params ={}):
        return request.urlopen(url)


class StockUtil:
    def __init__(self):
        self.commonUtil = CommonUtil()
    
    def getStockList(self, url):
        return self.commonUtil.getResponse(url)
    

class StockBean:
    def __init__(self, jsondata):
        self.code = ''
        self.name = ''
        self.company = ''
        self.

class StockDailyInfo:
    def __init__(self, jsondata):
        self.price = ''
        self.change_rate = ''
        self.change_num = ''
        


if __name__ == '__main__':
    url = 'http://70.push2.eastmoney.com/api/qt/clist/get?cb=jQuery1124037026644752220994_1703404940375&pn=2&pz=20&po=1&np=1&ut=bd1d9ddb04089700cf9c27f6f7426281&fltt=2&invt=2&wbp2u=|0|0|0|web&fid=f3&fs=m:0+t:6,m:0+t:80,m:1+t:2,m:1+t:23,m:0+t:81+s:2048&fields=f1,f2,f3,f4,f5,f6,f7,f8,f9,f10,f12,f13,f14,f15,f16,f17,f18,f20,f21,f23,f24,f25,f22,f11,f62,f128,f136,f115,f152&_=1703404940391'
    stocklist = StockUtil().getStockList(url)
    dataStr = str(stocklist.read().decode('utf-8'))
    dataJsonStr = dataStr[dataStr.find('({') +1 :dataStr.find(');')]
    jsondata = json.loads(dataJsonStr)
    for item in jsondata['data']['diff']:
        print(item['f12'], item.)
    # soup = BeautifulSoup(html)
    # print(soup.prettify())

