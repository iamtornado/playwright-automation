# 钉钉API SDK

一个专门用于封装钉钉开放平台服务端API的Python SDK，主要用于搜索钉钉知识库文档并获取详细信息。

## 功能特性

- 🔐 **自动Token管理**: 自动获取和刷新access_token，支持token缓存
- 👤 **用户信息获取**: 根据user_id获取用户详细信息，自动获取operator_id
- 🔍 **文档搜索**: 搜索钉钉知识库中的文档
- 📄 **文档详情**: 获取文档的详细信息，包括URL、创建者、时间等
- 🛡️ **错误处理**: 完善的异常处理机制
- 📚 **易于使用**: 简洁的API设计，符合PEP8标准
- 🔧 **易于扩展**: 模块化设计，便于添加新功能
- ⚡ **现代工具支持**: 支持pip和uv两种依赖管理方式
- 🧪 **完整测试**: 包含单元测试、集成测试和演示脚本

## 安装

### 1. 安装依赖


#### 使用 uv 安装（推荐）

```bash
# 如果项目使用 uv 管理依赖
uv add alibabacloud-dingtalk>=2.0.0
uv add alibabacloud-tea-openapi>=0.3.0
uv add alibabacloud-tea-util>=0.3.0

# 或者直接安装 requirements.txt 中的所有依赖
uv pip install -r requirements.txt

# 或者使用 pyproject.toml 安装（推荐）
uv sync
```

#### 手动安装依赖包

```bash
pip install alibabacloud-dingtalk>=2.0.0
pip install alibabacloud-tea-openapi>=0.3.0
pip install alibabacloud-tea-util>=0.3.0
```

### 2. 获取钉钉应用凭证

在使用SDK之前，您需要在钉钉开放平台创建应用并获取凭证：

1. 访问 [钉钉开放平台](https://open.dingtalk.com/)
2. 登录并进入开发者后台
3. 创建应用或选择现有应用
4. 在"凭据与基础信息"中获取 `App Key` 和 `App Secret`
5. 获取用户的 `user_id`（SDK会自动获取operator_id）

## 快速开始

### 环境准备

#### 使用 uv 创建项目（推荐）

```bash
# 创建新的 Python 项目
uv init my-dingtalk-project
cd my-dingtalk-project

# 添加钉钉SDK依赖
uv add alibabacloud-dingtalk>=2.0.0
uv add alibabacloud-tea-openapi>=0.3.0
uv add alibabacloud-tea-util>=0.3.0

# 激活虚拟环境
uv shell
```

#### 使用 pip 创建项目

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 基本使用（推荐方式）

```python
from dingtalk_sdk import create_sdk

# 创建SDK实例
sdk = create_sdk("your_app_key", "your_app_secret")

# 获取用户信息
user_id = "your_user_id"
user_info = sdk.get_user_info(user_id)
print(f"用户姓名: {user_info['name']}")
print(f"Union ID: {user_info['union_id']}")
print(f"手机号: {user_info['mobile']}")

# 搜索文档并获取详细信息（只需要提供user_id）
keyword = "远程桌面连接断开后本地屏幕没有响应"

# 使用便捷方法，SDK会自动获取operator_id
documents = sdk.search_and_get_document_details_with_user_id(keyword, user_id)

for doc in documents:
    print(f"标题: {doc.title}")
    print(f"URL: {doc.url}")
    print(f"创建者: {doc.creator}")
    print(f"创建时间: {doc.create_time}")
```

### 传统使用方式

```python
from dingtalk_sdk import DingTalkSDK, DingTalkConfig

# 配置信息
config = DingTalkConfig(
    app_key="your_app_key",
    app_secret="your_app_secret"
)

# 创建SDK实例
sdk = DingTalkSDK(config)

# 先获取用户信息获取operator_id
user_info = sdk.get_user_info("your_user_id")
operator_id = user_info['union_id']

# 搜索文档
documents = sdk.search_and_get_document_details("搜索关键词", operator_id)
```

## API 参考

### DingTalkConfig

配置类，用于存储钉钉API的配置信息。

```python
@dataclass
class DingTalkConfig:
    app_key: str          # 应用Key
    app_secret: str       # 应用Secret
    protocol: str = 'https'  # 协议，默认https
    region_id: str = 'central'  # 区域，默认central
```

### DingTalkSDK

主要的SDK类，提供所有API功能。

#### 方法

##### `get_access_token(force_refresh: bool = False) -> str`

获取access_token。

**参数:**
- `force_refresh`: 是否强制刷新token，默认False

**返回:**
- access_token字符串

**异常:**
- `DingTalkSDKError`: 获取token失败时抛出

##### `get_user_info(user_id: str) -> Dict[str, Any]`

获取用户信息（根据userid获取unionid/operator_id）。

**参数:**
- `user_id`: 用户ID

**返回:**
- 用户信息字典，包含unionid等信息

**异常:**
- `DingTalkSDKError`: 获取用户信息失败时抛出

##### `get_operator_id(user_id: str) -> str`

获取操作者ID（unionid）。

**参数:**
- `user_id`: 用户ID

**返回:**
- 操作者ID（unionid）

**异常:**
- `DingTalkSDKError`: 获取操作者ID失败时抛出

##### `search_documents(keyword: str, operator_id: str) -> List[Dict[str, Any]]`

搜索钉钉知识库文档。

**参数:**
- `keyword`: 搜索关键词
- `operator_id`: 操作者ID（unionid）

**返回:**
- 文档列表，每个文档包含基本信息

**异常:**
- `DingTalkSDKError`: 搜索失败时抛出

##### `get_document_details(node_id: str, operator_id: str) -> DocumentInfo`

获取文档详细信息。

**参数:**
- `node_id`: 文档节点ID（dentryUuid）
- `operator_id`: 操作者ID（unionid）

**返回:**
- `DocumentInfo`对象，包含文档的详细信息

**异常:**
- `DingTalkSDKError`: 获取文档详情失败时抛出

##### `search_and_get_document_details(keyword: str, operator_id: str) -> List[DocumentInfo]`

搜索文档并获取详细信息（包括URL）。只获取第一个搜索结果的详细信息。

**参数:**
- `keyword`: 搜索关键词
- `operator_id`: 操作者ID（unionid）

**返回:**
- `DocumentInfo`对象列表，包含完整的文档信息

**异常:**
- `DingTalkSDKError`: 操作失败时抛出

##### `search_documents_with_user_id(keyword: str, user_id: str) -> List[Dict[str, Any]]`

使用user_id搜索文档（自动获取operator_id）。

**参数:**
- `keyword`: 搜索关键词
- `user_id`: 用户ID

**返回:**
- 文档列表，每个文档包含基本信息

**异常:**
- `DingTalkSDKError`: 搜索失败时抛出

##### `get_document_details_with_user_id(node_id: str, user_id: str) -> DocumentInfo`

使用user_id获取文档详细信息（自动获取operator_id）。

**参数:**
- `node_id`: 文档节点ID
- `user_id`: 用户ID

**返回:**
- `DocumentInfo`对象，包含文档的详细信息

**异常:**
- `DingTalkSDKError`: 获取文档详情失败时抛出

##### `search_and_get_document_details_with_user_id(keyword: str, user_id: str) -> List[DocumentInfo]`

使用user_id搜索文档并获取详细信息（自动获取operator_id）。只获取第一个搜索结果的详细信息。

**参数:**
- `keyword`: 搜索关键词
- `user_id`: 用户ID

**返回:**
- `DocumentInfo`对象列表，包含完整的文档信息

**异常:**
- `DingTalkSDKError`: 操作失败时抛出

### DocumentInfo

文档信息数据类，包含文档的详细信息。

```python
@dataclass
class DocumentInfo:
    node_id: str          # 节点ID
    title: str            # 标题
    url: str              # 文档URL
    creator: str          # 创建者
    create_time: str      # 创建时间
    update_time: str      # 更新时间
    file_type: str        # 文件类型
    file_size: int        # 文件大小
    parent_node_id: str   # 父节点ID
```

## 使用示例

### 环境变量配置

推荐使用环境变量来存储敏感信息：

#### 使用 uv 项目

```bash
# 在项目根目录创建 .env 文件
echo "DINGTALK_APP_KEY=your_app_key" >> .env
echo "DINGTALK_APP_SECRET=your_app_secret" >> .env
echo "DINGTALK_USER_ID=your_user_id" >> .env

# 或者使用环境变量
export DINGTALK_APP_KEY="your_app_key"
export DINGTALK_APP_SECRET="your_app_secret"
export DINGTALK_USER_ID="your_user_id"
```

#### 使用 pip 项目

```bash
# Windows (PowerShell)
$env:DINGTALK_APP_KEY="your_app_key"
$env:DINGTALK_APP_SECRET="your_app_secret"
$env:DINGTALK_USER_ID="your_user_id"

# Linux/macOS (Bash)
export DINGTALK_APP_KEY="your_app_key"
export DINGTALK_APP_SECRET="your_app_secret"
export DINGTALK_USER_ID="your_user_id"
```

### 完整示例

```python
import os
from dingtalk_sdk import create_sdk, DingTalkSDKError

def main():
    # 从环境变量获取配置
    app_key = os.getenv('DINGTALK_APP_KEY')
    app_secret = os.getenv('DINGTALK_APP_SECRET')
    user_id = os.getenv('DINGTALK_USER_ID')
    
    if not all([app_key, app_secret, user_id]):
        print("请设置环境变量: DINGTALK_APP_KEY, DINGTALK_APP_SECRET, DINGTALK_USER_ID")
        return
    
    try:
        # 创建SDK实例
        sdk = create_sdk(app_key, app_secret)
        
        # 搜索文档（使用便捷方法，自动获取operator_id）
        keyword = "远程桌面连接断开后本地屏幕没有响应"
        documents = sdk.search_and_get_document_details_with_user_id(keyword, user_id)
        
        print(f"找到 {len(documents)} 个相关文档:")
        for i, doc in enumerate(documents, 1):
            print(f"\n文档 {i}:")
            print(f"  标题: {doc.title}")
            print(f"  URL: {doc.url}")
            print(f"  创建者: {doc.creator}")
            print(f"  创建时间: {doc.create_time}")
            
    except DingTalkSDKError as e:
        print(f"SDK错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")

if __name__ == '__main__':
    main()
```

## 错误处理

SDK使用自定义异常 `DingTalkSDKError` 来处理各种错误情况：

```python
from dingtalk_sdk import DingTalkSDKError

try:
    sdk = create_sdk("app_key", "app_secret")
    documents = sdk.search_and_get_document_details("keyword", "operator_id")
except DingTalkSDKError as e:
    print(f"SDK错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 注意事项

1. **Token管理**: SDK会自动管理access_token的获取和刷新，无需手动处理
2. **权限要求**: 确保您的钉钉应用具有相应的API权限
   - 用户信息获取权限
   - 文档搜索权限
   - 文档详情获取权限
3. **User ID**: 只需要提供user_id，SDK会自动获取operator_id（unionid）
4. **API限制**: 请注意钉钉API的调用频率限制
5. **错误处理**: 建议在生产环境中添加适当的错误处理和重试机制
6. **依赖管理**: 推荐使用uv进行依赖管理，它比pip更快且更可靠
7. **Python版本**: 需要Python 3.7+，推荐使用Python 3.9+
8. **便捷方法**: 推荐使用带`_with_user_id`后缀的方法，简化使用流程
9. **搜索优化**: 搜索并获取详情功能只获取第一个搜索结果的详细信息，避免过多API调用

## 开发说明

### 代码结构

```
dingtalk_sdk/
├── __init__.py              # 包初始化文件
├── dingtalk_sdk.py          # 主要SDK代码
├── example_usage.py         # 使用示例
├── test_dingtalk_sdk.py     # 测试代码
├── demo.py                  # 演示脚本
├── test_import.py           # 包结构测试
├── requirements.txt         # 依赖包列表（pip）
├── pyproject.toml           # 项目配置（uv推荐）
├── README.md               # 文档说明
├── INSTALL.md              # 安装指南
└── PROJECT_SUMMARY.md      # 项目总结
```

### 开发环境设置

#### 使用 uv 开发（推荐）

```bash
# 克隆项目
git clone <repository-url>
cd dingtalk_sdk

# 安装依赖（包括开发依赖）
uv sync --extra dev

# 激活开发环境
uv shell

# 运行测试
python test_dingtalk_sdk.py

# 运行演示
python demo.py

# 运行代码格式化
uv run black .
uv run isort .

# 运行类型检查
uv run mypy dingtalk_sdk.py
```

#### 使用 pip 开发

```bash
# 克隆项目
git clone <repository-url>
cd dingtalk_sdk

# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
# Windows
venv\Scripts\activate
# Linux/macOS
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行测试
python test_dingtalk_sdk.py
```

### 扩展功能

SDK采用模块化设计，便于扩展新功能：

1. 在 `DingTalkSDK` 类中添加新方法
2. 根据需要添加新的数据类
3. 更新配置类以支持新参数
4. 添加相应的测试用例

## 许可证

本项目采用MIT许可证。

## 更多资源

- [uv 使用示例](uv_example.md) - 详细的 uv 使用指南
- [安装指南](INSTALL.md) - 详细的安装和配置说明
- [项目总结](PROJECT_SUMMARY.md) - 项目概述和总结

## 贡献

欢迎提交Issue和Pull Request来改进这个SDK。

## 更新日志

### v1.0.0
- 初始版本
- 支持access_token获取和管理
- 支持用户信息获取功能
- 支持文档搜索功能
- 支持文档详细信息获取
- 完善的错误处理机制
- 支持pip和uv两种依赖管理方式
- 提供pyproject.toml配置文件
- 支持开发依赖和代码质量工具
- 完整的测试套件和文档
- 新增便捷方法，只需提供user_id即可自动获取operator_id
- 简化使用流程，无需手动获取unionid
- 优化搜索功能，只获取第一个搜索结果的详细信息