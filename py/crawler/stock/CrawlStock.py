#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Author        : Fan Liang (chcdlf@gmail.com)
Created Date  : 2015-03-20 19:30:53
Describtion   : crawler the stock information from sina
TODO          : compress the json storage; print the specific stock in real-time
"""

from bs4 import BeautifulSoup as bs
import urllib2
import requests
import json
from datetime import datetime
import sys, re, os

reload(sys)

sys.setdefaultencoding('utf-8')  

class CrawlStock:

    sname = ['name', 'open', 'close_yesterday', 'now', 'high', 'low', 'buy', 'sell', 'amount', 'volumn',
             'buy1-amount', 'buy1-price', 'buy2-amount', 'buy2-price', 'buy3-amount', 'buy3-price',
             'buy4-amount', 'buy4-price', 'buy5-amount', 'buy5-price',
             'sell1-amount', 'sell1-price', 'sell2-amount', 'sell2-price', 'sell3-amount', 'sell3-price',
             'sell4-amount', 'sell4-price', 'sell5-amount', 'sell5-price',
             'date', 'time'] # this order is defined by the website

    def parse_stock_data(self, stock_str):
        if not stock_str:
            return None
        sdata = stock_str.split(',')
        
        return dict(zip(self.sname, sdata))

    def get_stock_from_sina(self, stocks):
        """
        Get the information of stocks from 'http://hq.sinajc.cn' website
        """
        if type(stocks) is list or type(stocks) is tuple:
            stocks_ids = ",".join(stocks)
        else:
            stocks_ids = stocks

        url = 'http://hq.sinajs.cn/list=' + stocks_ids

        r = requests.get(url)
        if r.status_code != 200:
            return {}
        results = {}
        for s in r.text.split('\n'):
            s = s.strip()
            if not s:
                continue
            content = s.split('"')
            sre = re.match(r'^var +hq_str_(\w+)=$', content[0].strip())
            skey = sre.group(1)
            sval = self.parse_stock_data(content[1].strip())
            results[skey] = sval

        return results

    def save_stocks_by_day(self, stocks_ids, w_file):
        """
        According to the codes of stocks, get the corresponding information.
        Then, store them in the files as JSON and CSV format.
        """
        results = {}
        span = 60
        prev_cnt = 0
        stocks_len = len(stocks_ids)

        while True:
            if prev_cnt + span <  stocks_len:
                curr_cnt = prev_cnt + span
                codes = stocks_ids[prev_cnt:curr_cnt]
                results.update(self.get_stock_from_sina(codes))
            else:
                codes = stocks_ids[prev_cnt:stocks_len]       
                results.update(self.get_stock_from_sina(codes))
                print '\r%3d/%d......100%%' % (stocks_len, stocks_len)
                break

            prev_cnt = curr_cnt
            rate_num = float(curr_cnt)/stocks_len
            print '\r%3d/%d......%3d%%' % (curr_cnt, stocks_len, rate_num * 100)
            sys.stdout.flush()
            
        # dump the results with JSON format
        self.dump_json(results, w_file + ".json")

        # dump the results with CSV format
        self.dump_csv(results, w_file + ".csv")
    
    def dump_json(self, results, w_file):
        with open(w_file, "w") as fout:
            fout.write(json.dumps(results))

    def dump_csv(self, results, w_file):
        with open(w_file, "w") as fout:
            fout.write(",".join(["stock_id"] + self.sname)+"\n")
            def get_values(keys, dict_item):
                res = []
                for x in keys:
                    res.append(dict_item[x])

                return ",".join(res)

            for key, value in results.iteritems():
                if value and key:
                    fout.write(key + "," + get_values(self.sname, value) + "\n")

def load_stocks_by_file(r_file):
    with open(r_file) as file:
        return json.loads(file.readlines()[0].encode('utf8'), encoding = 'utf8')

def query(stocks, stock_id):
    if stocks.has_key(stock_id):
        return stocks[stock_id]
    else:
        return None

def parse_stock_list(w_file):
    """
    Read the stock list which is download from 'http://quote.eastmoney.com/stocklist.html#sz'.
    Extract the stock code and stock name.
    Output the stock code and name in the 'stock.list'
    """
    if os.path.exists("stocklist.html"):
        soup = bs(open("stocklist.html"))
    else:
        response = urllib2.urlopen("http://quote.eastmoney.com/stocklist.html")  
        soup = bs(response.read())

    stockName=soup.find(id="quotesearch").find_all(attrs={"class":"sltit"})
    stockList=soup.find(id="quotesearch").find_all("ul")

    fout=open(w_file, "w")

    name_re = re.compile('(.*)\((\d+)\)')
    code_re = re.compile('.*/(\w+\d+).html')

    for stock in soup.find(id="quotesearch").find_all("a"):
        if "href" in stock.attrs:
            stock_href = stock.attrs["href"]
            stock_name = stock.string
            nm = name_re.match(stock_name)
            cm = code_re.match(stock_href)
            if nm and cm:
                fout.write("%s\t%s\n" % (cm.group(1), nm.group(1)))

    fout.close()

def load_stock_list(r_file):
    """
    Load the stock list from file which is writen by @parse_stock_list
    """
    fin = open(r_file, "r")
    stocks = []
    for line in fin.readlines():
        stocks.append(line.split("\t"))

    fin.close()
    return stocks

if __name__ == '__main__':
    stock_file = "stock.list"
    base_dir = "data"
    dt = datetime.now()
    today = dt.strftime("%Y-%m-%d")
    today_dir = os.path.join(base_dir, today)
    if not os.path.isdir(today_dir):
        os.makedirs(today_dir)

    moment = dt.strftime("%H%M%S")
    stock_file_by_moment = os.path.join(today_dir, moment)  

    if os.path.exists(stock_file) is False:
        parse_stock_list(stock_file)

    c = CrawlStock()
    stocks = load_stock_list(stock_file)
    stocks_ids = zip(*stocks)[0]
    c.save_stocks_by_day(stocks_ids, stock_file_by_moment)
    # dump_csv(load_stocks_by_file("test"), "test.csv")
    # print query(load_stocks_by_file("test"), "sz002230")