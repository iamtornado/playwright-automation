# Word Counter SDK

一个简易的字数统计和文本处理SDK，专门用于中英文混合文本的字符数统计和优化。

## 功能特性

- 📊 **精确字符统计**：支持中文、英文、数字、标点符号等所有字符
- 🔧 **智能空格处理**：自动移除中英文之间的多余空格
- ⚠️ **长度验证警告**：自动检查文本是否超过指定长度限制
- 🎯 **豆包AI适配**：专门优化120字符限制验证
- 🚀 **简单易用**：提供便捷的API和丰富的示例
- 💡 **无依赖设计**：纯Python实现，无需额外依赖包

## 安装

将此SDK目录复制到您的项目中，或者直接导入使用。

```bash
# 无需额外依赖，Python 3.6+ 即可使用
```

## 快速开始

### 基本用法

```python
from word_counter_sdk import count_characters, validate_and_clean_text

# 基本字符统计
text = "Hello 世界!"
count = count_characters(text)
print(f"字符数: {count}")  # 输出: 字符数: 9

# 文本验证和优化
result = validate_and_clean_text("中文 English 混合", max_length=120)
print(f"处理结果: {result['message']}")
print(f"优化后文本: {result['cleaned_text']}")
```

### 高级用法

```python
from word_counter_sdk import (
    remove_spaces_between_chinese_english,
    check_length_warning,
    quick_validate,
    quick_count
)

# 移除中英文之间的空格
text = "AI 人工智能 machine learning"
cleaned = remove_spaces_between_chinese_english(text)
print(f"优化后: {cleaned}")  # 输出: AI人工智能machine learning

# 快速验证文本长度
is_valid = quick_validate("测试文本", max_length=120)
print(f"是否符合要求: {is_valid}")

# 快速获取字符数
count = quick_count("Hello World!")
print(f"字符数: {count}")
```

## API 参考

### 核心函数

#### `count_characters(text: str) -> int`
计算字符串中的字符数。

**参数：**
- `text`: 需要统计的字符串

**返回：**
- `int`: 字符总数

#### `validate_and_clean_text(text: str, max_length: int = 120) -> dict`
验证并清理文本，确保字符数不超过指定限制。

**参数：**
- `text`: 需要验证的文本
- `max_length`: 最大字符数限制，默认120

**返回：**
- `dict`: 包含处理结果的字典
  - `success`: 是否处理成功
  - `original_text`: 原始文本
  - `cleaned_text`: 清理后的文本
  - `original_count`: 原始字符数
  - `cleaned_count`: 清理后字符数
  - `message`: 处理结果信息

#### `remove_spaces_between_chinese_english(text: str) -> str`
移除中文字符和英文字符之间的空格。

**参数：**
- `text`: 需要处理的字符串

**返回：**
- `str`: 处理后的字符串

#### `check_length_warning(count: int, text_type: str = "") -> bool`
检查字符数是否超过120，如果超过则显示警告。

**参数：**
- `count`: 字符数
- `text_type`: 文本类型描述

**返回：**
- `bool`: 是否超过120字符

### 便捷函数

#### `quick_validate(text: str, max_length: int = 120) -> bool`
快速验证文本长度。

#### `quick_count(text: str) -> int`
快速获取字符数。

## 使用场景

### 1. 豆包AI文章总结验证

```python
from word_counter_sdk import validate_and_clean_text

# 验证豆包AI生成的总结是否符合120字限制
ai_summary = "这是豆包AI生成的文章总结..."
result = validate_and_clean_text(ai_summary, max_length=120)

if result['success']:
    print("✅ 总结长度合规")
    final_summary = result['cleaned_text']
else:
    print("❌ 总结过长，需要重新生成")
```

### 2. 社交媒体内容优化

```python
from word_counter_sdk import remove_spaces_between_chinese_english, count_characters

# 优化社交媒体发布内容
content = "分享一篇关于 AI 人工智能的文章"
optimized = remove_spaces_between_chinese_english(content)
print(f"优化前: {content} ({count_characters(content)}字符)")
print(f"优化后: {optimized} ({count_characters(optimized)}字符)")
```

### 3. 批量文本处理

```python
from word_counter_sdk import validate_and_clean_text

texts = [
    "文本1...",
    "文本2...",
    "文本3..."
]

for i, text in enumerate(texts, 1):
    result = validate_and_clean_text(text)
    print(f"文本{i}: {result['message']}")
```

## 命令行使用

SDK也支持命令行直接使用：

```bash
# 基本字数统计
python simple_word_counter.py "Hello World!"

# 处理中英文空格
python simple_word_counter.py --clean --text "中文 English 混合"

# 交互式模式
python simple_word_counter.py

# 查看演示
python simple_word_counter.py --demo

# 查看帮助
python simple_word_counter.py --help
```

## 运行示例

```bash
# 运行完整示例
python example_usage.py
```

## 字数计算规则

- **字符统计**：每个字符都算一个字（包括中文、英文、数字、标点符号、空格）
- **空格处理**：可以智能移除中英文之间的多余空格
- **特殊字符**：换行符(\n)、制表符(\t)等也会被计算
- **编码支持**：完全支持UTF-8编码的中文字符

## 测试用例

| 输入 | 输出 | 说明 |
|------|------|------|
| "Hello" | 5个字符 | 纯英文 |
| "你好" | 2个字符 | 纯中文 |
| "Hello World!" | 12个字符 | 英文+空格+标点 |
| "你好世界！" | 5个字符 | 中文+标点 |
| "Hello 世界!" | 9个字符 | 中英文混合 |
| "123" | 3个字符 | 纯数字 |
| "" | 0个字符 | 空字符串 |
| " " | 1个字符 | 单个空格 |

## 注意事项

1. **120字符限制**：专门针对豆包AI的字符数限制优化
2. **空格处理**：只处理中英文字母之间的空格，不影响其他空格
3. **字符编码**：确保文本使用UTF-8编码
4. **性能考虑**：适用于中小型文本处理，大文件请分批处理

## 更新日志

### v1.0.0
- ✨ 初始版本发布
- 📊 基本字符统计功能
- 🔧 中英文空格智能处理
- ⚠️ 120字符限制验证
- 🚀 便捷API设计
- 💡 命令行支持

## 许可证

本项目采用MIT许可证。

## 贡献

欢迎提交Issue和Pull Request！

---

**作者**: tornadoami  
**版本**: 1.0.0
