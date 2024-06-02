#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json
import random
import traceback

import flet as ft
from flet_core import Column, Row, TextStyle

from service.common import S_Button, open_snack_bar, build_tab_container, close_dlg, progress_bar
from service.es_service import es_service


class Rest(object):
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

        self.method_groups_dd = ft.Dropdown(
            label="请选择HTTP方法",
            options=[
                ft.dropdown.Option("GET"),
                ft.dropdown.Option("POST"),
                ft.dropdown.Option("PUT"),
                ft.dropdown.Option("DELETE"),
                ft.dropdown.Option("HEAD"),
                ft.dropdown.Option("PATCH"),
                ft.dropdown.Option("OPTIONS"),
            ],
            width=180,
            dense=True,
            content_padding=5,
            value="POST",
        )

        self.path_input = ft.TextField(
            label="请求path",
            label_style=TextStyle(size=14),
            height=33,
            expand=True,
            content_padding=5,
            value="*/_search"
        )

        self.dsl_input = ft.TextField(
            multiline=True,
            keyboard_type=ft.KeyboardType.MULTILINE,
            text_size=14,
            min_lines=20,
            max_lines=20,
            label="dsl",
            label_style=TextStyle(size=14),
            expand=True,
        )
        self.result_input = ft.TextField(
            label="结果",
            label_style=TextStyle(size=14),
            max_lines=20,
            expand=True,
            min_lines=20,
            text_size=14,
        )

        self.send_button = S_Button(
            text="发送请求",
            height=38,
            on_click=self.send_search,
        )
        self.format_button = S_Button(
            text="格式化",
            height=38,
            on_click=self.format_button,
        )

        self.demos = ft.MenuBar(
                            style=ft.MenuStyle(
                                alignment=ft.alignment.top_left,
                            ),
                            controls=[
                                ft.SubmenuButton(
                                    content=ft.Text("填充示例查询"),
                                    height=40,
                                    leading=ft.Icon(ft.icons.MORE_VERT),
                                    controls=[
                                        ft.MenuItemButton(
                                            data="""{
  "query": {
    "term": {
      "title": 0
    }
  },
  "size": 0,
  "track_total_hits": true
}""",
                                            content=ft.Text("term"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data="""{
  "query": {
    "wildcard": {
      "time.keyword": "*2022-12-30*"
    }
  },
  "size": 0,
  "track_total_hits": true
}""",
                                            content=ft.Text("wildcard"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data="""{
  "aggs": {
    "demo": {
      "terms": {
        "field": "age",
        "missing": "空值",
        "size": 5
      }
    }
  },
  "size": 0,
  "track_total_hits": true
}""",
                                            content=ft.Text("aggs"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data="""{
  "query": {
    "wildcard": {
      "time.keyword": "*2022-12-30*"
    }
  },
  "size": 0,
  "track_total_hits": true
}""",
                                            content=ft.Text("wildcard"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data="""{
  "size": 0,
  "aggs": {
    "dem": {
      "composite": {
		 // 每次请求返回的最大buckets数量，用于分页
		"size": 1000,
        "sources": [  
          { "category": { "terms": { "field": "category.keyword" } } },
          { "brand": { "terms": { "field": "brand.keyword" } } }
        ],
        "after": {}  // 可选：分页追加
      },
      // 可选agg, 写每个桶下要进一步聚合的操作，与 composite 同级，例如：每个结果里显示一条原始数据，
      "aggs": {  
        "top_docs": {
          "top_hits": {
            "size": 1
          }
        }
      },
      // 可选agg, 写每个桶下要进一步聚合的操作，与 composite 同级，例如：聚合每个桶下文档的指定字段求和，
      "aggs": {
        "total_sum": {
          "sum": {
            "field": "file_size"
          }
        }
      }
    }
  }
}""",
                                            content=ft.Text("composite"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data="""{
  "query":{},
  "aggs": {
    "": {
      "date_range": {
        "field": "指定字段",
        "ranges": [
          {
            "from": "2023-06-28 13:43:33",
            "to": "2023-06-28 14:13:33"
          },
          {
            "from": "2023-06-28 14:13:33",
            "to": "2023-06-28 14:43:33"
          },
          {
            "from": "2023-06-28 14:43:33",
            "to": "2023-06-28 15:13:33"
          },
          {
            "from": "2023-06-28 15:13:33",
            "to": "2023-06-28 15:43:33"
          }
        ]
      }
    }
  },
}""",
                                            content=ft.Text("date_range"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data="""{
  "aggs": {
    "demo": {
      "cardinality": {
        "field": "age",
        "missing": 0
      }
    }
  },
  "size": 0,
  "track_total_hits": true
}""",
                                            content=ft.Text("date_range"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data="""{
  "query": {
      ...
  },
  "sort":[
    {
      "title":{
          "order": "desc"
      }
    },
    {
      "age":{
          "order": "asc"
      }     
    }
  ],
  "size": 10,
  "track_total_hits": true
}""",
                                            content=ft.Text("sort"),
                                            on_click=self.insert_demo,
                                        ),
                                    ]
                                ),
                            ]
                        )

        self.save_button = S_Button(
            text="保存",
            height=38,
            # on_click=self.click_save_config,
        )
        self.rest_tab = ft.Tab(
            text='Rest HTTP客户端', content=ft.Column(), icon=ft.icons.HIVE_OUTLINED,
        )

        self.tab = ft.Tabs(
            tabs=[
                self.rest_tab,
            ],
            expand=1,
        )

        self.controls = [
            self.tab
        ]

    def init(self, page: ft.Page = None):
        if not es_service.connect_obj:
            return "请先选择一个可用的ES连接！\nPlease select an available ES connection first!"

        self.rest_tab.content = build_tab_container(
            col_controls=[
                ft.Row([
                    self.method_groups_dd,
                    self.path_input,
                ]),
                ft.Row([
                    self.dsl_input,
                    self.result_input,
                ], vertical_alignment=ft.CrossAxisAlignment.START),
                ft.Row(
                    [
                        self.send_button,
                        self.save_button,
                        self.format_button,
                        self.demos,
                    ]
                )
            ]
        )

    def init_data(self):
        pass

    def is_json(self, s):
        try:
            res = json.loads(s)
            return True, res
        except ValueError as e:
            return False, None

    def on_change_input(self, e):
        e.control.value = self.format_json(e.control.value)
        e.control.update()

    def format_button(self, e):
        self.dsl_input.value = self.format_json(self.dsl_input.value)
        self.dsl_input.update()

    def format_json(self, data):
        flag, res = self.is_json(data)
        if flag:
            return json.dumps(res, ensure_ascii=False, indent=2)
        else:
            return data

    def insert_demo(self, e):
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("创建索引"),
            content=ft.Column([
                ft.Text(e.control.data, selectable=True)
            ], scroll=ft.ScrollMode.ALWAYS),
            actions=[
                ft.TextButton("取消", on_click=close_dlg),
            ],
            # actions_alignment=ft.MainAxisAlignment.START,
        )
        e.page.dialog = dlg_modal
        dlg_modal.open = True
        e.page.update()

    def send_search(self, e):
        if self.path_input.value and self.method_groups_dd.value:
            progress_bar.visible = True
            e.page.update()

            success, res = es_service.search(self.method_groups_dd.value, self.path_input.value, json.loads(self.dsl_input.value))

            progress_bar.visible = False
            if not success:
                open_snack_bar(e.page, res, success=False)
            else:
                self.result_input.value = json.dumps(res, ensure_ascii=False, indent=2)
            e.page.update()
