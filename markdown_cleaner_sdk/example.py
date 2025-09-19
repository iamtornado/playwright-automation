#!/usr/bin/env python3
"""
Markdown清理工具使用示例

演示如何使用MarkdownCleaner类进行编程式操作
"""

from markdown_cleaner import MarkdownCleaner


def example_basic_usage():
    """基本使用示例"""
    print("=== 基本使用示例 ===")
    
    # 创建清理器实例
    cleaner = MarkdownCleaner(
        keywords=["微信公众号", "AI发烧友"],
        mode="contains",
        case_sensitive=False,
        backup=True
    )
    
    # 清理文件
    try:
        result = cleaner.clean_file("../markdown_files/craXcel，一个可以移除Excel密码的开源工具.md")
        
        print(f"清理完成!")
        print(f"原行数: {result['original_lines']}")
        print(f"删除行数: {result['removed_lines']}")
        print(f"剩余行数: {result['remaining_lines']}")
        
        if result['removed_content']:
            print("\n删除的内容:")
            for item in result['removed_content']:
                print(f"  第{item['line_number']}行: {item['content']}")
                
    except Exception as e:
        print(f"错误: {e}")


def example_dynamic_keywords():
    """动态关键字管理示例"""
    print("\n=== 动态关键字管理示例 ===")
    
    cleaner = MarkdownCleaner()
    
    # 添加关键字
    cleaner.add_keyword("广告")
    cleaner.add_keyword("推广")
    cleaner.add_keyword("关注")
    
    print(f"当前关键字: {cleaner.list_keywords()}")
    
    # 移除关键字
    cleaner.remove_keyword("广告")
    print(f"移除'广告'后: {cleaner.list_keywords()}")


def example_regex_mode():
    """正则表达式模式示例"""
    print("\n=== 正则表达式模式示例 ===")
    
    cleaner = MarkdownCleaner(
        keywords=[r".*关注.*微信公众号.*"],
        mode="regex",
        case_sensitive=False
    )
    
    print(f"使用正则表达式模式: {cleaner.list_keywords()}")


if __name__ == "__main__":
    example_basic_usage()
    example_dynamic_keywords()
    example_regex_mode()
