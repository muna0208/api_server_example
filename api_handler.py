#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import logging
import traceback
import inspect
import warnings
import time
import subprocess

warnings.simplefilter(action='ignore', category=FutureWarning)

_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(_SCRIPT_DIR))

import json
from json_patch import print_json, load_json

import sample_response

# metaclass 기반의 singleton 구성
import threading

class singleton(type):
    _singleton_lock = threading.Lock()
    _instances = {}
    def __call__(cls, *args, **kwargs):
        with singleton._singleton_lock:
            if cls not in cls._instances:
                cls._instances[cls] = super(singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class api_handler(object):
    __metaclass__ = singleton # api handler의 공용 리소스 공유를 위해 singleton으로 구성

    def __init__(self):
        pass

    # 미구현 API에 대해 샘플 응답을 제공
    def get_sample_response(self):
        api_name = inspect.stack()[1][3]  # caller function name
        return getattr(sample_response, api_name, None)

    #
    # 여기서부터 API 구현 영역
    #

    # 예제1
    def reverse(self, s):
        return s[::-1]

    # 예제2
    def area(self, width, height):
        return width * height

    # 예제3: list형 파라메터
    def order(self, s, reverse=False):
        return sorted(s, reverse=reverse)

    # 예제4: API 응답 예제 이용하기
    def poi(self, latitude, longitude, radius, top_n=10):
        return self.get_sample_response()

    # 예제5: subprocess를 이용하여 외부 커맨드를 실행하는 예제
    def ls(self, path, timeout):
        command = ["ls", path]
        return self._run_command(command, timeout)

    def _run_command(self, command, timeout):

        # 필요할 경우 timeout을 초단위로 세팅할 수 있음
        try:
            result = subprocess.run(command, capture_output=True, timeout=timeout)
            if result.returncode != 0:
                e = Exception("failed to run command {}".format(" ".join(command)))
                e.extra_info = {
                    "return_code": str(result.returncode),
                    "error_msg": result.stderr.decode("utf-8")
                }
                raise e
        except subprocess.TimeoutExpired as e:
            e.extra_info = {
                "return_code": "99",
                "error_msg": "timeout expired"
            }
            raise 
        except subprocess.CalledProcessError as e:
            e.extra_info = {
                "return_code": str(result.returncode),
                "error_msg": result.stderr.decode("utf-8")
            }
            raise 
        except:
            raise
        return result.stdout.decode("utf-8").split()

