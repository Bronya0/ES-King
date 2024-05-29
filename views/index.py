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
        # _lag_label: when select consumer groups, use it, that is 'loading...'
        self.page = None
        self.pr = progress_bar
        self.table_topics = []
        self._lag_label = None
        self.topic_offset = None
        self.topic_lag = None
        self.topic_op_content = None
        self.describe_topics_map: Optional[Dict] = None
        self.partition_table = None
        self.describe_topics = None
        self.describe_topics_tmp = []
        self.topic_table = None
        self.page_num = 1
        self.page_size = 8

        # search datatable
        self.search_text = ft.TextField(label='检索', on_submit=self.search_table, width=200,
                                        height=38, text_size=14, content_padding=5)

        # topic list tap
        self.topic_tab = ft.Tab(
            icon=ft.icons.LIST_ALT_OUTLINED, text="列表", content=ft.Row()
        )

        # partition list tap
        self.partition_tab = ft.Tab(
            icon=ft.icons.WAVES_OUTLINED, text="分区",
            content=ft.Container(content=ft.Text("请从主题列表的分区列点击进入", size=20))
        )

        # config tap
        self.config_tab = ft.Tab(
            text='主题配置', content=ft.Container(content=ft.Text("请从主题的配置按钮进入", size=20)),
            icon=ft.icons.CONSTRUCTION_OUTLINED
        )

        # all in one
        self.tab = ft.Tabs(
            animation_duration=300,
            tabs=[
                self.topic_tab,
                self.partition_tab,
                self.config_tab,
            ],
            expand=True,
        )

        self.controls = [
            self.tab,
        ]

    def init(self, page=None):
        if not es_service.connect_obj:
            return "请先选择一个可用的ES连接！\nPlease select an available ES connection first!"

