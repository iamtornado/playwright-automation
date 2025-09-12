# -*- coding: utf-8 -*-
"""
豆包AI图片生成测试脚本 - 简化版
展示如何使用DoubaoAIImageGenerator模块
"""

import pytest
import os
import sys
from playwright.sync_api import sync_playwright
from doubao_ai_image_generator import create_doubao_generator


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


def test_doubao_ai_image_generation(browser_context, request):
    """
    测试豆包AI图片生成功能
    """
    try:
        # 开始追踪
        browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)
        
        # 获取参数
        markdown_file = request.config.getoption("--markdown-file")
        if not markdown_file:
            markdown_file = "markdown_files/私有云Canonical's Charmed OpenStack部署教程.md"
        
        print("=" * 80)
        print("豆包AI图片生成测试")
        print("=" * 80)
        print(f"📄 使用Markdown文件: {markdown_file}")
        
        # 检查文件是否存在
        if not os.path.exists(markdown_file):
            print(f"❌ Markdown文件不存在: {markdown_file}")
            sys.exit(1)
        
        # 创建新页面
        page = browser_context.new_page()
        
        # 打开豆包AI页面
        print("🌐 正在打开豆包AI聊天页面...")
        page.goto("https://www.doubao.com/chat/")
        page.wait_for_load_state("networkidle")
        print("✅ 豆包AI页面加载完成")
        
        # 创建豆包AI图片生成器
        generator = create_doubao_generator(page, browser_context)
        
        # 执行完整的图片生成流程
        prompt, image_files = generator.generate_images_from_markdown(
            markdown_file=markdown_file,
            aspect_ratio="16:9"
        )
        
        # 输出结果
        if prompt and image_files:
            print("\n" + "=" * 60)
            print("🎉 图片生成成功！")
            print("=" * 60)
            print(f"📝 生成的提示词: {prompt[:100]}...")
            print(f"🖼️  生成的图片数量: {len(image_files)}")
            print("📁 图片文件:")
            for i, file_path in enumerate(image_files, 1):
                print(f"   {i}. {os.path.basename(file_path)}")
        else:
            print("\n❌ 图片生成失败")
        
        # 保存调试信息
        page.screenshot(path="test-results/doubao_ai_result.png", full_page=True)
        browser_context.tracing.stop(path="test-results/doubao_ai_trace.zip")
        
        print("\n✅ 测试完成")
        
    except Exception as e:
        print(f"❌ 测试过程中出错: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if browser_context:
            browser_context.close()


if __name__ == "__main__":
    print("豆包AI图片生成测试脚本")
    print("使用方法: pytest -s --headed ./test_doubao_ai_simple.py --markdown-file 'path/to/file.md'")
