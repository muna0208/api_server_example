#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import web
import time
import logging
import logging.handlers
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(_SCRIPT_DIR))

import request_handler

# 404: page not found
class not_found(object):
    def GET(self):
        raise web.notfound()
    def POST(self):
        raise web.notfound()

if __name__ == '__main__':
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)

    if len(sys.argv) != 2:
        print("usage: {} listen_port".format(sys.argv[0]))
        sys.exit(1)

    urls = (
        '/(.+)[.]json', 'request_handler.request_handler', # xxx.json 형태의 경로인 경우 request_handler class에서 처리
        '.*', 'not_found' # 그 외의 경로인 경우 not_found class에서 처리
    )

    request_handler.request_handler.initialize() # 혹시 request_handler에서 초기화해야 할 정보가 있으면 처리

    web.config.debug = False

    app = web.application(urls, fvars=globals(), autoreload=False)
    app.run() # sys.argv[1]을 포트 번호로 사용
