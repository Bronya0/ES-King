#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json
import time

import flet as ft
from flet_core import TextStyle

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
            label_style=TextStyle(size=14),
            options=[
                ft.dropdown.Option("GET"),
                ft.dropdown.Option("POST"),
                ft.dropdown.Option("PUT"),
                ft.dropdown.Option("DELETE"),
                ft.dropdown.Option("HEAD"),
                ft.dropdown.Option("PATCH"),
                ft.dropdown.Option("OPTIONS"),
            ],
            width=120,
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
            value="索引名/_search", autofocus=True,
            prefix=ft.Text(es_service.host),

        )

        self.dsl_input = ft.TextField(
            multiline=True,
            keyboard_type=ft.KeyboardType.MULTILINE,
            text_size=12,
            min_lines=20,
            max_lines=20,
            label="dsl",
            label_style=TextStyle(size=14),
            expand=True,
            on_change=self.on_change_input,
            # autocorrect=True,
            # enable_suggestions=True,
            # fill_color="#1A1C1E"
        )
        self.result_input = ft.TextField(
            label="结果",
            label_style=TextStyle(size=14),
            max_lines=20,
            expand=True,
            min_lines=20,
            text_size=12,
        )

        self.send_button = S_Button(
            text="发送请求",
            height=38,
            on_click=self.send_search,
        )
        self.format_button = S_Button(
            text="格式化JSON",
            height=38,
            on_click=self.format_button_func,
        )

        self.export_json_button = S_Button(
            text="导出为JSON",
            height=38,
            on_click=self.export_json_button_func,
        )
        self.history_button = S_Button(
            text="查询历史",
            height=38,
            # on_click=self.send_search,
        )

        self._convert = {
            "{": """{
  "query": {
    "bool": {
      "must": [
        {
          "term": {
            "": ""
          }
        }
      ]
    }
  },
  "aggs": {
    "a": {
      "terms": {
        "": ""
      }
    }
  },
  "size": 0,
  "track_total_hits": true
}""",
            "[": "[\n]",
            "term": """{
  "query": {
    "bool": {
      "must": [
        {
          "range": {
            "report_time_datetime": {
              "gte": "2024-05-31 00:00:00"
            }
          }
        },
        {
          "term": {
            "data.area.keyword": "110000"
          }
        }
      ]
    }
  },
  "size": 0,
  "track_total_hits": true,
  "aggs": {
    "ds": {
      "terms": {
        "field": "topic.keyword",
        "size": 100
      }
    }
  }
}""",
            "wildcard": """{
  "query": {
    "wildcard": {
      "time.keyword": "*2022-12-30*"
    }
  },
  "size": 0,
  "track_total_hits": true
}""",
            "aggs": """{
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
            "composite": """{
  "size": 0,
  "aggs": {
    "dem": {
      "composite": {
        "size": 1000,
        "sources": [
          {
            "category": {
              "terms": {
                "field": "category.keyword"
              }
            }
          },
          {
            "brand": {
              "terms": {
                "field": "brand.keyword"
              }
            }
          }
        ],
        "after": {}
      },
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
            "date_range": """{
  "query": {},
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
  }
}""",
            "cardinality": """{
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
            "sort": """{
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

                                }
        self.demos = ft.MenuBar(
                            style=ft.MenuStyle(
                                alignment=ft.alignment.top_left,
                            ),
                            controls=[
                                ft.SubmenuButton(
                                    content=ft.Text("关键字自动补全"),
                                    tooltip="在清空的输入框中输入关键字，自动补全",
                                    height=40,
                                    leading=ft.Icon(ft.icons.MORE_VERT),
                                    controls=[
                                        ft.MenuItemButton(
                                            data=self._convert['term'],
                                            content=ft.Text("term"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data=self._convert["wildcard"],
                                            content=ft.Text("wildcard"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data=self._convert["aggs"],
                                            content=ft.Text("aggs"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data=self._convert['wildcard'],
                                            content=ft.Text("wildcard"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data=self._convert['composite'],
                                            content=ft.Text("composite"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data=self._convert['date_range'],
                                            content=ft.Text("date_range"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data=self._convert['cardinality'],
                                            content=ft.Text("cardinality"),
                                            on_click=self.insert_demo,
                                        ),
                                        ft.MenuItemButton(
                                            data=self._convert['sort'],
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
                    ft.Column([
                        ft.Row(
                            [
                                self.dsl_input,
                            ]
                        ),
                        ft.Row(
                            [
                                self.send_button,
                                self.history_button,
                                # self.save_button,
                                self.format_button,
                                self.demos,
                            ]
                        )
                    ], expand=True),
                    ft.Column(
                        [
                            ft.Row(
                                [
                                    self.result_input,
                                ]
                            ),

                            ft.Row(
                                [
                                    self.export_json_button
                                ], vertical_alignment=ft.CrossAxisAlignment.START
                            ),
                        ], expand=True),
                ], vertical_alignment=ft.CrossAxisAlignment.START)


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
        # e.control.value = self.format_json(e.control.value)
        # e.control.update()
        _v = e.control.value
        if _v in self._convert:
            self.dsl_input.value = self._convert[_v]
            e.page.update()

    def format_button_func(self, e):
        flag, res = self.is_json(self.dsl_input.value)
        if not flag:
            open_snack_bar(e.page, "不是正确json文本格式，无法格式化", success=True)
        else:
            self.dsl_input.value = self.format_json(self.dsl_input.value)
            self.dsl_input.update()
            open_snack_bar(e.page, "格式化完成", success=True)

    def export_json_button_func(self, e):
        path = f"/es-king-export-{int(time.time())}.json"
        data = self.result_input.value
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(json.loads(data), f, ensure_ascii=False, indent=2)

        open_snack_bar(e.page, f"成功导出到根目录：{path}", success=True)

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
