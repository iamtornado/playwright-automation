#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号API SDK 使用示例

这个文件展示了如何使用微信公众号API SDK的各种功能。
"""

import os
import sys
from pathlib import Path

# 添加当前目录到Python路径，以便导入SDK
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from wechat_mp_sdk import WeChatMPSDK, WeChatMPSDKError, create_sdk


def main():
    """主函数 - 演示SDK的基本用法"""
    
    print("🚀 微信公众号API SDK 使用示例")
    print("=" * 50)
    
    # 从环境变量中读取配置
    app_id = os.getenv("WECHAT_APP_ID")
    app_secret = os.getenv("WECHAT_APP_SECRET")
    
    if not app_id or not app_secret:
        print("❌ 请设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
        print("\n环境变量设置方法：")
        print("Linux/macOS:")
        print("  export WECHAT_APP_ID=your_app_id")
        print("  export WECHAT_APP_SECRET=your_app_secret")
        print("\nWindows (命令提示符):")
        print("  set WECHAT_APP_ID=your_app_id")
        print("  set WECHAT_APP_SECRET=your_app_secret")
        print("\nWindows (PowerShell):")
        print("  $env:WECHAT_APP_ID='your_app_id'")
        print("  $env:WECHAT_APP_SECRET='your_app_secret'")
        return 1
    
    try:
        # 方法1: 直接创建SDK实例
        print("\n📱 方法1: 直接创建SDK实例")
        sdk1 = WeChatMPSDK(app_id=app_id, app_secret=app_secret)
        print(f"✅ SDK实例创建成功: {sdk1}")
        
        # 方法2: 使用便捷函数创建
        print("\n📱 方法2: 使用便捷函数创建")
        sdk2 = create_sdk(app_id, app_secret)
        print(f"✅ SDK实例创建成功: {sdk2}")
        
        # 获取access_token
        print("\n🔑 获取access_token")
        token = sdk1.get_access_token()
        print(f"✅ Access Token: {token[:20]}...")
        
        # 演示文件上传（需要实际的文件）
        demo_upload_examples(sdk1)
        
    except WeChatMPSDKError as e:
        print(f"❌ SDK错误: {e}")
        return 1
    except Exception as e:
        print(f"❌ 其他错误: {e}")
        return 1
    
    print("\n🎉 示例运行完成！")
    return 0


def demo_upload_examples(sdk: WeChatMPSDK):
    """演示文件上传功能"""
    
    print("\n📁 文件上传示例")
    print("-" * 30)
    
    # 检查是否有示例文件
    sample_files = {
        'image': ['sample.jpg', 'sample.png', 'test.gif'],
        'voice': ['sample.mp3', 'sample.wav'],
        'video': ['sample.mp4', 'sample.avi'],
    }
    
    for file_type, extensions in sample_files.items():
        print(f"\n🔍 查找{file_type}文件...")
        
        found_file = None
        for ext in extensions:
            if os.path.exists(ext):
                found_file = ext
                break
        
        if found_file:
            try:
                print(f"📤 上传{file_type}文件: {found_file}")
                
                if file_type == 'image':
                    result = sdk.upload_image(found_file)
                elif file_type == 'voice':
                    result = sdk.upload_voice(found_file)
                elif file_type == 'video':
                    result = sdk.upload_video(found_file, "示例视频", "这是一个示例视频")
                
                print(f"✅ 上传成功！Media ID: {result.get('media_id', 'N/A')}")
                if 'url' in result:
                    print(f"📷 文件URL: {result['url']}")
                    
            except Exception as e:
                print(f"❌ 上传失败: {e}")
        else:
            print(f"⚠️  未找到{file_type}文件，跳过上传示例")
            print(f"   可以创建以下文件之一进行测试: {', '.join(extensions)}")


def create_sample_files():
    """创建一些示例文件用于测试（可选）"""
    
    print("\n📝 创建示例文件")
    print("-" * 20)
    
    # 这里可以添加创建示例文件的代码
    # 例如：创建一个小的测试图片等
    print("💡 提示：您可以手动创建一些测试文件:")
    print("   - sample.jpg (图片文件)")
    print("   - sample.mp3 (音频文件)")
    print("   - sample.mp4 (视频文件)")


if __name__ == "__main__":
    exit_code = main()
    
    if exit_code != 0:
        print("\n💡 如需帮助，请查看README.md文件")
    
    sys.exit(exit_code)
