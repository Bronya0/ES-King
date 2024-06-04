#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@Time    : 2024/6/4 14:45
@File    : code.py
@Project : ES-King
@Desc    : 
"""

import flet as ft
import re
# Example theme class (GitHubDark)

class GitHubDarkTheme:
    def __init__(self):
        self.keyword = "bold blue"
        self.exception = "bold red"
        self.builtin = "italic cyan"
        self.docstring = "italic green"
        self.string = "italic yellow"
        self.type_annotation = "bold magenta"
        self.number = "bold orange"
        self.function_call = "bold purple"
        self.class_name = "bold green"
        self.decorator = "bold pink"
        self.instance = "italic white"
        self.comment = "italic gray"
        self.reset = "reset"
class Code(ft.UserControl):
    def __init__(
            self,
            language="python",
            code="",
            font="Code",
            theme=GitHubDarkTheme(),
            read_only=False,
            height=600,
            **kwargs,
    ):
        super().__init__(**kwargs)
        self.code_textfield_container = None
        self.code_highlight_container = None
        self.code_display = None
        self.code_field = None
        self.language = language
        self.code = code
        self.font = font
        self.theme = theme
        self.read_only = read_only
        self.height = height

        self.code_textfield = ft.TextField(
            value=None if self.read_only else self.code,
            multiline=True,
            dense=True,
            on_change=self.update_highlight,
            text_style=ft.TextStyle(
                font_family=self.font, size=14, color="transparent"
            ),
            cursor_color="#FFFFFF",
            border_color="transparent",
            bgcolor="transparent",
            width=800,
            height=600,
            content_padding=ft.padding.all(0),
            cursor_height=16,
            filled=True,
            expand=True,
        )

        self.syntax_rules = {
            "python": {
                "keywords": (
                    r"\b(?P<KEYWORD>False|None|True|and|as|assert|async|await|break|class|continue|def|del|elif|else|except|finally|for|from|global|if|import|in|is|lambda|nonlocal|not|or|pass|raise|return|try|while|with|yield)\b",
                    self.theme.keyword,
                ),
                "exceptions": (
                    r"([^.'\"\\#]\b|^)(?P<EXCEPTION>ArithmeticError|AssertionError|AttributeError|BaseException|BlockingIOError|BrokenPipeError|BufferError|BytesWarning|ChildProcessError|ConnectionAbortedError|ConnectionError|ConnectionRefusedError|ConnectionResetError|DeprecationWarning|EOFError|Ellipsis|EnvironmentError|Exception|FileExistsError|FileNotFoundError|FloatingPointError|FutureWarning|GeneratorExit|IOError|ImportError|ImportWarning|IndentationError|IndexError|InterruptedError|IsADirectoryError|KeyError|KeyboardInterrupt|LookupError|MemoryError|ModuleNotFoundError|NameError|NotADirectoryError|NotImplemented|NotImplementedError|OSError|OverflowError|PendingDeprecationWarning|PermissionError|ProcessLookupError|RecursionError|ReferenceError|ResourceWarning|RuntimeError|RuntimeWarning|StopAsyncIteration|StopIteration|SyntaxError|SyntaxWarning|SystemError|SystemExit|TabError|TimeoutError|TypeError|UnboundLocalError|UnicodeDecodeError|UnicodeEncodeError|UnicodeError|UnicodeTranslateError|UnicodeWarning|UserWarning|ValueError|Warning|WindowsError|ZeroDivisionError)\b",
                    self.theme.exception,
                ),
                "builtins": (
                    r"([^.'\"\\#]\b|^)(?P<BUILTIN>abs|all|any|ascii|bin|breakpoint|callable|chr|classmethod|compile|complex|copyright|credits|delattr|dir|divmod|enumerate|eval|exec|exit|filter|format|frozenset|getattr|globals|hasattr|hash|help|hex|id|input|isinstance|issubclass|iter|len|license|locals|map|max|memoryview|min|next|oct|open|ord|pow|print|quit|range|repr|reversed|round|set|setattr|slice|sorted|staticmethod|sum|type|vars|zip)\b",
                    self.theme.builtin,
                ),
                "docstrings": (
                    r"(?P<DOCSTRING>(?i:r|u|f|fr|rf|b|br|rb)?'''[^'\\]*((\\.|'(?!''))[^'\\]*)*(''')?|(?i:r|u|f|fr|rf|b|br|rb)?\"\"\"[^\"\\]*((\\.|\"(?!\"\"))[^\"\\]*)*(\"\"\")?)",
                    self.theme.docstring,
                ),
                "strings": (
                    r"(?P<STRING>(?i:r|u|f|fr|rf|b|br|rb)?'[^'\\\n]*(\\.[^'\\\n]*)*'?|(?i:r|u|f|fr|rf|b|br|rb)?\"[^\"\\\n]*(\\.[^\"\\\n]*)*\"?)",
                    self.theme.string,
                ),
                "types": (
                    r"\b(?P<TYPES>bool|bytearray|bytes|dict|float|int|list|str|tuple|object)\b",
                    self.theme.type_annotation,
                ),
                "numbers": (
                    r"\b(?P<NUMBER>((0x|0b|0o|#)[\da-fA-F]+)|((\d*\.)?\d+))\b",
                    self.theme.number,
                ),
                "function_calls": (
                    r"\b(\w+)\s*(?=\()",  # matches both standalone and dot-prefixed function calls
                    self.theme.function_call,
                ),
                "class_definitions": (
                    r"(?<=\bclass)[ \t]+(?P<CLASSDEF>\w+)[ \t]*[:\(]",  # recolor of DEFINITION for class definitions
                    self.theme.class_name,
                ),
                "decorators": (
                    r"(^[ \t]*(?P<DECORATOR>@[\w\d\.]+))",
                    self.theme.decorator,
                ),
                "instances": (
                    r"\b(?P<INSTANCE>super|self|cls)\b",
                    self.theme.instance,
                ),
                "comments": (
                    r"(?P<COMMENT>#[^\n]*)",
                    self.theme.comment,
                ),
            },
        }
    def apply_syntax_highlighting(self, text, language):
        rules = self.syntax_rules.get(language, {})
        formatted_lines = []
        full_lines = ft.ListView(spacing=1)
        lines = text.split("\n")
        for idx, line in enumerate(lines):
            parts = []
            last_idx = 0
            matches = []
            for element, (pattern, color) in rules.items():
                for match in re.finditer(pattern, line):
                    matches.append((match.start(), match.end(), match.group(0), color))
            matches.sort(key=lambda x: (x[0], -x[1]))
            for start, end, matched_text, color in matches:
                if start >= last_idx:
                    if start > last_idx:
                        parts.append(
                            ft.Text(
                                value=line[last_idx:start],
                                style=ft.TextStyle(size=14),
                                font_family=self.font,
                            )
                        )
                    parts.append(
                        ft.Text(
                            value=matched_text,
                            style=ft.TextStyle(color=color, size=14),
                            font_family=self.font,
                        )
                    )
                    last_idx = end

            if last_idx < len(line):
                parts.append(
                    ft.Text(
                        value=line[last_idx:],
                        style=ft.TextStyle(size=14),
                        font_family=self.font,
                    )
                )

            line_number = ft.Container(ft.Text(f"{idx + 1}", color="#60676f"), width=40)
            line_widgets = ft.Row(controls=[line_number] + parts, wrap=None, spacing=0)
            formatted_lines.append(line_widgets)
        full_lines.controls.extend(formatted_lines)
        return full_lines

    def update_highlight(self, e=None):
        highlighted_code = self.apply_syntax_highlighting(
            text=self.code_textfield_container.content.value, language=self.language
        )
        self.code_highlight_container.content = highlighted_code
        self.code_highlight_container.update()

    def build(self):
        if self.read_only:
            return ft.Stack(controls=[self.code_highlight_container])
        return ft.Stack(
            controls=[self.code_highlight_container, self.code_textfield_container]
        )

def init(page: ft.Page):
    code_ = Code()
    t = code_.build()
    page.add(t)

if __name__ == '__main__':

        ft.app(target=init, assets_dir="assets", name="ES-King")