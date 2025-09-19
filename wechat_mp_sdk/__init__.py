# -*- coding: utf-8 -*-
"""
微信公众号API SDK

这个SDK封装了微信公众号开放平台的API，主要用于：
1. 获取access_token
2. 上传永久素材（图片、语音、视频、缩略图）
3. 素材管理功能

作者: AI Assistant
版本: 1.0.0
"""

from .wechat_mp_sdk import (
    WeChatMPSDK,
    WeChatMPSDKError,
    create_sdk
)

__version__ = "1.0.0"
__author__ = "AI Assistant"
__email__ = "ai@example.com"

__all__ = [
    "WeChatMPSDK",
    "WeChatMPSDKError",
    "create_sdk"
]
