#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json

import flet as ft
from flet_core import ControlEvent, DataColumnSortEvent

from service.common import S_Text, build_tab_container, human_size
from service.es_service import es_service
from service.markdown_custom import Markdown


class Core(object):
    """
    """

    def __init__(self):
        self.settings = {}
        self.stats = None
        self.health = None

        # 先加载框架
        self.stats_tab = ft.Tab(
            text="核心指标", content=ft.Column(), icon=ft.icons.INFO_OUTLINE
        )

        self.settings_tab = ft.Tab(
            text="cluster settings", content=ft.Column(), icon=ft.icons.SETTINGS_OUTLINED
        )

        self.tab = ft.Tabs(
            tabs=[
                self.stats_tab,
                self.settings_tab,
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

        self.stats = es_service.get_stats()
        self.settings = es_service.get_cluster_settings()

    def init_table(self):

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
                            ft.DataRow(cells=[ft.DataCell(S_Text("节点总数")),
                                              ft.DataCell(S_Text(f"{stats_nodes['count']['total']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("协调节点数")),
                                              ft.DataCell(S_Text(f"{stats_nodes['count']['coordinating_only']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("存储节点数")),
                                              ft.DataCell(S_Text(f"{stats_nodes['count']['data']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("可写节点数")),
                                              ft.DataCell(S_Text(f"{stats_nodes['count']['ingest']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("允许主节点数")),
                                              ft.DataCell(S_Text(f"{stats_nodes['count']['master']}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("仅投票节点数")),
                                              ft.DataCell(S_Text(f"{stats_nodes['count']['voting_only']}"))]),
                        ], column_spacing=10, ), ),
                        ft.Card(ft.DataTable(columns=[
                            ft.DataColumn(S_Text("索引、分片", weight=ft.FontWeight.BOLD)), ft.DataColumn(S_Text("")),
                        ], rows=[
                            ft.DataRow(
                                cells=[ft.DataCell(S_Text("索引总数")),
                                       ft.DataCell(S_Text(f"{stats_indices['count']}")),
                                       ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("分片总数")),
                                              ft.DataCell(S_Text(f"{stats_indices['shards']['total']}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("主分片总数")),
                                              ft.DataCell(S_Text(f"{stats_indices['shards']['primaries']}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("平均副本数")), ft.DataCell(
                                S_Text(f"{round(stats_indices['shards']['replication'], 1)}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("最大索引分片数")), ft.DataCell(
                                S_Text(f"{stats_indices['shards']['index']['shards']['max']}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("最大索引主分片数")), ft.DataCell(
                                S_Text(f"{stats_indices['shards']['index']['primaries']['max']}")), ]),
                        ], column_spacing=10, )),
                        ft.Card(ft.DataTable(columns=[
                            ft.DataColumn(S_Text("文档、存储、缓存", weight=ft.FontWeight.BOLD)),
                            ft.DataColumn(S_Text("")),
                        ], rows=[
                            ft.DataRow(
                                cells=[
                                    ft.DataCell(S_Text("文档总数")), ft.DataCell(
                                        ft.Text(f"{str(stats_indices['docs']['count'])[:6]}...",
                                                tooltip=f"{stats_indices['docs']['count']}", selectable=True)),
                                ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("已删除文档数")), ft.DataCell(
                                ft.Text(f"{str(stats_indices['docs']['deleted'])[:6]}...",
                                        tooltip=f"{stats_indices['docs']['deleted']}", selectable=True))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("已使用存储")), ft.DataCell(
                                S_Text(f"{human_size(stats_indices['store']['size_in_bytes'])}"))]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("字段结构内存")), ft.DataCell(
                                S_Text(f"{human_size(stats_indices['fielddata']['memory_size_in_bytes'])}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("查询缓存")), ft.DataCell(
                                S_Text(f"{human_size(stats_indices['query_cache']['memory_size_in_bytes'])}")), ])
                        ], column_spacing=10, )),

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
                        ], column_spacing=10, )),

                        ft.Card(ft.DataTable(columns=[
                            ft.DataColumn(S_Text("集群系统", weight=ft.FontWeight.BOLD)), ft.DataColumn(S_Text("")),
                        ], rows=[
                            ft.DataRow(cells=[ft.DataCell(S_Text("可用CPU核心数")),
                                              ft.DataCell(S_Text(f"{stats_nodes['os']['available_processors']}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("分配给ES进程使用的CPU核心数")),
                                              ft.DataCell(S_Text(f"{stats_nodes['os']['allocated_processors']}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("操作系统及总数")), ft.DataCell(
                                ft.Text(value=json.dumps(f"{stats_nodes['os']['pretty_names']}")[:10] + "...",
                                        tooltip=json.dumps(f"{stats_nodes['os']['pretty_names']}"))), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("总内存")), ft.DataCell(
                                S_Text(f"{human_size(stats_nodes['os']['mem']['total_in_bytes'])}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("已使用内存")), ft.DataCell(
                                S_Text(f"{human_size(stats_nodes['os']['mem']['used_in_bytes'])}")), ]),
                            ft.DataRow(cells=[ft.DataCell(S_Text("已使用内存百分比")),
                                              ft.DataCell(S_Text(f"{stats_nodes['os']['mem']['used_percent']}%")), ]),

                        ], column_spacing=10, )),

                    ], vertical_alignment=ft.CrossAxisAlignment.START
                ),
            ]
        )

        if self.settings:
            # _data = self.flatten_dict(self.settings)
            # print(_data)
            # card集群基本信息
            self.settings_tab.content = build_tab_container(
                col_controls=[
                    ft.Text("集群cluster settings信息"),
                    ft.Row(
                        [
                            ft.Column(
                                [
                                    Markdown(
                                        f"""
```json
{json.dumps(self.settings, ensure_ascii=False, indent=4)}
```
""",
                                    ),

                                ],
                                scroll=ft.ScrollMode.ALWAYS,
                            ),

                        ], vertical_alignment=ft.CrossAxisAlignment.START
                    ),
                ]
            )

    def flatten_dict(self, d, parent_key='', sep='.'):
        """
        将嵌套字典扁平化,用指定的分隔符连接键。

        参数:
        d (dict): 要扁平化的字典,可以是嵌套的也可以是非嵌套的
        parent_key (str): 父级键,用于拼接
        sep (str): 分隔符,默认为'.'

        返回:
        dict: 扁平化后的字典
        """
        print("d", d)
        items = []
        for k, v in d.items():
            new_key = parent_key + sep + k if parent_key else k
            if v and isinstance(v, dict):
                items.extend(self.flatten_dict(v, new_key, sep).items())
            else:
                items.append((new_key, v))
        return dict(items)
