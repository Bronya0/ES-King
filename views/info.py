#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json

import flet as ft
from flet_core import ControlEvent, DataColumnSortEvent

from service.common import S_Text, build_tab_container, human_size
from service.es_service import es_service


class Info(object):
    """
    """

    def __init__(self):
        self.stats = None

        # 先加载框架
        self.stats_tab = ft.Tab(
            text="基础信息", content=ft.Column(), icon=ft.icons.INFO_OUTLINE
        )

        self.tab = ft.Tabs(
            tabs=[
                self.stats_tab,
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
        self.stats = es_service.get_stats()

    def init_table(self):
        if not es_service.connect_obj:
            return "请先选择一个可用的ES连接！\nPlease select an available ES connection first!"

        stats_nodes = self.stats['nodes']

        # card集群基本信息
        stats_indices = self.stats['indices']
        self.stats_tab.content = build_tab_container(
            col_controls=[

                ft.Row(
                    [
                        ft.Card(ft.DataTable(columns=[
                            ft.DataColumn(S_Text("节点", weight=ft.FontWeight.BOLD)), ft.DataColumn(S_Text("")),
                        ], rows=[
                            ft.DataRow(cells=[ft.DataCell(S_Text("节点总数")), ft.DataCell(S_Text(f"{stats_nodes['count']['total']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("协调节点数")), ft.DataCell(S_Text(f"{stats_nodes['count']['coordinating_only']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("存储节点数")), ft.DataCell(S_Text(f"{stats_nodes['count']['data']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("可写节点数")), ft.DataCell(S_Text(f"{stats_nodes['count']['ingest']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("允许主节点数")), ft.DataCell(S_Text(f"{stats_nodes['count']['master']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("仅投票节点数")), ft.DataCell(S_Text(f"{stats_nodes['count']['voting_only']}"))]),
                        ], column_spacing=10,),),
                        ft.Card(ft.DataTable(columns=[
                            ft.DataColumn(S_Text("索引、分片", weight=ft.FontWeight.BOLD)), ft.DataColumn(S_Text("")),
                        ], rows=[
                            ft.DataRow(
                                cells=[ft.DataCell(S_Text("索引总数")),
                                       ft.DataCell(S_Text(f"{stats_indices['count']}")),
                                       ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("分片总数")), ft.DataCell(S_Text(f"{stats_indices['shards']['total']}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("主分片总数")), ft.DataCell(S_Text(f"{stats_indices['shards']['primaries']}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("平均副本数")), ft.DataCell(S_Text(f"{round(stats_indices['shards']['replication'],1)}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("最大索引分片数")), ft.DataCell(S_Text(f"{stats_indices['shards']['index']['shards']['max']}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("最大索引主分片数")), ft.DataCell(S_Text(f"{stats_indices['shards']['index']['primaries']['max']}")), ]),
                        ], column_spacing=10,)),
                        ft.Card(ft.DataTable(columns=[
                            ft.DataColumn(S_Text("文档、存储、缓存", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(S_Text("")),
                        ], rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(S_Text("文档总数")), ft.DataCell(ft.Text(f"{str(stats_indices['docs']['count'])[:6]}...", tooltip=f"{stats_indices['docs']['count']}",selectable=True)),
                                ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("已删除文档数")), ft.DataCell(ft.Text(f"{str(stats_indices['docs']['deleted'])[:6]}...", tooltip=f"{stats_indices['docs']['deleted']}",selectable=True))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("存储大小")), ft.DataCell(S_Text(f"{human_size(stats_indices['store']['size_in_bytes'])}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("字段结构内存")), ft.DataCell(
                                S_Text(f"{human_size(stats_indices['fielddata']['memory_size_in_bytes'])}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("查询缓存")), ft.DataCell(
                                S_Text(f"{human_size(stats_indices['query_cache']['memory_size_in_bytes'])}")), ])
                        ], column_spacing=10,)),

                        ft.Card(ft.DataTable(columns=[
                            ft.DataColumn(S_Text("段", weight=ft.FontWeight.BOLD)), ft.DataColumn(S_Text("")),
                        ], rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(S_Text("段总数")),
                                    ft.DataCell(S_Text(f"{stats_indices['segments']['count']}")),

                                ]),
                            ft.DataRow([ft.DataCell(S_Text("段总占用内存")), ft.DataCell(
                                S_Text(f"{human_size(stats_indices['segments']['memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("terms词项内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['terms_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("存储字段内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['stored_fields_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("向量内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['term_vectors_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("norms归一化因子内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['term_vectors_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("数值型和地理坐标等点类型内存")), ft.DataCell(
                                S_Text(
                                    f"{human_size(stats_indices['segments']['points_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("Doc Values内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['doc_values_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("索引写入占用内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['index_writer_memory_in_bytes'])}"))]),
                            ft.DataRow([ft.DataCell(S_Text("固定位集合内存")), ft.DataCell(S_Text(
                                f"{human_size(stats_indices['segments']['fixed_bit_set_memory_in_bytes'])}"))]),
                        ], column_spacing=10,)),

                        ft.Card(ft.DataTable(columns=[
                            ft.DataColumn(S_Text("集群系统", weight=ft.FontWeight.BOLD)), ft.DataColumn(S_Text("")),
                        ], rows=[
                            ft.DataRow(cells=[ft.DataCell(S_Text("可用CPU核心数")), ft.DataCell(S_Text(f"{stats_nodes['os']['available_processors']}")),]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("分配给ES进程使用的CPU核心数")), ft.DataCell(S_Text(f"{stats_nodes['os']['allocated_processors']}")),]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("操作系统及总数")), ft.DataCell(ft.Text(value=json.dumps(f"{stats_nodes['os']['pretty_names']}")[:10]+"...",tooltip=json.dumps(f"{stats_nodes['os']['pretty_names']}"))),]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("总内存")), ft.DataCell(S_Text(f"{human_size(stats_nodes['os']['mem']['total_in_bytes'])}")),]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("已使用内存")), ft.DataCell(S_Text(f"{human_size(stats_nodes['os']['mem']['used_in_bytes'])}")),]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("已使用内存百分比")), ft.DataCell(S_Text(f"{stats_nodes['os']['mem']['used_percent']}%")),]),

                        ], column_spacing=10, )),

                    ], vertical_alignment=ft.CrossAxisAlignment.START
                ),
            ]
        )