# -*- coding: utf-8 -*-
"""
钉钉文档编辑器简单聚焦测试
专门测试不同的聚焦方法
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
        geolocation={"latitude": 22.558033372050147, "longitude": 113.46251764183725},
        locale="zh-CN",
        permissions=["geolocation"],
        timezone_id="Asia/Shanghai",
        viewport={"width": 1920, "height": 1080}
    )
    yield context
    context.close()

def test_dingtalk_simple_focus(browser_context, request):
    """
    简单的钉钉文档编辑器聚焦测试
    """
    try:
        # 获取参数
        title = request.config.getoption("--title")
        if not title:
            print("❌ 缺少必需参数 --title！")
            sys.exit(1)
        
        print("=" * 60)
        print("🔍 钉钉文档编辑器简单聚焦测试")
        print("=" * 60)
        print(f"📝 测试标题: {title}")
        print("=" * 60)
        
        # 1. 打开钉钉文档
        print("1️⃣ 打开钉钉文档...")
        page_dingtalk_search = browser_context.new_page()
        page_dingtalk_search.goto("https://alidocs.dingtalk.com/i/nodes/Amq4vjg890AlRbA6Td9ZvlpDJ3kdP0wQ")
        
        # 登录检查
        try:
            login_button = page_dingtalk_search.locator("#wiki-doc-iframe").content_frame.get_by_role("button", name="登录钉钉文档")
            if login_button.is_visible(timeout=5000):
                print("正在登录...")
                login_button.click()
                page_dingtalk_search.locator(".module-qrcode-op-line > .base-comp-check-box > .base-comp-check-box-rememberme-box").first.click()
                page_dingtalk_search.get_by_text("邓龙").click()
                print("✅ 登录完成")
        except:
            print("✅ 已登录")
        
        # 搜索并打开文档
        page_dingtalk_search.get_by_test_id("cn-dropdown-trigger").locator("path").click()
        page_dingtalk_search.get_by_role("textbox", name="搜索（Ctrl + J）").click()
        page_dingtalk_search.get_by_role("textbox", name="搜索（Ctrl + J）").fill(title)
        
        with page_dingtalk_search.expect_popup() as page1_info:
            page_dingtalk_search.get_by_role("heading", name=title).locator("red").click()
        page_dingtalk_doc = page1_info.value
        
        page_dingtalk_doc.wait_for_load_state("domcontentloaded", timeout=30000)
        page_dingtalk_doc.wait_for_timeout(3000)
        print("✅ 文档页面加载完成")
        
        # 2. 获取iframe内容
        print("2️⃣ 获取iframe内容...")
        iframe_content = page_dingtalk_doc.locator("#wiki-doc-iframe").content_frame
        print("✅ iframe内容获取成功")
        
        # 3. 测试不同的聚焦方法
        print("3️⃣ 测试聚焦方法...")
        
        # 方法A: 直接点击iframe
        print("方法A: 直接点击iframe内容区域")
        try:
            iframe_content.click()
            print("✅ 方法A: 成功点击iframe内容区域")
        except Exception as e:
            print(f"❌ 方法A失败: {e}")
        
        # 等待一下
        page_dingtalk_doc.wait_for_timeout(1000)
        
        # 方法B: 查找并点击编辑器容器
        print("方法B: 查找编辑器容器")
        try:
            # 尝试多种可能的编辑器容器选择器
            editor_selectors = [
                "#dingapp",
                ".editor-container",
                ".document-editor",
                "[contenteditable='true']",
                "[role='textbox']"
            ]
            
            for selector in editor_selectors:
                elements = page_dingtalk_doc.locator(selector)
                if elements.count() > 0:
                    elements.first.click()
                    print(f"✅ 方法B: 成功点击选择器 {selector}")
                    break
            else:
                print("⚠️  方法B: 未找到任何编辑器容器")
        except Exception as e:
            print(f"❌ 方法B失败: {e}")
        
        # 等待一下
        page_dingtalk_doc.wait_for_timeout(1000)
        
        # 方法C: 尝试键盘操作
        print("方法C: 尝试键盘操作")
        try:
            # 先点击iframe确保焦点
            iframe_content.click()
            page_dingtalk_doc.wait_for_timeout(500)
            
            # 尝试移动到文档开头
            iframe_content.press("Control+Home")
            print("✅ 方法C: 成功执行Control+Home")
        except Exception as e:
            print(f"❌ 方法C失败: {e}")
        
        # 等待一下
        page_dingtalk_doc.wait_for_timeout(1000)
        
        # 方法D: 尝试点击插入按钮
        print("方法D: 尝试点击插入按钮")
        try:
            insert_button = iframe_content.get_by_test_id("overlay-bi-toolbar-insertMore").get_by_text("插入")
            if insert_button.is_visible():
                insert_button.click()
                print("✅ 方法D: 成功点击插入按钮")
            else:
                print("⚠️  方法D: 插入按钮不可见")
        except Exception as e:
            print(f"❌ 方法D失败: {e}")
        
        # 4. 保存截图
        print("4️⃣ 保存测试截图...")
        page_dingtalk_doc.screenshot(path="test-results/dingtalk_simple_focus.png", full_page=True)
        print("✅ 截图已保存")
        
        # 5. 等待用户确认
        print("\n" + "=" * 60)
        print("测试完成！")
        print("=" * 60)
        print("请检查截图和输出信息")
        print("按 Enter 键退出...")
        input()
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 60)
    print("钉钉文档编辑器简单聚焦测试")
    print("=" * 60)
    print("使用方法：")
    print("pytest -s --headed ./test_dingtalk_simple_focus.py --title '文章标题'")
    print("=" * 60)
