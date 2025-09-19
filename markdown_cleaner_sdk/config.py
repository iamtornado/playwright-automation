#!/usr/bin/env python3
"""
Markdown清理工具配置文件

该模块包含默认配置和配置管理功能。
"""

from typing import Dict, Any

# 默认配置
DEFAULT_CONFIG: Dict[str, Any] = {
    'mode': 'contains',  # 匹配模式: exact, contains, regex
    'case_sensitive': False,  # 是否区分大小写
    'backup': True,  # 是否创建备份
    'encoding': 'utf-8',  # 文件编码
    'log_level': 'INFO',  # 日志级别
    'keywords_file': 'keywords.txt',  # 默认关键字文件
}

# 支持的匹配模式
SUPPORTED_MODES = ['exact', 'contains', 'regex']

# 支持的文件扩展名
SUPPORTED_EXTENSIONS = ['.md', '.markdown', '.mdown', '.mkdn']

# 日志格式
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

# 备份文件后缀
BACKUP_SUFFIX = '.backup'

# 正则表达式模式示例
REGEX_PATTERNS = {
    'wechat_public_account': r'.*微信公众号.*',
    'follow_us': r'.*关注.*我们.*',
    'qr_code': r'.*扫码.*关注.*',
    'click_follow': r'.*点击.*关注.*',
}

def get_config(config_file: str = None) -> Dict[str, Any]:
    """
    获取配置
    
    Args:
        config_file: 配置文件路径
        
    Returns:
        配置字典
    """
    import json
    import os
    from pathlib import Path
    
    config = DEFAULT_CONFIG.copy()
    
    if config_file and os.path.exists(config_file):
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                config.update(user_config)
        except (json.JSONDecodeError, IOError) as e:
            print(f"警告: 无法读取配置文件 {config_file}: {e}")
    
    return config

def save_config(config: Dict[str, Any], config_file: str) -> None:
    """
    保存配置到文件
    
    Args:
        config: 配置字典
        config_file: 配置文件路径
    """
    import json
    
    try:
        with open(config_file, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    except IOError as e:
        print(f"错误: 无法保存配置文件 {config_file}: {e}")
