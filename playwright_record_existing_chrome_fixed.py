"""
Playwright录制脚本 - 真正连接现有Chrome实例版本

修复问题：
1. 不会打开新的Chrome实例
2. 使用现有的标签页和上下文
3. 保持现有的登录状态和扩展
4. 正确处理下载功能
"""

from playwright.sync_api import sync_playwright
import sys
import os
import time

def main():
    """
    真正连接到已运行的Chrome实例，使用现有标签页
    """
    print("=" * 80)
    print("Playwright录制脚本 - 真正连接现有Chrome实例")
    print("=" * 80)
    
    # Chrome调试端口
    debug_port = "9222"
    
    # 设置下载目录
    downloads_dir = os.path.join(os.getcwd(), "downloads")
    os.makedirs(downloads_dir, exist_ok=True)
    
    print(f"🔗 连接到Chrome实例 (端口: {debug_port})")
    print(f"📁 下载目录: {downloads_dir}")
    print("📝 请确保Chrome已启动并开启调试端口：")
    print(f"   chrome.exe --remote-debugging-port={debug_port}")
    print()
    
    try:
        with sync_playwright() as playwright:
            # 连接到已运行的Chrome实例
            browser = playwright.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
            
            print(f"✅ 成功连接到Chrome实例")
            print(f"🌐 发现 {len(browser.contexts)} 个浏览器上下文")
            
            # 使用现有的上下文，而不是创建新的
            if browser.contexts:
                context = browser.contexts[0]  # 使用第一个现有上下文
                print("📱 使用现有的浏览器上下文")
            else:
                print("⚠️  没有找到现有上下文，这可能意味着Chrome没有打开任何标签页")
                print("请在Chrome中打开至少一个标签页，然后重新运行脚本")
                return
            
            print(f"📄 发现 {len(context.pages)} 个标签页")
            
            # 使用现有的页面，或者创建新页面（但在同一个上下文中）
            if context.pages:
                # 使用最后一个活跃的页面
                page = context.pages[-1]
                print(f"📖 使用现有标签页: {page.url}")
            else:
                # 在现有上下文中创建新页面
                page = context.new_page()
                print("📖 在现有上下文中创建新标签页")
            
            # 设置下载事件监听
            def handle_download(download):
                """处理下载事件 - 添加时间戳版本"""
                try:
                    original_filename = download.suggested_filename
                    print(f"📥 检测到下载: {original_filename}")
                    
                    # 处理文件名和扩展名
                    if original_filename:
                        # 分离文件名和扩展名
                        name_part, ext_part = os.path.splitext(original_filename)
                    else:
                        name_part = "download"
                        ext_part = ""
                    
                    # 生成时间戳
                    from datetime import datetime
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # 构造带时间戳的文件名
                    filename_with_timestamp = f"{name_part}_{timestamp}{ext_part}"
                    file_path = os.path.join(downloads_dir, filename_with_timestamp)
                    
                    print(f"📝 原始文件名: {original_filename}")
                    print(f"🕒 添加时间戳: {timestamp}")
                    print(f"📄 新文件名: {filename_with_timestamp}")
                    
                    # 保存下载文件
                    download.save_as(file_path)
                    
                    print(f"✅ 文件已保存到: {file_path}")
                    print(f"📊 文件大小: {os.path.getsize(file_path)} 字节")
                    
                except Exception as e:
                    print(f"❌ 下载处理失败: {e}")
            
            # 监听下载事件
            page.on("download", handle_download)
            
            print()
            print("🎬 启动Playwright录制模式...")
            print("=" * 60)
            print("录制说明：")
            print("1. 📹 Playwright Inspector窗口将会打开")
            print("2. 🖱️  在当前Chrome标签页中进行操作")
            print("3. 📥 下载文件会自动保存到 downloads 目录")
            print("4. 📝 Inspector会自动生成对应的代码")
            print("5. 📋 完成后点击'Copy'按钮复制生成的代码")
            print("6. ⏹️  关闭Inspector窗口结束录制")
            print()
            print("注意事项：")
            print("✅ 不会打开新的Chrome实例")
            print("✅ 保持现有的登录状态")
            print("✅ 保持现有的扩展和设置")
            print("✅ 使用当前活跃的标签页")
            print("=" * 60)
            print()
            
            # 启动录制模式 - 这会打开Playwright Inspector
            page.pause()
            
            print("🎉 录制会话结束")
            print(f"📁 下载的文件保存在: {downloads_dir}")
            print("💡 提示：生成的代码可以直接用于自动化测试")
            
            # 注意：不要关闭browser，因为那是外部的Chrome实例
            
    except ConnectionRefusedError:
        print("❌ 连接失败：无法连接到Chrome实例")
        print()
        print("解决方案：")
        print("1. 确保Chrome浏览器正在运行")
        print("2. 确保Chrome启动时包含调试参数：")
        print(f"   chrome.exe --remote-debugging-port={debug_port}")
        print("3. 或者使用完整命令：")
        print(f"   \"C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe\" --remote-debugging-port={debug_port}")
        print()
        print("🔍 检查Chrome是否正确启动：")
        print(f"   访问: http://localhost:{debug_port}/json/version")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        print("可能的原因：")
        print("1. Chrome没有以调试模式启动")
        print("2. 端口被其他程序占用")
        print("3. Chrome版本不兼容")
        sys.exit(1)

def test_record_existing_chrome_fixed():
    """
    pytest测试函数版本
    """
    main()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("Playwright录制脚本使用说明（修复版本）")
        print("=" * 50)
        print()
        print("主要修复：")
        print("✅ 不会打开新的Chrome实例")
        print("✅ 使用现有的标签页和上下文")
        print("✅ 保持所有现有状态（登录、扩展等）")
        print("✅ 正确处理下载功能")
        print()
        print("使用步骤：")
        print("1. 启动Chrome并开启调试端口：")
        print("   chrome.exe --remote-debugging-port=9222")
        print()
        print("2. 在Chrome中打开你要操作的网站")
        print()
        print("3. 运行此脚本：")
        print("   python playwright_record_existing_chrome_fixed.py")
        print()
        print("4. 在打开的Inspector中进行录制")
        print()
        print("重要提示：")
        print("⚠️  请确保Chrome以调试模式启动")
        print("⚠️  请在Chrome中先打开要操作的网站")
        print("⚠️  脚本会使用当前活跃的标签页")
        print("⚠️  录制结束后不会关闭Chrome")
        print()
        sys.exit(0)
    
    main()
