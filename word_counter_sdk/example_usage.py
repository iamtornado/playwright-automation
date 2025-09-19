#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Word Counter SDK 使用示例

演示如何使用字数统计SDK的各种功能
"""

# 导入SDK
from word_counter_sdk import (
    count_characters,
    remove_spaces_between_chinese_english,
    validate_and_clean_text,
    quick_validate,
    quick_count
)

def example_basic_counting():
    """基本字数统计示例"""
    print("=" * 50)
    print("1. 基本字数统计示例")
    print("=" * 50)
    
    test_texts = [
        "Hello World!",
        "你好世界！",
        "Hello 世界! 123",
        "Mixed text: 中英文混合 123!@#",
        "包含空格 和标点符号！"
    ]
    
    for text in test_texts:
        count = count_characters(text)
        print(f"文本: \"{text}\"")
        print(f"字符数: {count}")
        print("-" * 30)

def example_space_cleaning():
    """中英文空格清理示例"""
    print("\n" + "=" * 50)
    print("2. 中英文空格清理示例")
    print("=" * 50)
    
    test_texts = [
        "中文 English 混合",
        "测试 test 文本",
        "AI 人工智能 machine learning",
        "Python 编程语言 programming"
    ]
    
    for text in test_texts:
        cleaned = remove_spaces_between_chinese_english(text)
        original_count = count_characters(text)
        cleaned_count = count_characters(cleaned)
        
        print(f"原文: \"{text}\" ({original_count}字符)")
        print(f"处理后: \"{cleaned}\" ({cleaned_count}字符)")
        print(f"减少: {original_count - cleaned_count}字符")
        print("-" * 30)

def example_text_validation():
    """文本验证示例"""
    print("\n" + "=" * 50)
    print("3. 文本验证示例")
    print("=" * 50)
    
    test_texts = [
        "这是一个短文本",
        "这是一个稍长的文本 with English words 包含中英文混合内容",
        "这是一个很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长的超长文本示例"
    ]
    
    for text in test_texts:
        result = validate_and_clean_text(text, max_length=120)
        print(f"原文: \"{text[:50]}{'...' if len(text) > 50 else ''}\"")
        print(f"结果: {result['message']}")
        if result['original_text'] != result['cleaned_text']:
            print(f"优化后: \"{result['cleaned_text'][:50]}{'...' if len(result['cleaned_text']) > 50 else ''}\"")
        print("-" * 30)

def example_quick_functions():
    """快速函数示例"""
    print("\n" + "=" * 50)
    print("4. 快速函数示例")
    print("=" * 50)
    
    test_texts = [
        "短文本",
        "这是一个适中长度的文本示例",
        "这是一个超过120字符限制的很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长很长的文本示例"
    ]
    
    for text in test_texts:
        count = quick_count(text)
        is_valid = quick_validate(text, 120)
        
        print(f"文本: \"{text[:30]}{'...' if len(text) > 30 else ''}\"")
        print(f"字符数: {count}")
        print(f"是否符合120字限制: {'✅ 是' if is_valid else '❌ 否'}")
        print("-" * 30)

def example_integration_with_ai():
    """与AI功能集成示例"""
    print("\n" + "=" * 50)
    print("5. 与AI功能集成示例")
    print("=" * 50)
    
    # 模拟豆包AI生成的总结文本
    ai_generated_texts = [
        "本文介绍了 AI 技术在现代社会中的应用",
        "这篇文章详细探讨了 machine learning 算法的基本原理和实际应用场景，包括监督学习、无监督学习等多个方面",
        "文章深入分析了 deep learning 深度学习技术的发展历程，从最初的感知机到现在的 transformer 架构，展现了人工智能技术的巨大进步和未来发展潜力"
    ]
    
    print("模拟豆包AI生成的总结文本验证：")
    for i, text in enumerate(ai_generated_texts, 1):
        print(f"\nAI总结 {i}:")
        result = validate_and_clean_text(text, max_length=120)
        
        print(f"原文: \"{text}\"")
        print(f"字符数: {result['original_count']}")
        
        if result['success']:
            print(f"✅ {result['message']}")
            if result['cleaned_text'] != result['original_text']:
                print(f"优化后: \"{result['cleaned_text']}\"")
                print(f"优化后字符数: {result['cleaned_count']}")
        else:
            print(f"❌ {result['message']}")
            print("建议：需要进一步缩短文本内容")

def main():
    """主函数 - 运行所有示例"""
    print("Word Counter SDK 使用示例")
    print("=" * 60)
    
    # 运行所有示例
    example_basic_counting()
    example_space_cleaning()
    example_text_validation()
    example_quick_functions()
    example_integration_with_ai()
    
    print("\n" + "=" * 60)
    print("所有示例运行完成！")
    print("\n在您的代码中使用：")
    print("from word_counter_sdk import count_characters, validate_and_clean_text")
    print("result = validate_and_clean_text('您的文本', max_length=120)")

if __name__ == "__main__":
    main()
