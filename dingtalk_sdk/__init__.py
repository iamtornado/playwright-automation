# -*- coding: utf-8 -*-
"""
钉钉API SDK

这个SDK封装了钉钉开放平台的服务端API，主要用于：
1. 获取access_token
2. 查询用户信息
3. 搜索钉钉知识库文档
4. 获取文档详细信息

作者: AI Assistant
版本: 1.0.0
"""

from .dingtalk_sdk import (
    DingTalkSDK,
    DingTalkConfig,
    DocumentInfo,
    DingTalkSDKError,
    create_sdk
)

__version__ = "1.0.0"
__author__ = "AI Assistant"
__email__ = "ai@example.com"

__all__ = [
    "DingTalkSDK",
    "DingTalkConfig", 
    "DocumentInfo",
    "DingTalkSDKError",
    "create_sdk"
]
