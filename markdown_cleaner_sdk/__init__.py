# -*- coding: utf-8 -*-
"""
Markdown清理工具包

这个包提供了删除Markdown文件中包含指定关键字的行的功能。
支持多种匹配模式，包括精确匹配、部分匹配和正则表达式匹配。

主要功能:
1. MarkdownCleaner - 核心清理类
2. DEFAULT_CONFIG - 默认配置
3. MATCH_MODES - 支持的匹配模式

作者: AI Assistant
版本: 1.0.0
"""

from .markdown_cleaner import MarkdownCleaner, main
from .config import DEFAULT_CONFIG, SUPPORTED_MODES

__version__ = "1.0.0"
__author__ = "AI Assistant"
__email__ = "ai@example.com"

__all__ = [
    "MarkdownCleaner",
    "main",
    "DEFAULT_CONFIG", 
    "SUPPORTED_MODES"
]
