#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import requests
import logging
import copy
import traceback
import web
import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)

_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(_SCRIPT_DIR))

import json_patch
from action_table import action_table
from api_handler import api_handler

import random
import time

class request_handler(object):

    # API 처리기
    api = None

    # API 처리기 준비
    @classmethod
    def initialize(cls):
        logging.info("create api_handler")
        cls.api = api_handler()

    @classmethod
    def lookup_action_info(cls, action):
        alias = set()
        while action in action_table:
            # alias 처리
            if isinstance(action_table[action], str):
                if action in alias:
                    logging.error("invalid action alias {}".format(list(alias)))
                    return action, None
                alias.add(action)
                action = action_table[action]
            else:
                return action, action_table[action]
        return action, None

    @classmethod
    def adjust_value(cls, v):
        # list는 web.py에서 multiple value를 지원하는 것을 따르도록 함
        #if (len(v) >= 2) and ((v[0] + v[-1]) in ["[]", "{}"]):
        if (len(v) >= 2) and ((v[0] + v[-1]) in ["{}"]):
            return json_patch.load_json(v)
        else:
            return v

    @classmethod
    def adjust_request(cls, request):
        for k, v in request.items():
            if isinstance(v, list):
                try:
                    vv = [cls.adjust_value(d) for d in v]
                    request[k] = vv
                except:
                    pass
            elif isinstance(v, str):
                try:
                    vv = cls.adjust_value(v)
                    request[k] = vv
                except:
                    pass

    @classmethod
    def parse_request(cls, action_info):
        error_msg = ""
        content_type = web.ctx.env.get("CONTENT_TYPE")
        if action_info:
            request = web.input(**action_info["default_params"])
        else:
            request = web.input(pretty="N")

        # GET 방식에서 list/obj 표현 지원
        cls.adjust_request(request)

        if content_type != "application/x-www-form-urlencoded":
            payloads = web.data()
            if payloads:
                try:
                    data = json_patch.load_json(payloads)
                    request.update(data)
                except Exception as e:
                    error_msg = "invalid payloads: {}\ncall stack: {}".format(str(e), traceback.format_exc())
                    logging.error("invalid payloads: {}\nrequest: {}\npayloads: {}\ncall stack: {}".format(str(e), json_patch.dump_json(request), payloads, traceback.format_exc()))

        return request, error_msg

    @classmethod
    def check_missing_param(cls, action_info, request):
        if action_info:
            for name in action_info["essential_params"]:
                if not (name in request):
                    return name
        return None

    @classmethod
    def OPTIONS(cls, action):
        web.header("Access-Control-Allow-Origin", "*", unique=True)
        web.header("Access-Control-Allow-Methods", "GET,POST,OPTIONS", unique=True)
        web.header("Access-Control-Allow-Headers", "Origin,Accept,X-Requested-With,Content-Type,Access-Control-Request-Method,Access-Control-Request-Headers,Authorization", unique=True)
        web.header("Access-Control-Max-Age", "1000", unique=True)

    @classmethod
    def GET(cls, action):
        web.header("Access-Control-Allow-Origin", "*", unique=True)
        web.header("Access-Control-Max-Age", "1000", unique=True)

        # alias 처리 및 action table 조회 결과 얻어오기
        api_name, action_info = cls.lookup_action_info(action)

        # api_handler에서 action 처리기가 있는지 검사
        dispatcher = getattr(cls.api, api_name, None)
        # 요청 읽어들이기
        request, error_msg = cls.parse_request(action_info)

        if error_msg:
            rv = {"return_code": "04", "error_msg": error_msg}
        elif not action_info:
            rv = {"return_code": "01", "error_msg": "undefined action {}".format(action)}
        elif not dispatcher:
            rv = {"return_code": "02", "error_msg": "unimplemented action {}".format(action)}
        else:
            missed = cls.check_missing_param(action_info, request)

            request_id = random.randint(100000, 999999)
            logging.info("request_id: {}, action: {}, request: {}".format(request_id, action, json_patch.dump_json(request)))
            start_time = time.time()

            if missed:
                rv = {"return_code": "03", "error_msg": "no {} parameter".format(missed)}
            else:
                try:
                    api_params = action_info["api_params"](request)
                    try:
                        output = dispatcher(*api_params)
                        rv = {"return_code": "00", "error_msg": "", "data": output}
                        # 실행시간을 기록하고 싶을 때 사용
                        #logging.info("request_id: {}, action: {}, time: {}".format(request_id, action, time.time() - start_time))
                    except Exception as e:
                        if "extra_info" in dir(e): # api_handler에서 예측 가능한 오류(timeout, command 비정상 종료 등)가 발생해서 정보를 설정한 경우
                            return_code = e.extra_info.get("return_code", "99")
                            if "error_msg" in e.extra_info:
                                error_msg = e.extra_info["error_msg"]
                                logging.error("internal error: {}\naction: {}\nrequest: {}".format(error_msg, action, json_patch.dump_json(request)))
                            else:
                                error_msg = "internal error: {}\ncall stack: {}".format(str(e), traceback.format_exc())
                                logging.error("internal error: {}\naction: {}\nrequest: {}\ncall stack: {}".format(str(e), action, json_patch.dump_json(request), traceback.format_exc()))
                            rv = {"return_code": return_code, "error_msg": error_msg}
                        else: # api_handler 에서 예측하지 못한 exception이 발생한 경우
                            logging.error("internal error: {}\naction: {}\nrequest: {}\ncall stack: {}".format(str(e), action, json_patch.dump_json(request), traceback.format_exc()))
                            rv = {"return_code": "99", "error_msg": "internal error: {}\ncall stack: {}".format(str(e), traceback.format_exc())}
                except Exception as e:
                    logging.error("invalid parameters: {}\naction: {}\nrequest: {}\ncall stack: {}".format(str(e), action, json_patch.dump_json(request), traceback.format_exc()))
                    rv = {"return_code": "04", "error_msg": "invalid parameters: {}\ncall stack: {}".format(str(e), traceback.format_exc())}
        if request.get("pretty", "N") in ["Y", "y"]:
            response = json_patch.dump_json(rv, ind=4, max_indent="auto")
        else:
            response = json_patch.dump_json(rv)

        if ("callback" in request) and request["callback"]:
            web.header("Content-Type","text/javascript; charset=utf-8", unique=True)
            return request["callback"] + "(" + response + ");"
        else:
            web.header("Content-Type","application/json; charset=utf-8", unique=True)
            return response

    @classmethod
    def POST(cls, action):
        return cls.GET(action)
