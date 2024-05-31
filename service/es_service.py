#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/1/31 16:16
@File    : es_service.py
@Project : ES-king
@Desc    : 
"""
import base64
import logging
import traceback
from typing import Optional
from urllib.parse import urljoin

import requests

# 配置日志输出
logging.basicConfig(level=logging.INFO)

# API
FORMAT = "?format=json&pretty"
STATS_API = "_cluster/stats" + FORMAT
HEALTH_API = "_cluster/health"
NODES_API = "_cat/nodes?format=json&pretty&h=ip,name,heap.percent,heap.current,heap.max,ram.percent,ram.current,ram.max,node.role,master,cpu,load_1m,load_5m,load_15m,disk.used_percent,disk.used,disk.total"
ALL_INDEX_API = "_cat/indices?format=json&pretty"


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
        res = requests.get(url=urljoin(self.connect_obj.host, NODES_API), headers=self.headers)
        res.raise_for_status()
        return res.json()

    def get_health(self):
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
        res = requests.get(url=urljoin(self.connect_obj.host, HEALTH_API), headers=self.headers)
        res.raise_for_status()
        return res.json()

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
        print(urljoin(self.connect_obj.host, STATS_API))
        res = requests.get(url=urljoin(self.connect_obj.host, STATS_API), headers=self.headers)
        res.raise_for_status()
        return res.json()

    def get_indexes(self, name=None):
        """
        获取index
        [
            {
                "health": "green",
                "status": "close",
                "index": "bsa_normal-20240103-0",
                "uuid": "Cb-kefT0Q62qP6fWgt_JGw",
                "pri": "1",
                "rep": "0",
                "docs.count": null,
                "docs.deleted": null,
                "store.size": null,
                "pri.store.size": null
            },
        """
        print(urljoin(self.connect_obj.host, ALL_INDEX_API))
        res = requests.get(url=urljoin(self.connect_obj.host, ALL_INDEX_API+f"&index={name}" if name else ALL_INDEX_API), headers=self.headers)
        if res.status_code == 404:
            return []
        res.raise_for_status()
        return res.json()

    def create_index(self, name, number_of_shards=1, number_of_replicas=0):
        """
        创建索引
        """
        index_config = {
            "settings": {
                "number_of_shards": number_of_shards,  # 主分片数
                "number_of_replicas": number_of_replicas  # 副本数
            }
        }
        try:
            res = requests.put(url=urljoin(self.connect_obj.host, f"{name}"), headers=self.headers, json=index_config)
            res.raise_for_status()
            return True, None
        except Exception as e:
            traceback.print_exc()
            return False, str(e)

    def get_index_info(self, index_name):
        """
        获取索引信息
        """
        try:
            print(urljoin(self.connect_obj.host, f"{index_name}"))
            res = requests.get(url=urljoin(self.connect_obj.host, f"{index_name}"), headers=self.headers)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            traceback.print_exc()
            return None

    def delete_index(self, index_name):
        """
        删除索引
        """
        res = requests.delete(url=urljoin(self.connect_obj.host, f"{index_name}"), headers=self.headers)
        res.raise_for_status()
        return res.json()

    def get_index_mappings(self, index_name):
        """
        获取索引mappings
        """
        res = requests.get(url=urljoin(self.connect_obj.host, f"{index_name}"), headers=self.headers)
        res.raise_for_status()
        return res.json()

    def get_index_settings(self, index_name):
        """
        获取索引settings
        """
        res = requests.get(url=urljoin(self.connect_obj.host, f"{index_name}"), headers=self.headers)
        res.raise_for_status()
        return res.json()

    def get_index_aliases(self, index_name):
        """
        获取索引aliases
        """
        res = requests.get(url=urljoin(self.connect_obj.host, f"{index_name}"), headers=self.headers)
        res.raise_for_status()
        return res.json()

    def get_index_stats(self, index_name):
        """
        获取索引stats
        """
        res = requests.get(url=urljoin(self.connect_obj.host, f"{index_name}"), headers=self.headers)
        res.raise_for_status()
        return res.json()

    def get_index_segments(self, index_name):
        """
        获取索引segments
        """
        res = requests.get(url=urljoin(self.connect_obj.host, f"{index_name}"), headers=self.headers)
        res.raise_for_status()
        return res.json()


es_service = ESService()
