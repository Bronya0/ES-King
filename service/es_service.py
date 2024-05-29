#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/1/31 16:16
@File    : es_service.py
@Project : ES-king
@Desc    : 
"""
import base64
import copy
import logging
import os
import time
import traceback
from collections import defaultdict
from datetime import date, datetime
from typing import Optional
from urllib.parse import quote

import requests
from urllib.parse import urlsplit, urlunparse,urljoin, urlencode

# 配置日志输出
logging.basicConfig(level=logging.INFO)

# API
FORMAT = "?format=json&pretty"
STATS_API = "_cluster/stats" + FORMAT
NODES_API = "_cat/nodes?format=json&pretty&h=ip,name,heap.percent,heap.current,heap.max,ram.percent,ram.current,ram.max,node.role,master,cpu,load_1m,load_5m,load_15m,disk.used_percent,disk.used,disk.total"


class Connect:
    def __init__(self, host, username, pwd):
        self.host = host
        self.username = username
        self.pwd = pwd


class ESService:
    def __init__(self):
        self.connect_name = None
        self.connect_obj: Optional[Connect] = None
        self.headers = None
        self.host = None

    def set_connect(self, key, host, username, pwd):
        self.connect_name = key
        self.connect_obj = Connect(
            host=host,
            username=username,
            pwd=pwd,
        )
        self.headers = {'Authorization': base64.b64encode(f"{username}:{pwd}".encode()).decode()}
        print("设置当前连接：", self.connect_obj.host)

    def test_client(self, host, username, pwd):
        # 测试连接
        try:
            res = requests.get(url=host, headers=self.headers)
            res.raise_for_status()
            return True, None
        except Exception as e:
            return False, str(e)

    def get_nodes(self):

        """
        获取集群节点信息
        [
            {
                "ip": "",
                "name": "xxx",
                "heap.percent": "61",
                "heap.current": "71.9gb",
                "heap.max": "112gb",
                "ram.percent": "71",
                "ram.current": "417.2gb",
                "ram.max": "612.5gb",
                "node.role": "dim",
                "master": "*",
                "cpu": "20",
                "load_1m": "6.30",
                "load_5m": "51.32",
                "load_15m": "5.24",
                "disk.used_percent": "17.56",
                "disk.used": "178.1gb",
                "disk.total": "44.7gb"
            }
        ]
        """
        try:
            res = requests.get(url=urljoin(self.connect_obj.host, NODES_API), headers=self.headers)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            traceback.format_exc()
            return None

    def get_stats(self):
        """
        获取集群健康信息
        [
            {
                "epoch": "1716819919",
                "timestamp": "14:25:19",
                "cluster": "cluster1",
                "status": "yellow",
                "node.total": "1",
                "node.data": "1",
                "shards": "3",
                "pri": "3",
                "relo": "0",
                "init": "0",
                "unassign": "2",
                "pending_tasks": "0",
                "max_task_wait_time": "-",
                "active_shards_percent": "60.0%"
            }
        ]
        """
        try:
            print(urljoin(self.connect_obj.host, STATS_API))
            res = requests.get(url=urljoin(self.connect_obj.host, STATS_API), headers=self.headers)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            traceback.format_exc()
            return None


es_service = ESService()
