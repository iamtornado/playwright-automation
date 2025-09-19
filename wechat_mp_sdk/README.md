# 微信公众号API SDK

专门用于封装微信公众号开放平台API的Python SDK，主要功能包括素材管理和上传。

## 功能特性

- ✅ 获取access_token
- ✅ 上传永久素材（图片、语音、视频、缩略图）
- ✅ 自动token管理和刷新
- ✅ 完整的错误处理
- ✅ 类型提示支持
- ✅ 简单易用的API

## 安装

```bash
pip install requests
```

## 快速开始

### 基本用法

```python
from wechat_mp_sdk import WeChatMPSDK

# 初始化SDK
sdk = WeChatMPSDK(
    app_id="your_app_id",
    app_secret="your_app_secret"
)

# 上传图片
result = sdk.upload_image("path/to/your/image.jpg")
print(f"图片上传成功，media_id: {result['media_id']}")
```

### 使用便捷函数

```python
from wechat_mp_sdk import create_sdk

# 创建SDK实例
sdk = create_sdk("your_app_id", "your_app_secret")

# 上传不同类型的素材
image_result = sdk.upload_image("image.jpg")
voice_result = sdk.upload_voice("voice.mp3")
video_result = sdk.upload_video("video.mp4", "视频标题", "视频描述")
thumb_result = sdk.upload_thumb("thumb.jpg")
```

## 环境变量配置

建议使用环境变量来管理敏感信息：

### Linux/macOS
```bash
export WECHAT_APP_ID=your_app_id
export WECHAT_APP_SECRET=your_app_secret
```

### Windows (命令提示符)
```cmd
set WECHAT_APP_ID=your_app_id
set WECHAT_APP_SECRET=your_app_secret
```

### Windows (PowerShell)
```powershell
$env:WECHAT_APP_ID='your_app_id'
$env:WECHAT_APP_SECRET='your_app_secret'
```

然后在代码中使用：

```python
import os
from wechat_mp_sdk import create_sdk

app_id = os.getenv("WECHAT_APP_ID")
app_secret = os.getenv("WECHAT_APP_SECRET")

sdk = create_sdk(app_id, app_secret)
```

## API 文档

### WeChatMPSDK

主要的SDK类，提供所有微信公众号API功能。

#### 初始化

```python
sdk = WeChatMPSDK(app_id, app_secret)
```

#### 方法

- `get_access_token(force_refresh=False)`: 获取访问令牌
- `upload_permanent_material(file_path, material_type, title=None, introduction=None)`: 上传永久素材
- `upload_image(file_path)`: 上传图片素材
- `upload_voice(file_path)`: 上传语音素材
- `upload_video(file_path, title, introduction)`: 上传视频素材
- `upload_thumb(file_path)`: 上传缩略图素材

### 支持的文件格式

#### 图片
- JPG/JPEG
- PNG
- GIF
- BMP

#### 语音
- MP3
- WMA
- WAV
- AMR

#### 视频
- MP4
- AVI
- MOV
- WMV
- FLV
- MKV

## 错误处理

SDK提供了完整的错误处理机制：

```python
from wechat_mp_sdk import WeChatMPSDK, WeChatMPSDKError

try:
    sdk = WeChatMPSDK(app_id, app_secret)
    result = sdk.upload_image("image.jpg")
except WeChatMPSDKError as e:
    print(f"SDK错误: {e}")
except Exception as e:
    print(f"其他错误: {e}")
```

## 贡献

欢迎提交Issue和Pull Request！

## 许可证

MIT License

## 参考文档

- [微信公众号开发文档](https://developers.weixin.qq.com/doc/subscription/)
- [获取接口调用凭据](https://developers.weixin.qq.com/doc/subscription/api/base/api_getaccesstoken.html)
- [上传永久素材](https://developers.weixin.qq.com/doc/subscription/api/material/permanent/api_addmaterial.html)
