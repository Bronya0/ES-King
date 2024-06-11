#!/usr/bin/env python
# -*-coding:utf-8 -*-
import datetime

import flet as ft
from flet_core import DataColumnSortEvent, ControlEvent

from service.common import S_Text, build_tab_container, open_snack_bar, S_Button, progress_bar, common_page
from service.es_service import es_service
from service.page_table import PageTable


class Broker(object):
    """
    Cluster页的组件
    """

    def __init__(self):
        # page
        self.task_data_lst = []
        self.task_data_lst_tmp = []
        self.nodes_tmp = []
        self.page_num = 1
        self.page_size = 10
        # order
        # 每列对应的排序状态
        self.reverse = {}
        self.cluster_table_rows = None
        self.nodes = None
        self.cluster_table = None

        self.node_tab = ft.Tab(
            text='集群节点列表', content=ft.Column(), icon=ft.icons.HIVE_OUTLINED,
        )

        self.task_table_rows = []
        self.task_table = None

        self.get_task_button = ft.TextButton("读取集群Task列表", on_click=self.get_task, icon=ft.icons.READ_MORE,
                                             style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))

        self.task_tab = ft.Tab(
            text='ES Task列表', content=ft.Column(), icon=ft.icons.HIVE_OUTLINED,
        )
        self.tab = ft.Tabs(
            tabs=[
                self.node_tab,
                self.task_tab,
            ],
            expand=True,
            animation_duration=300,
        )

        self.controls = [
            self.tab
        ]

    def init(self, page=None):
        if not es_service.connect_obj:
            return "请先选择一个可用的ES连接！\nPlease select an available ES connection first!"

        self.init_data()
        self.init_table()

    def init_data(self):

        self.nodes = es_service.get_nodes()
        # page
        # 只在最开始、排序时执行一次
        self.nodes_tmp = self.nodes[:self.page_size]

    def init_table(self):

        # 节点列表表格
        def cluster_table_row_func(i, offset, _node):
            row = ft.DataRow(
                cells=[
                    ft.DataCell(S_Text(offset + i + 1)),
                    ft.DataCell(S_Text(f"{_node['ip']}")),
                    ft.DataCell(S_Text(f"{_node['name']}")),
                    ft.DataCell(
                        ft.Column([
                            ft.Text(f"{_node['heap.current']}/{_node['heap.max']}={_node['heap.percent']}%",
                                    size=12),
                            ft.ProgressBar(value=float(_node['heap.percent']) / 100.0,
                                           color="green" if float(_node['heap.percent']) < 70 else "amber" if float(
                                               _node['heap.percent']) < 80 else "red")
                        ], alignment=ft.MainAxisAlignment.CENTER), data=float(_node['heap.percent'])),
                    ft.DataCell(
                        ft.Column([
                            ft.Text(f"{_node['ram.current']}/{_node['ram.max']}={_node['ram.percent']}%", size=12),
                            ft.ProgressBar(value=float(_node['ram.percent']) / 100.0,
                                           color="green" if float(_node['ram.percent']) < 70 else "amber" if float(
                                               _node['ram.percent']) < 80 else "red", )
                        ], alignment=ft.MainAxisAlignment.CENTER)),
                    ft.DataCell(
                        ft.Column([
                            ft.Text(f"{_node['disk.used']}/{_node['disk.total']}={_node['disk.used_percent']}%",
                                    size=12),
                            ft.ProgressBar(value=float(_node['disk.used_percent']) / 100.0, color="green" if float(
                                _node['disk.used_percent']) < 70 else "amber" if float(
                                _node['disk.used_percent']) < 80 else "red", )
                        ], alignment=ft.MainAxisAlignment.CENTER)),
                    ft.DataCell(S_Text(f"{_node['node.role']}", tooltip=self.translate_node_roles(_node['node.role']))),
                    ft.DataCell(S_Text(f"{_node['master']}")),
                    ft.DataCell(S_Text(f"{_node['cpu']}%")),
                    ft.DataCell(S_Text(f"{_node['load_5m']}")),
                    ft.DataCell(S_Text(
                        f"{_node['fielddataMemory']}/{_node['queryCacheMemory']}/{_node['requestCacheMemory']}/{_node['segmentsMemory']}")),
                    ft.DataCell(S_Text(f"{_node['segments.count']}")),
                ]
            )
            return row

        self.cluster_table = PageTable(
            page=common_page.page,
            data_lst=self.nodes,
            data_lst_tmp=self.nodes_tmp,
            columns=[
                ft.DataColumn(S_Text("序号")),
                ft.DataColumn(S_Text("ip")),
                ft.DataColumn(S_Text("name")),
                ft.DataColumn(ft.Row([S_Text("堆使用率"), ft.Icon(
                    ft.icons.KEYBOARD_ARROW_DOWN if self.reverse.get(3) else ft.icons.KEYBOARD_ARROW_UP)]),
                              on_sort=self.on_sort),
                ft.DataColumn(ft.Row([S_Text("内存使用率"), ft.Icon(
                    ft.icons.KEYBOARD_ARROW_DOWN if self.reverse.get(4) else ft.icons.KEYBOARD_ARROW_UP)]),
                              on_sort=self.on_sort),
                ft.DataColumn(ft.Row([S_Text("磁盘使用率"), ft.Icon(
                    ft.icons.KEYBOARD_ARROW_DOWN if self.reverse.get(5) else ft.icons.KEYBOARD_ARROW_UP)]),
                              on_sort=self.on_sort),
                ft.DataColumn(S_Text("角色")),
                ft.DataColumn(S_Text("主节点")),
                ft.DataColumn(ft.Row([S_Text("cpu"), ft.Icon(
                    ft.icons.KEYBOARD_ARROW_DOWN if self.reverse.get(8) else ft.icons.KEYBOARD_ARROW_UP)]),
                              on_sort=self.on_sort),
                ft.DataColumn(ft.Row([S_Text("5m负载"), ft.Icon(
                    ft.icons.KEYBOARD_ARROW_DOWN if self.reverse.get(9) else ft.icons.KEYBOARD_ARROW_UP)]),
                              on_sort=self.on_sort),
                ft.DataColumn(ft.Row([S_Text("字段/查询/请求/段内存")])),
                ft.DataColumn(ft.Row([S_Text("段总数"), ft.Icon(
                    ft.icons.KEYBOARD_ARROW_DOWN if self.reverse.get(11) else ft.icons.KEYBOARD_ARROW_UP)]),
                              on_sort=self.on_sort),

            ],
            row_func=cluster_table_row_func,
            column_spacing=20,
            expand=True
        )

        self.node_tab.content = build_tab_container(
            col_controls=[

                ft.Row([
                    self.cluster_table,
                ]),
                self.cluster_table.page_controls
            ]
        )

        def task_table_row_func(i, offset, task):
            row = ft.DataRow(
                cells=[
                    ft.DataCell(S_Text(f"{task['task_id']}", size=12)),
                    ft.DataCell(S_Text(f"{task['node_name']}")),
                    # ft.DataCell(S_Text(f"{task['node_ip']}")),
                    ft.DataCell(S_Text(f"{task['type']}")),
                    ft.DataCell(S_Text(f"{task['action']}")),
                    ft.DataCell(S_Text(
                        f"{datetime.datetime.fromtimestamp(task['start_time_in_millis'] / 1000).strftime('%Y-%m-%d %H:%M:%S') if task['start_time_in_millis'] else ''}")),
                    ft.DataCell(S_Text(f"{int(task['running_time_in_nanos'] / 1000000000)}", size=12)),
                    # ft.DataCell(S_Text(f"{task['cancellable']}")),
                    ft.DataCell(S_Text(f"{task['parent_task_id']}", size=12)),
                    ft.DataCell(S_Button(text="取消任务", on_click=self.cancel_task, data=task['task_id'])),
                ]
            )
            return row

        self.task_table = PageTable(
            page=common_page.page,
            data_lst=self.task_data_lst,
            data_lst_tmp=self.task_data_lst_tmp,
            columns=[
                ft.DataColumn(S_Text("task_id")),
                ft.DataColumn(S_Text("node")),
                # ft.DataColumn(S_Text("node_ip")),
                ft.DataColumn(S_Text("type")),
                ft.DataColumn(S_Text("action")),
                ft.DataColumn(S_Text("任务开始时间")),
                ft.DataColumn(S_Text("运行时间(s)")),
                # ft.DataColumn(S_Text("是否可取消")),
                ft.DataColumn(S_Text("父任务")),
                ft.DataColumn(S_Text("")),

            ],
            row_func=task_table_row_func,
            column_spacing=20,
            expand=True
        )

        self.task_tab.content = build_tab_container(
            col_controls=[
                ft.Row([
                    self.get_task_button,
                ]),
                ft.Row([
                    self.task_table,
                ]),
                self.task_table.page_controls

            ]
        )

    def page_prev(self, e: ControlEvent):

        # page
        if self.page_num == 1:
            return
        self.page_num -= 1

        offset = (self.page_num - 1) * self.page_size
        self.nodes_tmp = self.nodes[offset:offset + self.page_size]

        self.init_table()
        e.page.update()

    def page_next(self, e):
        # page
        # 最后一页则return
        if self.page_num * self.page_size >= len(self.nodes):
            return
        self.page_num += 1
        offset = (self.page_num - 1) * self.page_size
        self.nodes_tmp = self.nodes[offset:offset + self.page_size]

        self.init_table()
        e.page.update()

    def page_size_change(self, e):
        # page
        self.page_size = int(e.control.value)
        self.nodes_tmp = self.nodes[:self.page_size]

        self.init_table()
        e.page.update()

    def on_sort(self, e: DataColumnSortEvent):
        """
        排序
        """
        # order
        # 反转true false
        if e.column_index in self.reverse:
            reverse = not self.reverse[e.column_index]
            self.reverse[e.column_index] = reverse
        else:
            self.reverse[e.column_index] = True
            reverse = True

        key = {
            3: lambda x: float(x['heap.percent'] if x['heap.percent'] is not None else 0),  # 堆
            4: lambda x: float(x['ram.percent'] if x['ram.percent'] is not None else 0),  # 内存
            5: lambda x: float(x['disk.used_percent'] if x['disk.used_percent'] is not None else 0),  # 磁盘
            8: lambda x: float(x['cpu'] if x['cpu'] is not None else 0),  # cpu
            9: lambda x: float(x['load_5m'] if x['load_5m'] is not None else 0),  # 负载
            11: lambda x: float(x['segments.count'] if x['segments.count'] is not None else 0),  # 段总数
        }[e.column_index]

        self.nodes = sorted(self.nodes, key=key, reverse=reverse)
        self.nodes_tmp = self.nodes[:self.page_size]
        self.init_table()
        e.page.update()

    def translate_node_roles(self, roles):
        # 定义角色映射
        role_mapping = {
            'm': '主节点（master-eligible）',
            'd': '数据节点（data）',
            'i': '预处理节点（ingest）',
            'c': '协调节点（coordinating）',
            'l': '机器学习节点（ml）',
            'v': '仅投票节点（voting-only）',
            'r': '远程集群客户端（remote-cluster-client）',
            's': '转换节点（transform）',
            't': '数据流节点（data_streams）'
        }

        # 将角色字符串拆分为单个字符
        role_list = list(roles)

        # 将角色翻译为中文
        translated_roles = [role_mapping.get(role, role) for role in role_list if role in role_mapping]

        # 用逗号连接翻译后的角色
        return '，'.join(translated_roles)

    def get_task(self, e):
        progress_bar.visible = True
        progress_bar.update()

        success, self.task_data_lst = es_service.get_tasks()
        if success:
            self.task_data_lst_tmp = self.task_data_lst[:self.task_table.page_size]

            self.init_table()
        else:
            open_snack_bar(e.page, self.task_data_lst, success=False)
        progress_bar.visible = False
        e.page.update()

    def cancel_task(self, e):
        progress_bar.visible = True
        progress_bar.update()

        task_id = e.control.data
        success, task_data_lst = es_service.cancel_tasks(task_id)
        open_snack_bar(e.page, "任务已取消", success=False)

        progress_bar.visible = False
        progress_bar.update()
