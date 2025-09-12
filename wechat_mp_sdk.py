"""
微信公众号API Python SDK
专注于上传永久素材功能

基于微信官方文档：
- 获取接口调用凭据: https://developers.weixin.qq.com/doc/subscription/api/base/api_getaccesstoken.html
- 上传永久素材: https://developers.weixin.qq.com/doc/subscription/api/material/permanent/api_addmaterial.html
"""

import requests
import json
import os
import time
from typing import Optional, Dict, Any, Union
from urllib.parse import urljoin


class WeChatMPSDK:
    """微信公众号API SDK"""
    
    BASE_URL = "https://api.weixin.qq.com"
    
    def __init__(self, app_id: str, app_secret: str):
        """
        初始化SDK
        
        Args:
            app_id: 微信公众号的AppID
            app_secret: 微信公众号的AppSecret
        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = None
        self.token_expires_at = 0
        
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        发送HTTP请求
        
        Args:
            method: HTTP方法 (GET, POST)
            endpoint: API端点
            **kwargs: 请求参数
            
        Returns:
            API响应数据
            
        Raises:
            Exception: 请求失败时抛出异常
        """
        url = urljoin(self.BASE_URL, endpoint)
        
        try:
            response = requests.request(method, url, **kwargs)
            response.raise_for_status()
            
            data = response.json()
            
            # 检查微信API返回的错误码
            if 'errcode' in data and data['errcode'] != 0:
                raise Exception(f"微信API错误: {data.get('errmsg', '未知错误')} (错误码: {data['errcode']})")
                
            return data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"网络请求失败: {str(e)}")
        except json.JSONDecodeError as e:
            raise Exception(f"响应解析失败: {str(e)}")
    
    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        获取接口调用凭据 (access_token)
        
        参考文档: https://developers.weixin.qq.com/doc/subscription/api/base/api_getaccesstoken.html
        
        Args:
            force_refresh: 是否强制刷新token
            
        Returns:
            access_token字符串
            
        Raises:
            Exception: 获取失败时抛出异常
        """
        # 检查token是否还有效（提前5分钟刷新）
        current_time = time.time()
        if not force_refresh and self.access_token and current_time < (self.token_expires_at - 300):
            return self.access_token
        
        params = {
            'grant_type': 'client_credential',
            'appid': self.app_id,
            'secret': self.app_secret
        }
        
        data = self._make_request('GET', '/cgi-bin/token', params=params)
        
        self.access_token = data['access_token']
        # 微信token有效期为7200秒，这里设置过期时间
        self.token_expires_at = current_time + data.get('expires_in', 7200)
        
        return self.access_token
    
    def upload_permanent_material(self, 
                                 file_path: str, 
                                 material_type: str = 'image',
                                 title: Optional[str] = None,
                                 introduction: Optional[str] = None) -> Dict[str, Any]:
        """
        上传永久素材
        
        参考文档: https://developers.weixin.qq.com/doc/subscription/api/material/permanent/api_addmaterial.html
        
        Args:
            file_path: 文件路径
            material_type: 素材类型 (image, voice, video, thumb)
            title: 视频素材的标题（仅video类型需要）
            introduction: 视频素材的描述（仅video类型需要）
            
        Returns:
            包含media_id等信息的字典
            
        Raises:
            Exception: 上传失败时抛出异常
        """
        if not os.path.exists(file_path):
            raise Exception(f"文件不存在: {file_path}")
        
        # 获取access_token
        access_token = self.get_access_token()
        
        # 构建请求URL
        url = f"{self.BASE_URL}/cgi-bin/material/add_material"
        params = {
            'access_token': access_token,
            'type': material_type
        }
        
        # 准备文件上传
        with open(file_path, 'rb') as file:
            files = {
                'media': (os.path.basename(file_path), file, self._get_content_type(file_path))
            }
            
            # 对于视频素材，需要额外的描述信息
            data = {}
            if material_type == 'video':
                if not title:
                    raise Exception("视频素材必须提供title参数")
                if not introduction:
                    raise Exception("视频素材必须提供introduction参数")
                
                description = {
                    'title': title,
                    'introduction': introduction
                }
                data['description'] = json.dumps(description, ensure_ascii=False)
            
            try:
                response = requests.post(url, params=params, files=files, data=data)
                response.raise_for_status()
                
                result = response.json()
                
                # 检查微信API返回的错误码
                if 'errcode' in result and result['errcode'] != 0:
                    raise Exception(f"微信API错误: {result.get('errmsg', '未知错误')} (错误码: {result['errcode']})")
                
                return result
                
            except requests.exceptions.RequestException as e:
                raise Exception(f"上传请求失败: {str(e)}")
            except json.JSONDecodeError as e:
                raise Exception(f"响应解析失败: {str(e)}")
    
    def _get_content_type(self, file_path: str) -> str:
        """
        根据文件扩展名获取Content-Type
        
        Args:
            file_path: 文件路径
            
        Returns:
            Content-Type字符串
        """
        ext = os.path.splitext(file_path)[1].lower()
        
        content_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.mp3': 'audio/mpeg',
            '.wma': 'audio/x-ms-wma',
            '.wav': 'audio/wav',
            '.amr': 'audio/amr',
            '.mp4': 'video/mp4',
            '.avi': 'video/x-msvideo',
            '.mov': 'video/quicktime',
            '.wmv': 'video/x-ms-wmv',
            '.flv': 'video/x-flv',
            '.mkv': 'video/x-matroska'
        }
        
        return content_types.get(ext, 'application/octet-stream')
    
    def upload_image(self, file_path: str) -> Dict[str, Any]:
        """
        上传图片素材的便捷方法
        
        Args:
            file_path: 图片文件路径
            
        Returns:
            包含media_id等信息的字典
        """
        return self.upload_permanent_material(file_path, 'image')
    
    def upload_voice(self, file_path: str) -> Dict[str, Any]:
        """
        上传语音素材的便捷方法
        
        Args:
            file_path: 语音文件路径
            
        Returns:
            包含media_id等信息的字典
        """
        return self.upload_permanent_material(file_path, 'voice')
    
    def upload_video(self, file_path: str, title: str, introduction: str) -> Dict[str, Any]:
        """
        上传视频素材的便捷方法
        
        Args:
            file_path: 视频文件路径
            title: 视频标题
            introduction: 视频描述
            
        Returns:
            包含media_id等信息的字典
        """
        return self.upload_permanent_material(file_path, 'video', title, introduction)
    
    def upload_thumb(self, file_path: str) -> Dict[str, Any]:
        """
        上传缩略图素材的便捷方法
        
        Args:
            file_path: 缩略图文件路径
            
        Returns:
            包含media_id等信息的字典
        """
        return self.upload_permanent_material(file_path, 'thumb')


# 使用示例
if __name__ == "__main__":
    # 从环境变量中读取配置
    app_id = os.getenv("WECHAT_APP_ID")
    app_secret = os.getenv("WECHAT_APP_SECRET")
    
    if not app_id or not app_secret:
        print("❌ 请设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
        print("例如：")
        print("Linux/macOS:")
        print("export WECHAT_APP_ID=your_app_id")
        print("export WECHAT_APP_SECRET=your_app_secret")
        print("")
        print("Windows (命令提示符):")
        print("set WECHAT_APP_ID=your_app_id")
        print("set WECHAT_APP_SECRET=your_app_secret")
        print("")
        print("Windows (PowerShell):")
        print("$env:WECHAT_APP_ID='your_app_id'")
        print("$env:WECHAT_APP_SECRET='your_app_secret'")
        exit(1)
    
    # 初始化SDK
    sdk = WeChatMPSDK(
        app_id=app_id,
        app_secret=app_secret
    )
    
    try:
        # 上传图片素材
        image_path = "D:/Users/14266/Downloads/创建移轴摄影风格画面.png"
        result = sdk.upload_image(image_path)
        print(f"图片上传成功，media_id: {result['media_id']}")
        print(f"图片URL: {result.get('url', 'N/A')}")
        
        # 上传视频素材
        # video_result = sdk.upload_video(
        #     file_path="path/to/your/video.mp4",
        #     title="视频标题",
        #     introduction="视频描述"
        # )
        # print(f"视频上传成功，media_id: {video_result['media_id']}")
        
    except Exception as e:
        print(f"上传失败: {str(e)}")