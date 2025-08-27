import pytest
import re
from playwright.sync_api import Page, expect
# import pyperclip

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright):
    return {
        "geolocation": {"latitude": 22.558033372050147, "longitude": 113.46251764183725}, 
        "locale": "zh-CN", 
        "permissions": ["geolocation"], 
        "timezone_id": "Asia/Shanghai", 
        "viewport": {"width": 1366, "height": 768}
    }

@pytest.fixture(scope="session")
def browser_context(playwright, request):
    user_data_dir = request.config.getoption("--user-data-dir")
    
    # 添加视频录制配置
    context = playwright.chromium.launch_persistent_context(
        user_data_dir=user_data_dir,
        headless=False,
        record_video_dir="test-results/videos/",  # 添加视频录制目录
        record_video_size={"width": 1366, "height": 768},  # 设置视频尺寸
        geolocation={"latitude": 22.558033372050147, "longitude": 113.46251764183725},
        locale="zh-CN",
        permissions=["geolocation"],
        timezone_id="Asia/Shanghai",
        viewport={"width": 1366, "height": 768}
    )
    yield context
    # 确保上下文被关闭，这样视频才会保存
    context.close()

def test_example(browser_context, request):
    try:
        # Start tracing before creating / navigating a page.
        # browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)
        # 从 pytest 配置中获取参数
        title = request.config.getoption("--title")
        author = request.config.getoption("--author")
        summary = request.config.getoption("--summary")
        url = request.config.getoption("--url")
        markdown_file = request.config.getoption("--markdown-file")
        
        page = browser_context.pages[0] if browser_context.pages else browser_context.new_page()
        
        page.goto("https://editor.mdnice.com/")
        page.wait_for_load_state("networkidle")
        page.wait_for_load_state("domcontentloaded")
        page.get_by_role("button", name="plus").click()
        page.get_by_role("textbox", name="请输入标题").click()
        # 使用配置中的标题
        page.get_by_role("textbox", name="请输入标题").fill(title)
        page.get_by_role("button", name="新 增").click()
        page.get_by_role("link", name="文件").click()
        # 使用配置中的Markdown文件路径
        page.get_by_text("导入 Markdown").set_input_files(markdown_file)
        
        page.locator("#nice-sidebar-wechat").click()

        page2 = page.context.new_page()
        page2.goto("https://mp.weixin.qq.com")
        with page2.expect_popup() as page2_info:
            page2.get_by_text("文章", exact=True).click()
        page2 = page2_info.value
        page2.wait_for_load_state("networkidle")
        page2.wait_for_load_state("domcontentloaded")
        page2.keyboard.press("Control+V")

        page2.wait_for_timeout(10000)
        
        # 使用配置中的标题
        page2.get_by_role("textbox", name="请在这里输入标题").click()
        page2.get_by_role("textbox", name="请在这里输入标题").fill(title)
        # 使用配置中的作者
        page2.get_by_role("textbox", name="请输入作者").click()
        page2.get_by_role("textbox", name="请输入作者").fill(author)
        
        page2.on("dialog", lambda dialog: dialog.accept())
        page2.get_by_text("未声明").click()
        page2.wait_for_load_state("networkidle")
        page2.get_by_role("button", name="确定").click()

        page2.locator("#js_reward_setting_area").get_by_text("不开启").click()
        page2.wait_for_selector(".weui-desktop-dialog", state="visible", timeout=10000)
        page2.wait_for_load_state("networkidle")
        page2.wait_for_timeout(5000)
        page2.get_by_role("heading", name="赞赏").locator("span").click()
        page2.locator(".weui-desktop-dialog .weui-desktop-btn_primary").filter(has_text="确定").click()
        # page2.get_by_role("button", name="确定").click()

        page2.locator("#js_article_tags_area").get_by_text("未添加").click()
        page2.get_by_role("textbox", name="请选择合集").click()
        page2.locator("#vue_app").get_by_text("AI", exact=True).click()
        page2.get_by_role("button", name="确认").click()



        page2.get_by_text('拖拽或选择封面').hover()
        page2.get_by_role("link", name="从图片库选择").click()
        page2.get_by_role("link", name="AI配图 (28)").click()
        page2.locator(".weui-desktop-img-picker__img-thumb").first.click()
        page2.get_by_role("button", name="下一步").click()
        page2.get_by_role("button", name="确认").click()
        page2.get_by_role("textbox", name="选填，不填写则默认抓取正文开头部分文字，摘要会在转发卡片和公众号会话展示。").click()
        # 使用配置中的摘要
        page2.get_by_role("textbox", name="选填，不填写则默认抓取正文开头部分文字，摘要会在转发卡片和公众号会话展示。").fill(summary)

        # page2.on("dialog", lambda dialog2: dialog2.accept())
        page2.locator("#js_article_url_area").get_by_text("未添加").click()
        page2.get_by_role("textbox", name="输入或粘贴原文链接").click()
        # 使用配置中的URL
        page2.get_by_role("textbox", name="输入或粘贴原文链接").fill(url)
        # page2.wait_for_timeout(10000)
        # page2.get_by_text('请勿添加其他公众号的主页链接 链接不合法 此链接为预览链接，将在短期内失效 确定 取消').click()
        ok_button = page2.get_by_role("link", name="确定")
        expect(ok_button).to_be_visible()
        expect(ok_button).to_be_enabled()
        ok_button.click()

        page2.wait_for_timeout(5000)
        page2.get_by_role("button", name="保存为草稿").click()
        page2.locator("#js_save_success").get_by_text("已保存").click()
        
        # 在测试末尾添加截图
        page.screenshot(path="test-results/screenshot_mdnice.png")
        page2.screenshot(path="test-results/screenshot_wechat.png")
        # Stop tracing and export it into a zip archive.
        # browser_context.tracing.stop(path = "test-results/trace.zip")
    finally:
        # 确保浏览器上下文被关闭
        if browser_context:
            browser_context.close()


if __name__ == "__main__":
    # 如果直接运行脚本，显示帮助信息
    print("使用 pytest 运行此脚本，例如：")
    print("pytest -s --headed --video on --screenshot on --tracing on ./test_social_media_automatic_publish.py --title '自定义标题' --author '自定义作者'")