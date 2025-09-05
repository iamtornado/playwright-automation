"""
Gemini图片生成测试脚本 - 完全参照录制脚本
"""

import pytest
import sys
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, expect

def test_gemini_image_generation():
    """
    测试Gemini图片生成功能 - 完全参照录制脚本
    """
    print("=" * 80)
    print("Gemini图片生成测试脚本 - 完全参照录制脚本")
    print("=" * 80)
    
    # 配置参数 - 与录制脚本完全一致
    debug_port = "9222"
    downloads_dir = os.path.join(os.getcwd(), "downloads")  # 改为与录制脚本相同的目录
    os.makedirs(downloads_dir, exist_ok=True)
    
    # 测试文件路径
    markdown_file = "D:/Users/14266/Downloads/远程批量加域（wsman协议和传统的协议RPC）.md"

    # 图片生成提示词
    prompt_text = "根据我提供的markdown文件，请生成合适的文章封面。图片的比例为16:9"
    
    print(f"🔗 连接到Chrome实例 (端口: {debug_port})")
    print(f"📁 下载目录: {downloads_dir}")
    print()
    
    try:
        with sync_playwright() as playwright:
            # 连接到已运行的Chrome实例 - 与录制脚本完全一致
            browser = playwright.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
            
            print(f"✅ 成功连接到Chrome实例")
            print(f"🌐 发现 {len(browser.contexts)} 个浏览器上下文")
            
            # 使用现有的上下文，而不是创建新的 - 与录制脚本完全一致
            if browser.contexts:
                context = browser.contexts[0]  # 使用第一个现有上下文
                print("📱 使用现有的浏览器上下文")
            else:
                print("⚠️  没有找到现有上下文，这可能意味着Chrome没有打开任何标签页")
                print("请在Chrome中打开至少一个标签页，然后重新运行脚本")
                return
            
            print(f"📄 发现 {len(context.pages)} 个标签页")
            
            # 使用现有的页面，或者创建新页面（但在同一个上下文中） - 与录制脚本完全一致
            if context.pages:
                # 使用最后一个活跃的页面
                page = context.pages[-1]
                print(f"📖 使用现有标签页: {page.url}")
            else:
                # 在现有上下文中创建新页面
                page = context.new_page()
                print("📖 在现有上下文中创建新标签页")
            
            # 设置下载事件监听 - 与录制脚本完全一致
            def handle_download(download):
                """处理下载事件 - 与录制脚本完全一致"""
                try:
                    original_filename = download.suggested_filename
                    print(f"📥 检测到下载: {original_filename}")
                    
                    # 处理文件名和扩展名 - 与录制脚本完全一致
                    if original_filename:
                        # 分离文件名和扩展名
                        name_part, ext_part = os.path.splitext(original_filename)
                    else:
                        name_part = "download"
                        ext_part = ""
                    
                    # 生成时间戳 - 与录制脚本完全一致
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    
                    # 构造带时间戳的文件名 - 与录制脚本完全一致
                    filename_with_timestamp = f"{name_part}_{timestamp}{ext_part}"
                    file_path = os.path.join(downloads_dir, filename_with_timestamp)
                    
                    print(f"📝 原始文件名: {original_filename}")
                    print(f"🕒 添加时间戳: {timestamp}")
                    print(f"📄 新文件名: {filename_with_timestamp}")
                    
                    # 保存下载文件 - 与录制脚本完全一致
                    download.save_as(file_path)
                    
                    print(f"✅ 文件已保存到: {file_path}")
                    print(f"📊 文件大小: {os.path.getsize(file_path)} 字节")
                    
                except Exception as e:
                    print(f"❌ 下载处理失败: {e}")
            
            # 监听下载事件 - 与录制脚本完全一致
            page.on("download", handle_download)
            
            print()
            print("🎨 开始执行Gemini图片生成流程...")
            print("-" * 60)
            
            try:
                               # 1. 点击工具按钮
                print("1️⃣ 点击工具按钮...")
                # page.locator("button.toolbox-drawer-button").click()
                page.wait_for_timeout(1000)
                
                # 2. 选择Imagen生成图片
                print("2️⃣ 选择Imagen生成图片...")
                # page.get_by_role("button", name="使用 Imagen 生成图片").click()
                page.wait_for_timeout(2000)
                
                # 3. 打开文件上传菜单
                print("3️⃣ 打开文件上传菜单...")
                # page.get_by_role("button", name="打开文件上传菜单").click()
                page.wait_for_timeout(1000)
                # 4. 点击文件上传按钮
                print("4️⃣ 选择文件上传...")
                page.locator("[data-test-id=\"local-image-file-uploader-button\"]").click()
                page.wait_for_timeout(1000)
                with page.expect_file_chooser() as fc_info:
                    page.locator("[data-test-id=\"local-image-file-uploader-button\"]").click()
                file_chooser = fc_info.value
                file_chooser.set_files(markdown_file)
                
                print("6️⃣ 输入图片生成提示...")
                
                # 输入图片生成提示
                try:
                    textbox = page.get_by_role("textbox", name="在此处输入提示")
                    if textbox.count() > 0:
                        print("   🎯 找到提示输入框")
                        # textbox.click()
                        # textbox.set_input_files(markdown_file)
                        page.wait_for_timeout(500)
                        textbox.fill("")
                        page.wait_for_timeout(200)
                        textbox.fill(prompt_text)
                        print("   ✅ 提示词输入成功")
                    else:
                        print("   🔍 使用键盘输入方式...")
                        page.keyboard.type(prompt_text)
                        print("   ✅ 键盘输入成功")
                        
                except Exception as e:
                    print(f"   ❌ 提示词输入失败: {e}")
                
                page.wait_for_timeout(1000)
                page.wait_for_load_state("networkidle")
                
                # 发送请求
                print("7️⃣ 发送图片生成请求...")
                try:
                    send_button = page.get_by_role("button", name="发送")
                    if send_button.count() > 0:
                        send_button.click()
                        print("✅ 已点击发送按钮")
                    else:
                        page.keyboard.press("Enter")
                        print("✅ 已按回车键发送")
                except Exception as e:
                    print(f"⚠️  发送失败，尝试回车: {e}")
                    page.keyboard.press("Enter")
                
                # 8. 等待图片生成完成
                print("8️⃣ 等待图片生成完成...")
                print("   ⏳ 这可能需要几十秒时间，请耐心等待...")

                # 等待图片下载按钮出现
                try:
                    page.wait_for_selector("[data-test-id=\"download-generated-image-button\"]", timeout=120000)
                    print("✅ 图片生成完成，下载按钮已出现")
                except:
                    print("⚠️  等待超时，仍然没有出现下载图片的按钮，请尝试再次发送提示词生成图片")
                    # 暂停程序，等待用户手动操作
                    print("\n⏸️  程序暂停，等待用户手动操作...")
                    page.pause()

                # 下载生成的图片
                print("9️⃣ 下载生成的图片...")

                try:
                    # 确保下载按钮存在且可见
                    download_button = page.locator("[data-test-id=\"download-generated-image-button\"]")
                    
                    # 等待按钮出现并可见
                    download_button.wait_for(state="visible", timeout=30000)
                    print("✅ 下载按钮已可见")
                    
                    # 滚动到按钮位置，确保完全可见
                    download_button.scroll_into_view_if_needed()
                    page.wait_for_timeout(1000)
                    
                    # 等待页面稳定
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(2000)
                    
                    # 点击下载按钮
                    print("⏳ 点击下载按钮...")
                    download_button.click()
                    print("✅ 已点击下载按钮")
                    
                    # 等待下载完成 - 给更长的时间
                    print("🔄 等待下载完成...")
                    page.wait_for_timeout(10000)  # 等待10秒让下载完成
                    
                    print("📁 下载过程完成，请检查下载目录")
                        
                except Exception as e:
                    print(f"❌ 下载过程出错: {e}")
                    import traceback
                    traceback.print_exc()
                
                print("-" * 60)
                print("🎉 Gemini图片生成流程完成！")
                print(f"📁 下载的文件保存在: {downloads_dir}")
                print("💡 提示：生成的代码可以直接用于自动化测试")
                
            except Exception as e:
                print(f"❌ 执行过程中出错: {e}")
                
            # 注意：不要关闭browser，因为那是外部的Chrome实例 - 与录制脚本完全一致
                
    except ConnectionRefusedError:
        print("❌ 连接失败：无法连接到Chrome实例")
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")

def main():
    """主函数"""
    test_gemini_image_generation()

if __name__ == "__main__":
    main()