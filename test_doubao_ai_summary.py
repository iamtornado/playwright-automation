"""
豆包AI文章总结测试脚本
使用豆包AI对Markdown文档进行总结，限制在120字以内
"""

import pytest
import sys
import os
from playwright.sync_api import Page, expect
from simple_word_counter import validate_and_clean_text

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
    
    # 添加视频录制配置、视频尺寸、地理位置、时区、语言、权限、视口、用户数据目录、无头模式
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
        record_video_dir="test-results/videos/",  # 添加视频录制目录
        record_video_size={"width": 1920, "height": 1080},  # 设置视频尺寸
        traces_dir="test-results/traces/",  # 添加追踪文件目录
        geolocation={"latitude": 22.558033372050147, "longitude": 113.46251764183725},
        locale="zh-CN",
        permissions=["geolocation"],
        timezone_id="Asia/Shanghai",
        viewport={"width": 1920, "height": 1080}
    )
    yield context
    # 确保上下文被关闭，这样视频才会保存
    context.close()

def test_doubao_ai_summary(browser_context, request):
    """
    测试豆包AI文章总结功能
    """
    try:
        # Start tracing before creating / navigating a page.
        browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        print("=" * 80)
        print("豆包AI文章总结测试脚本")
        print("=" * 80)
        
        # 从 pytest 配置中获取参数
        markdown_file = request.config.getoption("--markdown-file")
        
        # 验证文件是否存在
        if not os.path.exists(markdown_file):
            print(f"❌ 文件不存在: {markdown_file}")
            sys.exit(1)
        
        print(f"📄 使用的Markdown文件: {markdown_file}")
        print(f"📁 文件大小: {os.path.getsize(markdown_file)} 字节")
        print()
        
        # 使用豆包AI总结文章内容
        print("🤖 正在使用豆包AI总结文章...")
        page_doubao = browser_context.new_page()
        
        try:
            # 打开豆包AI聊天页面
            print("1️⃣ 打开豆包AI聊天页面...")
            page_doubao.goto("https://www.doubao.com/chat/")
            page_doubao.wait_for_load_state("networkidle")
            print("✅ 豆包AI页面加载完成")
            
            # 点击文件上传按钮
            print("2️⃣ 点击文件上传按钮...")
            page_doubao.get_by_test_id("upload_file_button").click()
            page_doubao.wait_for_timeout(1000)
            print("✅ 文件上传按钮点击成功")
            
            # 选择上传文件或图片选项
            print("3️⃣ 选择上传文件选项...")
            with page_doubao.expect_file_chooser() as page_upload_file:
                page_doubao.get_by_text("上传文件或图片").click()
            page_upload_file = page_upload_file.value
            print("4️⃣ 上传Markdown文件...")
            page_upload_file.set_files(markdown_file)
            # page_doubao.get_by_text("上传文件或图片").set_input_files(markdown_file)
            # page_upload_file.locator("body").set_input_files(markdown_file)
            page_doubao.wait_for_timeout(1000)
            print("✅ 上传选项选择成功")
            
            # 上传Markdown文件
            # print("4️⃣ 上传Markdown文件...")
            # page_doubao.locator("body").set_input_files(markdown_file)
            # page_doubao.wait_for_timeout(3000)  # 等待文件上传完成
            # print(f"✅ 文件上传成功: {os.path.basename(markdown_file)}")
            
            # 点击聊天输入框
            print("5️⃣ 点击聊天输入框...")
            page_doubao.get_by_test_id("chat_input_input").click()
            page_doubao.wait_for_timeout(500)
            print("✅ 聊天输入框获得焦点")
            
            # 输入总结请求的提示词，要求严格限制在120字以内
            print("6️⃣ 输入总结提示词...")
            prompt_text = "请帮我总结我提供的Markdown文档，总字数严格限制在120字以内。请注意：一个英文字母、一个空格、一个标点符号都算一个字"
            page_doubao.get_by_test_id("chat_input_input").fill(prompt_text)
            page_doubao.wait_for_timeout(1000)
            print("✅ 提示词输入完成")
            print(f"📝 提示词内容: {prompt_text}")
            # 等待网络空闲，确保页面完全加载
            print("⏳ 等待网络空闲...")
            page_doubao.wait_for_load_state("networkidle")
            print("✅ 网络空闲状态确认")
            # 发送消息
            print("7️⃣ 发送消息...")
            page_doubao.get_by_test_id("chat_input_send_button").click()
            print("✅ 消息发送成功，等待AI回复...")
            
            # 等待AI回复完成
            print("8️⃣ 等待AI回复...")
            page_doubao.wait_for_timeout(10000)  # 等待10秒让AI生成回复
            
            # 点击复制按钮获取AI回复内容
            print("9️⃣ 复制AI回复内容...")
            try:
                copy_button = page_doubao.get_by_test_id("receive_message").get_by_test_id("message_action_copy")
                copy_button.click()
                page_doubao.wait_for_timeout(1000)
                print("✅ AI回复已复制到剪贴板")
                
                # 使用 pyperclip 从剪贴板读取内容
                try:
                    import pyperclip
                    summary = pyperclip.paste().strip()
                    
                    if summary:
                        print(f"🤖 豆包AI总结内容: {summary}")
                        
                        # 验证总结长度
                        print("\n📏 验证总结长度...")
                        validation_result = validate_and_clean_text(summary, max_length=120)
                        print(validation_result['message'])
                        
                        if validation_result['success']:
                            print("✅ 总结长度符合要求")
                            final_summary = validation_result['cleaned_text'] if validation_result['cleaned_count'] < validation_result['original_count'] else summary
                            print(f"📝 最终总结: {final_summary}")
                            
                            # 保存总结到文件
                            summary_file = os.path.join("test-results", f"summary_{os.path.splitext(os.path.basename(markdown_file))[0]}.txt")
                            os.makedirs("test-results", exist_ok=True)
                            with open(summary_file, 'w', encoding='utf-8') as f:
                                f.write(final_summary)
                            print(f"📁 总结已保存到: {summary_file}")
                            
                        else:
                            print("⚠️  总结长度超出限制，需要进一步优化")
                            print(f"原始长度: {validation_result['original_count']}字符")
                            print(f"清理后长度: {validation_result['cleaned_count']}字符")
                            
                            # 即使超出限制也保存原始内容供参考
                            summary_file = os.path.join("test-results", f"summary_raw_{os.path.splitext(os.path.basename(markdown_file))[0]}.txt")
                            os.makedirs("test-results", exist_ok=True)
                            with open(summary_file, 'w', encoding='utf-8') as f:
                                f.write(summary)
                            print(f"📁 原始总结已保存到: {summary_file}")
                            
                    else:
                        print("⚠️  剪贴板内容为空，尝试备选方案...")
                        # 备选方案：直接从页面获取文本
                        try:
                            selectors_to_try = [
                                "[data-test-id='receive_message'] .message-content",
                                "[data-test-id='receive_message'] [class*='content']", 
                                "[data-test-id='receive_message'] p",
                                "[data-test-id='receive_message'] div[class*='text']",
                                "[data-test-id='receive_message']"
                            ]
                            
                            summary = None
                            for selector in selectors_to_try:
                                try:
                                    element = page_doubao.locator(selector).first
                                    if element.count() > 0:
                                        text = element.text_content().strip()
                                        if text and len(text) > 10:
                                            summary = text
                                            print(f"✅ 通过页面元素获取到内容")
                                            break
                                except:
                                    continue
                            
                            if summary:
                                print(f"🤖 豆包AI总结内容: {summary}")
                                # 这里可以复用上面的验证和保存逻辑
                            else:
                                print("⚠️  无法获取AI回复内容")
                                
                        except Exception as e:
                            print(f"⚠️  备选方案失败: {e}")
                            
                except ImportError:
                    print("❌ 需要安装 pyperclip 库")
                    print("请运行: pip install pyperclip")
                    print("或者: uv add pyperclip")
                    
                except Exception as e:
                    print(f"⚠️  从剪贴板读取内容时出错: {e}")
                    
            except Exception as e:
                print(f"⚠️  复制AI回复时出错: {e}")
                print("请手动查看AI回复内容")
            
            print("-" * 80)
            print("🎉 豆包AI总结完成！")
            
        except Exception as e:
            print(f"❌ 豆包AI操作过程中出错: {e}")
            import traceback
            traceback.print_exc()
        
        # 截图保存
        page_doubao.screenshot(path="test-results/screenshot_doubao.png", full_page=True)
        print("📸 页面截图已保存")
        
        # 等待用户确认
        print("\n" + "=" * 80)
        print("豆包AI总结完成！")
        print("=" * 80)
        print("请检查总结结果，确认无误后按 Y 继续，或按其他键退出...")
        user_input = input("是否继续？(Y/n): ").strip().upper()
        
        if user_input != 'Y':
            print("用户选择退出，测试结束。")
            return
        
        print("用户确认继续，正在保存测试结果...")
        # Stop tracing and export it into a zip archive.
        browser_context.tracing.stop(path="test-results/trace_doubao.zip")
        
    finally:
        # 确保浏览器上下文被关闭
        if browser_context:
            browser_context.close()

if __name__ == "__main__":
    # 如果直接运行脚本，显示帮助信息
    print("=" * 80)
    print("豆包AI文章总结测试脚本")
    print("=" * 80)
    print()
    print("功能说明：")
    print("本脚本使用豆包AI对Markdown文档进行智能总结，")
    print("自动限制总结内容在120字符以内，并进行长度验证。")
    print()
    print("使用方法：")
    print("使用 pytest 运行此脚本，例如：")
    print()
    print("1. 基本运行：")
    print("   pytest -s --headed --video on --screenshot on --tracing on ./test_doubao_ai_summary.py \\")
    print("     --markdown-file './article.md' \\")
    print("     --user-data-dir './chromium-browser-data'")
    print()
    print("2. 指定具体文件：")
    print("   pytest -s --headed ./test_doubao_ai_summary.py \\")
    print("     --markdown-file 'D:/path/to/your/article.md' \\")
    print("     --user-data-dir './chromium-browser-data'")
    print()
    print("参数说明：")
    print("--markdown-file      Markdown文件路径（必填，支持.md格式）")
    print("--user-data-dir      浏览器用户数据目录（必填，用于保存登录状态）")
    print()
    print("输出文件：")
    print("- 总结文本: test-results/summary_[文件名].txt")
    print("- 页面截图: test-results/screenshot_doubao.png")
    print("- 操作录制: test-results/trace_doubao.zip")
    print("- 视频录制: test-results/videos/")
    print()
    print("环境要求：")
    print("- Python 3.7+")
    print("- Playwright 已安装并配置")
    print("- 浏览器（Chrome/Chromium）已安装")
    print("- 豆包AI账号已登录（首次运行需要手动登录）")
    print()
    print("注意事项：")
    print("1. 首次运行前需要手动登录豆包AI账号")
    print("2. 确保Markdown文件格式正确，内容清晰")
    print("3. 总结会自动验证长度，超过120字符会给出提示")
    print("4. 脚本会自动保存总结结果和操作记录")
    print("5. 建议在测试环境中先验证功能")
    print()
    print("示例运行命令：")
    print("pytest -s --headed ./test_doubao_ai_summary.py \\")
    print("  --markdown-file './Windows系统信息查询Powershell脚本.md' \\")
    print("  --user-data-dir './chromium-browser-data'")
    print()
    print("作者：tornadoami")
    print("版本：1.0.0")
    print("更新日期：2025年")
    print("=" * 80)
