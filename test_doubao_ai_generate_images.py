# -*- coding: utf-8 -*-
"""
豆包AI调试测试脚本
基于录制的操作流程，专门用于豆包AI的图片生成功能，主要用于生成文章封面图
"""

import pytest
import os
import sys
import time
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright):
    return {
        "geolocation": {"latitude": 22.558033372050147, "longitude": 113.46251764183725}, 
        "locale": "zh-CN", 
        "permissions": ["geolocation"], 
        "timezone_id": "Asia/Shanghai", 
        "viewport": {"width": 1920, "height": 1080}
    }

@pytest.fixture(scope="session")
def browser_context(playwright, request):
    user_data_dir = request.config.getoption("--user-data-dir")
    
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
        record_video_dir="test-results/videos/",
        record_video_size={"width": 1920, "height": 1080},
        traces_dir="test-results/traces/",
        geolocation={"latitude": 22.558033372050147, "longitude": 113.46251764183725},
        locale="zh-CN",
        permissions=["geolocation"],
        timezone_id="Asia/Shanghai",
        viewport={"width": 1920, "height": 1080}
    )
    yield context
    context.close()

def test_doubao_ai_debug(browser_context, request):
    """
    测试豆包AI图片生成功能 - 正式版本
    """
    try:
        # 开始追踪
        browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        # 获取参数
        markdown_file = request.config.getoption("--markdown-file")
        if not markdown_file:
            # 使用默认文件
            markdown_file = "markdown_files/私有云Canonical's Charmed OpenStack部署教程.md"
        
        print("=" * 80)
        print("豆包AI图片生成功能测试脚本")
        print("=" * 80)
        print(f"📄 使用Markdown文件: {markdown_file}")
        
        # 检查markdown文件是否存在
        if not os.path.exists(markdown_file):
            print(f"❌ Markdown文件不存在: {markdown_file}")
            print("请确保文件存在于当前目录，或使用 --markdown-file 参数指定文件路径")
            print("例如: pytest -s --headed ./test_doubao_ai_generate_images.py --markdown-file 'path/to/file.md'")
            sys.exit(1)
        
        print(f"📊 文件大小: {os.path.getsize(markdown_file)} 字节")
        
        # 创建新页面
        page = browser_context.new_page()
        
        print("🌐 正在打开豆包AI聊天页面...")
        page.goto("https://www.doubao.com/chat/")
        page.wait_for_load_state("networkidle")
        print("✅ 豆包AI页面加载完成")
        
        # 步骤1：点击文件上传按钮
        print("1️⃣ 点击文件上传按钮...")
        page.get_by_test_id("upload_file_button").click()
        page.wait_for_timeout(1000)
        print("✅ 文件上传按钮点击成功")
        
        # 步骤2：选择上传文件或图片选项并上传文件
        print("2️⃣ 选择上传文件选项...")
        with page.expect_file_chooser() as page_upload_file:
            page.get_by_text("上传文件或图片").click()
        page_upload_file = page_upload_file.value
        print("3️⃣ 上传Markdown文件...")
        page_upload_file.set_files(markdown_file)
        page.wait_for_timeout(1000)
        print("✅ 上传选项选择成功")
        
        # 步骤4：点击聊天输入框
        print("4️⃣ 点击聊天输入框...")
        page.get_by_test_id("chat_input_input").click()
        page.wait_for_timeout(500)
        print("✅ 聊天输入框获得焦点")
        
        # 步骤5：输入文生图提示词请求
        print("5️⃣ 输入文生图提示词请求...")
        prompt_text = """请仔细阅读我提供的markdown文件，我计划将文章发布到微信公众号上，我需要文章封面图，请根据markdown文件内容，生成一段合适的文生图提示词。
注意：
1.提示词的语言为英文。
2.提示词中需要包含这个反向提示词：no Chinese character
3.你的回答只需返回提示词，不要返回任何其他内容。"""
        
        page.get_by_test_id("chat_input_input").fill(prompt_text)
        page.wait_for_timeout(1000)
        print("✅ 提示词输入完成")
        
        # 步骤6：发送消息
        print("6️⃣ 发送消息...")
        page.get_by_test_id("chat_input_send_button").click()
        print("✅ 消息发送成功，等待AI回复...")
        
        # 等待AI回复
        print("⏳ 等待AI回复...")
        page.wait_for_timeout(10000)  # 等待10秒让AI生成回复
        print("✅ AI回复完成")
        
        # 步骤7：复制AI回复内容
        print("7️⃣ 复制AI回复内容...")
        try:
            copy_button = page.get_by_test_id("message_action_copy")
            if copy_button.count() > 0:
                copy_button.click()
                page.wait_for_timeout(1000)
                print("✅ AI回复已复制到剪贴板")
                
                # 使用 pyperclip 从剪贴板读取内容
                try:
                    import pyperclip
                    prompt_result = pyperclip.paste().strip()
                    
                    if prompt_result:
                        print(f"🤖 豆包AI生成的文生图提示词: {prompt_result}")
                        
                        # 保存提示词到文件（备份）
                        prompt_file = os.path.join("test-results", f"doubao_prompt_{os.path.splitext(os.path.basename(markdown_file))[0]}.txt")
                        os.makedirs("test-results", exist_ok=True)
                        with open(prompt_file, 'w', encoding='utf-8') as f:
                            f.write(prompt_result)
                        print(f"📁 提示词已保存到: {prompt_file}")
                    else:
                        print("⚠️  剪贴板内容为空")
                        
                except ImportError:
                    print("❌ 需要安装 pyperclip 库")
                    print("请运行: pip install pyperclip 或 uv add pyperclip")
                except Exception as e:
                    print(f"⚠️  从剪贴板读取内容时出错: {e}")
            else:
                print("⚠️  未找到复制按钮")
        except Exception as e:
            print(f"⚠️  复制操作失败: {e}")
        
        # 步骤8：点击技能按钮
        print("8️⃣ 点击技能按钮...")
        try:
            page.get_by_test_id("chat-input-all-skill-button").click()
            page.wait_for_timeout(1000)
            print("✅ 技能按钮点击成功")
        except Exception as e:
            print(f"⚠️  技能按钮点击失败: {e}")
        
        # 步骤9：选择图片生成技能
        print("9️⃣ 选择图片生成技能...")
        try:
            page.get_by_role("dialog").get_by_test_id("skill_bar_button_3").click()
            page.wait_for_timeout(1000)
            print("✅ 图片生成技能选择成功")
        except Exception as e:
            print(f"⚠️  图片生成技能选择失败: {e}")
        
        # 步骤10：点击输入框
        print("🔟 点击输入框...")
        try:
            page.get_by_test_id("chat_input_input").locator("div").click()
            page.wait_for_timeout(500)
            print("✅ 输入框点击成功")
        except Exception as e:
            print(f"⚠️  输入框点击失败: {e}")
        
        # 步骤11：选择图片比例
        print("1️⃣1️⃣ 选择图片比例...")
        try:
            page.get_by_test_id("image-creation-chat-input-picture-ration-button").click()
            page.wait_for_timeout(1000)
            print("✅ 图片比例按钮点击成功")
        except Exception as e:
            print(f"⚠️  图片比例按钮点击失败: {e}")
        
        # 步骤12：选择16:9比例
        print("1️⃣2️⃣ 选择16:9比例...")
        try:
            page.get_by_text(":9 桌面壁纸，风景").click()
            page.wait_for_timeout(1000)
            print("✅ 16:9比例选择成功")
        except Exception as e:
            print(f"⚠️  16:9比例选择失败: {e}")
        
        # 步骤13：发送图片生成请求
        print("1️⃣3️⃣ 发送图片生成请求...")
        try:
            page.get_by_test_id("chat_input_send_button").click()
            print("✅ 图片生成请求发送成功")
        except Exception as e:
            print(f"⚠️  图片生成请求发送失败: {e}")
        
        # 等待图片生成完成
        print("⏳ 等待图片生成完成...")
        print("这可能需要几十秒时间，请耐心等待...")
        page.wait_for_timeout(30000)  # 等待30秒让图片生成完成
        
        # 步骤14：下载生成的图片
        print("1️⃣4️⃣ 下载生成的图片...")
        try:
            # 正确的下载按钮定位方式
            download_buttons = page.get_by_test_id("message-list").get_by_role("button", name="下载")
            
            if download_buttons.count() > 0:
                print(f"✅ 找到 {download_buttons.count()} 个下载按钮")
                
                # 创建下载目录
                downloads_dir = os.path.join(os.getcwd(), "test-results", "doubao_images")
                os.makedirs(downloads_dir, exist_ok=True)
                
                # 处理多个下载文件
                downloaded_files = []
                
                # 方法1：尝试处理多个下载事件
                try:
                    # 设置下载事件监听器
                    downloads = []
                    
                    def handle_download(download):
                        downloads.append(download)
                        print(f"📥 检测到下载: {download.suggested_filename}")
                    
                    page.on("download", handle_download)
                    
                    # 点击下载按钮
                    print("🖱️  点击豆包AI回答下的下载按钮...")
                    download_buttons.first.click()
                    print("✅ 点击最终的下载按钮")
                    final_download_button = page.get_by_role("button", name="下载").nth(2)
                    final_download_button.click()
                    # 等待所有下载完成
                    print("⏳ 等待下载完成...")
                    page.wait_for_timeout(30000)  # 等待30秒让所有下载完成
                    
                    # 处理所有下载的文件
                    if downloads:
                        print(f"📊 检测到 {len(downloads)} 个下载文件")
                        
                        for i, download in enumerate(downloads):
                            try:
                                # 生成文件名
                                timestamp = time.strftime("%Y%m%d_%H%M%S")
                                original_name = download.suggested_filename or f"image_{i+1}.png"
                                name, ext = os.path.splitext(original_name)
                                filename = f"doubao_generated_image_{i+1}_{timestamp}{ext}"
                                file_path = os.path.join(downloads_dir, filename)
                                
                                download.save_as(file_path)
                                file_size = os.path.getsize(file_path)
                                
                                downloaded_files.append(file_path)
                                print(f"✅ 图片 {i+1} 下载成功: {filename}")
                                print(f"📊 文件大小: {file_size} 字节")
                                
                            except Exception as e:
                                print(f"⚠️  处理下载文件 {i+1} 时出错: {e}")
                    else:
                        print("⚠️  未检测到任何下载文件")
                        
                except Exception as e:
                    print(f"⚠️  多文件下载处理失败: {e}")
                    print("尝试单文件下载方式...")
                                   
                # 总结下载结果
                if downloaded_files:
                    print(f"🎉 总共下载了 {len(downloaded_files)} 个图片文件")
                    print("📁 下载目录:", downloads_dir)
                    for i, file_path in enumerate(downloaded_files, 1):
                        print(f"   {i}. {os.path.basename(file_path)}")
                else:
                    print("❌ 没有成功下载任何文件")
                    page.pause()
                    
            else:
                print("⚠️  未找到下载按钮")
        except Exception as e:
            print(f"⚠️  图片下载失败: {e}")
            import traceback
            traceback.print_exc()
        
        print("-" * 60)
        print("豆包AI调试测试完成！")
        print("=" * 80)
        
        # 保存调试截图
        page.screenshot(path="test-results/doubao_ai_debug.png", full_page=True)
        print("📸 调试截图已保存到: test-results/doubao_ai_debug.png")
        
        # 停止追踪
        browser_context.tracing.stop(path="test-results/doubao_ai_debug_trace.zip")
        print("✅ 追踪文件已保存到: test-results/doubao_ai_debug_trace.zip")
        
        # 保持浏览器打开一段时间，方便查看结果
        print("浏览器将保持打开5秒，方便查看结果...")
        page.wait_for_timeout(5000)
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保浏览器上下文被关闭
        if browser_context:
            browser_context.close()

def main():
    """主函数"""
    test_doubao_ai_debug()

if __name__ == "__main__":
    print("=" * 80)
    print("豆包AI调试测试脚本")
    print("=" * 80)
    print()
    print("功能说明：")
    print("本脚本专门用于调试豆包AI的图片生成功能")
    print("基于录制的操作流程，支持完整的图片生成和下载")
    print()
    print("使用方法：")
    print("pytest -s --headed ./test_doubao_ai_generate_images.py --markdown-file 'path/to/file.md'")
    print()
    print("参数说明：")
    print("--markdown-file      Markdown文件路径（可选，默认使用项目中的文件）")
    print("--user-data-dir      浏览器用户数据目录（可选）")
    print()
    print("调试输出：")
    print("- 详细的步骤日志")
    print("- 错误处理和异常信息")
    print("- 调试截图和追踪文件")
    print("- 生成的图片和提示词文件")
    print()
    print("示例：")
    print("pytest -s --headed ./test_doubao_ai_generate_images.py --markdown-file 'test.md'")
    print("=" * 80)
