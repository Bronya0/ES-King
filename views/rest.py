#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json
import time

import flet as ft
from flet_core import TextStyle

from service.common import S_Button, open_snack_bar, build_tab_container, close_dlg, progress_bar, common_page
from service.es_service import es_service
from service.markdown_custom import Markdown

input_convert = {
    "{": """{

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
}"""

}


class Rest(object):
    """
    """

    def __init__(self):
        self.history_key = "history_key"

        method_groups_dd_param = {
            "label": "请选择HTTP方法",
            "label_style": TextStyle(size=14),
            "options": [
                ft.dropdown.Option("GET"),
                ft.dropdown.Option("POST"),
                ft.dropdown.Option("PUT"),
                ft.dropdown.Option("HEAD"),
                ft.dropdown.Option("PATCH"),
                ft.dropdown.Option("OPTIONS"),
                ft.dropdown.Option("DELETE", disabled=True),
            ],
            "width": 120,
            "dense": True,
            "content_padding": 5,
            "value": "POST"
        }
        self.method_groups_dd1, self.method_groups_dd2 = ft.Dropdown(**method_groups_dd_param), ft.Dropdown(
            **method_groups_dd_param)

        path_input_param = {
            "label": "请求path",
            "label_style": TextStyle(size=14),
            "height": 33,
            "expand": True,
            "content_padding": 5,
            "value": "索引名/_search",
            "autofocus": True,
            "prefix": ft.Text(es_service.host),
        }
        self.path_input1, self.path_input2 = ft.TextField(**path_input_param), ft.TextField(**path_input_param)

        dsl_input_param = {
            "multiline": True,
            "keyboard_type": ft.KeyboardType.MULTILINE,
            "text_size": 13,
            "min_lines": 25,
            "max_lines": 25,
            "label": "dsl",
            "label_style": TextStyle(size=14),
            "expand": True,
            "on_change": self.on_change_input,
        }
        self.dsl_input1, self.dsl_input2 = ft.TextField(**dsl_input_param), ft.TextField(**dsl_input_param),

        self.result_input1, self.result_input2 = Markdown(width=690), Markdown(width=690)

        send_button_param = {
            "text": "发送请求",
            "height": 38,
            "on_click": self.send_search,
        }
        self.send_button1, self.send_button2 = S_Button(**send_button_param), S_Button(**send_button_param)

        format_button_param = {
            "text": "格式化JSON",
            "height": 38,
            "on_click": self.format_button_func,
        }
        self.format_button1, self.format_button2 = S_Button(**format_button_param), S_Button(**format_button_param)

        export_json_button_param = {
            "text": "导出为JSON",
            "height": 38,
            "on_click": self.export_json_button_func,
        }
        self.export_json_button1, self.export_json_button2 = S_Button(**export_json_button_param), S_Button(
            **export_json_button_param)

        self.history_menu_controls = []
        self.history_menu = ft.MenuBar(
            controls=[
                ft.SubmenuButton(
                    content=ft.Text(f"查询历史"),
                    tooltip="保留过去成功查询的100条",
                    height=40,
                    leading=ft.Icon(ft.icons.MORE_VERT),
                    controls=self.history_menu_controls
                )
            ]
        )
        self.init_history()

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
                            data=input_convert['term'],
                            content=ft.Text("term"),
                            on_click=self.insert_demo,
                        ),
                        ft.MenuItemButton(
                            data=input_convert["wildcard"],
                            content=ft.Text("wildcard"),
                            on_click=self.insert_demo,
                        ),
                        ft.MenuItemButton(
                            data=input_convert["aggs"],
                            content=ft.Text("aggs"),
                            on_click=self.insert_demo,
                        ),
                        ft.MenuItemButton(
                            data=input_convert['wildcard'],
                            content=ft.Text("wildcard"),
                            on_click=self.insert_demo,
                        ),
                        ft.MenuItemButton(
                            data=input_convert['composite'],
                            content=ft.Text("composite"),
                            on_click=self.insert_demo,
                        ),
                        ft.MenuItemButton(
                            data=input_convert['date_range'],
                            content=ft.Text("date_range"),
                            on_click=self.insert_demo,
                        ),
                        ft.MenuItemButton(
                            data=input_convert['cardinality'],
                            content=ft.Text("cardinality"),
                            on_click=self.insert_demo,
                        ),
                        ft.MenuItemButton(
                            data=input_convert['sort'],
                            content=ft.Text("sort"),
                            on_click=self.insert_demo,
                        ),
                    ]
                ),
            ]
        )

        self.rest_tab1 = ft.Tab(
            text='Rest客户端1号', content=ft.Column(), icon=ft.icons.API,
        )
        self.rest_tab2 = ft.Tab(
            text='Rest客户端2号', content=ft.Column(), icon=ft.icons.API,
        )

        # 通过tab.selected_index获取当前是哪个index
        self.tab = ft.Tabs(
            tabs=[
                self.rest_tab1,
                self.rest_tab2,
            ],
            expand=1,
            animation_duration=300,
        )

        self.controls = [
            self.tab
        ]

    def init(self, page: ft.Page = None):
        if not es_service.connect_obj:
            return "请先选择一个可用的ES连接！\nPlease select an available ES connection first!"

        self.rest_tab1.content = build_tab_container(
            col_controls=[
                ft.Row([
                    self.method_groups_dd1,
                    self.path_input1,
                ]),
                ft.Row([
                    ft.Column([
                        ft.Row(
                            [
                                self.dsl_input1,
                            ], width=600
                        ),
                        ft.Row(
                            [
                                self.send_button1,
                                self.history_menu,
                                self.format_button1,
                                self.demos,
                            ]
                        )
                    ], expand=True),
                    ft.Column(
                        [
                            ft.Row(
                                [

                                    ft.Container(
                                        content=ft.Column(
                                            [
                                                self.result_input1
                                            ], scroll=ft.ScrollMode.ALWAYS,
                                        ),
                                        border=ft.border.all(1),
                                        height=514,
                                        width=710,
                                        # bgcolor="#282c34"
                                        # expand=True
                                    )

                                ], vertical_alignment=ft.CrossAxisAlignment.START, scroll=ft.ScrollMode.ALWAYS
                            ),

                            ft.Row(
                                [
                                    self.export_json_button1
                                ], vertical_alignment=ft.CrossAxisAlignment.START
                            ),
                        ], expand=True, scroll=ft.ScrollMode.ALWAYS, ),
                ], vertical_alignment=ft.CrossAxisAlignment.START)

            ]
        )

        self.rest_tab2.content = build_tab_container(
            col_controls=[
                ft.Row([
                    self.method_groups_dd2,
                    self.path_input2,
                ]),
                ft.Row([
                    ft.Column([
                        ft.Row(
                            [
                                self.dsl_input2,
                            ], width=600
                        ),
                        ft.Row(
                            [
                                self.send_button2,
                                self.history_menu,
                                self.format_button2,
                                self.demos,
                            ]
                        )
                    ], expand=True),
                    ft.Column(
                        [
                            ft.Row(
                                [

                                    ft.Container(
                                        content=ft.Column(
                                            [
                                                self.result_input2
                                            ], scroll=ft.ScrollMode.ALWAYS,
                                        ),
                                        border=ft.border.all(1),
                                        height=514,
                                        width=710,
                                        # bgcolor="#282c34"
                                        # expand=True
                                    )

                                ], vertical_alignment=ft.CrossAxisAlignment.START, scroll=ft.ScrollMode.ALWAYS
                            ),

                            ft.Row(
                                [
                                    self.export_json_button2
                                ], vertical_alignment=ft.CrossAxisAlignment.START
                            ),
                        ], expand=True, scroll=ft.ScrollMode.ALWAYS, ),
                ], vertical_alignment=ft.CrossAxisAlignment.START)

            ]
        )

    def init_history(self):
        # 初始化，填充查询历史
        history = common_page.page.client_storage.get(self.history_key)
        if history is not None:
            # [(path, dsl)]
            for method, path, dsl in history:
                self.history_menu_controls.append(
                    ft.MenuItemButton(
                        content=ft.Text(method + " " + path),
                        tooltip=dsl,
                        on_click=self.insert_history,
                        data=(method, path, dsl),
                    )
                )

    def is_json(self, s):
        try:
            res = json.loads(s)
            return True, res
        except ValueError as e:
            return False, None

    def on_change_input(self, e):
        _v = e.control.value
        if _v in input_convert:
            e.control.value = input_convert[_v]
            e.page.update()

    def format_button_func(self, e):
        """格式化json"""
        if self.tab.selected_index == 0:
            self._format_button_func(self.dsl_input1, e.control)
        elif self.tab.selected_index == 1:
            self._format_button_func(self.dsl_input2, e.control)

    def _format_button_func(self, _input, button):
        flag, res = self.is_json(_input.value)
        if not flag:
            button.text = "格式不正确"
        else:
            _input.value = self.format_json(_input.value)
            button.text = "格式化完成"
        button.update()
        _input.update()

    def export_json_button_func(self, e):
        """ 导出json """
        data = ""

        if self.tab.selected_index == 0:
            data: str = self.result_input1.data
        elif self.tab.selected_index == 1:
            data: str = self.result_input2.data
        if data:
            self._export_json_button_func(data, e.page)

    def _export_json_button_func(self, data, page):
        path = f"/es-king-export-{int(time.time())}.json"
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(json.loads(data), f, ensure_ascii=False, indent=2)
        open_snack_bar(page, f"成功导出到根目录：{path}", success=True)

    def format_json(self, data):
        flag, res = self.is_json(data)
        if flag:
            return json.dumps(res, ensure_ascii=False, indent=2)
        else:
            return data

    def insert_demo(self, e):
        """ 选择示例查询 """
        dlg_modal = ft.AlertDialog(
            modal=True,
            title=ft.Text("创建索引"),
            content=ft.Column([
                ft.Text(e.control.data, selectable=True)
            ], scroll=ft.ScrollMode.ALWAYS),
            actions=[
                ft.TextButton("取消", on_click=close_dlg),
            ],
        )
        e.page.dialog = dlg_modal
        dlg_modal.open = True
        e.page.update()

    def send_search(self, e):
        if self.tab.selected_index == 0:
            self._send_search(
                self.path_input1,
                self.method_groups_dd1,
                self.dsl_input1,
                self.result_input1,
            )
        elif self.tab.selected_index == 1:
            self._send_search(
                self.path_input2,
                self.method_groups_dd2,
                self.dsl_input2,
                self.result_input2,
            )

    def _send_search(self, path_input, method_groups_dd, dsl_input, result_input):
        """
        点击搜索
        """
        if not path_input.value or not method_groups_dd.value or not dsl_input.value:
            return
        progress_bar.visible = True
        progress_bar.update()

        success, res = es_service.search(method_groups_dd.value, path_input.value, json.loads(dsl_input.value))

        progress_bar.visible = False
        if not success:
            open_snack_bar(common_page.page, res, success=False)
        else:
            result_input.value = f"""
```json
{json.dumps(res, ensure_ascii=False, indent=4)}
```
"""
        result_input.data = json.dumps(res, ensure_ascii=False, indent=4)
        common_page.page.update()

        # 存储历史
        history = common_page.page.client_storage.get(self.history_key)
        if history is None:
            history = []
        if len(history) > 100:
            history.pop(-1)
        record = (method_groups_dd.value, path_input.value, dsl_input.value)
        history.insert(0, record)  # 倒序插入
        common_page.page.client_storage.set(self.history_key, history)

        # 搜索完添加到菜单里
        self.history_menu_controls.insert(0,
                                          ft.MenuItemButton(
                                              data=record,
                                              content=ft.Text(method_groups_dd.value + " " + path_input.value),
                                              tooltip=dsl_input.value,
                                              on_click=self.insert_history,
                                          ),
                                          )

        common_page.page.update()

    def insert_history(self, e):
        """插入到当前输入框里"""
        if self.tab.selected_index == 0:
            self.method_groups_dd1.value, self.path_input1.value, self.dsl_input1.value = e.control.data
        elif self.tab.selected_index == 1:
            self.method_groups_dd2.value, self.path_input2.value, self.dsl_input2.value = e.control.data
        e.page.update()
