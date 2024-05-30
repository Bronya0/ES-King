#!/usr/bin/env python
# -*-coding:utf-8 -*-
from typing import Optional, Dict

import flet as ft
from flet_core import ControlEvent

from service.common import S_Text, open_snack_bar, S_Button, dd_common_configs, close_dlg, view_instance_map, \
    Navigation, body, progress_bar, common_page, build_tab_container
from service.es_service import es_service


class Index(object):
    """
    """

    def __init__(self):
        # page
        self.indexes_tmp = []
        self.page_num = 1
        self.page_size = 10
        self.page_label = None
        # order
        self.reverse = None
        self.cluster_table_rows = None
        self.indexes = []
        self.indexes_table = None

        self.create_index_button = ft.TextButton("新建索引", on_click=self.create_index, icon=ft.icons.ADD,
                                                 style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
        self.search_text = ft.TextField(label=' 检索索引名及别名，支持通配符*',label_style=ft.TextStyle(size=14),
                                        on_submit=self.search_table, width=300,
                                        height=38, text_size=14, content_padding=5)

        self.index_tab = ft.Tab(
            text='集群索引列表', content=ft.Column(), icon=ft.icons.HIVE_OUTLINED,
        )

        self.tab = ft.Tabs(
            tabs=[
                self.index_tab,
            ],
            expand=True,
        )

        self.controls = [
            self.tab
        ]

    def init(self, page=None):
        # self.init_data()
        # self.init_rows()
        self.init_table()

    def init_data(self):
        self.indexes = es_service.get_indexes()
        # page
        # 只在最开始、排序时执行一次
        self.indexes_tmp = self.indexes[:self.page_size]

    def init_rows(self):
        # page
        offset = (self.page_num - 1) * self.page_size

        self.cluster_table_rows = [
            ft.DataRow(
                cells=[
                    ft.DataCell(S_Text(offset + i + 1)),
                    ft.DataCell(S_Text(f"{_index['index'] if _index['index'] is not None else ''}", color='primary')),
                    ft.DataCell(S_Text(f"{_index['health'] if _index['health'] is not None else ''}", color=_index['health'] if _index['health'] !="yellow" else "amber")),
                    ft.DataCell(S_Text(f"{_index['status'] if _index['status'] is not None else ''}")),
                    ft.DataCell(S_Text(f"{_index['pri']}主{_index['rep']}副本")),
                    ft.DataCell(S_Text(f"{_index['docs.count'] if _index['docs.count'] is not None else ''}")),
                    ft.DataCell(S_Text(f"{_index['docs.deleted'] if _index['docs.deleted'] is not None else ''}")),
                    ft.DataCell(S_Text(f"{_index['store.size'] if _index['store.size'] is not None else ''}")),
                ]
            ) for i, _index in enumerate(self.indexes_tmp)  # page
        ]

    def init_table(self):
        if not es_service.connect_obj:
            return "请先选择一个可用的ES连接！\nPlease select an available ES connection first!"

        self.indexes_table = ft.DataTable(
            columns=[
                ft.DataColumn(S_Text("序号")),
                ft.DataColumn(S_Text("索引名")),
                ft.DataColumn(S_Text("健康状态")),
                ft.DataColumn(S_Text("状态")),
                ft.DataColumn(S_Text("主分片及副本")),
                ft.DataColumn(S_Text("文档总数")),
                ft.DataColumn(S_Text("未清除的删除文档")),
                ft.DataColumn(S_Text("占用存储（主+副）")),

            ],
            rows=self.cluster_table_rows,
            column_spacing=20,
            expand=True
        )

        self.index_tab.content = build_tab_container(
            col_controls=[
                ft.Row([
                    self.search_text,
                    self.create_index_button,
                ]),
                ft.Row([
                    self.indexes_table,
                ]),
                # page
                ft.Row(
                    [
                        # 翻页图标和当前页显示
                        ft.IconButton(
                            icon=ft.icons.ARROW_BACK,
                            icon_size=20,
                            on_click=self.page_prev,
                            tooltip="上一页",
                        ),
                        ft.Text(f"{self.page_num}/{int(len(self.indexes) / self.page_size) + 1}"),
                        ft.IconButton(
                            icon=ft.icons.ARROW_FORWARD,
                            icon_size=20,
                            on_click=self.page_next,
                            tooltip="下一页",
                        ),
                        ft.Text(f"每页{self.page_size}条"),
                        ft.Slider(min=5, max=55, divisions=10, round=1, value=self.page_size, label="{value}",
                                  on_change_end=self.page_size_change),

                    ]
                )
            ]
        )

    def page_prev(self, e):
        # page
        if self.page_num == 1:
            return
        self.page_num -= 1

        offset = (self.page_num - 1) * self.page_size
        self.indexes_tmp = self.indexes[offset:offset + self.page_size]

        self.init_rows()
        self.init_table()
        e.page.update()

    def page_next(self, e):
        # page
        # 最后一页则return
        if self.page_num * self.page_size >= len(self.indexes):
            return
        self.page_num += 1
        offset = (self.page_num - 1) * self.page_size
        self.indexes_tmp = self.indexes[offset:offset + self.page_size]

        self.init_rows()
        self.init_table()
        e.page.update()

    def page_size_change(self, e):
        # page
        self.page_size = int(e.control.value)
        self.indexes_tmp = self.indexes[:self.page_size]

        self.init_rows()
        self.init_table()
        e.page.update()

    def search_table(self, e: ControlEvent):
        """
        搜索，配合分页
        :param e:
        :return:
        """
        progress_bar.visible = True
        e.page.update()
        try:
            indexes = es_service.get_indexes(e.control.value)
            self.search_table_handle(indexes)
        except:
            pass
        progress_bar.visible = False
        e.page.update()

    def search_table_handle(self, indexes):
        self.page_num = 1
        self.indexes = indexes
        self.indexes_tmp = indexes[:self.page_size]
        self.init_rows()
        self.init_table()

    def create_index(self, e):
        input_name = ft.TextField(label="索引名", hint_text="例如：test_index", height=40, content_padding=5)
        input_primary_shard = ft.TextField(label="主分片数", hint_text="例如：1", height=40, content_padding=5)
        input_replica_shard = ft.TextField(label="副本数", hint_text="例如：1", height=40, content_padding=5)

        def ensure(e):
            if input_name.value is None:
                open_snack_bar(e.page, "索引名填写错误！", success=False)
                return
            if input_primary_shard.value is None or int(input_primary_shard.value) < 0:
                open_snack_bar(e.page, "主分片数填写错误！", success=False)
                return
            if input_replica_shard.value is None or int(input_replica_shard.value) < 0:
                open_snack_bar(e.page, "副本数填写错误！", success=False)
                return

            res, err = es_service.create_index(input_name.value, int(input_primary_shard.value), int(input_replica_shard.value))
            if err is not None:
                open_snack_bar(e.page, err, success=False)
                return
            open_snack_bar(e.page, "创建成功！", success=True)
            close_dlg(e)
            e.page.update()

        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("创建索引"),
            content=ft.Column([
                input_name,
                input_primary_shard,
                input_replica_shard,
            ], height=130),
            actions=[
                    ft.TextButton("确认", on_click=ensure),
                    ft.TextButton("取消", on_click=close_dlg),
            ],
            # actions_alignment=ft.MainAxisAlignment.START,
        )
        e.page.dialog = dlg_modal
        dlg_modal.open = True
        e.page.update()
