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


class S_Button(flet.ElevatedButton):

    def __init__(self, **kwargs):

        super().__init__(style=flet.ButtonStyle(
            shape={
                "hovered": flet.RoundedRectangleBorder(radius=2),
                "": flet.RoundedRectangleBorder(radius=10),
            }), **kwargs)


import os
import platform
import subprocess


def open_directory(path):
    """
    打开指定的本地目录。

    :param path: 要打开的目录路径
    """
    if platform.system() == "Windows":
        # Windows系统使用start命令
        os.startfile(os.path.normpath(path))
    elif platform.system() == "Darwin":  # macOS
        # macOS使用open命令
        subprocess.Popen(["open", path])
    else:  # Linux系统
        # 假设使用Nautilus，其他Linux发行版可能需要使用不同的命令，如xdg-open
        try:
            subprocess.Popen(["xdg-open", path])
        except OSError:
            # 如果xdg-open不可用，尝试使用Nautilus
            subprocess.Popen(["nautilus", path])


def open_snack_bar(page: flet.Page, msg, success=True):
    page.overlay.append(flet.SnackBar(
        content=flet.Text(msg, selectable=True),
        open=True
    ))
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
    # min_width=100,
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


class CommonAlert(flet.AlertDialog):

    def __init__(self, title_str, **kwargs):
        super().__init__(
            modal=False,
            title=flet.Text(title_str),
            actions_alignment=flet.MainAxisAlignment.CENTER,
            shape=flet.RoundedRectangleBorder(radius=8),
            open=True,
            **kwargs
        )
