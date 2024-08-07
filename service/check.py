#!/usr/bin/env python
# -*-coding:utf-8 -*-
import platform

import flet as ft
import requests

from service.common import UPDATE_URL, BASEDIR, GITHUB_URL, close_dlg, CommonAlert, c_version


def version_check(page: ft.Page):
    print("开始检查版本……", UPDATE_URL)

    res = requests.get(UPDATE_URL)
    if res.status_code != 200:
        res = requests.get(UPDATE_URL)
        if res.status_code != 200:
            res = requests.get(UPDATE_URL)
            if res.status_code != 200:
                return
    latest_version = res.json()['tag_name']
    body = res.json()['body']
    version = open(f'{BASEDIR}/assets/version.txt', 'r', encoding='utf-8').read().rstrip().replace('\n', '')
    if version != latest_version:
        print("需要更新 {} -> {}".format(version, latest_version))

        page.dialog = CommonAlert(
            title_str="🎉🎉发现新版本: {}".format(latest_version),
            actions=[
                ft.Row(
                    controls=[
                        ft.Column(
                            [
                                ft.Column(
                                    [
                                        ft.Text(f"当前版本：{version}"),
                                        ft.Text(body, selectable=True),
                                    ],
                                    scroll=ft.ScrollMode.ALWAYS,
                                    height=180,
                                    width=600
                                ),
                                ft.Row(
                                    [
                                        ft.TextButton(text="前往下载", url=GITHUB_URL),
                                        ft.TextButton(text="下次再说", on_click=close_dlg,
                                                      tooltip="长期未更新可能会导致故障累积",
                                                      style=ft.ButtonStyle(color=ft.colors.GREY)),
                                    ]
                                )
                            ],
                            scroll=ft.ScrollMode.ALWAYS,
                        )],
                    scroll=ft.ScrollMode.ALWAYS,

                )
            ],
        )

        page.update()


def ping():
    # 统计使用情况， 不涉及敏感信息。
    try:
        ping_url = "https://ysboke.cn/api/kingTool/ping"
        requests.post(url=ping_url, json={
            "name": "ES-King",
            "version": c_version,
            "platform": platform.system()
        })
    except Exception as e:
        pass
