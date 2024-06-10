#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json

import flet as ft
from flet_core import ControlEvent, DataColumnSortEvent

from service.common import S_Text, open_snack_bar, S_Button, close_dlg, progress_bar, build_tab_container, human_size, \
    build_alert
from service.es_service import es_service
from service.markdown_custom import Markdown


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
        self.reverse = {}
        self.cluster_table_rows = []
        self.indexes = []
        self.indexes_table = None

        self.create_index_button = ft.TextButton("新建索引", on_click=self.create_index, icon=ft.icons.ADD,
                                                 style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=8)))
        self.search_text = ft.TextField(value='*', label=' 检索索引名及别名，支持通配符*。按回车搜索。', label_style=ft.TextStyle(size=14),
                                        on_submit=self.search_table, width=300,
                                        height=38, text_size=14, content_padding=5, autofocus=True, autocorrect=True)

        self.index_tab = ft.Tab(
            text='集群索引列表', content=ft.Column(), icon=ft.icons.HIVE_OUTLINED,
        )

        self.tab = ft.Tabs(
            tabs=[
                self.index_tab,
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

        name_lst = []
        for i, _index in enumerate(self.indexes_tmp):
            name_lst.append(_index['index'])
        alias = es_service.get_index_aliases(name_lst)
        self.cluster_table_rows = []
        for i, _index in enumerate(self.indexes_tmp):
            self.cluster_table_rows.append(
                ft.DataRow(
                    cells=[
                        ft.DataCell(S_Text(offset + i + 1)),
                        ft.DataCell(S_Text(f"{_index['index']}", data=_index['index'])),
                        ft.DataCell(
                            S_Text(f"{alias.get(_index['index'], '')}", data=_index['index'], num=6)),
                        ft.DataCell(S_Text(f"{_index['health'] if _index['health'] is not None else ''}",
                                           color=_index['health'] if _index['health'] != "yellow" else "amber")),
                        ft.DataCell(S_Text(f"{_index['status'] if _index['status'] is not None else ''}",
                                           color="green" if _index['status'] == "open" else "red")),
                        ft.DataCell(S_Text(f"{_index['pri']}/{_index['rep']}")),
                        ft.DataCell(S_Text(f"{_index['docs.count'] if _index['docs.count'] is not None else ''}")),
                        ft.DataCell(S_Text(f"{_index['docs.deleted'] if _index['docs.deleted'] is not None else ''}")),
                        ft.DataCell(S_Text(
                            f"{human_size(int(_index['store.size'])) if _index['store.size'] is not None else ''}")),
                        ft.DataCell(
                            ft.MenuBar(
                                style=ft.MenuStyle(
                                    alignment=ft.alignment.top_left,
                                ),
                                controls=[
                                    ft.SubmenuButton(
                                        content=ft.Text("操作"),
                                        height=40,
                                        leading=ft.Icon(ft.icons.MORE_VERT),
                                        controls=[
                                            ft.MenuItemButton(
                                                data=_index['index'],
                                                content=ft.Text("索引详情"),
                                                leading=ft.Icon(ft.icons.DETAILS),
                                                on_click=self.view_index_detail,
                                            ),
                                            ft.MenuItemButton(
                                                data=_index['index'],
                                                content=ft.Text("索引别名"),
                                                leading=ft.Icon(ft.icons.LABEL),
                                                on_click=self.get_label,
                                            ),
                                            ft.MenuItemButton(
                                                data=_index['index'],
                                                content=ft.Text("查看10条文档"),
                                                leading=ft.Icon(ft.icons.BOOK),
                                                on_click=self.get_doc_10
                                            ),
                                            ft.MenuItemButton(
                                                data=_index['index'],
                                                content=ft.Text("段合并"),
                                                leading=ft.Icon(ft.icons.MERGE_TYPE),
                                                on_click=self.merge_segments,
                                            ),
                                            ft.MenuItemButton(
                                                data=_index['index'],
                                                content=ft.Text("删除索引"),
                                                leading=ft.Icon(ft.icons.DELETE),
                                                on_click=self.delete_index,
                                            ),
                                            ft.MenuItemButton(
                                                data=_index['index'],
                                                content=ft.Text("关闭索引" if _index['status'] == "open" else "打开"),
                                                leading=ft.Icon(
                                                    ft.icons.CLOSE if _index[
                                                                          'status'] == "open" else ft.icons.OPEN_WITH),
                                                on_click=self.close_index if _index[
                                                                                 'status'] == "open" else self.open_index
                                            ),
                                            ft.MenuItemButton(
                                                data=_index['index'],
                                                content=ft.Text("refresh"),
                                                leading=ft.Icon(ft.icons.REFRESH),
                                                on_click=self.refresh
                                            ),
                                            ft.MenuItemButton(
                                                data=_index['index'],
                                                content=ft.Text("flush"),
                                                leading=ft.Icon(ft.icons.DOWNLOAD),
                                                on_click=self.flush
                                            ),
                                            ft.MenuItemButton(
                                                data=_index['index'],
                                                content=ft.Text("清理缓存"),
                                                leading=ft.Icon(ft.icons.DELETE_SWEEP_OUTLINED),
                                                on_click=self.cache_clear
                                            ),
                                        ]
                                    ),
                                ]
                            )
                        ),
                    ]
                )  # page
            )


    def init_table(self):
        if not es_service.connect_obj:
            return "请先选择一个可用的ES连接！\nPlease select an available ES connection first!"

        self.indexes_table = ft.DataTable(
            columns=[
                ft.DataColumn(S_Text("序号")),
                ft.DataColumn(ft.Row([S_Text("索引名"),ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN if self.reverse.get(1) else ft.icons.KEYBOARD_ARROW_UP)]), on_sort=self.on_sort),
                ft.DataColumn(ft.Row([S_Text("别名")])),
                ft.DataColumn(ft.Row([S_Text("健康状态"),ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN if self.reverse.get(3) else ft.icons.KEYBOARD_ARROW_UP)]), on_sort=self.on_sort),
                ft.DataColumn(ft.Row([S_Text("状态"),ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN if self.reverse.get(4) else ft.icons.KEYBOARD_ARROW_UP)]), on_sort=self.on_sort),
                ft.DataColumn(ft.Row([S_Text("主分片/副本"),ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN if self.reverse.get(5) else ft.icons.KEYBOARD_ARROW_UP)]), on_sort=self.on_sort),
                ft.DataColumn(ft.Row([S_Text("文档总数"),ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN if self.reverse.get(6) else ft.icons.KEYBOARD_ARROW_UP)]), on_sort=self.on_sort),
                ft.DataColumn(ft.Row([S_Text("未清除的删除文档"),ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN if self.reverse.get(7) else ft.icons.KEYBOARD_ARROW_UP)]), on_sort=self.on_sort),
                ft.DataColumn(ft.Row([S_Text("占用存储（主+副）"),ft.Icon(ft.icons.KEYBOARD_ARROW_DOWN if self.reverse.get(8) else ft.icons.KEYBOARD_ARROW_UP)]), on_sort=self.on_sort),
                ft.DataColumn(S_Text("")),

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

    def on_sort(self, e: DataColumnSortEvent):
        """
        排序
        """
        # order
        # 反转true false
        progress_bar.visible = True
        e.page.update()

        if e.column_index in self.reverse:
            reverse = not self.reverse[e.column_index]
            self.reverse[e.column_index] = reverse
        else:
            self.reverse[e.column_index] = True
            reverse = True
        key = {
            1: lambda x: str(x['index']),  # 索引名
            3: lambda x: str(x['health']),  # 健康
            4: lambda x: str(x['status']),  # status
            5: lambda x: int(x['pri'] if x['pri'] is not None else 0),  # status
            6: lambda x: int(x['docs.count'] if x['docs.count'] is not None else 0),  # status
            7: lambda x: int(x['docs.deleted'] if x['docs.deleted'] is not None else 0),  # status
            8: lambda x: float(x['store.size'] if x['store.size'] is not None else 0),  # status
        }[e.column_index]

        self.indexes = sorted(self.indexes, key=key, reverse=reverse)
        self.indexes_tmp = self.indexes[:self.page_size]
        self.init_rows()
        self.init_table()

        progress_bar.visible = False
        e.page.update()

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

            res, err = es_service.create_index(input_name.value, int(input_primary_shard.value),
                                               int(input_replica_shard.value))
            if err is not None:
                open_snack_bar(e.page, err, success=False)
                return
            open_snack_bar(e.page, "创建成功！", success=True)
            close_dlg(e)
            e.page.update()

        dlg_modal = ft.AlertDialog(
            modal=False,
            title=ft.Text("创建索引"),
            content=ft.Column([
                input_name,
                input_primary_shard,
                input_replica_shard,
            ], height=130),
            actions=[
                ft.TextButton("确认", on_click=ensure),
            ],
            # actions_alignment=ft.MainAxisAlignment.START,
        )
        e.page.dialog = dlg_modal
        dlg_modal.open = True
        e.page.update()

    def view_index_detail(self, e):
        """
        索引详情
        """
        success, res = es_service.get_index_info(e.control.data)
        if not success:
            open_snack_bar(e.page, res, success=False)
            return
        dlg_modal = ft.AlertDialog(
            modal=False,
            title=ft.Text(e.control.data),
            actions=[
                ft.Row(
                    controls=[
                        ft.Column(
                            [
                                ft.Column(
                                    [
                                        Markdown(
                                            f"""
```json
{json.dumps(res, ensure_ascii=False, indent=4)}
```
                                            """,
                                        )

                                    ],
                                    scroll=ft.ScrollMode.ALWAYS,
                                    height=600,
                                    width=600,
                                ),
                            ],
                            scroll=ft.ScrollMode.ALWAYS,
                        )],
                    scroll=ft.ScrollMode.ALWAYS,

                )

            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            shape=ft.RoundedRectangleBorder(radius=8),
            open=True,
        )
        e.page.dialog = dlg_modal
        dlg_modal.open = True
        e.page.update()

    def delete_index(self, e):
        progress_bar.visible = True
        e.page.update()

        success, res = es_service.delete_index(e.control.data)
        progress_bar.visible = False
        e.page.update()
        if not success:
            open_snack_bar(e.page, res, success=False)
        else:
            open_snack_bar(e.page, "删除成功", success=True)

    def open_index(self, e):
        progress_bar.visible = True
        e.page.update()

        success, res = es_service.open_close_index(e.control.data, now="close")
        progress_bar.visible = False
        e.page.update()
        if not success:
            open_snack_bar(e.page, res, success=False)
        else:
            open_snack_bar(e.page, "打开成功", success=True)

    def close_index(self, e):
        progress_bar.visible = True
        e.page.update()
        success, res = es_service.open_close_index(e.control.data, now="open")
        progress_bar.visible = False
        e.page.update()
        if not success:
            open_snack_bar(e.page, res, success=False)
        else:
            open_snack_bar(e.page, "关闭成功", success=True)

    def merge_segments(self, e):
        progress_bar.visible = True
        e.page.update()
        success, res = es_service.merge_segments(e.control.data)
        print(res)
        progress_bar.visible = False
        e.page.update()
        if not success:
            open_snack_bar(e.page, res, success=False)
        else:
            open_snack_bar(e.page, f"已提交后台合并请求：{res}", success=True)

    def refresh(self, e):
        progress_bar.visible = True
        e.page.update()
        success, res = es_service.refresh(e.control.data)
        print(res)
        progress_bar.visible = False
        e.page.update()
        if not success:
            open_snack_bar(e.page, res, success=False)
        else:
            open_snack_bar(e.page, f"refresh成功：{res}", success=True)

    def flush(self, e):
        progress_bar.visible = True
        e.page.update()
        success, res = es_service.flush(e.control.data)
        print(res)
        progress_bar.visible = False
        e.page.update()
        if not success:
            open_snack_bar(e.page, res, success=False)
        else:
            open_snack_bar(e.page, f"flush成功：{res}", success=True)

    def cache_clear(self, e):
        progress_bar.visible = True
        e.page.update()
        success, res = es_service.cache_clear(e.control.data)
        progress_bar.visible = False
        e.page.update()
        if not success:
            open_snack_bar(e.page, res, success=False)
        else:
            open_snack_bar(e.page, f"缓存清理成功：{res}", success=True)

    def get_doc_10(self, e):
        progress_bar.visible = True
        e.page.update()
        success, res = es_service.get_doc_10(e.control.data)
        progress_bar.visible = False
        e.page.update()
        if not success:
            open_snack_bar(e.page, res, success=False)
            return

        dlg_modal = ft.AlertDialog(
            modal=False,
            title=ft.Text(e.control.data),
            actions=[
                ft.Row(
                    controls=[
                        ft.Column(
                            [
                                ft.Column(
                                    [
                                        Markdown(
                                            f"""
```json
{json.dumps(res, ensure_ascii=False, indent=4)}
```
""",
                                        )
                                    ],
                                    scroll=ft.ScrollMode.ALWAYS,
                                    height=600,
                                    width=600,
                                ),

                            ],
                            scroll=ft.ScrollMode.ALWAYS,
                        )],
                    scroll=ft.ScrollMode.ALWAYS,

                )

            ],
            actions_alignment=ft.MainAxisAlignment.CENTER,
            shape=ft.RoundedRectangleBorder(radius=8),
            open=True,
        )
        e.page.dialog = dlg_modal
        dlg_modal.open = True
        e.page.update()

    def get_label(self, e):
        alias = es_service.get_index_aliases(e.control.data)
        alert = build_alert(e.page, e.control.data + "别名", ft.Column([
                ft.Text(alias, selectable=True),
            ], height=130))

        e.page.dialog = alert
        alert.open = True
        e.page.update()
