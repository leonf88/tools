#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2015 Fan Liang <chcdlf@gmail.com>
#
# Distributed under terms of the MIT license.

from utils.common import *

def get_data(dbcode, indicator, sjtime, region, rowcode = "zb", colcode = "sj"):
    import time
    dfwds = []
    if indicator:
        dfwds.append({"wdcode": "zb", "valuecode": indicator})
    if sjtime:
        dfwds.append({"wdcode": "sj", "valuecode": sjtime})
    if region:
        dfwds.append({"wdcode": "reg", "valuecode": region})

    payload = {"m":"QueryData",
        "dbcode": dbcode,       # 指定数据库
        "rowcode":rowcode,      # 行数据类型
        "colcode":colcode,      # 列数据类型
        "wds":'[]',
        "dfwds":json.dumps(dfwds),
        "k1": str(int(time.time() * 1000))}

    base_url = "http://data.stats.gov.cn/easyquery.htm"
    _data = get_page(base_url, payload)

    if not _data:
        logging.info("not data get.")
        return None

    logging.debug(_data)
    data = json.loads(_data)

    if data["returncode"] != 200:
        logging.info("returncode is not correct.")
        return None

    return data

if __name__ == '__main__':
    get_data("csnd", "A02", "2010-", "110000")
