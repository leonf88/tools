#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2015 Fan Liang <chcdlf@gmail.com>
#
# Distributed under terms of the MIT license.

"""
1. download the indicator tree from `data.stats.gov.cn`;
2. restore the pages, and save the child-indicators into csv file.
"""

from utils.common import *

def download_zb(base_url, payload, data_dir):
    """
    download zhibiao recursively in the bfs way.
    """
    fname = payload["id"] + ".dat"
    _data = save_page(base_url, payload, fname, data_dir)
    if not _data:
        logging.info("no data get.")
        return
    data = json.loads(_data)

    _id = payload["id"]

    for item in data:
        if item.has_key("isParent"): # when it has child, them step into the child
            indi_code = item["id"]
            if item["isParent"] is True:
                payload["id"] = indi_code
                get_zb(base_url, payload, data_dir)

    payload["id"] = _id

def run_dw_zb():
    data_dirs = [
             'csyd', #'获取城市月度数据'
             'csnd', #'获取城市年度数据'
             'hgyd', #'获取宏观月度数据'
             'hgjd', #'获取宏观季度数据'
             'hgnd', #'获取宏观年度数据'
             'fsyd', #'获取分省月度数据'
             'fsjd', #'获取分省季度数据'
             'fsnd', #'获取分省年度数据'
             ]

    base_url = "http://data.stats.gov.cn/easyquery.htm"
    payload = {"m":"getTree",
            "dbcode":"hgnd",
            "wdcode":"zb",
            "id":"zb"}

    data_dir = "data"
    for db in data_dirs:
        logging.info("extract the %s data." % db)
        payload["dbcode"] = db
        data_dir = os.path.join("data", db)
        download_zb(base_url, payload, data_dir)

def save_zb_as_csv(data_dir):
    res = []
    def func(arg, dirname, names):
        for filespath in names:
            fpath = os.path.join(dirname, filespath)
            if os.path.isfile(fpath):
                fint = codecs.open(fpath, "r", "utf-8-sig")
                data = json.loads(fint.readline())
                for d in data:
                    if d.has_key("isParent") and not d["isParent"]:
                        res.append([d["dbcode"], d["id"], d["name"]])
    os.path.walk(data_dir, func, ())

    fout = codecs.open("zb.csv", "w", "utf-8-sig")
    fout.write("dbcode, zb, name\n")

    for item in res:
        fout.write(",".join(item).decode("utf8")+"\n")
    fout.close()

if __name__ == '__main__':
    run_dw_zb()
    save_zb_as_csv()
