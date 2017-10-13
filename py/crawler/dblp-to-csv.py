#!/usr/bin/env python

import os
import sys
import requests
import urlparse
from lxml import html

reload(sys)
sys.setdefaultencoding('utf-8')

def extract_auth():
    pass

def extract_title():
    pass

def save_as_csv():
    pass

def run():
    pass

def enter_article(html_url):
    dirname = os.path.join('journals', html_url.split('/')[-2])
    fname = html_url.split('/')[-1].split('.')[0] + '.csv'

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    fpath = os.path.join(dirname, fname)

    if not os.path.exists(fpath): 
        with open(fpath, 'w') as fout:
            html_page = requests.get(html_url)
            html_lxml = html.fromstring(html_page.content)

            titles = html_lxml.xpath('//li[@class="entry article"]/div[@class="data"]/span[@class="title"]/text()')
            for title in titles:
                fout.write(title)
                fout.write('\n')

def enter_proceeding(html_url):
    dirname = os.path.join('conf', html_url.split('/')[-2])
    fname = html_url.split('/')[-1].split('.')[0] + '.csv'

    if not os.path.exists(dirname):
        os.makedirs(dirname)

    fpath = os.path.join(dirname, fname)

    if not os.path.exists(fpath): 
        with open(fpath, 'w') as fout:
            html_page = requests.get(html_url)
            html_lxml = html.fromstring(html_page.content)

            titles = html_lxml.xpath('//li[@class="entry inproceedings"]/div[@class="data"]/span[@class="title"]/text()')
            for title in titles:
                fout.write(title)
                fout.write('\n')

def enter_editor(html_url):
    print "process", html_url
    html_page = requests.get(html_url)
    html_lxml = html.fromstring(html_page.content)
    # years = html_lxml.xpath('//li[@class="entry editor"]/span[@itemprop="datepublished"]/text()')
    urls = html_lxml.xpath('//li[@class="entry editor"]/div[@class="data"]/a[text()="[contents]"]/@href')

    for u in urls:
        enter_proceeding(u)

def enter_journal(html_url):
    print "process", html_url
    html_page = requests.get(html_url)
    html_lxml = html.fromstring(html_page.content)
    urls = html_lxml.xpath('//div[@id="main"]/ul/li/a/@href')

    for u in urls:
        enter_article(u)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print "Usage: %s <url list file>" % sys.argv[0]
        sys.exit(-1)

    file = sys.argv[1]
    with open(file, 'r') as fin:
        data = fin.readlines()
        for d in data:
            if d.startswith('#'):
                continue
            else:
                if 'journals' in d:
                    enter_journal(d)
                elif 'conf' in d:
                    enter_editor(d)
