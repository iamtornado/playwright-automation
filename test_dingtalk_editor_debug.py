# -*- coding: utf-8 -*-
"""
钉钉文档编辑器聚焦调试脚本
专门用于调试钉钉文档编辑器的聚焦和定位问题
"""

import pytest
import os
import sys
from playwright.sync_api import Page, expect

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

def test_dingtalk_editor_focus_debug(browser_context, request):
    """
    调试钉钉文档编辑器聚焦问题
    """
    try:
        # 开始追踪
        browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        # 获取参数
        title = request.config.getoption("--title")
        if not title:
            print("❌ 缺少必需参数 --title！")
            print("请提供文章标题，例如：")
            print("pytest -s --headed ./test_dingtalk_editor_debug.py --title '文章标题'")
            sys.exit(1)
        
        print("=" * 80)
        print("🔍 钉钉文档编辑器聚焦调试")
        print("=" * 80)
        print(f"📝 测试标题: {title}")
        print("=" * 80)
        
        # 1. 打开钉钉文档搜索页面
        print("1️⃣ 打开钉钉文档搜索页面...")
        page_dingtalk_search = browser_context.new_page()
        page_dingtalk_search.goto("https://alidocs.dingtalk.com/i/nodes/Amq4vjg890AlRbA6Td9ZvlpDJ3kdP0wQ")
        
        # 2. 登录检查
        print("2️⃣ 检查登录状态...")
        try:
            login_button = page_dingtalk_search.locator("#wiki-doc-iframe").content_frame.get_by_role("button", name="登录钉钉文档")
            if login_button.is_visible(timeout=5000):
                print("检测到需要登录钉钉文档，正在执行登录...")
                login_button.click()
                page_dingtalk_search.locator(".module-qrcode-op-line > .base-comp-check-box > .base-comp-check-box-rememberme-box").first.click()
                page_dingtalk_search.get_by_text("邓龙").click()
                print("✅ 登录钉钉文档完成")
            else:
                print("✅ 已登录钉钉文档，跳过登录步骤")
        except Exception as e:
            print(f"⚠️  登录检查过程中出现异常: {e}")
            print("继续执行后续步骤...")
        
        # 3. 搜索文档
        print("3️⃣ 搜索文档...")
        page_dingtalk_search.get_by_test_id("cn-dropdown-trigger").locator("path").click()
        page_dingtalk_search.get_by_role("textbox", name="搜索（Ctrl + J）").click()
        page_dingtalk_search.get_by_role("textbox", name="搜索（Ctrl + J）").fill(title)
        
        # 4. 打开文档
        print("4️⃣ 打开文档...")
        with page_dingtalk_search.expect_popup() as page1_info:
            page_dingtalk_search.get_by_role("heading", name=title).locator("red").click()
        page_dingtalk_doc = page1_info.value
        
        # 等待页面加载
        page_dingtalk_doc.wait_for_load_state("domcontentloaded", timeout=30000)
        print("✅ 钉钉文档页面基本加载完成")
        page_dingtalk_doc.wait_for_timeout(3000)
        
        # 5. 调试iframe内容
        print("5️⃣ 调试iframe内容...")
        iframe_content = page_dingtalk_doc.locator("#wiki-doc-iframe").content_frame
        print(f"✅ 获取到iframe内容: {iframe_content}")
        
        # 6. 尝试多种聚焦方法
        print("6️⃣ 尝试多种聚焦方法...")
        
        
        # 方法1: 查找文档主体
        print("方法4: 查找文档主体")
        try:
            doc_body = iframe_content.locator('body, .document-body, .editor-content')
            if doc_body.count() > 0:
                doc_body.first.click()
                print("✅ 方法4成功: 点击文档主体")
                doc_body.first.press("Control+Home")
            else:
                print("⚠️  方法4: 未找到文档主体")
        except Exception as e:
            print(f"❌ 方法4失败: {e}")
        
        # 方法2: 查找特定类名元素
        # print("方法5: 查找特定类名元素")
        # try:
        #     # 尝试查找常见的编辑器类名
        #     editor_classes = ['.sc-psedN', '.editor', '.content', '.document', '.text-editor']
        #     for class_name in editor_classes:
        #         elements = iframe_content.locator(class_name)
        #         if elements.count() > 0:
        #             elements.first.click()
        #             print(f"✅ 方法5成功: 找到并点击了类名为 {class_name} 的元素")
        #             break
        #     else:
        #         print("⚠️  方法5: 未找到任何编辑器类名元素")
        # except Exception as e:
        #     print(f"❌ 方法5失败: {e}")
        
        # 7. 等待焦点设置
        print("7️⃣ 等待焦点设置...")
        page_dingtalk_doc.wait_for_timeout(2000)
        
        # 8. 尝试移动到文档开头
        print("8️⃣ 尝试移动到文档开头...")
        try:
            print("正在按下组合键（Control+Home）...")
            iframe_content.press("Control+Home")
            print("✅ 组合键（Control+Home）按下成功")
            page_dingtalk_doc.wait_for_timeout(2000)
        except Exception as e:
            print(f"❌ 组合键（Control+Home）失败: {e}")
        
        # 9. 尝试点击插入按钮
        print("9️⃣ 尝试点击插入按钮...")
        try:
            insert_button = iframe_content.get_by_test_id("overlay-bi-toolbar-insertMore").get_by_text("插入")
            if insert_button.is_visible():
                insert_button.click()
                print("✅ 插入按钮点击成功")
            else:
                print("⚠️  插入按钮不可见")
        except Exception as e:
            print(f"❌ 插入按钮点击失败: {e}")
        
        # 10. 调试信息收集
        print("🔍 调试信息收集...")
        
        # 获取iframe内容的所有元素
        try:
            all_elements = iframe_content.locator('*')
            print(f"📊 iframe中总共有 {all_elements.count()} 个元素")
        except Exception as e:
            print(f"⚠️  无法统计iframe元素数量: {e}")
        
        # 获取可点击元素
        try:
            clickable_elements = iframe_content.locator('button, a, [onclick], [role="button"]')
            print(f"📊 找到 {clickable_elements.count()} 个可点击元素")
        except Exception as e:
            print(f"⚠️  无法统计可点击元素: {e}")
        
        # 获取输入元素
        try:
            input_elements = iframe_content.locator('input, textarea, [contenteditable="true"]')
            print(f"📊 找到 {input_elements.count()} 个输入元素")
        except Exception as e:
            print(f"⚠️  无法统计输入元素: {e}")
        
        # 11. 截图保存
        print("📸 保存调试截图...")
        page_dingtalk_doc.screenshot(path="test-results/dingtalk_editor_debug.png", full_page=True)
        print("✅ 调试截图已保存到: test-results/dingtalk_editor_debug.png")
        
        # 12. 等待用户确认
        print("\n" + "=" * 80)
        print("调试完成！")
        print("=" * 80)
        print("请检查调试截图和输出信息，分析聚焦问题。")
        print("按 Enter 键继续...")
        input()
        
        # 停止追踪
        browser_context.tracing.stop(path="test-results/dingtalk_editor_debug_trace.zip")
        print("✅ 追踪文件已保存到: test-results/dingtalk_editor_debug_trace.zip")
        
    except Exception as e:
        print(f"❌ 调试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # 确保浏览器上下文被关闭
        if browser_context:
            browser_context.close()

if __name__ == "__main__":
    print("=" * 80)
    print("钉钉文档编辑器聚焦调试脚本")
    print("=" * 80)
    print()
    print("功能说明：")
    print("本脚本专门用于调试钉钉文档编辑器的聚焦和定位问题")
    print("会尝试多种聚焦方法并记录调试信息")
    print()
    print("使用方法：")
    print("pytest -s --headed ./test_dingtalk_editor_debug.py --title '文章标题'")
    print()
    print("参数说明：")
    print("--title              文章标题（必填）")
    print("--user-data-dir      浏览器用户数据目录（可选）")
    print()
    print("调试输出：")
    print("- 会尝试多种聚焦方法")
    print("- 记录每种方法的成功/失败状态")
    print("- 收集iframe元素统计信息")
    print("- 保存调试截图和追踪文件")
    print()
    print("示例：")
    print("pytest -s --headed ./test_dingtalk_editor_debug.py --title '测试文章'")
    print("=" * 80)
