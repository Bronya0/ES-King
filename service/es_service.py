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
from requests.auth import HTTPBasicAuth

# 配置日志输出
logging.basicConfig(level=logging.INFO)

# API
FORMAT = "?format=json&pretty"
STATS_API = "_cluster/stats" + FORMAT
HEALTH_API = "_cluster/health"
NODES_API = "_cat/nodes?format=json&pretty&h=ip,name,heap.percent,heap.current,heap.max,ram.percent,ram.current,ram.max,node.role,master,cpu,load_5m,disk.used_percent,disk.used,disk.total,fielddataMemory,queryCacheMemory,requestCacheMemory,segmentsMemory,segments.count"
ALL_INDEX_API = "_cat/indices?format=json&pretty&bytes=b"
CLUSTER_SETTINGS = "_cluster/settings"
FORCE_MERGE = "_forcemerge?wait_for_completion=false"  # 异步
REFRESH = "_refresh"
FLUSH = "_flush"
CACHE_CLEAR = "_cache/clear"
TASKS_API = "_tasks" + FORMAT
CANCEL_TASKS_API = "_tasks/{task_id}/_cancel"


class Connect:
    def __init__(self, host, username, pwd):
        self.host = host
        self.username = username
        self.pwd = pwd


class ESService:
    def __init__(self):
        self.connect_name = None
        self.connect_obj: Optional[Connect] = None
        self.auth = None
        self.host = None

    def set_connect(self, key, host, username, pwd):
        self.connect_name = key
        self.connect_obj = Connect(
            host=host,
            username=username,
            pwd=pwd,
        )
        self.auth = HTTPBasicAuth(username, pwd)
        print("设置当前连接：", self.connect_obj.host)

    def test_client(self, host, username, pwd):
        # 测试连接
        try:
            res = requests.get(url=urljoin(host, HEALTH_API), auth=HTTPBasicAuth(username, pwd))
            if res.status_code != 200:
                return False, res.text
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
        print(urljoin(self.connect_obj.host, NODES_API))
        res = requests.get(url=urljoin(self.connect_obj.host, NODES_API), auth=self.auth)
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
        res = requests.get(url=urljoin(self.connect_obj.host, HEALTH_API), auth=self.auth)
        res.raise_for_status()
        return res.json()

    def get_stats(self) -> str:
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
        res = requests.get(url=urljoin(self.connect_obj.host, STATS_API), auth=self.auth)
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
        print(urljoin(self.connect_obj.host, ALL_INDEX_API + f"&index={name}" if name else ALL_INDEX_API))
        res = requests.get(
            url=urljoin(self.connect_obj.host, ALL_INDEX_API + f"&index={name}" if name else ALL_INDEX_API), auth=self.auth)
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
            res = requests.put(url=urljoin(self.connect_obj.host, f"{name}"), auth=self.auth, json=index_config)
            if res.status_code != 200:
                return False, res.text
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
            res = requests.get(url=urljoin(self.connect_obj.host, f"{index_name}"), auth=self.auth)
            if res.status_code != 200:
                return False, res.text
            return True, res.json()
        except Exception as e:
            traceback.print_exc()
            return False, e

    def delete_index(self, index_name):
        """
        删除索引
        """
        try:
            res = requests.delete(url=urljoin(self.connect_obj.host, f"{index_name}"), auth=self.auth)
            if res.status_code != 200:
                return False, res.text
            return True, res.json()
        except Exception as e:
            traceback.print_exc()
            return False, e

    def open_close_index(self, index_name, now):
        """
        开启/关闭索引
        """
        try:
            action = {
                "open": "_close",
                "close": "_open"
            }[now]
            print(urljoin(self.connect_obj.host, f"{index_name}/{action}"))

            res = requests.post(url=urljoin(self.connect_obj.host, f"{index_name}/{action}"), auth=self.auth)
            if res.status_code != 200:
                return False, res.text
            return True, res.json()
        except Exception as e:
            traceback.print_exc()
            return False, e

    def get_index_mappings(self, index_name):
        """
        获取索引mappings
        """
        res = requests.get(url=urljoin(self.connect_obj.host, f"{index_name}"), auth=self.auth)
        res.raise_for_status()
        return res.json()

    def merge_segments(self, index_name):
        """
        获取索引mappings
        """
        print(urljoin(self.connect_obj.host, f"{index_name}/{FORCE_MERGE}"))
        try:
            res = requests.post(url=urljoin(self.connect_obj.host, f"{index_name}/{FORCE_MERGE}"), auth=self.auth)
            if res.status_code != 200:
                return False, res.text
            return True, res.json()
        except Exception as e:
            traceback.print_exc()
            return False, str(e)

    def refresh(self, index_name):
        """
        """
        print(urljoin(self.connect_obj.host, f"{index_name}/{REFRESH}"))
        try:
            res = requests.post(url=urljoin(self.connect_obj.host, f"{index_name}/{REFRESH}"), auth=self.auth)
            if res.status_code != 200:
                return False, res.text
            return True, res.json()
        except Exception as e:
            traceback.print_exc()
            return False, str(e)

    def flush(self, index_name):
        """
        """
        print(urljoin(self.connect_obj.host, f"{index_name}/{FLUSH}"))
        try:
            res = requests.post(url=urljoin(self.connect_obj.host, f"{index_name}/{FLUSH}"), auth=self.auth)
            if res.status_code != 200:
                return False, res.text
            return True, res.json()
        except Exception as e:
            traceback.print_exc()
            return False, str(e)

    def cache_clear(self, index_name):
        """
        """
        print(urljoin(self.connect_obj.host, f"{index_name}/{CACHE_CLEAR}"))
        try:
            res = requests.post(url=urljoin(self.connect_obj.host, f"{index_name}/{CACHE_CLEAR}"), auth=self.auth)
            if res.status_code != 200:
                return False, res.text
            return True, res.json()
        except Exception as e:
            traceback.print_exc()
            return False, str(e)

    def get_doc_10(self, index_name):
        """
        """
        print(urljoin(self.connect_obj.host, f"{index_name}/_search"))
        try:
            res = requests.post(url=urljoin(self.connect_obj.host, f"{index_name}/_search"), auth=self.auth,
                                json={
                                    "query": {
                                        "query_string": {
                                            "query": "*"
                                        }
                                    },
                                    "size": 10,
                                    "from": 0,
                                    "sort": []
                                })
            if res.status_code != 200:
                return False, res.text
            return True, res.json()
        except Exception as e:
            traceback.print_exc()
            return False, str(e)

    def search(self, method, path, body):
        """
        """
        print(method, urljoin(self.connect_obj.host, f"{path}"))
        try:
            res = requests.request(method=method, url=urljoin(self.connect_obj.host, f"{path}"), auth=self.auth,
                                json=body)
            if res.status_code != 200:
                return False, res.text
            return True, res.json()
        except Exception as e:
            traceback.print_exc()
            return False, str(e)

    def get_cluster_settings(self):
        """
        获取索引settings
        """
        try:
            print(urljoin(self.connect_obj.host, f"{CLUSTER_SETTINGS}"))
            res = requests.get(url=urljoin(self.connect_obj.host, f"{CLUSTER_SETTINGS}"), auth=self.auth)
            res.raise_for_status()
            return res.json()
        except Exception as e:
            traceback.print_exc()
            return None

    def get_index_settings(self, index_name):
        """
        获取索引settings
        """
        res = requests.get(url=urljoin(self.connect_obj.host, f"{index_name}"), auth=self.auth)
        res.raise_for_status()
        return res.json()

    def get_index_aliases(self, index_name_list):
        """
        获取索引aliases
        """
        index_names = ",".join(index_name_list)
        print(urljoin(self.connect_obj.host, f"{index_names}/_alias"))
        alias = {}

        try:
            res = requests.get(url=urljoin(self.connect_obj.host, f"{index_names}/_alias"), auth=self.auth)
            res.raise_for_status()
            data: dict = res.json()
            for name, obj in data.items():
                names = list(obj['aliases'].keys())
                if names:
                    alias[name] = ','.join(names)
            return alias
        except Exception as e:
            return alias

    def get_index_segments(self, index_name):
        """
        获取索引segments
        """
        res = requests.get(url=urljoin(self.connect_obj.host, f"{index_name}"), auth=self.auth)
        res.raise_for_status()
        return res.json()

    def get_tasks(self):
        """
        获取tasks
        """
        print(urljoin(self.connect_obj.host, f"{TASKS_API}"))
        try:
            res = requests.get(url=urljoin(self.connect_obj.host, f"{TASKS_API}"), auth=self.auth,)
            nodes: dict = res.json()["nodes"]
            data = []
            for node_id, node_obj in nodes.items():
                for task_id, task_info in node_obj["tasks"].items():
                    data.append({
                        "task_id": task_id,
                        "node_name": node_obj['name'],
                        "node_ip": node_obj['ip'],
                        "type": task_info['type'],
                        "action": task_info['action'],
                        "start_time_in_millis": task_info['start_time_in_millis'],
                        "running_time_in_nanos": task_info['running_time_in_nanos'],
                        "cancellable": task_info['cancellable'],
                        "parent_task_id": task_info['parent_task_id'] if "parent_task_id" in task_info else "",
                    })
            return True, data
        except Exception as e:
            traceback.print_exc()
            return False, str(e)

    def cancel_tasks(self, task_id):
        """
        取消tasks
        """
        print(urljoin(self.connect_obj.host,  CANCEL_TASKS_API.format(task_id=task_id)))
        try:
            res = requests.post(url=urljoin(self.connect_obj.host, CANCEL_TASKS_API.format(task_id=task_id)), auth=self.auth,)
            if res.status_code != 200:
                return False, res.text
            return True, res.json()
        except Exception as e:
            traceback.print_exc()
            return False, str(e)


es_service = ESService()
