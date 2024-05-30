#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json

import flet as ft
from flet_core import ControlEvent, DataColumnSortEvent

from service.common import S_Text, build_tab_container, human_size, common_page, Navigation
from service.es_service import es_service


class Info(object):
    """
    """

    def __init__(self):
        self.stats = None
        self.health = None

        # 先加载框架
        self.health_tab = ft.Tab(
            text="集群健康", content=ft.Column(), icon=ft.icons.INFO_OUTLINE
        )

        self.tab = ft.Tabs(
            tabs=[
                self.health_tab,
            ],
            expand=True,
        )

        self.controls = [
            self.tab
        ]

    def init(self, page=None):
        self.init_data()
        self.init_table()

    def init_data(self):
        self.health = es_service.get_health()

    def init_table(self):
        if not es_service.connect_obj:
            return "请先选择一个可用的ES连接！\nPlease select an available ES connection first!"

        status = self.health['status']
        color = {
            "green": "green",
            "yellow": "amber",
            "red": "red",
        }[status]

        # 设置左侧图标的颜色，作为健康度
        Navigation.destinations[0].icon_content.color = color
        Navigation.destinations[0].selected_icon_content.color = color

        self.health_tab.content = build_tab_container(
            col_controls=[
                ft.Row(
                    [
                        ft.Card(ft.DataTable(columns=[
                            ft.DataColumn(S_Text("健康", weight=ft.FontWeight.BOLD)), ft.DataColumn(S_Text("")),
                        ], rows=[
                            ft.DataRow(cells=[ft.DataCell(S_Text("集群名称")),
                                              ft.DataCell(S_Text(f"{self.health['cluster_name']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("集群状态")),
                                              ft.DataCell(S_Text(status, color=color))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("集群超时")),
                                              ft.DataCell(S_Text(f"{self.health['timed_out']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("节点总数")),
                                              ft.DataCell(S_Text(f"{self.health['number_of_nodes']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("集群数据节点总数")),
                                              ft.DataCell(S_Text(f"{self.health['number_of_data_nodes']}"))]),

                        ], column_spacing=10, ), ),
                ft.Card(ft.DataTable(columns=[
                    ft.DataColumn(S_Text("分片信息", weight=ft.FontWeight.BOLD)), ft.DataColumn(S_Text("")),
                ], rows=[
                    ft.DataRow(cells=[ft.DataCell(S_Text("活跃的分片总数（主分片和副本分片）")),
                                      ft.DataCell(S_Text(f"{self.health['active_shards']}"))]),
                    ft.DataRow(cells=[ft.DataCell(S_Text("活跃的主分片数量")),
                                      ft.DataCell(S_Text(f"{self.health['active_primary_shards']}"))]),
                    ft.DataRow(cells=[ft.DataCell(S_Text("重新分配中的分片数量（分片移动到另一个节点）")),
                                      ft.DataCell(S_Text(f"{self.health['relocating_shards']}"))]),
                    ft.DataRow(cells=[ft.DataCell(S_Text("初始化中的分片数量（正在被创建但尚未开始服务请求）")),
                                      ft.DataCell(S_Text(f"{self.health['initializing_shards']}"))]),
                    ft.DataRow(cells=[ft.DataCell(S_Text("未分配的分片数量（节点故障或配置问题）")),
                                      ft.DataCell(S_Text(f"{self.health['unassigned_shards']}"))]),
                    ft.DataRow(cells=[ft.DataCell(S_Text("延迟未分配的分片数量（可能因为分配策略等待条件未满足）")),
                                      ft.DataCell(S_Text(f"{self.health['delayed_unassigned_shards']}"))]),
                    ft.DataRow(cells=[ft.DataCell(S_Text("活跃分片占比（可能冻结、关闭、故障等）")),
                                      ft.DataCell(
                                          S_Text(f"{round(self.health['active_shards_percent_as_number'], 2)}%"))]),

                ], column_spacing=10, ), ),
                        ft.Card(ft.DataTable(columns=[
                            ft.DataColumn(S_Text("Task", weight=ft.FontWeight.BOLD)), ft.DataColumn(S_Text("")),
                        ], rows=[

                            ft.DataRow(cells=[ft.DataCell(S_Text("待处理的任务积压数")),
                                              ft.DataCell(S_Text(f"{self.health['number_of_pending_tasks']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("等待执行的任务数量，比如索引操作、设置改变等")),
                                              ft.DataCell(S_Text(f"{self.health['number_of_pending_tasks']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("正在进行的fetch操作数量，通常指查询操作")),
                                              ft.DataCell(S_Text(f"{self.health['number_of_in_flight_fetch']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("任务队列中最长等待时间（毫秒）")),
                                              ft.DataCell(S_Text(f"{self.health['task_max_waiting_in_queue_millis']}"))]),
                        ], column_spacing=10, ), ),
            ],  vertical_alignment=ft.CrossAxisAlignment.START
        ),
                ]
        )
