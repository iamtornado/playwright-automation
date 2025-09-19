# -*- coding: utf-8 -*-
"""
钉钉SDK使用示例

这个文件展示了如何使用钉钉SDK进行各种操作
"""

import os
from dingtalk_sdk import DingTalkSDK, DingTalkConfig, DingTalkSDKError


def main():
    """主函数 - 演示SDK的基本用法"""
    
    # 配置信息（请替换为实际的配置）
    # 这些信息可以从钉钉开放平台获取
    APP_KEY = os.getenv('DINGTALK_APP_KEY', 'your_app_key_here')
    APP_SECRET = os.getenv('DINGTALK_APP_SECRET', 'your_app_secret_here')
    USER_ID = os.getenv('DINGTALK_USER_ID', 'your_user_id_here')  # 用于获取operator_id
    
    # 检查配置
    if APP_KEY == 'your_app_key_here' or APP_SECRET == 'your_app_secret_here' or USER_ID == 'your_user_id_here':
        print("请先设置环境变量或修改代码中的配置信息：")
        print("DINGTALK_APP_KEY - 钉钉应用的App Key")
        print("DINGTALK_APP_SECRET - 钉钉应用的App Secret")
        print("DINGTALK_USER_ID - 用户ID（用于自动获取operator_id）")
        print("\n注意：不需要手动设置DINGTALK_OPERATOR_ID，SDK会自动通过USER_ID获取")
        return
    
    try:
        # 创建SDK实例
        print("正在初始化钉钉SDK...")
        config = DingTalkConfig(
            app_key=APP_KEY,
            app_secret=APP_SECRET
        )
        sdk = DingTalkSDK(config)
        
        # 1. 获取access_token
        print("\n1. 获取access_token...")
        token = sdk.get_access_token()
        print(f"✓ access_token获取成功: {token[:20]}...")
        
        # 2. 获取用户信息并自动获取operator_id
        print(f"\n2. 获取用户信息 (User ID: {USER_ID})...")
        try:
            user_info = sdk.get_user_info(USER_ID)
            print("✓ 用户信息获取成功:")
            print(f"  姓名: {user_info.get('name', 'N/A')}")
            print(f"  Union ID: {user_info.get('union_id', 'N/A')}")
            print(f"  手机号: {user_info.get('mobile', 'N/A')}")
            print(f"  邮箱: {user_info.get('email', 'N/A')}")
            print(f"  工号: {user_info.get('job_number', 'N/A')}")
            
            # 自动获取operator_id
            operator_id = user_info.get('union_id', '')
            print(f"  自动获取Operator ID: {operator_id}")
                
        except DingTalkSDKError as e:
            print(f"✗ 获取用户信息失败: {e}")
            return
        
        # 3. 搜索文档（使用新的便捷方法）
        print("\n3. 搜索钉钉知识库文档...")
        keyword = "远程桌面连接断开后本地屏幕没有响应"
        print(f"搜索关键词: {keyword}")
        
        # 使用新的便捷方法，只需要提供user_id
        documents = sdk.search_and_get_document_details_with_user_id(keyword, USER_ID)
        
        if documents:
            print(f"✓ 找到 {len(documents)} 个相关文档:")
            
            for i, doc in enumerate(documents, 1):
                print(f"\n--- 文档 {i} ---")
                print(f"标题: {doc.title}")
                print(f"URL: {doc.url}")
                print(f"创建者: {doc.creator}")
                print(f"创建时间: {doc.create_time}")
                print(f"更新时间: {doc.update_time}")
                print(f"文件类型: {doc.file_type}")
                print(f"文件大小: {doc.file_size} bytes")
                print(f"节点ID: {doc.node_id}")
        else:
            print("✗ 未找到相关文档")
        
        # 4. 单独测试文档搜索（使用新的便捷方法）
        print("\n4. 单独测试文档搜索...")
        search_results = sdk.search_documents_with_user_id(keyword, USER_ID)
        print(f"搜索到 {len(search_results)} 个文档")
        
        # 5. 如果有搜索结果，获取第一个文档的详细信息
        if search_results:
            first_doc = search_results[0]
            node_id = first_doc.get('node_id')
            if node_id:
                print(f"\n5. 获取文档详细信息 (节点ID: {node_id})...")
                try:
                    # 使用新的便捷方法
                    doc_details = sdk.get_document_details_with_user_id(node_id, USER_ID)
                    print("✓ 文档详细信息获取成功:")
                    print(f"  标题: {doc_details.title}")
                    print(f"  URL: {doc_details.url}")
                    print(f"  创建者: {doc_details.creator}")
                except DingTalkSDKError as e:
                    print(f"✗ 获取文档详情失败: {e}")
        
        print("\n✓ 所有操作完成!")
        
    except DingTalkSDKError as e:
        print(f"✗ SDK错误: {e}")
    except Exception as e:
        print(f"✗ 未知错误: {e}")


def test_token_refresh():
    """测试token刷新功能"""
    print("\n=== 测试Token刷新功能 ===")
    
    APP_KEY = os.getenv('DINGTALK_APP_KEY', 'your_app_key_here')
    APP_SECRET = os.getenv('DINGTALK_APP_SECRET', 'your_app_secret_here')
    
    if APP_KEY == 'your_app_key_here':
        print("请先设置DINGTALK_APP_KEY和DINGTALK_APP_SECRET环境变量")
        return
    
    try:
        config = DingTalkConfig(app_key=APP_KEY, app_secret=APP_SECRET)
        sdk = DingTalkSDK(config)
        
        # 第一次获取token
        print("第一次获取token...")
        token1 = sdk.get_access_token()
        print(f"Token 1: {token1[:20]}...")
        
        # 第二次获取token（应该使用缓存的）
        print("第二次获取token（应该使用缓存）...")
        token2 = sdk.get_access_token()
        print(f"Token 2: {token2[:20]}...")
        
        # 强制刷新token
        print("强制刷新token...")
        token3 = sdk.get_access_token(force_refresh=True)
        print(f"Token 3: {token3[:20]}...")
        
        print("✓ Token刷新测试完成")
        
    except DingTalkSDKError as e:
        print(f"✗ Token刷新测试失败: {e}")


if __name__ == '__main__':
    print("钉钉SDK使用示例")
    print("=" * 50)
    
    # 运行主示例
    main()
    
    # 运行token刷新测试
    test_token_refresh()
