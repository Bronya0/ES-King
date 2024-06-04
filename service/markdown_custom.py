#!/usr/bin/env python
# -*-coding:utf-8 -*-
import flet as ft


class Markdown(ft.Markdown):
    """
    Markdown类提供了一个用于处理Markdown文本的封装。

    :param value: Markdown文本的值。
    :param selectable: 是否可选择，默认为True。
    :param extension_set: Markdown扩展集，默认为COMMON_MARK。
    :param code_theme: 代码块的主题，默认为'atom-one-dark'。
    :param code_style: 代码块的样式，默认为一个空的TextStyle对象。
    :param kwargs: 传递给ft.Markdown基类构造函数的额外参数。
    """

    def __init__(self, value="", selectable=True, extension_set=ft.MarkdownExtensionSet.GITHUB_WEB,
                 code_style=ft.TextStyle(),
                 code_theme="darcula", **kwargs):

        # 使用try-except结构以处理可能的异常
        try:
            super().__init__(value=value,
                             selectable=selectable,
                             extension_set=extension_set,
                             code_theme=code_theme,
                             code_style=code_style,
                             **kwargs)
        except Exception as e:
            # 在实际应用中，应该使用更具体的异常类型，并合理处理异常（如记录日志、抛出自定义异常等）
            print(f"初始化Markdown对象时发生错误: {e}")
            raise
