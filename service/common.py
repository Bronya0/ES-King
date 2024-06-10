#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/2/5 19:25
@File    : common.py
@Project : ES-king
@Desc    : 
"""
import math
import os

import flet
from flet_core import TextStyle

from service.translate import i18n

# 假设有一个全局的存储连接信息的变量
prefix = "__es_connects__"
KAFKA_KING_GROUP = "__es_king_group"
CONFIG_KEY = "__config"
GITHUB_URL = "https://github.com/Bronya0/ES-King"
GITHUB_REPOS_URL = "https://api.github.com/repos/Bronya0/ES-King"
UPDATE_URL = "https://api.github.com/repos/Bronya0/ES-King/releases/latest"
ISSUES_URL = "https://github.com/Bronya0/ES-King/issues"
ISSUES_API_URL = "https://api.github.com/repos/Bronya0/ES-King/issues?state=open"

BASEDIR = os.path.dirname(os.path.dirname(__file__))

c_version = open(f'{BASEDIR}/assets/version.txt', 'r', encoding='utf-8').read().rstrip().replace('\n', '')
TITLE = "ES-King {}".format(c_version)
CURRENT_ES_CONNECT_KEY = "current_es_connect"

view_instance_map = {}
# page index
INFO = 0
CORE = 1
BROKER = 2
INDEX = 3
REST = 4
SETTINGS = 5
SUGGEST = 6
HELP = 7

PAGE_WIDTH = 1620
PAGE_HEIGHT = 880
WINDOW_TOP = 200
WINDOW_LEFT = 260
PAGE_MIN_WIDTH = 1140
PAGE_MIN_HEIGHT = 720


def S_Text(value, **kwargs):
    if "tooltip" not in kwargs:
        kwargs["tooltip"] = value
    if "num" in kwargs:
        if len(value) > kwargs["num"]:
            value = value[:kwargs["num"]] + "..."
        kwargs.pop("num")
    return flet.Text(
        selectable=True,
        value=value,
        **kwargs
    )


def S_Button(**kwargs):
    return flet.ElevatedButton(
        style=flet.ButtonStyle(
            shape={
                flet.MaterialState.HOVERED: flet.RoundedRectangleBorder(radius=2),
                flet.MaterialState.DEFAULT: flet.RoundedRectangleBorder(radius=10),
            },
        ),
        **kwargs,
    )


def open_snack_bar(page: flet.Page, msg, success=True):
    page.snack_bar.content = flet.Text(msg, selectable=True)
    page.snack_bar.open = True
    # if success:
    #     color = "#1677ff"
    # else:
    #     color = "#000000"
    # page.snack_bar.bgcolor = color
    page.update()


def close_dlg(e):
    e.page.dialog.open = False
    e.page.update()


dd_common_configs = {
    "options": [],
    "height": 36,
    "width": 200,
    "text_size": 14,
    "alignment": flet.alignment.center_left,
    "dense": True,
    "content_padding": 5,
}

input_kwargs = {
    "width": 200,
    "height": 35,
    "text_size": 16,
    "label_style": TextStyle(size=12),
    "content_padding": 10
}

Navigation = flet.NavigationRail(
    selected_index=0,
    label_type=flet.NavigationRailLabelType.ALL,
    min_width=100,
    min_extended_width=100,
    group_alignment=-0.8,
    # 定义在导航栏中排列的按钮项的外观，该值必须是两个或更多NavigationRailDestination实例的列表。
    destinations=[
        flet.NavigationRailDestination(
            icon_content=flet.Icon(flet.icons.FAVORITE_OUTLINE, ),
            selected_icon_content=flet.Icon(flet.icons.FAVORITE),
            label=i18n("健康"),
        ),
        flet.NavigationRailDestination(
            icon_content=flet.Icon(flet.icons.INSERT_CHART_OUTLINED,),
            selected_icon_content=flet.Icon(flet.icons.INSERT_CHART),
            label=i18n("指标"),
        ),
        flet.NavigationRailDestination(
            icon_content=flet.Icon(flet.icons.HIVE_OUTLINED,),
            selected_icon_content=flet.Icon(flet.icons.HIVE),
            label=i18n("集群"),
        ),
        flet.NavigationRailDestination(
            icon_content=flet.Icon(flet.icons.LIBRARY_BOOKS_OUTLINED,),
            selected_icon_content=flet.Icon(flet.icons.LIBRARY_BOOKS),
            label=i18n("索引"),
        ),
        flet.NavigationRailDestination(
            icon_content=flet.Icon(flet.icons.API_OUTLINED,),
            selected_icon_content=flet.Icon(flet.icons.API),
            label=i18n("REST"),
        ),

        # flet.NavigationRailDestination(
        #     icon_content=flet.Icon(flet.icons.STACKED_BAR_CHART_ROUNDED,),
        #     selected_icon_content=flet.Icon(flet.icons.STACKED_BAR_CHART),
        #     label=i18n("监控"),
        # ),
        flet.NavigationRailDestination(
            icon_content=flet.Icon(flet.icons.SETTINGS_OUTLINED, ),
            selected_icon_content=flet.Icon(flet.icons.SETTINGS_SUGGEST_OUTLINED),
            label_content=S_Text(i18n("设置")),
        ),
        flet.NavigationRailDestination(
            icon_content=flet.Icon(flet.icons.AUTO_GRAPH_OUTLINED, tooltip="建议我们"),
            selected_icon_content=flet.Icon(flet.icons.AUTO_GRAPH),
            label_content=S_Text(i18n("建议")),
        ),
        flet.NavigationRailDestination(
            icon_content=flet.Icon(flet.icons.HELP_OUTLINE, tooltip="使用帮助"),
            selected_icon_content=flet.Icon(flet.icons.HELP),
            label_content=S_Text(i18n("帮助")),
        ),
    ],
)

body = flet.Column(
    controls=[],
    expand=True,
)

# 全局进度条
progress_bar = flet.ProgressBar(visible=False)


class page_info:
    """
    存储通用page对象
    """

    def __init__(self):
        self.page = None

    def set_page(self, page):
        self.page: flet.Page = page


common_page = page_info()


def human_size(size_in_bytes):
    if size_in_bytes == 0:
        return "0 B"
    units = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
    index = int(math.floor(math.log(size_in_bytes, 1024)))
    size = round(size_in_bytes / math.pow(1024, index), 2)
    return f"{size} {units[index]}"


def build_tab_container(col_controls):
    """
    一个通用的、自适应的内容
    """
    return flet.Column(
        scroll=flet.ScrollMode.ALWAYS,  # 设置滚动条始终显示
        controls=[
            flet.Container(
                alignment=flet.alignment.top_left, padding=10,
                content=flet.Column(
                    scroll=flet.ScrollMode.ALWAYS,
                    controls=col_controls
                )
            )
        ])


def build_alert(page, title, column: flet.Column):
    dlg_modal = flet.AlertDialog(
        modal=False,
        title=flet.Text(title),
        content=column,
        actions=[
        ],
        # actions_alignment=ft.MainAxisAlignment.START,
    )
    return dlg_modal