#!/usr/bin/env python
# -*-coding:utf-8 -*-

import flet as ft
from flet_core import ControlEvent

from service.common import S_Text, build_tab_container
from service.es_service import es_service


class Broker(object):
    """
    Cluster页的组件
    kafka版本、操作系统、集群信息等等
    """

    def __init__(self):
        self.nodes_table = None
        self.nodes = None
        self.base_info = None
        self.api_version = None
        self.meta = None
        self.cluster_table = None

        # if not kafka_service.kac:
        #     raise Exception("请先选择一个可用的kafka连接！")

        # 先加载框架
        self.base_info_tab = ft.Tab(
            text="基础信息", content=ft.Column(), icon=ft.icons.INFO_OUTLINE
        )

        self.node_tab = ft.Tab(
            text='集群节点列表', content=ft.Column(), icon=ft.icons.HIVE_OUTLINED,
        )

        self.config_tab = ft.Tab(
            text='Broker配置', content=ft.Container(content=ft.Text("请从broker的配置按钮进入", size=20)),
            icon=ft.icons.CONSTRUCTION_OUTLINED,
        )

        self.tab = ft.Tabs(
            tabs=[
                self.node_tab,
                # self.base_info_tab,
                # self.config_tab,
            ],
        )

        self.controls = [
            self.tab
        ]

    def init(self, page=None):
        if not es_service.connect_obj:
            return "请先选择一个可用的ES连接！\nPlease select an available kafka connection first!"

        self.nodes = es_service.get_nodes()
        self.cluster_table = ft.DataTable(
            columns=[
                ft.DataColumn(S_Text("ip")),
                ft.DataColumn(S_Text("name")),
                ft.DataColumn(S_Text("堆使用率")),
                ft.DataColumn(S_Text("内存使用率")),
                ft.DataColumn(S_Text("磁盘使用率")),
                ft.DataColumn(S_Text("角色")),
                ft.DataColumn(S_Text("是否为master")),
                ft.DataColumn(S_Text("cpu")),
                ft.DataColumn(S_Text("5分钟负载")),

            ],
            rows=[
                ft.DataRow(
                    cells=[
                        ft.DataCell(S_Text(f"{_node['ip']}")),
                        ft.DataCell(S_Text(f"{_node['name']}")),
                        ft.DataCell(
                            ft.Column([
                                ft.Text(f"{_node['heap.current']}/{_node['heap.max']}={_node['heap.percent']}%", size=12),
                                ft.ProgressBar(value=float(_node['heap.percent']) / 100.0, color="amber",bgcolor="#eeeeee")
                            ], alignment=ft.MainAxisAlignment.CENTER)),
                        ft.DataCell(
                            ft.Column([
                                ft.Text(f"{_node['ram.current']}/{_node['ram.max']}={_node['ram.percent']}%", size=12),
                                ft.ProgressBar(value=float(_node['ram.percent']) / 100.0, color="amber",
                                               bgcolor="#eeeeee")
                            ], alignment=ft.MainAxisAlignment.CENTER)),
                        ft.DataCell(
                            ft.Column([
                                ft.Text(f"{_node['disk.used']}/{_node['disk.total']}={_node['disk.used_percent']}%",size=12),
                                ft.ProgressBar(value=float(_node['disk.used_percent']) / 100.0, color="amber",
                                               bgcolor="#eeeeee")
                            ], alignment=ft.MainAxisAlignment.CENTER)),
                        ft.DataCell(S_Text(f"{_node['node.role']}")),
                        ft.DataCell(S_Text(f"{_node['master']}")),
                        ft.DataCell(S_Text(f"{_node['cpu']}")),
                        ft.DataCell(S_Text(f"{_node['load_5m']}")),
                    ],
                ) for _node in self.nodes
            ],
            column_spacing=20,
            expand=True
        )

        # self.base_info_tab.content = build_tab_container(
        #     col_controls=[
        #         ft.Row([
        #             self.base_info,
        #         ])
        #     ]
        # )

        self.node_tab.content = build_tab_container(
            col_controls=[
                ft.Row([
                    self.cluster_table,
                ])
            ]
        )

    def show_config_tab(self, e: ControlEvent):
        """
        打开侧边栏
        """
        e.control.disabled = True
        broker_id = e.control.data
        configs = es_service.get_configs(res_type='broker', name=broker_id)

        _col = ft.ListView(expand=True, spacing=10, padding=10)

        for config in configs:
            config_names = f"{config['config_names']}"
            config_value = f"{config['config_value']}" if config['config_value'] is not None else ""
            _col.controls.append(ft.Row([
                ft.Text(f" • {config_names}", style=ft.TextStyle(weight=ft.FontWeight.BOLD), ),
                ft.Text(f"    值：{config_value}"),
            ]))
        self.config_tab.content = _col

        self.tab.selected_index = 2
        e.control.disabled = False
        e.page.update()
