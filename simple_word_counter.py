#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单字数统计脚本
快速计算字符串的字数（每个字符都算一个字）

功能说明：
- 计算字符串总字符数
- 交互式输入界面
- 命令行参数支持

字数计算规则：
一个英文字母、一个空格、一个标点符号都算一个字

使用方法：
1. 交互式使用：
   python simple_word_counter.py

2. 命令行参数：
   python simple_word_counter.py "Hello World!"
   python simple_word_counter.py --demo
   python simple_word_counter.py Hello World 123 !

3. 在Python代码中使用：
   from simple_word_counter import count_characters
   count = count_characters("Hello World!")
   print(f"字符数: {count}")  # 输出: 字符数: 12

测试用例：
- "Hello" → 5个字符 (纯英文)
- "你好" → 2个字符 (纯中文)
- "Hello World!" → 12个字符 (英文+空格+标点)
- "你好世界！" → 5个字符 (中文+标点)
- "Hello 世界!" → 9个字符 (中英文混合)
- "123" → 3个字符 (纯数字)
- "" → 0个字符 (空字符串)
- " " → 1个字符 (单个空格)

系统要求：
- Python 3.6+
- 无需额外依赖包
"""

def remove_spaces_between_chinese_english(text):
    """
    移除中文字符和英文字符之间的空格
    
    Args:
        text (str): 需要处理的字符串
        
    Returns:
        str: 处理后的字符串
    """
    import re
    
    # 匹配中文字符和英文字母之间的一个或多个空格
    # 中文字符范围：\u4e00-\u9fff
    # 英文字母：a-zA-Z
    
    # 中文字符后面跟着空格再跟着英文字母
    pattern1 = r'([\u4e00-\u9fff])\s+([a-zA-Z])'
    # 英文字母后面跟着空格再跟着中文字符
    pattern2 = r'([a-zA-Z])\s+([\u4e00-\u9fff])'
    
    # 替换操作：移除空格
    text = re.sub(pattern1, r'\1\2', text)
    text = re.sub(pattern2, r'\1\2', text)
    
    return text

def count_characters(text):
    """
    计算字符串中的字符数
    注意：一个英文字母、一个空格、一个标点符号都算一个字
    
    Args:
        text (str): 需要统计的字符串
        
    Returns:
        int: 字符总数
    """
    return len(text)

def check_length_warning(count, text_type=""):
    """
    检查字符数是否超过120，如果超过则显示警告
    
    Args:
        count (int): 字符数
        text_type (str): 文本类型描述
    """
    if count > 120:
        print(f"⚠️  警告：{text_type}字符数为 {count}，已超过120字符！")
        print(f"   建议：考虑缩短文本内容以提高可读性")
        return True
    return False

def validate_and_clean_text(text, max_length=120):
    """
    验证并清理文本，确保字符数不超过指定限制
    
    Args:
        text (str): 需要验证的文本
        max_length (int): 最大字符数限制，默认120
        
    Returns:
        dict: 包含处理结果的字典
            - 'success': bool, 是否处理成功
            - 'original_text': str, 原始文本
            - 'cleaned_text': str, 清理后的文本
            - 'original_count': int, 原始字符数
            - 'cleaned_count': int, 清理后字符数
            - 'message': str, 处理结果信息
    """
    original_count = count_characters(text)
    
    # 始终尝试清理中英文之间的空格
    cleaned_text = remove_spaces_between_chinese_english(text)
    cleaned_count = count_characters(cleaned_text)
    
    result = {
        'success': True,
        'original_text': text,
        'cleaned_text': cleaned_text,
        'original_count': original_count,
        'cleaned_count': cleaned_count,
        'message': ''
    }
    
    # 如果原始文本长度在限制内
    if original_count <= max_length:
        if cleaned_count < original_count:
            # 有空格被清理，但原文本已经合规
            spaces_removed = original_count - cleaned_count
            result['message'] = f"✅ 文本长度合规（{original_count}字符 ≤ {max_length}字符），可优化减少{spaces_removed}个字符"
        else:
            # 没有空格需要清理
            result['message'] = f"✅ 文本长度合规（{original_count}字符 ≤ {max_length}字符）"
        return result
    
    # 原始文本超长，检查清理后的长度
    if cleaned_count <= max_length:
        spaces_removed = original_count - cleaned_count
        result['message'] = f"✅ 清理空格后文本长度合规（{original_count} → {cleaned_count}字符，减少了{spaces_removed}个字符）"
        return result
    
    # 清理后仍然超长
    result['success'] = False
    result['message'] = f"❌ 文本过长：原始{original_count}字符，清理后{cleaned_count}字符，仍超过{max_length}字符限制"
    
    return result

def show_help():
    """显示帮助信息"""
    help_text = """
字数统计脚本使用说明
==================

功能：计算指定字符串的字数
规则：一个英文字母、一个空格、一个标点符号都算一个字

使用方法：
---------
1. 交互式使用：
   python simple_word_counter.py

2. 命令行直接统计：
   python simple_word_counter.py "Hello World!"
   python simple_word_counter.py Hello World 123 !

3. 处理中英文空格（移除中文和英文之间的空格）：
   python simple_word_counter.py --clean --text "中文 English 混合"
   python simple_word_counter.py -c -t "测试 test 文本"

4. 指定输入文本：
   python simple_word_counter.py --text "要统计的文本"
   python simple_word_counter.py -t "Hello World!"

5. 查看演示：
   python simple_word_counter.py --demo

6. 查看帮助：
   python simple_word_counter.py --help

7. 在Python代码中使用：
   from simple_word_counter import count_characters
   count = count_characters("Hello World!")

测试示例：
---------
"Hello" → 5个字符 (纯英文)
"你好" → 2个字符 (纯中文)
"Hello World!" → 12个字符 (英文+空格+标点)
"你好世界！" → 5个字符 (中文+标点)
"Hello 世界!" → 9个字符 (中英文混合)
"123" → 3个字符 (纯数字)
"" → 0个字符 (空字符串)
" " → 1个字符 (单个空格)

注意事项：
---------
- 换行符(\\n)、制表符(\\t)等特殊字符也会被计算
- 支持中文、英文、数字、标点符号等所有字符
- 脚本使用UTF-8编码，完全支持中文
- 使用 --clean 参数可以移除中英文之间的空格
- 字符数超过120时会显示警告提示

新功能示例：
----------
原文: "中文 English 混合 text"
处理后: "中文English混合text"
效果: 移除了中文和英文字母之间的空格
"""
    print(help_text)

def main():
    """主函数"""
    print("简单字数统计工具")
    print("注意：一个英文字母、一个空格、一个标点符号都算一个字")
    print("输入 'help' 查看详细使用说明，'clean:文本' 可处理中英文空格")
    print("-" * 60)
    
    while True:
        # 获取用户输入
        text = input("\n请输入要统计的文本（输入 'quit' 退出，'help' 查看帮助）: ")
        
        # 检查是否退出
        if text.lower() == 'quit':
            print("再见！")
            break
        elif text.lower() == 'help':
            show_help()
            continue
        elif text.lower().startswith('clean:'):
            # 处理中英文空格功能
            original_text = text[6:]  # 移除 'clean:' 前缀
            if original_text:
                # 处理原文
                cleaned_text = remove_spaces_between_chinese_english(original_text)
                
                # 计算原文字数
                original_count = count_characters(original_text)
                cleaned_count = count_characters(cleaned_text)
                
                # 显示结果
                print(f"原文: \"{original_text}\"")
                print(f"原文字符数: {original_count}")
                check_length_warning(original_count, "原文")
                
                if original_text != cleaned_text:
                    print(f"处理后: \"{cleaned_text}\"")
                    print(f"处理后字符数: {cleaned_count}")
                    check_length_warning(cleaned_count, "处理后")
                    print(f"减少了 {original_count - cleaned_count} 个字符")
                else:
                    print("文本无需处理（没有中英文之间的空格）")
            else:
                print("请提供要处理的文本，格式：clean:您的文本")
            continue
        
        # 计算字数
        char_count = count_characters(text)
        
        # 显示结果
        print(f"字符数: {char_count}")
        print(f"原文: \"{text}\"")
        
        # 检查长度警告
        check_length_warning(char_count)

# 命令行使用示例
def demo():
    """演示函数"""
    test_cases = [
        "Hello World!",
        "你好世界！",
        "Hello 世界! 123",
        "This is a test.",
        "包含空格 和标点符号！",
        "Mixed text: 中英文混合 123!@#"
    ]
    
    print("演示不同文本的字数统计：")
    print("=" * 40)
    
    for text in test_cases:
        count = count_characters(text)
        print(f"文本: \"{text}\"")
        print(f"字数: {count}")
        print("-" * 30)

def parse_arguments():
    """解析命令行参数"""
    import sys
    
    args = {
        'help': False,
        'demo': False,
        'clean': False,
        'text': None,
        'interactive': True
    }
    
    i = 1
    while i < len(sys.argv):
        arg = sys.argv[i]
        
        if arg in ['--help', '-h', 'help']:
            args['help'] = True
            args['interactive'] = False
            break
        elif arg == '--demo':
            args['demo'] = True
            args['interactive'] = False
            break
        elif arg in ['--clean', '-c']:
            args['clean'] = True
            args['interactive'] = False
        elif arg in ['--text', '-t']:
            # 获取下一个参数作为文本
            if i + 1 < len(sys.argv):
                args['text'] = sys.argv[i + 1]
                args['interactive'] = False
                i += 1  # 跳过下一个参数，因为已经作为文本处理了
            else:
                print("错误：--text 参数需要提供文本内容")
                print("用法：python simple_word_counter.py --text \"您的文本\"")
                return None
        else:
            # 如果没有指定 --text 参数，将所有剩余参数作为文本（向后兼容）
            if args['text'] is None and not args['help'] and not args['demo']:
                args['text'] = ' '.join(sys.argv[i:])
                args['interactive'] = False
                break
        
        i += 1
    
    return args

if __name__ == "__main__":
    import sys
    
    # 解析命令行参数
    args = parse_arguments()
    
    if args is None:
        # 参数解析失败
        sys.exit(1)
    
    # 根据参数执行相应功能
    if args['help']:
        show_help()
    elif args['demo']:
        demo()
    elif args['text'] is not None:
        # 有文本输入
        original_text = args['text']
        
        if args['clean']:
            # 处理中英文空格功能
            cleaned_text = remove_spaces_between_chinese_english(original_text)
            
            # 计算字数
            original_count = count_characters(original_text)
            cleaned_count = count_characters(cleaned_text)
            
            # 显示结果
            print("=== 中英文空格处理结果 ===")
            print(f"原文: \"{original_text}\"")
            print(f"原文字符数: {original_count}")
            check_length_warning(original_count, "原文")
            
            if original_text != cleaned_text:
                print(f"处理后: \"{cleaned_text}\"")
                print(f"处理后字符数: {cleaned_count}")
                check_length_warning(cleaned_count, "处理后")
                print(f"✅ 成功减少了 {original_count - cleaned_count} 个字符")
            else:
                print("ℹ️  文本无需处理（没有中英文之间的空格）")
        else:
            # 普通字数统计
            count = count_characters(original_text)
            print(f"文本: \"{original_text}\"")
            print(f"字数: {count}")
            check_length_warning(count)
    elif args['clean']:
        # 只有 --clean 参数但没有文本
        print("错误：--clean 参数需要配合 --text 参数使用")
        print("用法：python simple_word_counter.py --clean --text \"您的文本\"")
        print("或者：python simple_word_counter.py -c -t \"您的文本\"")
    else:
        # 运行交互式模式
        main()
