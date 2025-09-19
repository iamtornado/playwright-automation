# -*- coding: utf-8 -*-
"""
Word Counter SDK

一个简易的字数统计和文本处理SDK，专门用于中英文混合文本的字符数统计和优化。

主要功能：
- 精确的字符数统计
- 中英文空格智能处理
- 文本长度验证和优化
- 120字限制验证（适配豆包AI）

作者: tornadoami
版本: 1.0.0
"""

from .simple_word_counter import (
    count_characters,
    remove_spaces_between_chinese_english,
    validate_and_clean_text,
    check_length_warning
)

__version__ = "1.0.0"
__author__ = "tornadoami"

# 导出主要函数
__all__ = [
    'count_characters',
    'remove_spaces_between_chinese_english', 
    'validate_and_clean_text',
    'check_length_warning'
]

# 便捷的创建函数
def create_counter():
    """
    创建一个字数统计器实例（向后兼容）
    
    Returns:
        dict: 包含所有主要函数的字典
    """
    return {
        'count_characters': count_characters,
        'remove_spaces_between_chinese_english': remove_spaces_between_chinese_english,
        'validate_and_clean_text': validate_and_clean_text,
        'check_length_warning': check_length_warning
    }

# 快速验证文本的便捷函数
def quick_validate(text, max_length=120):
    """
    快速验证文本长度的便捷函数
    
    Args:
        text (str): 需要验证的文本
        max_length (int): 最大字符数限制，默认120
        
    Returns:
        bool: 是否符合长度要求
    """
    result = validate_and_clean_text(text, max_length)
    return result['success']

# 快速获取字符数的便捷函数
def quick_count(text):
    """
    快速获取字符数的便捷函数
    
    Args:
        text (str): 需要统计的文本
        
    Returns:
        int: 字符数
    """
    return count_characters(text)
