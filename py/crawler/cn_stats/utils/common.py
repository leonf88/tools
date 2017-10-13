#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright © 2015 Fan Liang <chcdlf@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Common Utils
"""

import logging
import requests
import codecs
import os
import sys
import json

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
reload(sys)
sys.setdefaultencoding("utf-8")

def get_page(url, payload, mode = "GET"):
    if mode != "GET":
        raise Exception("Current support get protocol only.")

    req = requests.get(url, params = payload)

    if req.status_code != 200:
        return None

    return req.text

def save_page(url, payload, fname, save_dir, mode = "GET"):
    data = get_page(url, payload, mode)

    if not save_dir:
        save_dir = '.'

    if not os.path.isdir(save_dir):
        if os.path.isfile(save_dir):
            os.remove(save_dir)
            logging.info("delete the file [%s]." % save_dir)
        os.makedirs(save_dir)
        logging.info("make the directory [%s]." % save_dir)

    outfile_name = os.path.join(save_dir, fname)
    fout = codecs.open(outfile_name, "w", "utf-8-sig")
    fout.write(data.decode("utf8"))
    fout.close()

    return data

