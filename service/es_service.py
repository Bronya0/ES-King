#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/1/31 16:16
@File    : kafka_service.py
@Project : kafka-king
@Desc    : 
"""
import base64
import copy
import logging
import os
import time
import traceback
from collections import defaultdict
from typing import Optional

import requests

# 配置日志输出
logging.basicConfig(level=logging.INFO)

HEALTHY_API = "_cat/health"


class Connect:
    def __init__(self, host, username, pwd):
        self.host = host
        self.username = username
        self.pwd = pwd


class ESService:
    def __init__(self):
        self.connect_name = None
        self.connect_obj = None

    def set_connect(self, key, host, username, pwd):
        self.connect_name = key
        self.connect_obj = Connect(
            host=host,
            username=username,
            pwd=pwd,
        )

    def test_client(self, host, username, pwd):
        # 测试连接
        try:
            res = requests.get(url=os.path.join(host), headers={
                'Authorization': base64.b64encode(f"{username}:{pwd}".encode()).decode()})
            res.raise_for_status()
            return True, None
        except Exception as e:
            return False, str(e)


es_service = ESService()
