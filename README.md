# 社交媒体自动发布测试脚本

## 项目简介

这是一个基于 Playwright 的自动化测试脚本，用于将 Markdown 格式的文章自动发布到多个社交媒体平台。支持微信公众号、知乎、CSDN、51CTO、博客园、小红书、抖音、快手、哔哩哔哩等主流平台。

## 主要特性

- 🚀 **多平台支持**：一键发布到多个社交媒体平台
- 🔄 **智能转换**：使用 mdnice 将 Markdown 转换为微信公众号兼容格式
- ✨ **自动填充**：自动填充标题、作者、摘要、封面图片等信息
- 🤖 **AI 智能生成**：集成豆包AI自动生成摘要、话题标签、短标题和封面图
- 📄 **钉钉文档集成**：自动从钉钉文档下载Markdown文件和获取URL
- 🎨 **AI 图片生成**：支持豆包AI和Gemini AI自动生成文章封面图
- 💾 **草稿保存**：自动保存为草稿，避免意外丢失
- 🎥 **视频录制**：自动录制操作过程，便于调试和演示
- 📸 **截图保存**：为每个平台保存操作截图
- 🔍 **智能调试**：提供详细的调试脚本和trace分析功能

## 支持平台

| 平台 | 类型 | 说明 |
|------|------|------|
| mdnice | 格式转换 | Markdown 转微信公众号格式 |
| wechat | 公众号 | 微信公众号文章发布 |
| zhihu | 专栏 | 知乎专栏文章发布 |
| csdn | 博客 | CSDN 博客文章发布 |
| 51cto | 博客 | 51CTO 博客文章发布 |
| cnblogs | 博客 | 博客园文章发布 |
| xiaohongshu_newspic | 图文 | 小红书图文发布 |
| douyin_newspic | 图文 | 抖音图文发布 |
| kuaishou_newspic | 图文 | 快手图文发布 |
| bilibili_newspic | 专栏 | 哔哩哔哩专栏发布 |

## 环境要求

- Python 3.9+
- Playwright
- uv
- 已安装的浏览器（Chrome/Chromium）
- 各平台的登录账号
- 豆包AI账号（用于AI功能）
- Google账号（用于Gemini AI图片生成）
- 微信公众号开发者账号（用于素材上传）

## 安装步骤

### 1. 克隆项目

```bash
git clone <repository-url>
cd playwright-automation
```

### 2. 安装依赖

```bash
# 使用 pip 安装
pip install -r requirements.txt

# 或使用 uv 安装
uv sync

# 安装额外的AI功能依赖
pip install pyperclip pillow
```

### 3. 安装 Playwright 浏览器

```bash
playwright install chromium
```

### 4. 配置环境变量

设置微信公众号开发者账号信息：

```bash
# Windows (命令提示符)
set WECHAT_APP_ID=your_app_id
set WECHAT_APP_SECRET=your_app_secret

# Windows (PowerShell)
$env:WECHAT_APP_ID='your_app_id'
$env:WECHAT_APP_SECRET='your_app_secret'

# Linux/macOS
export WECHAT_APP_ID=your_app_id
export WECHAT_APP_SECRET=your_app_secret
```

### 5. 配置浏览器用户数据目录

确保 `conftest.py` 中的 `--user-data-dir` 路径正确：

```python
parser.addoption("--user-data-dir", type=str, 
                 default='D:/tornadofiles/scripts_脚本/github_projects/playwright-automation/chromium-browser-data',
                 help='浏览器用户数据目录')
```

## 使用方法

### 基本用法

```bash
# 使用默认参数运行（需要提供title参数）
pytest -s --headed --video on --screenshot on --tracing on ./test_social_media_automatic_publish.py --title "文章标题"
```

### AI 智能生成功能

```bash
# 使用豆包AI自动生成摘要、话题标签和封面图
pytest -s --headed ./test_social_media_automatic_publish.py \
  --title "文章标题" \
  --summary auto \
  --tags auto \
  --platforms "wechat,zhihu"
```

### 钉钉文档集成

```bash
# 从钉钉文档自动下载Markdown文件和获取URL
pytest -s --headed ./test_social_media_automatic_publish.py \
  --title "钉钉文档中的文章标题" \
  --platforms "all"
```

### 自定义参数运行（Windows）

```bash
uv run pytest `
    -s `
    --headed `
    --video on `
    --screenshot on `
    --full-page-screenshot `
    --tracing on `
    ./test_social_media_automatic_publish.py `
    --platforms zhihu `
    --title "ollama，免费低门槛的开源大模型推理平台" `
    --summary "本文介绍 Ollama，一个免费开源大模型推理平台，可本地运行管理模型。含官网、GitHub 地址，Linux 和 Windows 安装命令，下载、运行等常用命令，API 调用示例，多 GPU 推理支持" `
    --url "https://docs.dingtalk.com/i/nodes/np9zOoBVBYA16qAPTEkzObKgW1DK0g6l" `
    --markdown-file "D:/Users/14266/Downloads/ollama，免费低门槛的开源大模型推理平台.md" `
    --cover-image "D:/Users/14266/Downloads/ollama，免费低门槛的开源大模型推理平台封面图.png"

```

### 自定义参数运行（Linux）

```bash
uv run pytest -s --headed ./test_social_media_automatic_publish.py \
  --title "自定义标题" \
  --author "自定义作者" \
  --summary "自定义摘要" \
  --url "原文链接" \
  --markdown-file "/path/to/article.md" \
  --cover-image "cover.jpg" \
  --platforms "wechat,zhihu"
```

### 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `--title` | string | ✅ | 文章标题（必填参数） |
| `--author` | string | ❌ | 作者名称（可选，默认使用配置值） |
| `--summary` | string | ❌ | 文章摘要（可选，支持'auto'/'doubao'/'豆包'/'ai'使用豆包AI生成） |
| `--url` | string | ❌ | 原文链接（可选，如不指定则从钉钉文档自动获取） |
| `--markdown-file` | string | ❌ | Markdown文件路径（可选，如不指定则从钉钉文档自动下载） |
| `--user-data-dir` | string | ❌ | 浏览器用户数据目录（可选，默认使用配置值） |
| `--platforms` | string | ❌ | 指定要发布到的平台，用逗号分隔，或 'all' 表示所有平台 |
| `--cover-image` | string | ❌ | 文章封面图片路径（可选，如不指定则使用AI自动生成） |
| `--tags` | string | ❌ | 话题标签（可选，支持'auto'/'doubao'/'豆包'/'ai'使用豆包AI生成） |
| `--backup-browser-data` | boolean | ❌ | 是否备份浏览器数据（可选，默认true） |

### 平台选择示例

```bash
# 发布到所有平台
--platforms all

# 只发布到特定平台
--platforms wechat,zhihu
--platforms csdn,51cto
--platforms xiaohongshu_newspic,douyin_newspic

# 只处理格式转换
--platforms mdnice
```

## 配置说明

### conftest.py 配置

在 `conftest.py` 文件中可以设置默认参数：

```python
def pytest_addoption(parser):
    parser.addoption("--title", type=str, 
                     default='默认标题',
                     help='文章标题')
    parser.addoption("--author", type=str, 
                     default='默认作者', 
                     help='作者名称')
    # ... 其他参数
```

### 浏览器配置

脚本会自动配置浏览器环境：

- 地理位置：深圳（22.558033372050147, 113.46251764183725）
- 时区：Asia/Shanghai
- 语言：zh-CN
- 视口：1920x1080
- 视频录制：开启，保存到 `test-results/videos/`
- 截图：为每个平台保存操作截图

## 工作流程

1. **初始化**：启动浏览器，设置环境参数
2. **钉钉文档处理**：自动下载Markdown文件和获取URL（如未指定）
3. **AI 智能生成**：使用豆包AI生成摘要、话题标签、短标题（如未指定）
4. **封面图生成**：使用豆包AI或Gemini AI生成文章封面图（如未指定）
5. **图片压缩**：自动压缩封面图以符合平台要求
6. **微信公众号素材上传**：将封面图上传到微信公众号素材库
7. **钉钉文档更新**：将封面图插入钉钉文档并重新下载
8. **mdnice 转换**：将 Markdown 转换为微信公众号兼容格式
9. **多平台发布**：依次发布到各个指定平台
10. **自动填充**：自动设置标题、作者、摘要、封面等
11. **草稿保存**：自动保存为草稿，避免内容丢失
12. **结果记录**：保存截图、视频录制、操作轨迹

## 注意事项

### 首次使用

1. **账号登录**：首次运行前需要手动登录各平台账号
   - 豆包AI账号：用于AI功能
   - Google账号：用于Gemini AI图片生成
   - 微信公众号账号：用于素材上传
   - 各社交媒体平台账号：用于内容发布
2. **权限设置**：确保各平台账号有发布权限
3. **内容审核**：注意各平台的内容审核规则
4. **环境变量配置**：设置微信公众号开发者账号信息

### 运行建议

1. **测试环境**：建议先在测试环境中验证功能
2. **网络稳定**：确保网络连接稳定，避免上传失败
3. **磁盘空间**：视频录制和截图会生成大量文件
4. **内容合规**：确保发布内容符合各平台规范

### 常见问题

1. **登录失效**：定期检查登录状态，必要时重新登录
2. **元素定位**：如果网站结构变化，可能需要更新选择器
3. **上传失败**：检查文件格式和大小是否符合要求
4. **超时错误**：适当调整等待时间，适应网络环境

## 示例用例

### 发布技术文章

```bash
pytest -s --headed ./test_social_media_automatic_publish.py \
  --title "AutoGPT：可持续运行的智能代理平台" \
  --author "tornadoami" \
  --summary "本文介绍AutoGPT的核心功能和使用方法，包括安装配置、功能特性、应用场景等" \
  --url "https://example.com/autogpt-guide" \
  --markdown-file "./articles/autogpt-guide.md" \
  --cover-image "./images/autogpt-cover.jpg" \
  --platforms "wechat,zhihu,csdn"
```

### 发布产品介绍

```bash
pytest -s --headed ./test_social_media_automatic_publish.py \
  --title "新一代AI助手：让工作更高效" \
  --author "产品团队" \
  --summary "介绍我们最新开发的AI助手产品，展示其核心功能和实际应用效果" \
  --url "https://company.com/ai-assistant" \
  --markdown-file "./articles/ai-assistant.md" \
  --cover-image "./images/ai-assistant-cover.jpg" \
  --platforms "all"
```

## 开发说明

### 项目结构

```
playwright-automation/
├── conftest.py                           # pytest 配置文件
├── test_social_media_automatic_publish.py # 主测试脚本
├── doubao_ai_image_generator.py         # 豆包AI图片生成模块
├── wechat_mp_sdk.py                     # 微信公众号API SDK
├── simple_word_counter.py               # 字数统计工具
├── find_downloads_directory.py          # 下载目录查找工具
├── test_doubao_ai_generate_images.py    # 豆包AI图片生成测试脚本
├── test_dingtalk_editor_debug.py        # 钉钉编辑器调试脚本
├── test_dingtalk_simple_focus.py        # 钉钉简单聚焦测试脚本
├── test_dingtalk_iframe_analysis.py     # 钉钉iframe分析脚本
├── DINGTALK_DEBUG_README.md             # 钉钉调试说明文档
├── README.md                             # 项目说明文档
├── requirements.txt                      # 依赖包列表
├── pyproject.toml                       # 项目配置文件
├── chromium-browser-data/               # 浏览器用户数据目录
├── markdown_files/                      # Markdown文件存储目录
├── generated_images/                    # AI生成的图片存储目录
└── test-results/                        # 测试结果输出目录
    ├── videos/                          # 视频录制文件
    ├── traces/                          # 操作轨迹文件
    ├── doubao_images/                   # 豆包AI生成的图片
    └── screenshot_*.png                 # 各平台截图
```

### 扩展新平台

要添加新的平台支持，需要：

1. 在 `conftest.py` 中添加平台标识
2. 在测试脚本中添加对应的发布逻辑
3. 实现平台特定的元素定位和操作
4. 添加错误处理和状态检查

### 代码规范

- 使用清晰的注释说明每个步骤
- 统一的错误处理机制
- 合理的等待时间和超时设置
- 详细的日志输出便于调试

## 贡献指南

欢迎提交 Issue 和 Pull Request 来改进这个项目！

### 提交规范

1. Fork 项目到自己的仓库
2. 创建功能分支：`git checkout -b feature/new-platform`
3. 提交更改：`git commit -m 'feat: add support for new platform'`
4. 推送分支：`git push origin feature/new-platform`
5. 创建 Pull Request

## 许可证

本项目采用 MIT 许可证，详见 [LICENSE](LICENSE) 文件。

## 联系方式

- 作者：tornadoami
- 版本：1.0.0
- 更新日期：2025年

## 调试功能

### Trace Viewer 使用

```bash
# 打开trace viewer查看操作轨迹
uv run playwright show-trace test-results/trace.zip

# 或使用单个trace文件
uv run playwright show-trace test-results/traces/6a21fd0659eae06a50b06968b7549a32.trace
```

### 调试脚本

- `test_dingtalk_editor_debug.py`：钉钉编辑器调试脚本
- `test_dingtalk_simple_focus.py`：钉钉简单聚焦测试脚本
- `test_dingtalk_iframe_analysis.py`：钉钉iframe分析脚本
- `test_doubao_ai_generate_images.py`：豆包AI图片生成测试脚本

## 更新日志

### v2.0.0 (2025-09-11)
- 🆕 新增豆包AI集成功能
  - 自动生成文章摘要
  - 自动生成话题标签
  - 自动生成短标题
  - 自动生成文章封面图
- 🆕 新增钉钉文档集成
  - 自动下载Markdown文件
  - 自动获取文档URL
  - 自动上传封面图到钉钉文档
- 🆕 新增Gemini AI图片生成
  - 支持Google Gemini AI生成封面图
  - 自动图片压缩功能
- 🆕 新增微信公众号素材管理
  - 自动上传封面图到微信公众号素材库
  - 集成微信公众号API SDK
- 🆕 新增智能调试功能
  - 详细的调试脚本
  - Trace Viewer支持
  - 钉钉编辑器调试工具
- 🔧 优化参数配置
  - 大部分参数改为可选
  - 支持AI自动生成
  - 智能参数验证
- 🔧 优化错误处理
  - 更精确的元素定位
  - 更好的错误恢复机制
  - 详细的日志输出

### v1.0.0 (2025-08-29)
- 初始版本发布
- 支持10个主流社交媒体平台
- 完整的自动化发布流程
- 视频录制和截图功能
- 详细的配置和说明文档

---

**注意**：本脚本仅供学习和研究使用，请遵守各平台的使用条款和内容规范。使用本脚本发布的内容，作者需承担相应的法律责任。
