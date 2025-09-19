# -*- coding: utf-8 -*-
"""
钉钉API SDK

这个SDK封装了钉钉开放平台的服务端API，主要用于：
1. 获取access_token
2. 查询用户信息
3. 搜索钉钉知识库文档
4. 获取文档详细信息

作者: tornadoami
版本: 1.0.0
website: https://alidocs.dingtalk.com/i/nodes/Amq4vjg890AlRbA6Td9ZvlpDJ3kdP0wQ
"""

from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime, timedelta

try:
    from alibabacloud_dingtalk.oauth2_1_0.client import Client as DingTalkOAuth2Client
    from alibabacloud_dingtalk.oauth2_1_0 import models as oauth2_models
    from alibabacloud_dingtalk.storage_2_0.client import Client as DingTalkStorageClient
    from alibabacloud_dingtalk.storage_2_0 import models as storage_models
    from alibabacloud_dingtalk.wiki_2_0.client import Client as DingTalkWikiClient
    from alibabacloud_dingtalk.wiki_2_0 import models as wiki_models
    from alibabacloud_dingtalk.contact_1_0.client import Client as DingTalkContactClient
    from alibabacloud_dingtalk.contact_1_0 import models as contact_models
    from alibabacloud_tea_openapi import models as open_api_models
    from alibabacloud_tea_util import models as util_models
except ImportError as e:
    raise ImportError(
        "钉钉SDK依赖包未安装。请运行: pip install -r requirements.txt"
    ) from e


@dataclass
class DingTalkConfig:
    """钉钉API配置类"""
    app_key: str
    app_secret: str
    protocol: str = 'https'
    region_id: str = 'central'


@dataclass
class DocumentInfo:
    """文档信息数据类"""
    node_id: str
    title: str
    url: str
    creator: str
    create_time: str
    update_time: str
    file_type: str
    file_size: int
    parent_node_id: str


class DingTalkSDKError(Exception):
    """钉钉SDK自定义异常"""
    pass


class DingTalkSDK:
    """钉钉API SDK主类"""
    
    def __init__(self, config: DingTalkConfig):
        """
        初始化钉钉SDK
        
        Args:
            config: 钉钉API配置
        """
        self.config = config
        self._access_token = None
        self._token_expires_at = None
        
        # 初始化各个API客户端
        self._init_clients()
    
    def _init_clients(self):
        """初始化各种API客户端"""
        # OAuth2客户端配置
        oauth2_config = open_api_models.Config()
        oauth2_config.protocol = self.config.protocol
        oauth2_config.region_id = self.config.region_id
        self.oauth2_client = DingTalkOAuth2Client(oauth2_config)
        
        # Storage客户端配置
        storage_config = open_api_models.Config()
        storage_config.protocol = self.config.protocol
        storage_config.region_id = self.config.region_id
        self.storage_client = DingTalkStorageClient(storage_config)
        
        # Wiki客户端配置
        wiki_config = open_api_models.Config()
        wiki_config.protocol = self.config.protocol
        wiki_config.region_id = self.config.region_id
        self.wiki_client = DingTalkWikiClient(wiki_config)
        
        # Contact客户端配置
        contact_config = open_api_models.Config()
        contact_config.protocol = self.config.protocol
        contact_config.region_id = self.config.region_id
        self.contact_client = DingTalkContactClient(contact_config)
    
    def get_access_token(self, force_refresh: bool = False) -> str:
        """
        获取access_token
        
        Args:
            force_refresh: 是否强制刷新token
            
        Returns:
            access_token字符串
            
        Raises:
            DingTalkSDKError: 获取token失败时抛出
        """
        # 检查token是否还有效
        if (not force_refresh and 
            self._access_token and 
            self._token_expires_at and 
            datetime.now() < self._token_expires_at):
            return self._access_token
        
        try:
            request = oauth2_models.GetAccessTokenRequest(
                app_key=self.config.app_key,
                app_secret=self.config.app_secret
            )
            
            response = self.oauth2_client.get_access_token(request)
            
            if response.body.access_token:
                self._access_token = response.body.access_token
                # 设置过期时间（默认72小时，提前1小时刷新）
                expires_in = getattr(response.body, 'expire_in', 72 * 3600)
                self._token_expires_at = datetime.now() + timedelta(seconds=expires_in - 3600)
                return self._access_token
            else:
                raise DingTalkSDKError("获取access_token失败：响应中无token")
                
        except Exception as e:
            raise DingTalkSDKError(f"获取access_token失败: {str(e)}")
    
    def get_user_info(self, user_id: str) -> Dict[str, Any]:
        """
        获取用户信息（根据userid获取unionid/operator_id）
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户信息字典，包含unionid等信息
            
        Raises:
            DingTalkSDKError: 获取用户信息失败时抛出
        """
        try:
            import requests
            
            access_token = self.get_access_token()
            
            # 使用REST API调用钉钉查询用户详情接口
            url = f"https://oapi.dingtalk.com/user/get"
            params = {
                'access_token': access_token,
                'userid': user_id
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            result = response.json()
            
            # 检查API返回结果
            if result.get('errcode') != 0:
                raise DingTalkSDKError(f"钉钉API错误: {result.get('errmsg', '未知错误')}")
            
            # 解析用户信息 - 数据直接在根级别
            return {
                'user_id': user_id,
                'union_id': result.get('unionid', ''),
                'name': result.get('name', ''),
                'mobile': result.get('mobile', ''),
                'email': result.get('email', ''),
                'avatar_url': result.get('avatar', ''),
                'job_number': result.get('jobnumber', ''),
                'title': result.get('position', ''),
                'dept_id_list': result.get('department', []),
                'leader_in_dept': result.get('isLeaderInDepts', [])
            }
                
        except Exception as e:
            raise DingTalkSDKError(f"获取用户信息失败: {str(e)}")
    
    def get_operator_id(self, user_id: str) -> str:
        """
        获取操作者ID（unionid）
        
        Args:
            user_id: 用户ID
            
        Returns:
            操作者ID（unionid）
            
        Raises:
            DingTalkSDKError: 获取操作者ID失败时抛出
        """
        try:
            user_info = self.get_user_info(user_id)
            union_id = user_info.get('union_id')
            
            if not union_id:
                raise DingTalkSDKError(f"用户 {user_id} 的union_id为空")
            
            return union_id
            
        except Exception as e:
            raise DingTalkSDKError(f"获取操作者ID失败: {str(e)}")
    
    def search_documents(self, keyword: str, operator_id: str) -> List[Dict[str, Any]]:
        """
        搜索钉钉知识库文档
        
        Args:
            keyword: 搜索关键词
            operator_id: 操作者ID（unionid）
            
        Returns:
            文档列表
            
        Raises:
            DingTalkSDKError: 搜索失败时抛出
        """
        try:
            access_token = self.get_access_token()
            
            # 设置请求头
            headers = storage_models.SearchDentriesHeaders()
            headers.x_acs_dingtalk_access_token = access_token
            
            # 设置搜索选项
            option = storage_models.SearchDentriesRequestOption(
                max_results=20
            )
            
            # 设置搜索请求
            request = storage_models.SearchDentriesRequest(
                operator_id=operator_id,
                keyword=keyword,
                option=option
            )
            
            # 执行搜索
            response = self.storage_client.search_dentries_with_options(
                request, 
                headers, 
                util_models.RuntimeOptions()
            )
            
            # 解析响应
            if response.body and hasattr(response.body, 'items') and response.body.items:
                documents = []
                for item in response.body.items:
                    # 解析创建者信息
                    creator_info = getattr(item, 'creator', {})
                    creator_name = getattr(creator_info, 'name', '') if creator_info else ''
                    
                    doc_info = {
                        'node_id': getattr(item, 'dentry_uuid', ''),
                        'title': getattr(item, 'name', ''),
                        'creator': creator_name,
                        'create_time': getattr(item, 'create_time', ''),
                        'update_time': getattr(item, 'update_time', ''),
                        'file_type': getattr(item, 'file_type', ''),
                        'file_size': getattr(item, 'file_size', 0),
                        'parent_node_id': getattr(item, 'parent_node_id', ''),
                        'url': getattr(item, 'url', '')
                    }
                    documents.append(doc_info)
                return documents
            else:
                return []
                
        except Exception as e:
            raise DingTalkSDKError(f"搜索文档失败: {str(e)}")
    
    def get_document_details(self, node_id: str, operator_id: str) -> DocumentInfo:
        """
        获取文档详细信息
        
        Args:
            node_id: 文档节点ID
            operator_id: 操作者ID（unionid）
            
        Returns:
            文档详细信息
            
        Raises:
            DingTalkSDKError: 获取文档详情失败时抛出
        """
        try:
            access_token = self.get_access_token()
            
            # 设置请求头
            headers = wiki_models.GetNodeHeaders()
            headers.x_acs_dingtalk_access_token = access_token
            
            # 设置请求参数 - 根据官方示例代码
            request = wiki_models.GetNodeRequest(
                with_statistical_info=False,
                with_permission_role=False,
                operator_id=operator_id
            )
            
            # 执行请求
            response = self.wiki_client.get_node_with_options(
                node_id,
                request,
                headers,
                util_models.RuntimeOptions()
            )
            
            # 解析响应
            if response.body:
                body = response.body
                # 数据在node字段中
                node_info = getattr(body, 'node', {})
                if node_info:
                    return DocumentInfo(
                        node_id=node_id,
                        title=getattr(node_info, 'name', ''),
                        url=getattr(node_info, 'url', ''),
                        creator=getattr(node_info, 'creatorId', ''),
                        create_time=getattr(node_info, 'createTime', ''),
                        update_time=getattr(node_info, 'modifiedTime', ''),
                        file_type=getattr(node_info, 'extension', ''),
                        file_size=getattr(node_info, 'size', 0),
                        parent_node_id=getattr(node_info, 'parentNodeId', '')
                    )
                else:
                    raise DingTalkSDKError("获取文档详情失败：节点信息为空")
            else:
                raise DingTalkSDKError("获取文档详情失败：响应为空")
                
        except Exception as e:
            raise DingTalkSDKError(f"获取文档详情失败: {str(e)}")
    
    def search_and_get_document_details(self, keyword: str, operator_id: str) -> List[DocumentInfo]:
        """
        搜索文档并获取详细信息（包括URL）
        
        Args:
            keyword: 搜索关键词
            operator_id: 操作者ID（unionid）
            
        Returns:
            文档详细信息列表
            
        Raises:
            DingTalkSDKError: 操作失败时抛出
        """
        try:
            # 先搜索文档
            search_results = self.search_documents(keyword, operator_id)
            
            if not search_results:
                return []
            
            # 只获取第一个文档的详细信息
            detailed_documents = []
            first_doc = search_results[0]
            node_id = first_doc.get('node_id')
            
            if node_id:
                try:
                    details = self.get_document_details(node_id, operator_id)
                    detailed_documents.append(details)
                except DingTalkSDKError as e:
                    print(f"获取文档 {node_id} 详情失败: {e}")
                    # 如果获取详情失败，至少返回搜索到的基本信息
                    basic_info = DocumentInfo(
                        node_id=node_id,
                        title=first_doc.get('title', ''),
                        url=first_doc.get('url', ''),
                        creator=first_doc.get('creator', ''),
                        create_time=first_doc.get('create_time', ''),
                        update_time=first_doc.get('update_time', ''),
                        file_type=first_doc.get('file_type', ''),
                        file_size=first_doc.get('file_size', 0),
                        parent_node_id=first_doc.get('parent_node_id', '')
                    )
                    detailed_documents.append(basic_info)
            
            return detailed_documents
            
        except Exception as e:
            raise DingTalkSDKError(f"搜索并获取文档详情失败: {str(e)}")
    
    def search_documents_with_user_id(self, keyword: str, user_id: str) -> List[Dict[str, Any]]:
        """
        使用user_id搜索文档（自动获取operator_id）
        
        Args:
            keyword: 搜索关键词
            user_id: 用户ID
            
        Returns:
            文档列表
            
        Raises:
            DingTalkSDKError: 操作失败时抛出
        """
        try:
            # 自动获取operator_id
            operator_id = self.get_operator_id(user_id)
            return self.search_documents(keyword, operator_id)
        except Exception as e:
            raise DingTalkSDKError(f"使用user_id搜索文档失败: {str(e)}")
    
    def get_document_details_with_user_id(self, node_id: str, user_id: str) -> DocumentInfo:
        """
        使用user_id获取文档详细信息（自动获取operator_id）
        
        Args:
            node_id: 文档节点ID
            user_id: 用户ID
            
        Returns:
            文档详细信息
            
        Raises:
            DingTalkSDKError: 操作失败时抛出
        """
        try:
            # 自动获取operator_id
            operator_id = self.get_operator_id(user_id)
            return self.get_document_details(node_id, operator_id)
        except Exception as e:
            raise DingTalkSDKError(f"使用user_id获取文档详情失败: {str(e)}")
    
    def search_and_get_document_details_with_user_id(self, keyword: str, user_id: str) -> List[DocumentInfo]:
        """
        使用user_id搜索文档并获取详细信息（自动获取operator_id）
        
        Args:
            keyword: 搜索关键词
            user_id: 用户ID
            
        Returns:
            文档详细信息列表
            
        Raises:
            DingTalkSDKError: 操作失败时抛出
        """
        try:
            # 自动获取operator_id
            operator_id = self.get_operator_id(user_id)
            return self.search_and_get_document_details(keyword, operator_id)
        except Exception as e:
            raise DingTalkSDKError(f"使用user_id搜索并获取文档详情失败: {str(e)}")


def create_sdk(app_key: str, app_secret: str) -> DingTalkSDK:
    """
    创建钉钉SDK实例的便捷函数
    
    Args:
        app_key: 应用Key
        app_secret: 应用Secret
        
    Returns:
        DingTalkSDK实例
    """
    config = DingTalkConfig(app_key=app_key, app_secret=app_secret)
    return DingTalkSDK(config)


# 使用示例
if __name__ == '__main__':
    # 配置信息（请替换为实际的app_key和app_secret）
    APP_KEY = "your_app_key_here"
    APP_SECRET = "your_app_secret_here"
    OPERATOR_ID = "your_operator_id_here"  # 需要先通过其他方式获取
    
    try:
        # 创建SDK实例
        sdk = create_sdk(APP_KEY, APP_SECRET)
        
        # 测试获取access_token
        print("正在获取access_token...")
        token = sdk.get_access_token()
        print(f"access_token: {token[:20]}...")
        
        # 搜索文档
        print("\n正在搜索文档...")
        keyword = "远程桌面连接断开后本地屏幕没有响应"
        documents = sdk.search_and_get_document_details(keyword, OPERATOR_ID)
        
        print(f"\n找到 {len(documents)} 个文档:")
        for i, doc in enumerate(documents, 1):
            print(f"\n文档 {i}:")
            print(f"  标题: {doc.title}")
            print(f"  URL: {doc.url}")
            print(f"  创建者: {doc.creator}")
            print(f"  创建时间: {doc.create_time}")
            print(f"  更新时间: {doc.update_time}")
            print(f"  文件类型: {doc.file_type}")
            print(f"  文件大小: {doc.file_size} bytes")
            
    except DingTalkSDKError as e:
        print(f"SDK错误: {e}")
    except Exception as e:
        print(f"未知错误: {e}")
