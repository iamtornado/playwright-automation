# -*- coding: utf-8 -*-
"""
钉钉文档iframe内容分析脚本
专门分析iframe内的DOM结构和元素
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

def test_dingtalk_iframe_analysis(browser_context, request):
    """
    分析钉钉文档iframe内容
    """
    try:
        # 获取参数
        title = request.config.getoption("--title")
        if not title:
            print("❌ 缺少必需参数 --title！")
            sys.exit(1)
        
        print("=" * 80)
        print("🔍 钉钉文档iframe内容分析")
        print("=" * 80)
        print(f"📝 测试标题: {title}")
        print("=" * 80)
        
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
        
        # 3. 分析iframe内容
        print("3️⃣ 分析iframe内容...")
        
        # 获取所有元素
        try:
            all_elements = iframe_content.locator('*')
            total_count = all_elements.count()
            print(f"📊 iframe中总共有 {total_count} 个元素")
        except Exception as e:
            print(f"⚠️  无法统计总元素数量: {e}")
            total_count = 0
        
        # 分析不同类型的元素
        element_types = {
            'div': 'div',
            'span': 'span',
            'button': 'button',
            'input': 'input',
            'textarea': 'textarea',
            'a': 'a',
            'img': 'img',
            'svg': 'svg',
            'p': 'p',
            'h1': 'h1',
            'h2': 'h2',
            'h3': 'h3',
            'h4': 'h4',
            'h5': 'h5',
            'h6': 'h6'
        }
        
        print("\n📊 元素类型统计:")
        for tag_name, selector in element_types.items():
            try:
                count = iframe_content.locator(selector).count()
                if count > 0:
                    print(f"  {tag_name}: {count} 个")
            except:
                pass
        
        # 分析特殊属性元素
        special_attributes = {
            'contenteditable': '[contenteditable="true"]',
            'role_textbox': '[role="textbox"]',
            'role_button': '[role="button"]',
            'role_editor': '[role="editor"]',
            'clickable': '[onclick]',
            'testid': '[data-testid]',
            'class_editor': '.editor',
            'class_content': '.content',
            'class_document': '.document'
        }
        
        print("\n📊 特殊属性元素统计:")
        for attr_name, selector in special_attributes.items():
            try:
                count = iframe_content.locator(selector).count()
                if count > 0:
                    print(f"  {attr_name}: {count} 个")
            except:
                pass
        
        # 分析可能的编辑器元素
        editor_selectors = [
            '.sc-psedN',
            '.editor-content',
            '.document-body',
            '.text-editor',
            '.rich-editor',
            '.markdown-editor',
            '.wysiwyg-editor',
            '[data-editor]',
            '[data-content]',
            '[data-document]'
        ]
        
        print("\n📊 可能的编辑器元素:")
        for selector in editor_selectors:
            try:
                count = iframe_content.locator(selector).count()
                if count > 0:
                    print(f"  {selector}: {count} 个")
            except:
                pass
        
        # 4. 尝试获取元素的详细信息
        print("\n4️⃣ 获取元素详细信息...")
        
        # 获取所有可点击元素
        try:
            clickable_elements = iframe_content.locator('button, a, [onclick], [role="button"], [tabindex]')
            clickable_count = clickable_elements.count()
            print(f"📊 可点击元素: {clickable_count} 个")
            
            if clickable_count > 0:
                print("前10个可点击元素:")
                for i in range(min(10, clickable_count)):
                    try:
                        element = clickable_elements.nth(i)
                        tag_name = element.evaluate('el => el.tagName')
                        text_content = element.text_content()[:50] if element.text_content() else ""
                        class_name = element.get_attribute('class') or ""
                        print(f"  {i+1}. <{tag_name}> {text_content} (class: {class_name})")
                    except:
                        pass
        except Exception as e:
            print(f"⚠️  无法获取可点击元素详情: {e}")
        
        # 获取所有输入元素
        try:
            input_elements = iframe_content.locator('input, textarea, [contenteditable="true"]')
            input_count = input_elements.count()
            print(f"\n📊 输入元素: {input_count} 个")
            
            if input_count > 0:
                print("所有输入元素:")
                for i in range(input_count):
                    try:
                        element = input_elements.nth(i)
                        tag_name = element.evaluate('el => el.tagName')
                        input_type = element.get_attribute('type') or ""
                        placeholder = element.get_attribute('placeholder') or ""
                        class_name = element.get_attribute('class') or ""
                        print(f"  {i+1}. <{tag_name}> type={input_type} placeholder='{placeholder}' class='{class_name}'")
                    except:
                        pass
        except Exception as e:
            print(f"⚠️  无法获取输入元素详情: {e}")
        
        # 5. 保存iframe的HTML内容
        print("\n5️⃣ 保存iframe HTML内容...")
        try:
            html_content = iframe_content.content()
            with open("test-results/dingtalk_iframe_content.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            print("✅ iframe HTML内容已保存到: test-results/dingtalk_iframe_content.html")
        except Exception as e:
            print(f"⚠️  无法保存iframe HTML内容: {e}")
        
        # 6. 保存截图
        print("6️⃣ 保存分析截图...")
        page_dingtalk_doc.screenshot(path="test-results/dingtalk_iframe_analysis.png", full_page=True)
        print("✅ 分析截图已保存到: test-results/dingtalk_iframe_analysis.png")
        
        # 7. 等待用户确认
        print("\n" + "=" * 80)
        print("分析完成！")
        print("=" * 80)
        print("请检查以下文件:")
        print("- test-results/dingtalk_iframe_analysis.png (截图)")
        print("- test-results/dingtalk_iframe_content.html (iframe HTML内容)")
        print("按 Enter 键退出...")
        input()
        
    except Exception as e:
        print(f"❌ 分析过程中出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("=" * 80)
    print("钉钉文档iframe内容分析脚本")
    print("=" * 80)
    print("使用方法：")
    print("pytest -s --headed ./test_dingtalk_iframe_analysis.py --title '文章标题'")
    print("=" * 80)
