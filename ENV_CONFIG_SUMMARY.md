# 环境变量配置优化总结

## 完成的更改

### 1. 创建了 `.env.example` 文件
- 包含微信和钉钉所需的所有环境变量
- 提供了详细的配置说明和使用方法
- 支持 Linux/macOS 和 Windows 系统的环境变量设置示例

### 2. 更新了 `.gitignore` 文件
- 添加了 `.env` 到忽略列表，防止敏感信息被提交到版本控制

### 3. 修改了主脚本 `test_social_media_automatic_publish.py`
- 添加了 `python-dotenv` 库的导入和 `.env` 文件加载功能
- 更新了环境变量检查的错误提示信息，优先推荐使用 `.env` 文件
- 提供了更友好的错误指导和解决方案

### 4. 更新了 `pyproject.toml` 文件
- 添加了 `python-dotenv>=1.0.0` 依赖

### 5. 更新了 `README.md` 文件
- 修改了环境变量配置说明，优先推荐使用 `.env` 文件
- 添加了 `python-dotenv` 安装说明

## 使用方法

### 推荐方式：使用 `.env` 文件
```bash
# 1. 复制示例文件
cp .env.example .env

# 2. 编辑 .env 文件，填入实际配置
# 编辑 .env 文件，将示例值替换为你的实际API密钥
```

### 备选方式：设置系统环境变量
```bash
# Linux/macOS
export WECHAT_APP_ID=your_app_id
export WECHAT_APP_SECRET=your_app_secret
export DINGTALK_APP_KEY=your_app_key
export DINGTALK_APP_SECRET=your_app_secret
export DINGTALK_USER_ID=your_user_id

# Windows (PowerShell)
$env:WECHAT_APP_ID='your_app_id'
$env:WECHAT_APP_SECRET='your_app_secret'
$env:DINGTALK_APP_KEY='your_app_key'
$env:DINGTALK_APP_SECRET='your_app_secret'
$env:DINGTALK_USER_ID='your_user_id'
```

## 环境变量说明

| 变量名 | 说明 | 获取方式 |
|--------|------|----------|
| `WECHAT_APP_ID` | 微信公众号的AppID | 微信公众平台 |
| `WECHAT_APP_SECRET` | 微信公众号的AppSecret | 微信公众平台 |
| `DINGTALK_APP_KEY` | 钉钉应用的AppKey | 钉钉开放平台 |
| `DINGTALK_APP_SECRET` | 钉钉应用的AppSecret | 钉钉开放平台 |
| `DINGTALK_USER_ID` | 钉钉用户ID | 钉钉开放平台 |

## 安装依赖

如果需要使用 `.env` 文件功能，需要安装 `python-dotenv`：

```bash
pip install python-dotenv
# 或者使用 uv
uv add python-dotenv
```

## 优势

1. **安全性**：`.env` 文件不会被提交到版本控制，保护敏感信息
2. **便利性**：一次配置，永久使用，无需每次设置环境变量
3. **兼容性**：支持系统环境变量和 `.env` 文件两种方式
4. **友好性**：提供详细的错误提示和解决方案
5. **标准化**：遵循业界最佳实践，使用标准的 `.env` 文件格式

## 注意事项

- `.env` 文件包含敏感信息，请勿提交到版本控制
- 确保 `.env` 文件权限设置正确，避免被其他用户读取
- 如果同时设置了系统环境变量和 `.env` 文件，系统环境变量优先级更高
