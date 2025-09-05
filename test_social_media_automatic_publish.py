import pytest
import re
import random
import sys
import os
from playwright.sync_api import Page, expect
# import pyperclip

# 导入字数统计功能
from simple_word_counter import validate_and_clean_text

# 定义各平台的话题标签数量限制
PLATFORM_TAG_LIMITS = {
    'zhihu': 3,           # 知乎最多3个话题标签
    'csdn': 10,           # CSDN最多10个话题标签
    'xiaohongshu': 10,    # 小红书最多10个话题标签
    'douyin': 5,          # 抖音最多5个话题标签
    'kuaishou': 4,        # 快手最多4个话题标签
    '51cto': 5,           # 51CTO最多5个话题标签
}

def get_platform_tags(all_tags, platform, limit=None):
    """
    根据平台获取合适数量的话题标签
    
    Args:
        all_tags: 所有可用的话题标签列表
        platform: 平台名称
        limit: 自定义限制数量（可选）
    
    Returns:
        适合该平台的话题标签列表
    """
    if limit is None:
        limit = PLATFORM_TAG_LIMITS.get(platform, len(all_tags))
    
    if len(all_tags) <= limit:
        return all_tags
    
    # 随机选择指定数量的标签
    return random.sample(all_tags, limit)

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

def test_example(browser_context, request):
    try:
        # Start tracing before creating / navigating a page.
        browser_context.tracing.start(screenshots=True, snapshots=True, sources=True)
        # 从 pytest 配置中获取参数
        title = request.config.getoption("--title")
        author = request.config.getoption("--author")
        summary = request.config.getoption("--summary")
        url = request.config.getoption("--url")
        markdown_file = request.config.getoption("--markdown-file")
        platforms = request.config.getoption("--platforms")
        cover_image = request.config.getoption("--cover-image")
        tags_str = request.config.getoption("--tags")
        
        # 验证并清理summary文本长度
        print("=" * 60)
        print("📏 验证summary文本长度...")
        validation_result = validate_and_clean_text(summary, max_length=120)
        print(validation_result['message'])
        
        if not validation_result['success']:
            print("\n❌ Summary文本过长，无法继续执行脚本！")
            print("请修改summary参数，确保字符数不超过120个。")
            print(f"当前summary: \"{validation_result['original_text']}\"")
            print(f"原始长度: {validation_result['original_count']}字符")
            print(f"清理后长度: {validation_result['cleaned_count']}字符")
            print("\n建议解决方案：")
            print("1. 缩短summary文本内容")
            print("2. 移除不必要的词汇和标点符号")
            print("3. 使用更简洁的表达方式")
            sys.exit(1)
        
        # 如果清理后的文本更短，使用清理后的版本
        if validation_result['cleaned_count'] < validation_result['original_count']:
            summary = validation_result['cleaned_text']
            print(f"✅ 已自动使用清理后的summary（减少了{validation_result['original_count'] - validation_result['cleaned_count']}个字符）")
        
        print("=" * 60)
        
        # 下载钉钉文档为本地markdown文件
        page_dingtalk_DreamAI_KB = browser_context.new_page()
        page_dingtalk_DreamAI_KB.goto("https://alidocs.dingtalk.com/i/nodes/Amq4vjg890AlRbA6Td9ZvlpDJ3kdP0wQ")
        # 登录钉钉文档
        # 检查是否需要登录
        try:
            login_button = page_dingtalk_DreamAI_KB.locator("#wiki-doc-iframe").content_frame.get_by_role("button", name="登录钉钉文档")
            if login_button.is_visible(timeout=5000):
                print("检测到需要登录钉钉文档，正在执行登录...")
                login_button.click()
                page_dingtalk_DreamAI_KB.locator(".module-qrcode-op-line > .base-comp-check-box > .base-comp-check-box-rememberme-box").first.click()
                page_dingtalk_DreamAI_KB.get_by_text("邓龙").click()
                print("登录钉钉文档完成")
            else:
                print("已登录钉钉文档，跳过登录步骤")
        except Exception as e:
            print(f"登录检查过程中出现异常: {e}")
            print("继续执行后续步骤...")
        # page.goto("https://alidocs.dingtalk.com/i/nodes/Amq4vjg890AlRbA6Td9ZvlpDJ3kdP0wQ?code=1d328c3fafd03cf4bc3c319882ced3d4&authCode=1d328c3fafd03cf4bc3c319882ced3d4")
        # page_dingtalk_DreamAI_KB.get_by_role("textbox", name="快速搜索文档标题").click()
        # page_dingtalk_DreamAI_KB.get_by_role("textbox", name="快速搜索文档标题").fill("craXcel，一个可以移除Excel密码的开源工具")
        page_dingtalk_DreamAI_KB.get_by_test_id("cn-dropdown-trigger").locator("path").click()
        page_dingtalk_DreamAI_KB.get_by_role("textbox", name="搜索（Ctrl + J）").click()
        page_dingtalk_DreamAI_KB.get_by_role("textbox", name="搜索（Ctrl + J）").fill("craXcel，一个可以移除Excel密码的开源工具")
        with page_dingtalk_DreamAI_KB.expect_popup() as page1_info:
            page_dingtalk_DreamAI_KB.get_by_role("heading", name="craXcel，一个可以移除Excel密码的开源工具").locator("red").click()
        page_dingtalk_doc = page1_info.value
        page_dingtalk_doc.locator("#wiki-doc-iframe").content_frame.get_by_test_id("doc-header-more-button").click()
        # 下载钉钉文档为本地markdown文件
        page_dingtalk_doc.locator("#wiki-doc-iframe").content_frame.get_by_text("下载到本地").first.click()
        with page_dingtalk_doc.expect_download() as download_info:
            page_dingtalk_doc.locator("#wiki-doc-iframe").content_frame.get_by_text("Markdown(.md)").click()
        download = download_info.value
        # Wait for the download process to complete and save the downloaded file somewhere
        # 获取下载文件的建议文件名
        suggested_filename = download.suggested_filename
        # 构建保存路径
        save_path = os.path.join("D:/tornadofiles/scripts_脚本/github_projects/playwright-automation/markdown_files", suggested_filename)
        # 保存文件
        download.save_as(save_path)
        
        # 获取下载文件的绝对路径和文件名
        downloaded_file_path = os.path.abspath(save_path)
        downloaded_filename = os.path.basename(downloaded_file_path)
        
        print(f"📁 下载文件名: {downloaded_filename}")
        print(f"📂 下载文件绝对路径: {downloaded_file_path}")

        # 将gemini生成的文章封面图上传到相应钉钉文档的第一行中
        try:
            # 1. 定位到文档开头
            iframe_content = page_dingtalk_doc.locator("#wiki-doc-iframe").content_frame
            first_paragraph = iframe_content.locator(".sc-psedN").first
            
            # 确保元素可见并点击获得焦点
            first_paragraph.wait_for(state="visible", timeout=10000)
            first_paragraph.click()
            
            # 等待焦点设置完成
            page_dingtalk_doc.wait_for_timeout(1000)
            
            # 2. 尝试移动到文档开头（修复组合键问题）
            try:
                first_paragraph.press("Control+Home")
                print("✅ 成功移动到文档开头")
            except Exception as e:
                print(f"⚠️  组合键失败，继续执行: {e}")
            
            # 3. 点击插入按钮
            iframe_content.get_by_test_id("overlay-bi-toolbar-insertMore").get_by_text("插入").click()
            # iframe_content.get_by_text("图片上传本地图片").click()
            
            # 4. 使用文件选择器处理方式上传图片（参考51CTO的方法）
            with page_dingtalk_doc.expect_file_chooser() as fc_info_dingtalk:
                # 触发文件选择器的元素可能需要调整，这里可能需要点击一个上传按钮或输入区域
                # 由于当前定位到的是textbox，我们需要找到实际的文件输入触发元素
                try:
                    # 尝试点击可能的文件上传触发元素
                    iframe_content.get_by_text("图片上传本地图片").click()
                except:
                    try:
                        # 如果没有"点击上传"，尝试其他可能的触发元素
                        iframe_content.locator("input[type='file']").first.click()
                    except:
                        # 如果都找不到，尝试点击上传区域
                        iframe_content.locator(".upload-area, .file-upload, [data-upload]").first.click()
            
            # 获取文件选择器并设置文件
            file_chooser_dingtalk = fc_info_dingtalk.value
            file_chooser_dingtalk.set_files(cover_image)
            
            # 等待封面图上传完成
            page_dingtalk_doc.wait_for_timeout(3000)
            page_dingtalk_doc.wait_for_load_state("networkidle")
            print("✅ 图片上传成功")
            
        except Exception as e:
            print(f"❌ 图片上传失败: {e}")
            print("跳过图片上传，继续执行后续步骤...")

        # 解析话题标签
        all_tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        print(f"📝 所有话题标签: {all_tags}")
        
        # 解析平台参数
        if platforms.lower() == 'all':
            target_platforms = ['mdnice', 'wechat', 'zhihu', 'csdn', '51cto', 'cnblogs', 'xiaohongshu_newspic', 'douyin_newspic', 'kuaishou_newspic', 'bilibili_newspic']
        else:
            target_platforms = [p.strip().lower() for p in platforms.split(',')]
        
        print(f"将发布到以下平台: {', '.join(target_platforms)}")
        print(f"使用封面图片: {cover_image}")
        
        ## 使用mdnice，将markdown文件转换为微信公众号兼容的格式。
        ## 这是发布到微信公众号的预处理步骤，确保格式兼容性
        if 'wechat' in target_platforms:
            print("正在处理 mdnice...")
            page_mdnice = browser_context.pages[0] if browser_context.pages else browser_context.new_page()
            page_mdnice.goto("https://editor.mdnice.com/")
            page_mdnice.wait_for_load_state("networkidle")
            page_mdnice.wait_for_load_state("domcontentloaded")
            
            # 创建新文章
            page_mdnice.get_by_role("button", name="plus").click()
            page_mdnice.get_by_role("textbox", name="请输入标题").click()

            # 截断标题，确保不超过64个字符
            mdnice_title = title[:64] if len(title) > 64 else title
            print(f"📝 mdnice 标题（已截断至64字符）: {mdnice_title}")

            # 使用截断后的标题
            page_mdnice.get_by_role("textbox", name="请输入标题").fill(mdnice_title)
            page_mdnice.get_by_role("button", name="新 增").click()
            
            # 导入Markdown文件
            page_mdnice.get_by_role("link", name="文件").click()
            # 使用配置中的Markdown文件路径，上传markdown文件
            page_mdnice.get_by_text("导入 Markdown").set_input_files(markdown_file)
            
            # 切换到微信公众号预览模式
            page_mdnice.locator("#nice-sidebar-wechat").click()

            # 清理：删除刚刚新建的文章，使用截断后的标题进行匹配
            try:
                page_mdnice.wait_for_timeout(2000)  # 等待文章列表更新
                
                # 使用截断后的标题进行匹配
                article_locator = page_mdnice.get_by_role("listitem").filter(
                    has_text=re.compile(f"{re.escape(mdnice_title)}.*")
                )
                
                # 检查是否找到文章
                if article_locator.count() > 0:
                    article_locator.locator("svg").nth(1).click()
                    page_mdnice.get_by_role("menuitem", name="删除文章").locator("a").click()
                    page_mdnice.get_by_role("button", name="确 认").click()
                    print("✅ 成功删除 mdnice 测试文章")
                else:
                    print("⚠️  未找到要删除的文章项，跳过删除步骤")
                    
            except Exception as e:
                print(f"⚠️  删除 mdnice 文章时出错: {e}")
                print("继续执行后续步骤...")
            
            ## 微信公众号，发布文章。
            ## 注意：需要先在微信公众号平台登录，脚本会自动填充内容并保存为草稿
            print("正在发布到微信公众号...")
            page_wechat = browser_context.new_page()
            page_wechat.goto("https://mp.weixin.qq.com")
            
            # 点击"文章"按钮，会打开新窗口
            with page_wechat.expect_popup() as page_wechat_info:
                page_wechat.get_by_text("文章", exact=True).click()
            page_wechat = page_wechat_info.value
            page_wechat.wait_for_load_state("networkidle")
            page_wechat.wait_for_load_state("domcontentloaded")
            
            # 粘贴从mdnice复制的HTML内容
            page_wechat.keyboard.press("Control+V")
            # 等待60秒，确保编辑器中的图片正常转存到微信服务器
            page_wechat.wait_for_load_state("networkidle")
            # page_wechat.wait_for_timeout(60000)
            
            # 设置文章标题
            page_wechat.get_by_role("textbox", name="请在这里输入标题").click()
            page_wechat.get_by_role("textbox", name="请在这里输入标题").fill(title)
            
            # 设置作者名称
            page_wechat.get_by_role("textbox", name="请输入作者").click()
            page_wechat.get_by_role("textbox", name="请输入作者").fill(author)
            
            # 处理弹窗确认
            page_wechat.on("dialog", lambda dialog: dialog.accept())
            page_wechat.locator(".js_unset_original_title").filter(has_text="未声明").click()
            page_wechat.wait_for_load_state("networkidle")
            page_wechat.get_by_role("button", name="确定").click()

            # 设置赞赏功能（开启）
            page_wechat.locator("#js_reward_setting_area").get_by_text("不开启").click()
            # page_wechat.wait_for_selector(".weui-desktop-dialog", state="visible", timeout=10000)
            page_wechat.wait_for_load_state("networkidle")
            page_wechat.wait_for_timeout(5000)
            page_wechat.get_by_role("heading", name="赞赏").locator("span").click()
            page_wechat.locator(".weui-desktop-dialog .weui-desktop-btn_primary").filter(has_text="确定").click()

            # 设置文章合集标签
            page_wechat.locator("#js_article_tags_area").get_by_text("未添加").click()
            page_wechat.get_by_role("textbox", name="请选择合集").click()
            page_wechat.locator("#vue_app").get_by_text("AI", exact=True).click()
            page_wechat.get_by_role("button", name="确认").click()

            # 设置文章封面图片
            # 使用CSS类名定位，更精确和稳定
            page_wechat.locator(".js_share_type_none_image").hover()
            page_wechat.get_by_role("link", name="从图片库选择").click()
            # 点击AI配图文件夹，使用正则表达式匹配"AI配图 (数字)"格式的链接
            # 例如："AI配图 (15)" 或 "AI配图 (23)" 等，数字表示该文件夹中的图片数量
            page_wechat.get_by_role("link", name=re.compile(r"AI配图 \(\d+\)")).click()
            page_wechat.locator(".weui-desktop-img-picker__img-thumb").first.click()
            page_wechat.get_by_role("button", name="下一步").click()
            page_wechat.get_by_role("button", name="确认").click()
            
            # 设置文章摘要
            page_wechat.get_by_role("textbox", name="选填，不填写则默认抓取正文开头部分文字，摘要会在转发卡片和公众号会话展示。").click()
            # 使用配置中的摘要
            page_wechat.get_by_role("textbox", name="选填，不填写则默认抓取正文开头部分文字，摘要会在转发卡片和公众号会话展示。").fill(summary)

            # 设置原文链接
            page_wechat.locator("#js_article_url_area").get_by_text("未添加").click()
            page_wechat.get_by_role("textbox", name="输入或粘贴原文链接").click()
            # 使用配置中的URL
            page_wechat.get_by_role("textbox", name="输入或粘贴原文链接").fill(url)
            
            # 确认链接设置
            ok_button = page_wechat.get_by_role("link", name="确定")
            expect(ok_button).to_be_visible()
            expect(ok_button).to_be_enabled()
            ok_button.click()

            page_wechat.wait_for_timeout(5000)
            # 保存为草稿（避免意外丢失）
            page_wechat.get_by_role("button", name="保存为草稿").click()
            page_wechat.locator("#js_save_success").get_by_text("已保存").click()
        
        ## 知乎，发布文章。
        ## 支持Markdown文件导入，自动设置标题、封面、话题标签等
        if 'zhihu' in target_platforms:
            print("正在发布到知乎...")
            # 获取知乎平台的话题标签
            zhihu_tags = get_platform_tags(all_tags, 'zhihu')
            print(f"🏷️  知乎话题标签: {zhihu_tags}")
            
            page_zhihu = browser_context.new_page()
            page_zhihu.goto("https://www.zhihu.com/")
            
            # 点击"写文章"按钮，会打开编辑器新窗口
            with page_zhihu.expect_popup() as page_zhihu_info:
                page_zhihu.get_by_text("写文章").click()
            page_zhihu_editor = page_zhihu_info.value
            
            # 点击"文档"按钮打开导入模态框
            page_zhihu_editor.get_by_role("button", name="文档").click()
            page_zhihu_editor.locator("#Popover5-content").get_by_role("button", name="文档").click()            
            
            # 等待文档导入模态框出现
            page_zhihu_editor.wait_for_selector(".Editable-docModal", state="visible", timeout=10000)
            
            # 直接选择文件输入框并上传文件
            page_zhihu_editor.locator(".Editable-docModal input[type='file']").set_input_files(markdown_file)
            
            # 等待文件上传完成和内容解析
            page_zhihu_editor.wait_for_timeout(10000)
            
            # 设置文章标题
            page_zhihu_editor.get_by_placeholder("请输入标题（最多 100 个字）").click()
            page_zhihu_editor.get_by_placeholder("请输入标题（最多 100 个字）").fill(title)
            
            # 设置文章目录
            page_zhihu_editor.get_by_role("button", name="目录").click()
            
            # 设置文章封面图片
            page_zhihu_editor.get_by_text("添加文章封面").set_input_files(cover_image)
            
            # 添加话题标签（知乎的话题标签需要从下拉框中选择，不能随便填写）
            # 知乎最多支持添加3个话题标签
            for tag in zhihu_tags:
                page_zhihu_editor.get_by_role("button", name="添加话题").click()
                page_zhihu_editor.get_by_role("textbox", name="搜索话题").click()
                page_zhihu_editor.get_by_role("textbox", name="搜索话题").fill(tag)
                page_zhihu_editor.get_by_role("textbox", name="搜索话题").press("Enter")
                page_zhihu_editor.get_by_role("button", name=tag, exact=True).click()
                page_zhihu_editor.wait_for_timeout(1000)
            
            # 设置送礼物功能（开启）
            page_zhihu_editor.locator("label").filter(has_text="开启送礼物").get_by_role("img").click()
            page_zhihu_editor.get_by_role("button", name="确定").click()
            
            # page_zhihu_editor.wait_for_timeout(5000)
            # 知乎编辑器会自动保存草稿，无需手动保存
            # 点击发布按钮并等待页面导航完成。注意：点击“发布”按钮后，新的网页会报错，实际上文章已经发布成功了。错误信息：{"error":{"message":"您当前请求存在异常，暂时限制本次访问。如有疑问，您可以通过手机摇一摇或登录后私信知乎小管家反馈。8131ab59c0a33a85e9efb02aaaf1b643","code":40362}}
            page_zhihu_editor.wait_for_load_state("networkidle")
            page_zhihu_editor.get_by_role("button", name="发布").click()
            
            # 等待页面跳转并检查URL是否包含发布成功标识
            page_zhihu_editor.wait_for_url("**/just_published=1", timeout=30000)
            print("知乎文章发布成功！")
            page_zhihu_editor.wait_for_load_state("networkidle")

        ## CSDN博客，发布文章。
        ## 支持Markdown导入，自动设置标签、分类、封面等
        if 'csdn' in target_platforms:
            print("正在发布到CSDN...")
            # 获取CSDN平台的话题标签
            csdn_tags = get_platform_tags(all_tags, 'csdn')
            print(f"🏷️  CSDN话题标签: {csdn_tags}")
            
            page_csdn = browser_context.new_page()
            page_csdn.goto("https://www.csdn.net/")
            page_csdn.get_by_role("link", name="创作", exact=True).click()
            
            # 使用MD编辑器
            with page_csdn.expect_popup() as page_csdn_editor:
                page_csdn.get_by_role("button", name="使用 MD 编辑器").click()
            page_csdn_md_editor = page_csdn_editor.value
            
            # 导入Markdown文件
            # page_csdn_md_editor.get_by_text("导入 导入").click()
            page_csdn_md_editor.get_by_text("导入 导入").set_input_files(markdown_file)
            page_csdn_md_editor.wait_for_timeout(10000)
            
            # 设置文章目录
            page_csdn_md_editor.get_by_role("button", name="目录").click()
            
            # 设置文章标签（CSDN支持自定义标签）
            page_csdn_md_editor.get_by_role("button", name="发布文章").click()
            page_csdn_md_editor.get_by_role("button", name="添加文章标签").click()
            
            # 添加多个话题标签，CSDN最多支持添加10个话题标签
            for tag in csdn_tags:
                page_csdn_md_editor.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").click()
                page_csdn_md_editor.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").fill(tag)
                page_csdn_md_editor.get_by_role("textbox", name="请输入文字搜索，Enter键入可添加自定义标签").press("Enter")
            
            # 关闭标签设置
            page_csdn_md_editor.get_by_role("button", name="关闭").nth(2).click()
            
            # 设置文章封面图片 - 使用组合定位器确保定位到封面上传区域的文件输入框
            page_csdn_md_editor.locator(".cover-upload-box .el-upload__input").set_input_files(cover_image)
            page_csdn_md_editor.get_by_text("确认上传").click()
            
            # 设置文章摘要
            page_csdn_md_editor.get_by_role("textbox", name="本内容会在各展现列表中展示，帮助读者快速了解内容。若不填，则默认提取正文前256个字。").click()
            page_csdn_md_editor.get_by_role("textbox", name="本内容会在各展现列表中展示，帮助读者快速了解内容。若不填，则默认提取正文前256个字。").fill(summary)
            
            # 设置文章分类
            page_csdn_md_editor.get_by_role("button", name="新建分类专栏").click()
            page_csdn_md_editor.locator("span").filter(has_text=re.compile(r"^AI$")).click()
            # page_csdn_md_editor.locator("div:nth-child(2) > .tag__option-label > .tag__option-icon").click()
            page_csdn_md_editor.get_by_role("button", name="关闭").nth(2).click()
            
            # 设置备份到GitCode
            page_csdn_md_editor.locator("label").filter(has_text="同时备份到GitCode").locator("span").nth(1).click()
            
            # 保存草稿
            # page_csdn_md_editor.get_by_label("Insert publishArticle").get_by_role("button", name="保存为草稿").click()
            # 发布文章
            page_csdn_md_editor.get_by_label("Insert publishArticle").get_by_role("button", name="发布文章").click()
            page_csdn_md_editor.get_by_text("发布成功！正在审核中").click()

        ## 51CTO博客，发布文章。
        ## 51CTO发布文章时，支持自动从正文中找一张合适的图片作为封面图
        if '51cto' in target_platforms:
            print("正在发布到51CTO...")
            # 获取51CTO平台的话题标签
            cto_tags = get_platform_tags(all_tags, '51cto')
            print(f"🏷️  51CTO话题标签: {cto_tags}")
            
            page_51cto = browser_context.new_page()
            page_51cto.goto("https://blog.51cto.com/")
            
            # 检查是否存在新功能提示元素，如果存在则关闭
            if page_51cto.get_by_text("Hi，有新功能更新啦！").count() > 0:
                page_51cto.get_by_text("Hi，有新功能更新啦！").click()
                page_51cto.locator(".tip-close").click()

            # 点击写文章按钮 - 使用CSS类名精确匹配
            page_51cto.locator(".want-write").click()
            
            # 导入Markdown文件 - 先点击导入按钮
            # 导入Markdown文件 - 使用正确的文件选择器处理方式
            with page_51cto.expect_file_chooser() as fc_info:
                page_51cto.locator("button .iconeditor.editorimport").click()
            
            file_chooser = fc_info.value
            file_chooser.set_files(markdown_file)
            
            page_51cto.wait_for_timeout(10000)
            
            # 设置文章标题
            page_51cto.get_by_role("textbox", name="请输入标题").click()
            page_51cto.get_by_role("textbox", name="请输入标题").fill(title)
            page_51cto.get_by_role("textbox", name="请输入标题").click()
            
            # 点击发布文章按钮（会打开设置面板）
            # 注意：这部分设置不会自动保存，如果没有点击发布按钮，则不会保存设置
            page_51cto.get_by_role("button", name=" 发布文章").click()
            # 检查是否弹出确认窗口，如果有"继续发布"按钮则点击
            try:
                # 等待可能出现的确认窗口
                page_51cto.wait_for_timeout(2000)
                
                # 检查是否存在"继续发布"按钮
                continue_publish_button = page_51cto.get_by_role("button", name="继续发布")
                if continue_publish_button.count() > 0:
                    continue_publish_button.click()
                    print("✅ 点击了继续发布按钮")
                
            except Exception as e:
                # 如果没有找到按钮或出现其他错误，继续执行
                print(f"ℹ️  未发现继续发布按钮或处理时出错: {e}")
                pass
            # 设置文章分类
            page_51cto.get_by_text("文章分类").click()
            page_51cto.get_by_text("人工智能").click()
            page_51cto.get_by_text("NLP").click()
            
            # 设置个人分类
            page_51cto.get_by_role("textbox", name="请填写个人分类").click()
            page_51cto.get_by_role("listitem").filter(has_text=re.compile(r"^AI$")).click()
            
            # 清空现有话题标签（如果有的话）
            try:
                # 清空标签列表容器
                page_51cto.evaluate("document.querySelector('.has-list.tage-list-arr').innerHTML = ''")
                
                print("✅ 已清空现有标签")
            except Exception as e:
                print(f"ℹ️ 清空标签时出错（可能没有现有标签）: {e}")
            
            # 设置文章标签
            page_51cto.get_by_text("标签", exact=True).click()
            page_51cto.get_by_role("textbox", name="请设置标签，最多可设置5个，支持，；enter间隔").click()
            
            # 添加多个标签，51cto默认会自动填写三个话题标签，所以还可以手工填写两个(之前的代码已经清空了现有标签)。最多只能填写5个标签。
            for tag in cto_tags:
                page_51cto.get_by_role("textbox", name="请设置标签，最多可设置5个，支持，；enter间隔").fill(tag)
                page_51cto.get_by_role("textbox", name="请设置标签，最多可设置5个，支持，；enter间隔").press("Enter")
            
            # 设置文章摘要
            page_51cto.get_by_role("textbox", name="请填写文章摘要，最多可填写500").click()
            page_51cto.get_by_role("textbox", name="请填写文章摘要，最多可填写500").fill(summary)
            
            # 设置话题
            page_51cto.get_by_role("textbox", name="请填写话题").click()
            page_51cto.get_by_text("#yyds干货盘点#").click()
            
            # 添加封面设置代码。注意：51CTO支持自动从正文中提取图片作为封面图（默认设置），如果要自己设置封面图，这里可以手动上传封面图
            # 先选择手动上传封面模式（而不是自动设置）
            # page_51cto.locator("input[name='imgtype'][value='1']").check()  # 选择手动上传模式

            # 或者使用更精确的选择器，注意，图片不能超过1.9MB，否则会报错
            # page_51cto.locator("input[type='file'].upload_input").set_input_files(cover_image)

            # 注意：这里只是保存设置，实际发布需要手动点击发布按钮
            page_51cto.get_by_role("button", name="发布", exact=True).click()
            # 验证是否发布成功
            page_51cto.get_by_text("发布成功 - 待审核").click()

        ## 博客园，发布文章。
        ## 支持Markdown导入，自动提取图片，设置分类等
        if 'cnblogs' in target_platforms:
            print("正在发布到博客园...")
            page_cnblogs = browser_context.new_page()
            page_cnblogs.goto("https://www.cnblogs.com/")
            page_cnblogs.get_by_role("link", name="写随笔").click()
            
            # 切换到文章模式
            page_cnblogs.get_by_role("link", name="文章").click()
            
            # 导入文章 - 使用最稳定的定位器
            page_cnblogs.get_by_role("link", name="导入文章").click()
            
            # 上传Markdown文件 - 使用文件选择器处理方式
            with page_cnblogs.expect_file_chooser() as fc_info:
                # 点击"选择文件"链接或拖拽区域来触发文件选择器
                page_cnblogs.get_by_role("link", name="选择文件").click()
            
            file_chooser = fc_info.value
            file_chooser.set_files(markdown_file)
            
            # 确认导入
            page_cnblogs.get_by_text("导入 1 个文件").click()
            page_cnblogs.get_by_role("button", name="开始导入").click()
            page_cnblogs.get_by_role("button", name="完成").click()
            
            # 编辑导入的文章
            # 使用更灵活的匹配方式，因为title后面的时间标记是动态变化的
            page_cnblogs.get_by_role("row").filter(has_text=title).get_by_role("link").nth(1).click()
            
            # 设置文章分类
            # page_cnblogs.locator("nz-tree-select div").click()
            page_cnblogs.get_by_role("checkbox", name="AI").check()
            
            # 设置发布状态
            page_cnblogs.get_by_role("checkbox", name="发布", exact=True).check()
            
            # 提取文章中的图片
            page_cnblogs.get_by_role("button", name="提取图片").click()
            page_cnblogs.get_by_text("成功:").click()
            
            # 设置题图 - 使用文件选择器
            page_cnblogs.get_by_text("插入题图").click()
            
            with page_cnblogs.expect_file_chooser() as fc_info2:
                page_cnblogs.get_by_role("button", name="选择要上传的图片").click()
            
            file_chooser2 = fc_info2.value
            file_chooser2.set_files(cover_image)
            
            page_cnblogs.get_by_role("button", name="确定").click()
            
            # 设置文章摘要
            page_cnblogs.locator("#summary").click()
            page_cnblogs.locator("#summary").fill(summary)
            
            # 保存草稿
            # page_cnblogs.get_by_role("button", name="保存草稿").click()
            # 注意：实际发布需要手动点击发布按钮
            page_cnblogs.get_by_role("button", name="发布草稿").click()
            page_cnblogs.locator("#cdk-overlay-4").get_by_text("发布成功").click()

        ## 小红书，发布图文（xiaohongshu_newspic）。
        ## 支持图片上传，设置标题、描述、地点等
        if 'xiaohongshu_newspic' in target_platforms:
            print("正在发布到小红书图文消息...")
            # 获取小红书平台的话题标签
            xiaohongshu_tags = get_platform_tags(all_tags, 'xiaohongshu')
            print(f"🏷️  小红书话题标签: {xiaohongshu_tags}")
            
            page_xiaohongshu = browser_context.new_page()
            page_xiaohongshu.goto("https://creator.xiaohongshu.com/publish/publish?source=official")
            
            # 选择图文发布模式
            page_xiaohongshu.get_by_text("上传图文").nth(1).click()
            
            # 上传封面图片
            with page_xiaohongshu.expect_file_chooser() as fc_info_xiaohongshu:
                page_xiaohongshu.get_by_role("button", name="Choose File").click()
            
            file_chooser_xiaohongshu = fc_info_xiaohongshu.value
            file_chooser_xiaohongshu.set_files(cover_image)
            
            # 设置标题
            page_xiaohongshu.get_by_role("textbox", name="填写标题会有更多赞哦～").click()
            page_xiaohongshu.get_by_role("textbox", name="填写标题会有更多赞哦～").fill(title)
            
            # 设置描述内容
            page_xiaohongshu.get_by_role("textbox").nth(1).click()
            # 先填入摘要和链接
            # 设置描述内容，使用type方法逐步输入以确保换行生效
            page_xiaohongshu.get_by_role("textbox").nth(1).click()
            page_xiaohongshu.get_by_role("textbox").nth(1).type(summary)
            page_xiaohongshu.get_by_role("textbox").nth(1).press("Enter")
            page_xiaohongshu.get_by_role("textbox").nth(1).type("详情请查阅此文章：")
            page_xiaohongshu.get_by_role("textbox").nth(1).type(url)
            page_xiaohongshu.get_by_role("textbox").nth(1).press("Enter")
            
            # 模拟人工操作添加话题标签，小红书笔记最多支持添加10个话题标签
            for tag in xiaohongshu_tags:
                page_xiaohongshu.get_by_role("textbox").nth(1).type("#")
                page_xiaohongshu.get_by_role("textbox").nth(1).type(tag)
                page_xiaohongshu.locator("#creator-editor-topic-container").get_by_text(f"#{tag}", exact=True).click()
                # page_xiaohongshu.get_by_role("textbox").nth(1).press("Enter")
            
            # 设置地点
            page_xiaohongshu.get_by_text("添加地点").nth(1).click()
            page_xiaohongshu.locator("form").filter(has_text="添加地点 添加地点").get_by_role("textbox").fill("深圳")
            page_xiaohongshu.get_by_text("深圳市", exact=True).click()
            
            # 暂存离开（保存草稿）
            # page_xiaohongshu.get_by_role("button", name="暂存离开").click()
            # 注意：实际发布需要手动点击发布按钮
            page_xiaohongshu.get_by_role("button", name="发布").click()
            # 验证是否发布成功
            page_xiaohongshu.get_by_text('发布成功').click()

        ## 抖音，发布图文（douyin_newspic）。
        ## 支持图片上传，设置标题、描述、合集等
        if 'douyin_newspic' in target_platforms:
            print("正在发布到抖音图文消息...")  
            # 获取抖音平台的话题标签
            douyin_tags = get_platform_tags(all_tags, 'douyin')
            print(f"🏷️  抖音话题标签: {douyin_tags}")
            
            page_douyin = browser_context.new_page()
            page_douyin.goto("https://creator.douyin.com/creator-micro/home?enter_from=dou_web")
            page_douyin.get_by_text("发布图文").click()
            
            # 上传图文
            # page_douyin.get_by_role("button", name="上传图文").click()
            with page_douyin.expect_file_chooser() as fc_info3:
                page_douyin.get_by_role("button", name="上传图文").click()
            
            file_chooser3 = fc_info3.value
            file_chooser3.set_files(cover_image)
            
            # 设置作品标题
            page_douyin.get_by_role("textbox", name="添加作品标题").click()
            page_douyin.get_by_role("textbox", name="添加作品标题").fill(title)
            
            # 设置描述内容
            page_douyin.locator(".ace-line > div").click()
            page_douyin.locator(".zone-container").fill(f"{summary}")
            page_douyin.locator(".zone-container").press("Enter")
            page_douyin.locator(".zone-container").type("详情请查阅此文章：")
            page_douyin.locator(".zone-container").type(url)
            page_douyin.locator(".zone-container").press("Enter")
            # 模拟人工操作添加话题标签
            # 注意：抖音最多支持添加5个话题标签，不支持横杠
            for tag in douyin_tags:
                # 过滤掉包含横杠的标签
                if '-' not in tag:
                    page_douyin.locator(".zone-container").type("#")
                    page_douyin.locator(".zone-container").type(tag)
                    page_douyin.locator(".zone-container").press("Enter")
            
            # 设置合集
            page_douyin.locator("div").filter(has_text=re.compile(r"^添加合集合集不选择合集$")).locator("svg").nth(1).click()
            page_douyin.get_by_text("AI", exact=True).click()
            # 验证是否添加了图片
            page_douyin.get_by_text('已添加1张图片继续添加').click()

            # 发布
            page_douyin.get_by_role("button", name="发布", exact=True).click()

            # 验证是否发布成功
            page_douyin.get_by_text("发布成功").click()
            
        ## 快手，发布图文（kuaishou_newspic）。
        ## 支持图片上传，设置描述、链接等
        if 'kuaishou_newspic' in target_platforms:
            print("正在发布到快手图文消息...")  
            # 获取快手平台的话题标签
            kuaishou_tags = get_platform_tags(all_tags, 'kuaishou')
            print(f"🏷️  快手话题标签: {kuaishou_tags}")
            
            page_kuaishou = browser_context.new_page()
            page_kuaishou.goto("https://cp.kuaishou.com/profile")
            
            # 打开发布图文窗口
            with page_kuaishou.expect_popup() as page_new_newspic:
                page_kuaishou.get_by_text("发布图文", exact=True).click()
            page_kuaishou_newspic = page_new_newspic.value
            
            # 上传图片
            # page_kuaishou_newspic.get_by_role("button", name="上传图片").click()
            with page_kuaishou_newspic.expect_file_chooser() as fc_info4:
                page_kuaishou_newspic.get_by_role("button", name="上传图片").click()
            
            file_chooser4 = fc_info4.value
            file_chooser4.set_files(cover_image)

            # 验证是否上传了图片
            page_kuaishou_newspic.get_by_text(re.compile(r'\d+张图片上传成功')).click()
            
            # 快手图文没有标题
            # 设置描述内容
            page_kuaishou_newspic.locator("#work-description-edit").click()
            page_kuaishou_newspic.locator("#work-description-edit").fill(f"{summary}")
            page_kuaishou_newspic.locator("#work-description-edit").press("Enter")
            page_kuaishou_newspic.locator("#work-description-edit").type("详情请查阅此文章：")
            page_kuaishou_newspic.locator("#work-description-edit").type(url)
            page_kuaishou_newspic.locator("#work-description-edit").press("Enter")

            page_kuaishou_newspic.wait_for_load_state("networkidle")
            # 添加话题标签，注意：快手最多支持添加4个话题标签
            # 快手添加话题标签很简单，直接输入标签名即可，不是一定要从下拉列表中选择
            for tag in kuaishou_tags:
                page_kuaishou_newspic.locator("#work-description-edit").type(f"#{tag} ")
            
            # 等待网络空闲状态
            page_kuaishou_newspic.wait_for_load_state("networkidle")
            # 发布
            page_kuaishou_newspic.get_by_text("发布", exact=True).click()

        ## 哔哩哔哩，发布图文（bilibili_newspic）。
        ## 支持专栏投稿，设置标题、内容、分类等
        if 'bilibili_newspic' in target_platforms:
            print("正在发布到哔哩哔哩图文消息...")  
            page_bilibili = browser_context.new_page()
            page_bilibili.goto("https://member.bilibili.com/platform/home")
            # 点击投稿按钮
            # 使用ID定位器精确选择投稿按钮，避免与其他"投稿"文本冲突
            page_bilibili.locator("#nav_upload_btn").click()
            
            # 选择专栏投稿
            page_bilibili.locator("#video-up-app").get_by_text("专栏投稿").click()
            
            # 设置标题 - 修正iframe的name属性
            page_bilibili.wait_for_selector("iframe[src*='/article-text/home']")
            iframe = page_bilibili.locator("iframe[src*='/article-text/home']").content_frame
            iframe.get_by_role("textbox", name="请输入标题（建议30字以内）").fill(title)
            
            # 设置正文内容
            iframe.get_by_role("paragraph").click()
            # 既然光标已经在闪烁，直接使用页面的键盘输入
            page_bilibili.keyboard.type(summary + "\n详情请查阅此文章：" + url + "\n")
                                  
            # 设置分类
            iframe.get_by_text("更多设置").click()
            iframe.get_by_role("button", name="科技").click()
            iframe.get_by_text("学习").click()
            
            # 设置原创声明
            iframe.get_by_role("checkbox", name="我声明此文章为原创").click()
            iframe.get_by_role("button", name="确认为我原创").click()
            
            # 设置转载权限
            iframe.get_by_title("他人可对专栏内容进行转载，但转载时需注明文章作者、出处、来源").locator("span").nth(1).click()

            # 设置封面图 - 参考快手的文件上传方式
            try:
                with page_bilibili.expect_file_chooser() as fc_info_bilibili:
                    iframe.get_by_text("点击上传封面图（选填）").click()
                
                file_chooser_bilibili = fc_info_bilibili.value
                file_chooser_bilibili.set_files(cover_image)
                
                # 如果有确认按钮则点击
                try:
                    iframe.get_by_role("button", name="确认").click()
                    print("✅ 哔哩哔哩封面图上传成功")
                except:
                    print("ℹ️  未找到确认按钮，封面图可能已自动确认")
                    
            except Exception as e:
                print(f"⚠️  上传封面图时出错: {e}")
                print("跳过封面图设置，继续执行...")
                
            page_bilibili.wait_for_timeout(5000)
            # page_bilibili.wait_for_load_state("networkidle")
            # 提交文章
            iframe.get_by_role("button", name="提交文章").click()
            iframe.get_by_text("点击查看").click()



        # 在测试末尾添加截图
        if 'mdnice' in target_platforms:
            page_mdnice.screenshot(path="test-results/screenshot_mdnice.png", full_page=True)
        if 'wechat' in target_platforms:
            page_wechat.screenshot(path="test-results/screenshot_wechat.png", full_page=True)
        if 'zhihu' in target_platforms:
            page_zhihu_editor.screenshot(path="test-results/screenshot_zhihu.png", full_page=True)
        if 'csdn' in target_platforms:
            page_csdn.screenshot(path="test-results/screenshot_csdn.png", full_page=True)
        if '51cto' in target_platforms:
            page_51cto.screenshot(path="test-results/screenshot_51cto.png", full_page=True)
        if 'cnblogs' in target_platforms:
            page_cnblogs.screenshot(path="test-results/screenshot_cnblogs.png", full_page=True)
        if 'xiaohongshu_newspic' in target_platforms:
            page_xiaohongshu.screenshot(path="test-results/screenshot_xiaohongshu.png", full_page=True)
        if 'douyin_newspic' in target_platforms:
            page_douyin.screenshot(path="test-results/screenshot_douyin.png", full_page=True)
        if 'kuaishou_newspic' in target_platforms:
            page_kuaishou.screenshot(path="test-results/screenshot_kuaishou.png", full_page=True)
        if 'bilibili_newspic' in target_platforms:
            page_bilibili.screenshot(path="test-results/screenshot_bilibili.png", full_page=True)


        # 等待用户确认是否继续
        print("\n" + "=" * 80)
        print("发布完成！")
        print("=" * 80)
        print("请检查各平台的发布结果，确认无误后按 Y 继续，或按其他键退出...")
        user_input = input("是否继续？(Y/n): ").strip().upper()
        
        if user_input != 'Y':
            print("用户选择退出，测试结束。")
            return
        
        print("用户确认继续，正在保存测试结果...")
        # Stop tracing and export it into a zip archive.
        browser_context.tracing.stop(path = "test-results/trace.zip")
    finally:
        # 确保浏览器上下文被关闭
        if browser_context:
            browser_context.close()


if __name__ == "__main__":
    # 如果直接运行脚本，显示帮助信息
    print("=" * 80)
    print("社交媒体自动发布测试脚本")
    print("=" * 80)
    print()
    print("功能说明：")
    print("本脚本可以自动将Markdown格式的文章发布到多个社交媒体平台，")
    print("支持微信公众号、知乎、CSDN、51CTO、博客园、小红书、抖音、快手、哔哩哔哩等平台。")
    print()
    print("使用方法：")
    print("使用 pytest 运行此脚本，例如：")
    print()
    print("1. 基本运行（使用默认参数）：")
    print("   pytest -s --headed --video on --screenshot on --tracing on ./test_social_media_automatic_publish.py")
    print()
    print("2. 自定义参数运行：")
    print("   pytest -s --headed ./test_social_media_automatic_publish.py \\")
    print("     --title '自定义标题' \\")
    print("     --author '自定义作者' \\")
    print("     --summary '自定义摘要' \\")
    print("     --url '原文链接' \\")
    print("     --markdown-file '/path/to/article.md' \\")
    print("     --cover-image 'cover.jpg' \\")
    print("     --platforms 'wechat,zhihu'")
    print()
    print("参数说明：")
    print("--title              文章标题（必填，最多100字）")
    print("--author             作者名称（必填）")
    print("--summary            文章摘要（必填，用于转发卡片展示，最多120字符）")
    print("--url                原文链接（必填，用于引用来源）")
    print("--markdown-file      Markdown文件路径（必填，支持.md格式）")
    print("--user-data-dir      浏览器用户数据目录（必填，用于保存登录状态）")
    print("--platforms          指定要发布到的平台（可选，默认发布到所有平台）")
    print("--cover-image        文章封面图片路径（必填，建议JPG/PNG格式）")
    print("--tags               话题标签（可选，用逗号分隔，如：AI,人工智能,大模型）")
    print("--backup-browser-data 是否备份浏览器数据（可选，true/false，默认true）")
    print()
    print("平台选择参数 --platforms 的使用方法：")
    print("--platforms all                    # 发布到所有平台（默认）")
    print("--platforms wechat,zhihu          # 只发布到微信公众号和知乎")
    print("--platforms csdn,51cto            # 只发布到CSDN和51CTO")
    print("--platforms mdnice                # 只处理mdnice转换")
    print("--platforms xiaohongshu_newspic   # 只发布到小红书图文")
    print()
    print("支持的平台列表：")
    print("- mdnice: Markdown转微信公众号格式")
    print("- wechat: 微信公众号")
    print("- zhihu: 知乎")
    print("- csdn: CSDN博客")
    print("- 51cto: 51CTO博客")
    print("- cnblogs: 博客园")
    print("- xiaohongshu_newspic: 小红书图文")
    print("- douyin_newspic: 抖音图文")
    print("- kuaishou_newspic: 快手图文")
    print("- bilibili_newspic: 哔哩哔哩专栏")
    print()
    print("封面图片参数 --cover-image 的使用方法：")
    print("--cover-image cover.jpg           # 使用默认封面图片（默认）")
    print("--cover-image my_cover.png        # 使用自定义封面图片")
    print("--cover-image /path/to/image.jpg  # 使用绝对路径的封面图片")
    print()
    print("浏览器数据备份参数 --backup-browser-data 的使用方法：")
    print("--backup-browser-data true        # 执行备份（默认，推荐）")
    print("--backup-browser-data false       # 跳过备份（快速测试时使用）")
    print("--backup-browser-data 1           # 执行备份（true的别名）")
    print("--backup-browser-data 0           # 跳过备份（false的别名）")
    print()
    print("环境要求：")
    print("- Python 3.7+")
    print("- Playwright 已安装并配置")
    print("- 浏览器（Chrome/Chromium）已安装")
    print("- 各平台账号已登录（首次运行需要手动登录）")
    print()
    print("注意事项：")
    print("1. 首次运行前需要手动登录各平台账号")
    print("2. 确保Markdown文件格式正确，图片链接有效")
    print("3. 封面图片建议使用JPG/PNG格式，大小适中")
    print("4. 脚本会自动保存为草稿，需要手动发布")
    print("5. 建议在测试环境中先验证功能")
    print("6. 视频录制和截图功能会生成大量文件，注意磁盘空间")
    print("7. summary参数会自动验证长度，超过120字符时会尝试优化")
    print("8. 浏览器数据备份默认开启，可通过 --backup-browser-data=false 跳过")
    print("9. 跳过备份可能导致浏览器数据丢失，仅在快速测试时使用")
    print()
    print("示例运行命令：")
    print("# 发布到所有平台")
    print("pytest -s --headed ./test_social_media_automatic_publish.py \\")
    print("  --title 'AutoGPT：可持续运行的智能代理平台' \\")
    print("  --author 'tornadoami' \\")
    print("  --summary '本文介绍AutoGPT的核心功能和使用方法' \\")
    print("  --url 'https://example.com/article' \\")
    print("  --markdown-file './article.md' \\")
    print("  --cover-image './cover.jpg'")
    print()
    print("# 只发布到特定平台")
    print("pytest -s --headed ./test_social_media_automatic_publish.py \\")
    print("  --title '测试标题' \\")
    print("  --author '测试作者' \\")
    print("  --summary '测试摘要' \\")
    print("  --url 'https://test.com' \\")
    print("  --markdown-file './test.md' \\")
    print("  --cover-image './test_cover.jpg' \\")
    print("  --platforms 'zhihu,csdn'")
    print()
    print("# 快速测试（跳过备份）")
    print("pytest -s --headed ./test_social_media_automatic_publish.py \\")
    print("  --title '快速测试' \\")
    print("  --author '测试用户' \\")
    print("  --summary '快速测试摘要' \\")
    print("  --url 'https://example.com' \\")
    print("  --markdown-file './test.md' \\")
    print("  --cover-image './cover.jpg' \\")
    print("  --platforms 'zhihu' \\")
    print("  --backup-browser-data false")
    print()
    print("作者：tornadoami")
    print("版本：1.0.0")
    print("更新日期：2025年")
    print("=" * 80)