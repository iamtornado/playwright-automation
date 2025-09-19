# Markdown文件清理工具

一个简易的Python脚本，用于删除Markdown文件中包含指定关键字的行。

## 功能特性

- 🎯 **多种匹配模式**: 支持精确匹配、包含匹配和正则表达式匹配
- 🔍 **灵活的关键字管理**: 支持命令行参数和关键字文件
- 💾 **自动备份**: 处理前自动创建备份文件
- 📝 **详细日志**: 提供详细的操作日志和统计信息
- 🛡️ **安全可靠**: 符合PEP8规范，代码结构清晰，易于扩展

## 安装要求

- Python 3.6+
- 无需额外依赖包

## 使用方法

### 基本用法

```bash
# 删除包含"微信公众号"的行
python markdown_cleaner.py -k "微信公众号" file.md

# 删除包含多个关键字的行
python markdown_cleaner.py -k "微信公众号" -k "AI发烧友" file.md

# 使用关键字文件
python markdown_cleaner.py --keywords-file keywords.txt file.md
```

### 高级选项

```bash
# 精确匹配模式
python markdown_cleaner.py -k "关注微信公众号" --mode exact file.md

# 正则表达式匹配
python markdown_cleaner.py -k ".*关注.*" --mode regex file.md

# 区分大小写
python markdown_cleaner.py -k "WeChat" --case-sensitive file.md

# 不创建备份文件
python markdown_cleaner.py -k "广告" --no-backup file.md

# 显示详细信息
python markdown_cleaner.py -k "推广" --verbose file.md
```

### 命令行参数

| 参数 | 描述 | 默认值 |
|------|------|--------|
| `file` | 要处理的Markdown文件路径 | 必需 |
| `-k, --keyword` | 要匹配的关键字（可多次使用） | 无 |
| `--keywords-file` | 包含关键字的文件路径 | 无 |
| `-m, --mode` | 匹配模式：exact/contains/regex | contains |
| `-c, --case-sensitive` | 区分大小写 | False |
| `--no-backup` | 不创建备份文件 | False |
| `-v, --verbose` | 显示详细信息 | False |

## 匹配模式说明

### 1. contains（默认）
包含匹配模式，删除包含关键字的行。

```bash
python markdown_cleaner.py -k "微信公众号" file.md
```
会删除包含"微信公众号"的所有行。

### 2. exact
精确匹配模式，只有完全匹配关键字的行才会被删除。

```bash
python markdown_cleaner.py -k "# 关注微信公众号" --mode exact file.md
```
只有完全匹配"# 关注微信公众号"的行才会被删除。

### 3. regex
正则表达式匹配模式，支持复杂的匹配规则。

```bash
python markdown_cleaner.py -k ".*关注.*微信公众号.*" --mode regex file.md
```
使用正则表达式匹配模式。

## 关键字文件格式

创建 `keywords.txt` 文件，每行一个关键字：

```
# 这是注释
微信公众号
AI发烧友
广告
推广
```

## 使用示例

### 示例1：删除微信公众号相关行

```bash
python markdown_cleaner.py -k "微信公众号" -k "AI发烧友" markdown_files/craXcel.md
```

### 示例2：使用关键字文件批量清理

```bash
python markdown_cleaner.py --keywords-file keywords.txt markdown_files/craXcel.md
```

### 示例3：正则表达式删除关注相关行

```bash
python markdown_cleaner.py -k ".*关注.*" --mode regex markdown_files/craXcel.md
```

## 输出示例

```
2024-01-01 10:00:00 - INFO - 已创建备份文件: file.md.backup
2024-01-01 10:00:01 - INFO - 删除第123行: # 关注微信公众号"AI发烧友"，获取更多IT开发运维实用工具与技巧，还有很多AI技术文档！
2024-01-01 10:00:02 - INFO - 清理完成: 原125行，删除1行，剩余124行

清理结果:
文件: file.md
原行数: 125
删除行数: 1
剩余行数: 124
备份文件: file.md.backup
```

## 文件结构

```
markdown_cleaner/
├── markdown_cleaner.py    # 主脚本文件
├── config.py              # 配置文件
├── keywords.txt           # 关键字文件
└── README.md              # 说明文档
```

## 扩展开发

### 添加新的匹配模式

在 `MarkdownCleaner` 类的 `_match_line` 方法中添加新的匹配逻辑：

```python
elif self.mode == 'custom':
    # 自定义匹配逻辑
    if custom_match_logic(line_to_check, keyword_to_check):
        return True
```

### 添加新的配置选项

在 `config.py` 中的 `DEFAULT_CONFIG` 字典中添加新选项：

```python
DEFAULT_CONFIG: Dict[str, Any] = {
    # ... 现有配置
    'new_option': 'default_value',
}
```

## 注意事项

1. **备份重要性**: 建议始终保留备份文件，以防误删重要内容
2. **关键字选择**: 选择关键字时要谨慎，避免误删重要内容
3. **正则表达式**: 使用正则表达式时要确保语法正确
4. **文件编码**: 脚本会自动处理UTF-8和GBK编码的文件

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个工具。
