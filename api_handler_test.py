#!/usr/bin/env python
# -*- coding: utf8 -*-

import os
import sys
import logging
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

_SCRIPT_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(_SCRIPT_DIR))

import json_patch
from api_handler import api_handler

if __name__ == '__main__':

    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', level=logging.DEBUG)
    x = api_handler()

    json_patch.print_json(x.reverse("abc"))
    json_patch.print_json(x.area(10, 20))
    json_patch.print_json(x.order(["개구리", "올챙이", "매미", "잠자리"]))
    json_patch.print_json(x.poi(37.2, 128.3, 3.0, 10))
    json_patch.print_json(x.ls("."))

