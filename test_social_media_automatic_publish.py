import pytest
import re
import random
import sys
import os
from pathlib import Path
from playwright.sync_api import Page, expect
# import pyperclip

# 导入字数统计功能
from word_counter_sdk import validate_and_clean_text

# 导入钉钉SDK
from dingtalk_sdk import create_sdk

# 定义各平台的话题标签数量限制
PLATFORM_TAG_LIMITS = {
    'zhihu': 3,           # 知乎最多3个话题标签
    'csdn': 10,           # CSDN最多10个话题标签
    'xiaohongshu': 10,    # 小红书最多10个话题标签
    'douyin': 5,          # 抖音最多5个话题标签
    'kuaishou': 4,        # 快手最多4个话题标签
    '51cto': 5,           # 51CTO最多5个话题标签
}

# 获取微信公众号APP_ID和APP_SECRET
app_id = os.getenv("WECHAT_APP_ID")
app_secret = os.getenv("WECHAT_APP_SECRET")

# 获取钉钉APP_KEY和APP_SECRET
dingtalk_app_key = os.getenv("DINGTALK_APP_KEY")
dingtalk_app_secret = os.getenv("DINGTALK_APP_SECRET")
dingtalk_user_id = os.getenv("DINGTALK_USER_ID")

if not app_id or not app_secret:
    print("❌ 请设置环境变量 WECHAT_APP_ID 和 WECHAT_APP_SECRET")
    print("例如：")
    print("Linux/macOS:")
    print("export WECHAT_APP_ID=your_app_id")
    print("export WECHAT_APP_SECRET=your_app_secret")
    print("")
    print("Windows (命令提示符):")
    print("set WECHAT_APP_ID=your_app_id")
    print("set WECHAT_APP_SECRET=your_app_secret")
    print("")
    print("Windows (PowerShell):")
    print("$env:WECHAT_APP_ID='your_app_id'")
    print("$env:WECHAT_APP_SECRET='your_app_secret'")
    exit(1)

if not dingtalk_app_key or not dingtalk_app_secret or not dingtalk_user_id:
    print("❌ 请设置环境变量 DINGTALK_APP_KEY, DINGTALK_APP_SECRET 和 DINGTALK_USER_ID")
    print("例如：")
    print("Linux/macOS:")
    print("export DINGTALK_APP_KEY=your_app_key")
    print("export DINGTALK_APP_SECRET=your_app_secret")
    print("export DINGTALK_USER_ID=your_user_id")
    print("")
    print("Windows (命令提示符):")
    print("set DINGTALK_APP_KEY=your_app_key")
    print("set DINGTALK_APP_SECRET=your_app_secret")
    print("set DINGTALK_USER_ID=your_user_id")
    print("")
    print("Windows (PowerShell):")
    print("$env:DINGTALK_APP_KEY='your_app_key'")
    print("$env:DINGTALK_APP_SECRET='your_app_secret'")
    print("$env:DINGTALK_USER_ID='your_user_id'")
    exit(1)

def compress_image(image_path, max_size_mb=5, quality=85):
    """
    压缩图片文件，确保文件大小不超过指定限制，输出格式为PNG
    
    Args:
        image_path: 原始图片文件路径
        max_size_mb: 最大文件大小（MB），默认5MB
        quality: 压缩质量（1-100），默认85（对PNG主要影响压缩级别）
        
    Returns:
        str: 压缩后的PNG图片文件路径，如果失败返回None
    """
    try:
        from PIL import Image
        import os
        
        print(f"🖼️ 开始压缩图片: {image_path}")
        
        # 检查原始文件是否存在
        if not os.path.exists(image_path):
            print(f"❌ 图片文件不存在: {image_path}")
            return None
            
        # 获取原始文件大小
        original_size = os.path.getsize(image_path)
        original_size_mb = original_size / (1024 * 1024)
        print(f"📊 原始文件大小: {original_size_mb:.2f}MB")
        
        # 打开图片
        with Image.open(image_path) as img:
            # 获取原始尺寸
            original_width, original_height = img.size
            print(f"📐 原始尺寸: {original_width}x{original_height}")
            
            # 转换为RGBA模式以支持PNG透明度
            if img.mode != 'RGBA':
                print("🔄 转换图片模式为RGBA")
                img = img.convert('RGBA')
            
            # 生成压缩后的PNG文件名
            file_dir = os.path.dirname(image_path)
            file_name = os.path.basename(image_path)
            name, _ = os.path.splitext(file_name)
            compressed_path = os.path.join(file_dir, f"{name}_compressed.png")
            
            # 如果原文件已经是PNG且大小符合要求，检查是否需要压缩
            if image_path.lower().endswith('.png') and original_size_mb <= max_size_mb:
                print(f"✅ 原PNG文件大小已符合要求({original_size_mb:.2f}MB <= {max_size_mb}MB)")
                return image_path
            
            # 尝试不同的压缩策略
            scale_factor = 1.0
            max_attempts = 15
            attempt = 0
            
            while attempt < max_attempts:
                attempt += 1
                print(f"🔄 压缩尝试 {attempt}/{max_attempts} - 缩放: {scale_factor:.2f}")
                
                # 计算新尺寸
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                
                # 调整图片尺寸
                if scale_factor < 1.0:
                    resized_img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                else:
                    resized_img = img
                
                # 保存为PNG格式，使用optimize参数进行优化
                # PNG的compress_level参数范围是0-9，9为最高压缩
                compress_level = min(9, int((100 - quality) / 10))
                resized_img.save(compressed_path, 'PNG', optimize=True, compress_level=compress_level)
                
                # 检查压缩后的文件大小
                compressed_size = os.path.getsize(compressed_path)
                compressed_size_mb = compressed_size / (1024 * 1024)
                print(f"📊 压缩后文件大小: {compressed_size_mb:.2f}MB")
                
                # 如果文件大小符合要求，返回压缩后的文件路径
                if compressed_size_mb <= max_size_mb:
                    print(f"✅ 图片压缩成功!")
                    print(f"📁 压缩后PNG文件路径: {compressed_path}")
                    print(f"📊 压缩比: {(1 - compressed_size/original_size)*100:.1f}%")
                    print(f"📐 最终尺寸: {new_width}x{new_height}")
                    return compressed_path
                
                # 调整缩放因子，逐步减小图片尺寸
                if scale_factor > 0.3:
                    scale_factor -= 0.05
                else:
                    break
            
            print(f"⚠️ 经过{max_attempts}次尝试仍无法将PNG文件压缩到{max_size_mb}MB以下")
            print(f"📊 最终文件大小: {compressed_size_mb:.2f}MB")
            
            # 即使超过限制，也返回压缩后的PNG文件（已经是最小的了）
            return compressed_path
            
    except ImportError:
        print("❌ 缺少PIL库，请安装: pip install Pillow")
        return None
    except Exception as e:
        print(f"❌ 图片压缩失败: {e}")
        return None



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

def generate_summary_with_doubao(browser_context, markdown_file):
    """
    使用豆包AI生成文章summary
    
    Args:
        browser_context: Playwright浏览器上下文
        markdown_file: Markdown文件路径
        
    Returns:
        str: 生成的summary文本，如果失败返回None
    """
    try:
        print("🤖 正在使用豆包AI总结文章...")
        page_doubao = browser_context.new_page()
        
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
        
        # 选择上传文件或图片选项并上传文件
        print("3️⃣ 选择上传文件选项...")
        with page_doubao.expect_file_chooser() as page_upload_file:
            page_doubao.get_by_text("上传文件或图片").click()
        page_upload_file = page_upload_file.value
        print("4️⃣ 上传Markdown文件...")
        page_upload_file.set_files(markdown_file)
        page_doubao.wait_for_timeout(1000)
        print("✅ 上传选项选择成功")
        
        # 点击聊天输入框
        print("5️⃣ 点击聊天输入框...")
        page_doubao.get_by_test_id("chat_input_input").click()
        page_doubao.wait_for_timeout(500)
        print("✅ 聊天输入框获得焦点")
        
        # 输入总结请求的提示词
        print("6️⃣ 输入总结提示词...")
        prompt_text = "请帮我总结我提供的Markdown文档，总字数严格限制在120字以内，你的回答只需包含总结内容，不要包含任何其他文字。请注意：一个英文字母、一个空格、一个标点符号都算一个字"
        page_doubao.get_by_test_id("chat_input_input").fill(prompt_text)
        page_doubao.wait_for_timeout(1000)
        print("✅ 提示词输入完成")
        
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
        
        # 使用Playwright的wait_for等待复制按钮出现（最多等待60秒）
        print("🔄 等待复制按钮出现...")
        try:
            # 等待复制按钮出现，最多等待60秒
            copy_buttons = page_doubao.get_by_test_id("receive_message").get_by_test_id("message_action_copy")
            copy_buttons.wait_for(state="visible", timeout=120000)  # 等待120秒
            copy_button_count = copy_buttons.count()
            print(f"✅ 找到 {copy_button_count} 个复制按钮")
        except Exception as e:
            print(f"⚠️  等待复制按钮超时或出错: {e}")
            print("❌ 未找到复制按钮")
            raise Exception("未找到复制按钮")
        
        # 点击复制按钮获取AI回复内容
        print("9️⃣ 复制AI回复内容...")
        
        if copy_button_count > 0:
            # 选择最后一个复制按钮（索引为 count-1）
            last_copy_button = copy_buttons.nth(copy_button_count - 1)
            last_copy_button.click(timeout=10000)
            page_doubao.wait_for_timeout(2000)  # 增加等待时间确保复制完成
            print("✅ AI最新回复已复制到剪贴板")
        else:
            print("❌ 未找到复制按钮")
            raise Exception("未找到复制按钮")
        
        # 使用 pyperclip 从剪贴板读取内容
        try:
            import pyperclip
            print("🔄 从剪贴板读取内容...，注意：如果电脑锁屏了，则无法正常从剪贴板读取内容")
            summary = pyperclip.paste().strip()
            
            if summary:
                print(f"🤖 豆包AI总结内容: {summary}")
                
                # 保存总结到文件（备份）
                summary_file = os.path.join("test-results", f"doubao_summary_{os.path.splitext(os.path.basename(markdown_file))[0]}.txt")
                os.makedirs("test-results", exist_ok=True)
                with open(summary_file, 'w', encoding='utf-8') as f:
                    f.write(summary)
                print(f"📁 豆包总结已保存到: {summary_file}")
                
                # 关闭豆包页面
                # page_doubao.close()
                return summary
            else:
                print("⚠️  剪贴板内容为空")
                return None
                
        except ImportError:
            print("❌ 需要安装 pyperclip 库")
            print("请运行: pip install pyperclip 或 uv add pyperclip")
            return None
            
        except Exception as e:
            print(f"⚠️  从剪贴板读取内容时出错: {e}")
            return None


    except Exception as e:
        print(f"❌ 豆包AI操作过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return None
    

    
    finally:
        # 确保页面被关闭
        try:
            if 'page_doubao' in locals():
                page_doubao.close()
        except:
            pass

def generate_newspic_title_with_doubao(browser_context, markdown_file):
    """
    使用豆包AI生成图文消息的标题
    
    Args:
        browser_context: Playwright浏览器上下文
        markdown_file: Markdown文件路径
        
    Returns:
        str: 生成的图文消息的标题，如果失败返回None
    """
    try:
        print("🤖 正在使用豆包AI生成图文消息的标题...")
        page_doubao = browser_context.new_page()
        
        # 打开豆包AI聊天页面
        print("1️⃣ 打开豆包AI聊天页面...")
        page_doubao.goto("https://www.doubao.com/chat/")
        page_doubao.wait_for_load_state("networkidle")
        print("✅ 豆包AI页面加载完成")
        
        mode = "超能"
        try:
            print(f"🔄 正在选择豆包AI的'{mode}'模式...")
            
            # 方法1：通过文本内容定位指定模式按钮
            try:
                mode_button = page_doubao.get_by_text(mode, exact=True)
                if mode_button.count() > 0:
                    mode_button.click()
                    page_doubao.wait_for_timeout(1000)
                    print(f"✅ 通过文本定位成功选择'{mode}'模式")
                    
            except Exception as e1:
                print(f"⚠️  方法1失败: {e1}")
            
            # 方法2：通过CSS类名和文本内容定位
            try:
                mode_button = page_doubao.locator(f"span.button-mE6AaR:has-text('{mode}')")
                if mode_button.count() > 0:
                    mode_button.click()
                    page_doubao.wait_for_timeout(1000)
                    print(f"✅ 通过CSS类名和文本内容定位成功选择'{mode}'模式")
                    
            except Exception as e2:
                print(f"⚠️  方法2失败: {e2}")
            
            # 方法3：通过包含指定文本的span元素定位
            try:
                mode_button = page_doubao.locator(f"span:has-text('{mode}')")
                if mode_button.count() > 0:
                    # 过滤出具有button-mE6AaR类的元素
                    for i in range(mode_button.count()):
                        element = mode_button.nth(i)
                        if "button-mE6AaR" in element.get_attribute("class", ""):
                            element.click()
                            page_doubao.wait_for_timeout(1000)
                            print(f"✅ 通过span元素定位成功选择'{mode}'模式")
                            
            except Exception as e3:
                print(f"⚠️  方法3失败: {e3}")
            
            # 方法4：通过tabindex属性定位（查找所有可点击的按钮）
            try:
                all_buttons = page_doubao.locator("span[tabindex='0']")
                if all_buttons.count() > 0:
                    for i in range(all_buttons.count()):
                        button = all_buttons.nth(i)
                        button_text = button.text_content()
                        if button_text == mode:
                            button.click()
                            page_doubao.wait_for_timeout(1000)
                            print(f"✅ 通过tabindex属性定位成功选择'{mode}'模式")
                            
            except Exception as e4:
                print(f"⚠️  方法4失败: {e4}")
            
            # 方法5：兜底方案 - 查找所有包含指定文本的元素
            try:
                all_mode_elements = page_doubao.locator(f"*:has-text('{mode}')")
                if all_mode_elements.count() > 0:
                    # 遍历所有包含指定文本的元素，找到可点击的按钮
                    for i in range(all_mode_elements.count()):
                        element = all_mode_elements.nth(i)
                        element_class = element.get_attribute("class", "")
                        if "button-mE6AaR" in element_class or "button" in element_class:
                            element.click()
                            page_doubao.wait_for_timeout(1000)
                            print(f"✅ 通过兜底方案成功选择'{mode}'模式")
                           
            except Exception as e5:
                print(f"⚠️  方法5失败: {e5}")
            
            print(f"❌ 所有方法都无法找到'{mode}'模式按钮")
            return False
            
        except Exception as e:
            print(f"❌ 选择'{mode}'模式时出错: {e}")

        # 点击文件上传按钮
        print("2️⃣ 点击文件上传按钮...")
        page_doubao.get_by_test_id("upload_file_button").click()
        page_doubao.wait_for_timeout(1000)
        print("✅ 文件上传按钮点击成功")
        
        # 选择上传文件或图片选项并上传文件
        print("3️⃣ 选择上传文件选项...")
        with page_doubao.expect_file_chooser() as page_upload_file:
            page_doubao.get_by_text("上传文件或图片").click()
        page_upload_file = page_upload_file.value
        print("4️⃣ 上传Markdown文件...")
        page_upload_file.set_files(markdown_file)
        page_doubao.wait_for_timeout(1000)
        print("✅ 上传选项选择成功")
        
        # 点击聊天输入框
        print("5️⃣ 点击聊天输入框...")
        page_doubao.get_by_test_id("chat_input_input").click()
        page_doubao.wait_for_timeout(500)
        print("✅ 聊天输入框获得焦点")
        
        # 输入图文消息的标题请求的提示词
        print("6️⃣ 输入图文消息的标题提示词...")
        prompt_text = "请帮我生成我提供的Markdown文档的图文消息的标题，总字数严格限制在20字以内，你的回答只需包含标题内容，不要包含任何其他文字。请注意：一个英文字母、一个空格、一个标点符号都算一个字"
        page_doubao.get_by_test_id("chat_input_input").fill(prompt_text)
        page_doubao.wait_for_timeout(1000)
        print("✅ 提示词输入完成")
        
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
        copy_button = page_doubao.get_by_test_id("receive_message").get_by_test_id("message_action_copy")
        copy_button.click(timeout=60000)  # 设置点击操作的超时时间为1分钟
        page_doubao.wait_for_timeout(1000)
        print("✅ AI回复已复制到剪贴板")
        # 使用 pyperclip 从剪贴板读取内容
        try:
            import pyperclip
            newspic_title = pyperclip.paste().strip()
            
            if newspic_title:
                print(f"🤖 豆包AI生成的图文消息的标题: {newspic_title}")
                
                # 保存图文消息的标题到文件（备份）
                newspic_title_file = os.path.join("test-results", f"doubao_newspic_title_{os.path.splitext(os.path.basename(markdown_file))[0]}.txt")
                os.makedirs("test-results", exist_ok=True)
                with open(newspic_title_file, 'w', encoding='utf-8') as f:
                    f.write(newspic_title)
                print(f"📁 豆包AI生成图文消息的标题已保存到: {newspic_title_file}")
                
                # 关闭豆包页面
                # page_doubao.close()
                return newspic_title
            else:
                print("⚠️  豆包AI生成图文消息的标题剪贴板内容为空")
                return None
                
        except ImportError:
            print("❌ 需要安装 pyperclip 库")
            print("请运行: pip install pyperclip 或 uv add pyperclip")
            return None
            
        except Exception as e:
            print(f"⚠️  豆包AI生成图文消息的标题从剪贴板读取内容时出错: {e}")
            return None


    except Exception as e:
        print(f"❌ 豆包AI生成图文消息的标题操作过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return None
    

    
    finally:
        # 确保页面被关闭
        try:
            if 'page_doubao' in locals():
                page_doubao.close()
        except:
            pass


def generate_tags_with_doubao(browser_context, markdown_file):
    """
    使用豆包AI生成话题标签
    
    Args:
        browser_context: Playwright浏览器上下文
        markdown_file: Markdown文件路径
        
    Returns:
        list: 生成的话题标签列表，如果失败返回空列表
    """
    try:
        print("🏷️  正在使用豆包AI生成话题标签...")
        page_doubao = browser_context.new_page()
        
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
        
        # 选择上传文件或图片选项并上传文件
        print("3️⃣ 选择上传文件选项...")
        with page_doubao.expect_file_chooser() as page_upload_file:
            page_doubao.get_by_text("上传文件或图片").click()
        page_upload_file = page_upload_file.value
        print("4️⃣ 上传Markdown文件...")
        page_upload_file.set_files(markdown_file)
        page_doubao.wait_for_timeout(1000)
        print("✅ 上传选项选择成功")
        
        # 点击聊天输入框
        print("5️⃣ 点击聊天输入框...")
        page_doubao.get_by_test_id("chat_input_input").click()
        page_doubao.wait_for_timeout(500)
        print("✅ 聊天输入框获得焦点")
        
        # 输入话题标签生成请求的提示词
        print("6️⃣ 输入话题标签生成提示词...")
        prompt_text = "我想将这篇文章发布到各个主流的社交媒体平台，包括但不限于：微信公众号、CSDN、知乎、51CTO、博客园、小红书、快手、抖音等等，请根据文章的内容，帮我想出10个话题标签。请严格按照以下格式返回：['标签1', '标签2', '标签3', '标签4', '标签5', '标签6', '标签7', '标签8', '标签9', '标签10']，不要换行，不要添加其他文字，标签决不能包含空格，不能包含横杠，也不能包含任何特殊字符,只返回Python列表格式的字符串。"
        page_doubao.get_by_test_id("chat_input_input").fill(prompt_text)
        page_doubao.wait_for_timeout(1000)
        print("✅ 提示词输入完成")
        
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
        copy_button = page_doubao.get_by_test_id("receive_message").get_by_test_id("message_action_copy")
        copy_button.click()
        page_doubao.wait_for_timeout(1000)
        print("✅ AI回复已复制到剪贴板")
        
        # 使用 pyperclip 从剪贴板读取内容
        try:
            import pyperclip
            tags_text = pyperclip.paste().strip()
            
            if tags_text:
                print(f"🤖 豆包AI生成的话题标签: {tags_text}")
                
                # 解析标签文本为列表 - 支持多种格式
                tags_list = []
                try:
                    # 方法1：尝试解析Python列表格式 ['标签1', '标签2', '标签3']
                    if tags_text.strip().startswith('[') and tags_text.strip().endswith(']'):
                        import ast
                        tags_list = ast.literal_eval(tags_text.strip())
                        print("✅ 使用Python列表格式解析")
                    
                    # 方法2：尝试解析带引号的格式 "标签1", "标签2", "标签3"
                    elif '"' in tags_text or "'" in tags_text:
                        # 提取引号内的内容
                        import re
                        quoted_tags = re.findall(r'["\']([^"\']+)["\']', tags_text)
                        if quoted_tags:
                            tags_list = quoted_tags
                            print("✅ 使用引号格式解析")
                        else:
                            # 如果引号解析失败，按逗号分隔
                            tags_list = [tag.strip().strip('"\'') for tag in tags_text.split(',') if tag.strip()]
                            print("✅ 使用逗号分隔格式解析（引号清理）")
                    
                    # 方法3：按逗号分隔（兜底方案）
                    else:
                        tags_list = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                        print("✅ 使用逗号分隔格式解析")
                    
                    # 清理标签：移除可能的引号、方括号等
                    tags_list = [tag.strip().strip('"\'[]') for tag in tags_list if tag.strip()]
                    
                    # 移除包含横杠的标签
                    tags_list = [tag for tag in tags_list if '-' not in tag]
                    print("✅ 已移除包含横杠的标签")
                    
                    # 限制标签数量（最多10个）
                    if len(tags_list) > 10:
                        tags_list = tags_list[:10]
                        print("⚠️  标签数量超过10个，已截取前10个")
                    
                    print(f"📝 解析后的标签列表: {tags_list}")
                    
                except Exception as e:
                    print(f"⚠️  标签解析出错: {e}")
                    # 兜底方案：按逗号分隔
                    tags_list = [tag.strip() for tag in tags_text.split(',') if tag.strip()]
                    # 移除包含横杠的标签
                    tags_list = [tag for tag in tags_list if '-' not in tag]
                    print("✅ 使用兜底方案（逗号分隔）解析，已移除包含横杠的标签")
                
                # 保存标签到文件（备份）
                tags_file = os.path.join("test-results", f"doubao_tags_{os.path.splitext(os.path.basename(markdown_file))[0]}.txt")
                os.makedirs("test-results", exist_ok=True)
                with open(tags_file, 'w', encoding='utf-8') as f:
                    f.write(tags_text)
                print(f"📁 豆包标签已保存到: {tags_file}")
                
                # 关闭豆包页面
                # page_doubao.close()
                return tags_list
            else:
                print("⚠️  剪贴板内容为空")
                return []
                
        except ImportError:
            print("❌ 需要安装 pyperclip 库")
            print("请运行: pip install pyperclip 或 uv add pyperclip")
            return []
            
        except Exception as e:
            print(f"⚠️  从剪贴板读取内容时出错: {e}")
            return []
            
    except Exception as e:
        print(f"❌ 豆包AI操作过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return []
    finally:
        # 确保页面被关闭
        try:
            if 'page_doubao' in locals():
                page_doubao.close()
        except:
            pass

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
        short_title = request.config.getoption("--short-title")
        
        # 验证必需参数
        if not title:
            print("❌ 缺少必需参数 --title！")
            print("请提供文章标题，例如：")
            print("pytest -s --headed ./test_social_media_automatic_publish.py --title '文章标题'")
            sys.exit(1)
        
        # 显示参数使用情况
        print("=" * 60)
        print("📋 参数使用情况：")
        print("=" * 60)
        print(f"📝 使用指定的标题: {title}")
            
        if summary:
            print(f"📄 使用指定的摘要: {summary}")
        else:
            print("📄 摘要: 将使用豆包AI自动生成")
            
        if url:
            print(f"🔗 使用指定的URL: {url}")
        else:
            print("🔗 URL: 将从钉钉文档自动获取")
            
        if markdown_file:
            print(f"📁 使用指定的Markdown文件: {markdown_file}")
            # 提取markdown文件名（不含后缀），因为cnblogs会自动将markdown的文件名作为文章标题。如果命令行参数中title与markdown不一致会报错。
            markdown_filename = os.path.splitext(os.path.basename(markdown_file))[0]
            print(f"📁 Markdown文件名: {markdown_filename}")
        else:
            print("📁 Markdown文件: 将从钉钉文档自动下载")
            
        # 标记是否需要从钉钉文档下载markdown文件
        need_download_markdown = not markdown_file
        
        # 标记是否需要利用dingtalk_sdk获取钉钉文档的url
        # 只有在提供了markdown文件但没有提供url参数时，才需要获取钉钉文档的url
        need_get_dingtalk_url = not url and markdown_file

        if cover_image:
            print(f"🖼️  使用指定的封面图: {cover_image}")
        else:
            print("🖼️  封面图: 将使用Gemini自动生成")
            
        if short_title:
            print(f"📝 使用指定的短标题: {short_title}")
        else:
            print("📝 短标题: 将自动生成")
        print("=" * 60)
        
        # 标记是否需要使用豆包AI自动生成summary（在markdown文件下载后执行）
        need_ai_summary = not summary or summary.lower() in ['auto', 'doubao', '豆包', 'ai']
        
        # 解析平台参数
        if platforms.lower() == 'all':
            target_platforms = ['mdnice', 'wechat', 'zhihu', 'csdn', '51cto', 'cnblogs', 'xiaohongshu_newspic', 'douyin_newspic', 'kuaishou_newspic', 'bilibili_newspic']
        else:
            target_platforms = [p.strip().lower() for p in platforms.split(',')]
        
        print(f"将发布到以下平台: {', '.join(target_platforms)}")
        print(f"使用封面图片: {cover_image}")

        # 如果未指定url，则利用dingtalk_sdk搜索并获取钉钉文档的url
        if need_get_dingtalk_url:
            print("📁 未指定URL，正在利用dingtalk_sdk搜索钉钉文档...")
            print(f"🔍 搜索关键词: {title}")
            
            try:
                # 创建钉钉SDK实例
                dingtalk_sdk = create_sdk(dingtalk_app_key, dingtalk_app_secret)
                
                # 使用title作为关键词搜索文档并获取详细信息
                documents = dingtalk_sdk.search_and_get_document_details_with_user_id(title, dingtalk_user_id)
                
                if documents:
                    # 获取第一个搜索结果的URL
                    url = documents[0].url
                    print(f"✅ 找到文档: {documents[0].title}")
                    print(f"🔗 获取到的钉钉文档URL: {url}")
                else:
                    print(f"❌ 未找到包含关键词 '{title}' 的钉钉文档")
                    print("请检查标题是否正确，或手动指定URL参数")
                    sys.exit(1)
                    
            except Exception as e:
                print(f"❌ 获取钉钉文档URL失败: {e}")
                print("请检查钉钉API配置或手动指定URL参数")
                sys.exit(1)
        else:
            print(f"🔗 使用指定的URL: {url}")

        # 如果没有指定markdown文件，则从钉钉文档下载
        if need_download_markdown:
            print("📁 未指定Markdown文件，正在从钉钉文档下载...")
            
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

            # 使用提供的title进行搜索
            page_dingtalk_DreamAI_KB.get_by_role("textbox", name="搜索（Ctrl + J）").fill(title)
            
            with page_dingtalk_DreamAI_KB.expect_popup() as page1_info:
                # 使用更精确的定位方式，避免匹配到多个元素
                # 优先查找具有title属性的span元素（这是正确的可点击元素）
                try:
                    # 方法1：查找具有title属性的span元素
                    target_element = page_dingtalk_DreamAI_KB.locator(f'span[title="{title}"]')
                    if target_element.count() > 0:
                        print(f"✅ 找到目标元素（span with title）: {title}")
                        target_element.first.click()
                    else:
                        # 方法2：在表格容器中查找文本
                        target_element = page_dingtalk_DreamAI_KB.get_by_test_id("base-table-container").get_by_text(title)
                        if target_element.count() > 0:
                            print(f"✅ 找到目标元素（table container）: {title}")
                            target_element.first.click()
                        else:
                            # 方法3：查找heading元素
                            heading_element = page_dingtalk_DreamAI_KB.get_by_role("heading").filter(has_text=title)
                            if heading_element.count() > 0:
                                print(f"✅ 找到目标元素（heading）: {title}")
                                try:
                                    heading_element.get_by_role("link").first.click()
                                except Exception:
                                    heading_element.first.click()
                            else:
                                # 方法4：使用更精确的文本匹配，排除包含"在高级搜索中查看"的元素
                                all_elements = page_dingtalk_DreamAI_KB.get_by_text(title)
                                for i in range(all_elements.count()):
                                    element_text = all_elements.nth(i).text_content()
                                    if element_text == title and "在高级搜索中查看" not in element_text:
                                        print(f"✅ 找到目标元素（精确匹配）: {title}")
                                        all_elements.nth(i).click()
                                        break
                                else:
                                    raise Exception("未找到匹配的目标元素")
                except Exception as e:
                    print(f"❌ 定位目标元素失败: {e}")
                    raise
            page_dingtalk_doc = page1_info.value

            # 等待页面基本加载完成
            page_dingtalk_doc.wait_for_load_state("domcontentloaded", timeout=30000)
            print("✅ 钉钉文档页面基本加载完成")
            # 等待额外3秒让页面稳定
            page_dingtalk_doc.wait_for_timeout(3000)

            
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
            
            # 更新markdown_file变量为下载的文件路径
            markdown_file = downloaded_file_path
            
            print(f"📁 下载文件名: {downloaded_filename}")
            print(f"📂 下载文件绝对路径: {downloaded_file_path}")
            
            # 获取当前网页的网址并赋值给url
            if not url:
                try:
                    current_url = page_dingtalk_doc.url
                    url = current_url
                    print(f"🔗 从钉钉文档自动获取URL: {url}")
                except Exception as e:
                    print(f"⚠️  获取URL失败: {e}")
                    print("❌ 获取URL失败，脚本暂停执行")
                    sys.exit(1)
        else:
            print(f"📁 使用指定的Markdown文件: {markdown_file}")
            # 验证文件是否存在
            if not os.path.exists(markdown_file):
                print(f"❌ 指定的Markdown文件不存在: {markdown_file}")
                sys.exit(1)

        # 获取当前网页的网址并赋值给url
        if not url:
            try:
                current_url = page_dingtalk_doc.url
                url = current_url
                print(f"🔗 从钉钉文档自动获取URL: {url}")
            except Exception as e:
                print(f"⚠️  获取URL失败: {e}")
                print("❌ 获取URL失败，脚本暂停执行")
                sys.exit(1)

        # 如果需要使用豆包AI自动生成summary，现在执行
        if need_ai_summary:
            print("=" * 60)
            print("🤖 使用豆包AI自动生成summary...")
            print("=" * 60)
            
            print(f"📄 使用的Markdown文件: {markdown_file}")
            print(f"📁 文件大小: {os.path.getsize(markdown_file)} 字节")
            
            # 使用豆包AI生成summary
            try:
                summary = generate_summary_with_doubao(browser_context, markdown_file)
                if not summary:
                    print("❌ 豆包AI生成summary失败，请手动提供summary参数")
                    print("将退出脚本")
                    sys.exit(1)
                print(f"🤖 豆包AI生成的summary: {summary}")
            except Exception as e:
                print(f"❌ 豆包AI操作失败: {e}")
                print("请手动提供summary参数，或检查网络连接和豆包AI登录状态")
                sys.exit(1)

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
            print("4. 如果使用豆包AI，可能需要调整提示词")
            sys.exit(1)
        
        # 如果清理后的文本更短，使用清理后的版本
        if validation_result['cleaned_count'] < validation_result['original_count']:
            summary = validation_result['cleaned_text']
            print(f"✅ 已自动使用清理后的summary（减少了{validation_result['original_count'] - validation_result['cleaned_count']}个字符）")
        
        # 如果title长度超过20字符，使用豆包AI生成短标题
        print("=" * 60)
        print("📏 检查标题长度...")
        title_length = len(title)
        print(f"📝 当前标题: {title}")
        print(f"📊 标题长度: {title_length}字符")
        
        # 如果用户提供了短标题参数，直接使用
        if short_title:
            short_title_length = len(short_title)
            print(f"✅ 使用用户指定的短标题: {short_title}")
            print(f"📊 短标题长度: {short_title_length}字符")
            
            # 验证用户提供的短标题长度
            if short_title_length > 20:
                print(f"⚠️  用户指定的短标题过长({short_title_length}字符)，建议不超过20字符")
                print("将使用用户指定的短标题，但可能在某些平台显示不完整")
        else:
            # 如果title长度超过20字符，使用豆包AI生成短标题
            if title_length > 20:
                print("⚠️  标题长度超过20字符，需要生成短标题")
                print("🤖 正在使用豆包AI生成短标题...")
                
                try:
                    short_title = generate_newspic_title_with_doubao(browser_context, markdown_file)
                    if short_title:
                        short_title_length = len(short_title)
                        print(f"✅ 豆包AI生成的短标题: {short_title}")
                        print(f"📊 短标题长度: {short_title_length}字符")
                        
                        # 验证生成的短标题长度
                        if short_title_length <= 20:
                            print("✅ 短标题长度符合要求，将使用生成的短标题")
                        else:
                            print(f"⚠️  生成的短标题仍然过长({short_title_length}字符)")
                            print("设置默认短标题")
                            short_title = "imgurl，一个免费的图床"
                            sys.exit(1)
                    else:
                        print("❌ 豆包AI生成短标题失败，将使用原标题")
                        short_title = title
                        print(f"✅ 将使用原标题作为短标题: {short_title}")
                except Exception as e:
                    print(f"❌ 豆包AI生成短标题时出错: {e}")
                    print("将使用原标题作为短标题")
                    short_title = title
                    print(f"✅ 将使用原标题作为短标题: {short_title}")
            else:
                print("✅ 标题长度符合要求，无需生成短标题")
                short_title = title
                print(f"✅ 标题长度符合要求，已将title赋值给short_title，将使用short_title: {short_title}")
        
        print("=" * 60)





        # 使用豆包AI生成文章封面图（如果没有提供cover_image）
        if not cover_image:
            print("=" * 60)
            print("🎨 正在使用豆包AI生成文章封面图...")
            print("=" * 60)
            try:
                # 导入豆包AI图片生成模块
                from doubao_ai_image_generator import create_doubao_generator
                import random
                
                # 创建新页面用于豆包AI
                page_doubao = browser_context.new_page()
                page_doubao.goto("https://www.doubao.com/chat/")
                page_doubao.wait_for_load_state("networkidle")
                print("✅ 豆包AI页面加载完成")
                
                # 创建豆包AI图片生成器
                generator = create_doubao_generator(page_doubao, browser_context)
                
                # 生成图片（豆包AI会生成4张图片）
                prompt, image_files = generator.generate_images_from_markdown(
                    markdown_file=markdown_file,
                    aspect_ratio="16:9"
                )
                
                if image_files and len(image_files) > 0:
                    # 随机选择一张图片作为封面图
                    cover_image = random.choice(image_files)
                    print(f"✅ 豆包AI图片生成成功，共生成 {len(image_files)} 张图片")
                    print(f"🎲 随机选择封面图: {os.path.basename(cover_image)}")
                    print(f"📁 封面图路径: {cover_image}")
                    
                    # 验证文件是否存在且可读
                    if os.path.exists(cover_image) and os.path.getsize(cover_image) > 0:
                        print(f"✅ 封面图验证成功，文件大小: {os.path.getsize(cover_image)} 字节")
                    else:
                        print(f"❌ 封面图验证失败，文件不存在或为空")
                        # 如果随机选择的图片有问题，尝试使用第一张图片
                        if len(image_files) > 1:
                            cover_image = image_files[0]
                            print(f"🔄 尝试使用第一张图片作为封面图: {os.path.basename(cover_image)}")
                        else:
                            print("❌ 所有生成的图片都有问题，将退出脚本")
                            sys.exit(1)
                else:
                    print("❌ 豆包AI图片生成失败，将退出脚本")
                    sys.exit(1)
                
                # 关闭豆包AI页面
                page_doubao.close()
                print("✅ 豆包AI页面已关闭")
                
            except ImportError:
                print("❌ 无法导入豆包AI图片生成模块")
                print("请确保 doubao_ai_image_generator.py 文件存在")

                cover_image = None  # 重置为None，让后续代码使用Gemini
            except Exception as e:
                print(f"❌ 豆包AI图片生成失败: {e}")

                cover_image = None  # 重置为None，让后续代码使用Gemini
        else:
            print(f"🖼️  使用指定的封面图: {cover_image}")

        # 使用Gemini生成文章封面图（如果没有提供cover_image且豆包AI也失败）
        # if not cover_image:
        #     print("=" * 60)
        #     print("🎨 正在使用Gemini生成文章封面图...")
        #     print("=" * 60)
        #     try:
        #         # 直接调用另外一个脚本来生成封面图
        #         import subprocess
        #         import sys

        #         # 设置生成图片的下载目录
        #         generated_images_dir = os.path.join(os.getcwd(), "generated_images")
        #         os.makedirs(generated_images_dir, exist_ok=True)
        #         env = os.environ.copy()
        #         # 构建调用命令
        #         script_path = "test_gemini_image_generation_upload_fixed.py"
        #         cmd = ["uv", "run", "python", script_path]
        #         # 设置环境变量传递markdown文件路径
        #         env['MARKDOWN_FILE_PATH'] = markdown_file

        #         # 设置环境变量以确保UTF-8编码
        #         env['PYTHONIOENCODING'] = 'utf-8'
        #         env['PYTHONUTF8'] = '1'

        #         print(f"📄 使用Markdown文件: {markdown_file}")
        #         print(f"📁 图片保存目录: {generated_images_dir}")
        #         print(f"🚀 执行命令: {' '.join(cmd)}")
        #         print("⚠️  注意：请确保Chrome已启动并开启调试端口：")
        #         print("   chrome.exe --remote-debugging-port=9222")
        #         print("   或者使用以下命令启动Chrome：")
        #         print("   chrome.exe --remote-debugging-port=9222 --user-data-dir=C:\\temp\\chrome-debug")
        #         print()
        #         print("📺 子脚本输出：")
        #         print("-" * 40)

        #         # 执行脚本并实时显示输出
        #         process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, 
        #                  text=True, encoding='utf-8', cwd=os.getcwd(), env=env, bufsize=1, universal_newlines=True)
                
        #         # 实时读取并显示输出
        #         for line in process.stdout:
        #             print(line.rstrip())
                
        #         # 等待进程完成
        #         process.wait()
                
        #         print("-" * 40)
        #         print("📺 子脚本执行完成")
                
        #         if process.returncode == 0:
        #             print("✅ Gemini图片生成脚本执行成功")
                    
        #             # 查找生成的图片文件
        #             downloads_dir = os.path.join(os.getcwd(), "generated_images")
        #             if os.path.exists(downloads_dir):
        #                 image_files = [f for f in os.listdir(downloads_dir) 
        #                              if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
                        
        #                 if image_files:
        #                     # 使用最新生成的图片（按修改时间排序）
        #                     latest_image = max(image_files, 
        #                                      key=lambda x: os.path.getctime(os.path.join(downloads_dir, x)))
        #                     cover_image = os.path.abspath(os.path.join(downloads_dir, latest_image))
        #                     print(f"✅ Gemini图片生成成功，封面图: {cover_image}")
                            
        #                     # 验证文件是否存在且可读
        #                     if os.path.exists(cover_image) and os.path.getsize(cover_image) > 0:
        #                         print(f"✅ 封面图验证成功，文件大小: {os.path.getsize(cover_image)} 字节")
        #                     else:
        #                         print(f"❌ 封面图验证失败，文件不存在或为空")
        #                         sys.exit(1)
        #                 else:
        #                     print("⚠️  未找到生成的图片，将退出脚本")
        #                     sys.exit(1)
        #             else:
        #                 print("⚠️  生成图片目录不存在，将退出脚本")
        #                 sys.exit(1)
        #         else:
        #             print(f"❌ Gemini图片生成脚本执行失败，将退出脚本")
        #             print(f"返回码: {process.returncode}")
        #             sys.exit(1)
                    
        #     except FileNotFoundError:
        #         print(f"⚠️  找不到Gemini生成脚本: test_gemini_image_generation_upload_fixed.py，将退出脚本")
        #         print("请确保该文件存在于当前目录")
        #         sys.exit(1)
                
        #     except Exception as e:
        #         print(f"⚠️  调用Gemini生成图片时出错: {e}，将退出脚本")
        #         sys.exit(1)
        # else:
        #     print(f"🖼️  使用指定的封面图: {cover_image}")
        #     if not os.path.exists(cover_image):
        #         print(f"❌ 封面图文件不存在: {cover_image}，将退出脚本")
        #         sys.exit(1)
        
        # 检查封面图大小，如果超过5MB则进行压缩
        print("=" * 60)
        print("📏 检查封面图文件大小...")
        print("=" * 60)
        
        cover_image_size = os.path.getsize(cover_image)
        cover_image_size_mb = cover_image_size / (1024 * 1024)
        print(f"📊 封面图文件大小: {cover_image_size_mb:.2f}MB")
        
        if cover_image_size_mb > 5:
            print(f"⚠️  封面图文件大小({cover_image_size_mb:.2f}MB)超过5MB限制，开始压缩...")
            compressed_cover_image = compress_image(cover_image, max_size_mb=5, quality=85)
            
            if compressed_cover_image and os.path.exists(compressed_cover_image):
                print(f"✅ 封面图压缩成功")
                print(f"📁 压缩后文件路径: {compressed_cover_image}")
                compressed_size = os.path.getsize(compressed_cover_image)
                compressed_size_mb = compressed_size / (1024 * 1024)
                print(f"📊 压缩后文件大小: {compressed_size_mb:.2f}MB")
                

            else:
                print(f"❌ 封面图压缩失败，将使用原始图片")
                print(f"⚠️  注意：原始图片大小({cover_image_size_mb:.2f}MB)可能超过某些平台的限制")
        else:
            print(f"✅ 封面图文件大小符合要求({cover_image_size_mb:.2f}MB <= 5MB)")
            compressed_cover_image = cover_image
        
        # 将豆包AI生成的文章封面图上传到微信公众号图片库
        print("确定是否需要将生成的文章封面图上传到微信公众平台图片库.")
        if 'wechat' in target_platforms:
            print("=" * 60)
            print("🎨 正在将豆包AI生成的文章封面图上传到微信公众号图片库...")
            print("=" * 60)
            try:
                # 在test_social_media_automatic_publish.py中使用
                from wechat_mp_sdk import WeChatMPSDK

                # 上传封面图到微信公众号素材库
                sdk = WeChatMPSDK(app_id=app_id, app_secret=app_secret)
                material_result = sdk.upload_image(cover_image)
                media_id = material_result['media_id']
                print(f"✅ 上传封面图到微信公众号素材库成功，media_id: {media_id}")
                print(f"✅ 上传封面图到微信公众号素材库成功，url: {material_result['url']}")
            except Exception as e:
                print(f"❌ 上传封面图到微信公众号素材库失败: {e}，将退出脚本")
                sys.exit(1)
        else:
            print("⏭️  未指定wechat，跳过将生成的文章封面图上传到微信公众平台图片库.")

        # 将豆包AI生成的文章封面图上传到相应钉钉文档的第一行中
        # 如果命令行中已经指定了markdown_file，则跳过执行这部分代码
        if need_download_markdown:
            try:
                print("命令行中未指定markdown_file，将执行钉钉文档封面图上传步骤")
                # 1. 直接聚焦到iframe内容区域
                iframe_content = page_dingtalk_doc.locator("#wiki-doc-iframe").content_frame
                print(f"✅ 获取到iframe内容: {iframe_content}")
               
                print("查找文档主体以找到可编辑区域")
                try:
                    doc_body = iframe_content.locator('body, .document-body, .editor-content')
                    if doc_body.count() > 0:
                        doc_body.first.click()
                        print("✅ 成功聚焦到文档主体")
                        
                    else:
                        print("⚠️  未找到文档主体")
                except Exception as e:
                    print(f"❌ 未找到文档主体: {e}")

                print("✅ 已聚焦到iframe内容区域")

                # 等待焦点设置完成
                page_dingtalk_doc.wait_for_timeout(1000)

                # 2. 尝试移动到文档开头
                try:
                    print("正在按下组合键（Control+Home）...")
                    # iframe_content.press("Control+Home")
                    # editor_area.press("Control+Home")
                    # editor_container.press("Control+Home")
                    doc_body.first.press("Control+Home")
                    print("✅ 组合键（Control+Home）按下成功，等待2秒...")
                    page_dingtalk_doc.wait_for_timeout(2000)
                    # editor_area.press("Control+Home")
                    print("✅ 成功移动到文档开头")
                except Exception as e:
                    print(f"⚠️  组合键（Control+Home）失败: {e}")
                    sys.exit(1)
                # 3. 点击插入按钮
                print("3️⃣ 点击插入按钮...")
                iframe_content.get_by_test_id("overlay-bi-toolbar-insertMore").get_by_text("插入").click()
                print("✅ 插入按钮点击成功")
            # iframe_content.get_by_text("图片上传本地图片").click()
                
                print("开始将豆包AI生成的文章封面图上传到钉钉文档...")
                print(f"即将上传的图片的绝对路径: {cover_image}")
                # 4. 使用文件选择器处理方式上传图片（参考51CTO的方法）
                with page_dingtalk_doc.expect_file_chooser() as fc_info_dingtalk:
                    # 点击文件上传触发元素
                    print("4️⃣ 点击文件上传触发元素...")
                    iframe_content.get_by_text("图片上传本地图片").click()          
                    print("✅ 文件上传触发元素点击成功")
                # 获取文件选择器并设置文件
                file_chooser_dingtalk = fc_info_dingtalk.value
                file_chooser_dingtalk.set_files(cover_image)
                print("✅ 图片成功上传到钉钉文档")
                # 等待封面图上传完成
                page_dingtalk_doc.wait_for_timeout(3000)
                # 等待文档加载完成
                print("5️⃣ 等待文档加载完成...")
                page_dingtalk_doc.wait_for_load_state("domcontentloaded")
                page_dingtalk_doc.wait_for_timeout(2000)  # 额外等待确保文档完全加载
                print("✅ 图片上传结束")
                # 下载钉钉文档为本地markdown文件（新的markdown文件包含封面图），作为markdown_file参数，上传到mdnice
                print("=" * 60)
                print("🎨 正在下载钉钉文档为本地markdown文件（新的markdown文件包含封面图）...")
                print("=" * 60)
                try:
                    page_dingtalk_doc.locator("#wiki-doc-iframe").content_frame.get_by_test_id("doc-header-more-button").click()
                
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
                    downloaded_new_markdown_file_path = os.path.abspath(save_path)
                    downloaded_filename = os.path.basename(downloaded_new_markdown_file_path)
                    
                    print(f"📁 下载文件名（新的markdown文件包含封面图）: {downloaded_filename}")
                    print(f"📂 下载文件（新的markdown文件包含封面图）绝对路径: {downloaded_new_markdown_file_path}")

                    # 更新markdown_file变量为下载的文件路径
                    print(f"✅ 更新markdown_file变量为下载的文件路径: {downloaded_new_markdown_file_path}")
                    markdown_file = downloaded_new_markdown_file_path
                except Exception as e:
                    print(f"❌ 下载钉钉文档为本地markdown文件失败: {e}，将退出脚本")
                    sys.exit(1)
            except Exception as e:
                print(f"❌ 图片上传失败: {e}，将退出脚本")
                sys.exit(1)
        else:
            print("⏭️  已指定markdown文件，跳过钉钉文档封面图上传步骤")

        print("=" * 60)

        # 解析话题标签
        all_tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()]
        print(f"📝 原始话题标签: {all_tags}")
        
        # 检查是否需要使用豆包AI自动生成话题标签
        if not all_tags or (len(all_tags) == 1 and all_tags[0].lower() in ['auto', 'doubao', '豆包', 'ai']):
            print("=" * 60)
            print("🏷️  使用豆包AI自动生成话题标签...")
            print("=" * 60)
            
            try:
                ai_generated_tags = generate_tags_with_doubao(browser_context, markdown_file)
                if ai_generated_tags:
                    all_tags = ai_generated_tags
                    print(f"🤖 豆包AI生成的话题标签: {all_tags}")
                else:
                    print("⚠️  豆包AI生成标签失败，使用默认标签")
                    all_tags = ['AI', 'LLM', '人工智能', '开发', '大模型']
                    
            except Exception as e:
                print(f"❌ 豆包AI生成标签失败: {e}")
                print("使用默认标签...")
                all_tags = ['AI', 'LLM', '人工智能', '开发', '大模型']
            
            print("=" * 60)
        
        print(f"📝 最终话题标签: {all_tags}")
        
        
        # 在发布到各个平台之前，先处理markdown文件，移除微信公众号关注行和作者信息行
        print("=" * 60)
        print("🧹 正在处理51CTO专用的markdown文件...")
        print("=" * 60)
        
        # 初始化变量，默认使用原始文件
        final_51cto_markdown_path = markdown_file
        
        try:
            # 导入markdown清理工具（简化后的导入方式）
            from markdown_cleaner_sdk import MarkdownCleaner
            
            
            # 创建原始markdown文件的副本，专门用于51CTO
            original_markdown_path = Path(markdown_file)
            cto_markdown_path = original_markdown_path.parent / f"51CTO_{original_markdown_path.name}"
            
            print(f"📁 原始markdown文件: {original_markdown_path}")
            print(f"📁 51CTO专用文件: {cto_markdown_path}")
            
            # 复制原始文件
            import shutil
            shutil.copy2(original_markdown_path, cto_markdown_path)
            print("✅ 已创建51CTO专用markdown文件副本")
            
            # 创建markdown清理器实例，专门移除微信公众号关注行和作者信息行
            cleaner = MarkdownCleaner(
                keywords=["关注微信公众号", "关于作者和DreamAI", "Amq4vjg890AlRbA6Td9ZvlpDJ3kdP0wQ"],
                mode="contains",
                case_sensitive=False,
                backup=False  # 不为51CTO文件创建备份
            )
            # 清理51CTO专用文件
            result = cleaner.clean_file(cto_markdown_path)
            
            print("✅ 51CTO markdown文件清理完成!")
            print(f"📊 原行数: {result['original_lines']}")
            print(f"📊 删除行数: {result['removed_lines']}")
            print(f"📊 剩余行数: {result['remaining_lines']}")
            
            if result['removed_content']:
                print("🗑️  删除的内容:")
                for item in result['removed_content']:
                    print(f"   第{item['line_number']}行: {item['content']}")
            
            # 更新markdown_file变量为清理后的51CTO专用文件
            final_51cto_markdown_path = str(cto_markdown_path)
            print(f"✅ 已更新markdown_file为51CTO专用文件: {final_51cto_markdown_path}")
            
        except ImportError as e:
            print(f"❌ 无法导入markdown清理工具: {e}")
            print("⚠️  将使用原始markdown文件，可能包含微信公众号关注信息")
        except Exception as e:
            print(f"❌ 处理51CTO markdown文件时出错: {e}")
            print("⚠️  将使用原始markdown文件，可能包含微信公众号关注信息")
        
        print("=" * 60)


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
            # page_wechat.get_by_role("link", name=re.compile(r"AI配图 \(\d+\)")).click()
            # 点击我的图片文件夹，使用正则表达式匹配"我的图片 (数字)"格式的链接
            # 例如："我的图片 (15)" 或 "我的图片 (23)" 等，数字表示该文件夹中的图片数量
            page_wechat.get_by_role("link", name=re.compile(r"我的图片 \(\d+\)")).click()
            page_wechat.locator(".weui-desktop-img-picker__img-thumb").first.click()
            page_wechat.get_by_role("button", name="下一步").click()
            page_wechat.get_by_role("button", name="确认").click()
            
            # 设置文章摘要
            print("📝 正在设置文章摘要...")
            page_wechat.get_by_role("textbox", name="选填，不填写则默认抓取正文开头部分文字，摘要会在转发卡片和公众号会话展示。").click()
            # 使用配置中的摘要
            page_wechat.get_by_role("textbox", name="选填，不填写则默认抓取正文开头部分文字，摘要会在转发卡片和公众号会话展示。").fill(summary)
            print(f"✅ 文章摘要设置完成: {summary}")

            # 设置原文链接
            print("🔗 正在设置原文链接...")
            page_wechat.locator("#js_article_url_area").get_by_text("未添加").click()
            page_wechat.get_by_role("textbox", name="输入或粘贴原文链接").click()
            # 使用配置中的URL
            page_wechat.get_by_role("textbox", name="输入或粘贴原文链接").fill(url)
            print(f"✅ 原文链接设置完成: {url}")
            
            # 确认链接设置
            print("🔄 正在确认链接设置...")
            ok_button = page_wechat.get_by_role("link", name="确定")
            expect(ok_button).to_be_visible()
            expect(ok_button).to_be_enabled()
            ok_button.click()
            print("✅ 链接设置确认完成")
            # 等待文档加载完成
            print("等待文档基本加载完成...")
            page_wechat.wait_for_load_state("domcontentloaded", timeout=60000)
            print("文档页面基本加载完成！")
            page_wechat.wait_for_load_state("networkidle")

            page_wechat.wait_for_timeout(5000)
            # 保存为草稿（避免意外丢失）
            print("💾 正在保存为草稿...")
            page_wechat.get_by_role("button", name="保存为草稿").click()
            # 检查是否出现"已保存"文本，如果出现则点击，否则继续执行。如果正文中有图片转存失败，则“已保存”提示不会出现。最终保存为草稿也会失败。
            try:
                save_success_element = page_wechat.locator("#js_save_success").get_by_text("已保存")
                print("🔍 检查是否出现'已保存'提示...超时时间为30秒")
                is_visible = save_success_element.is_visible(timeout=30000)
                if is_visible:
                    save_success_element.click()
                    print("✅ 点击了'已保存'提示")
                else:
                    print("ℹ️  未出现'已保存'提示，继续执行")
                    # page_wechat.pause()
            except Exception as e:
                print(f"ℹ️  处理'已保存'提示时出错，继续执行: {e}")
            print("✅ 文章已保存为草稿")
        
        ## 知乎，发布文章。
        ## 支持Markdown文件导入，自动设置标题、封面、话题标签等
        if 'zhihu' in target_platforms:
            print("正在发布到知乎...")
            # 获取知乎平台的话题标签
            # 使用固定的知乎话题标签
            zhihu_tags = ["LLM", "AI", "大模型"]
            # zhihu_tags = get_platform_tags(all_tags, 'zhihu')
            print(f"🏷️  知乎话题标签: {zhihu_tags}")
            
            page_zhihu = browser_context.new_page()
            page_zhihu.goto("https://www.zhihu.com/")
            
            # 点击"写文章"按钮，会打开编辑器新窗口
            with page_zhihu.expect_popup() as page_zhihu_info:
                # 使用更精确的定位方式，避免匹配到多个元素
                try:
                    # 方法1：使用exact=True进行精确匹配
                    page_zhihu.get_by_text("写文章", exact=True).click()
                    print("✅ 找到并点击了'写文章'按钮（精确匹配）")
                except Exception:
                    # 方法2：使用CSS类名定位
                    try:
                        page_zhihu.locator("div.css-hv22zf").click()
                        print("✅ 找到并点击了'写文章'按钮（CSS类名）")
                    except Exception:
                        # 方法3：遍历所有包含"写文章"的元素，选择正确的
                        all_elements = page_zhihu.get_by_text("写文章")
                        for i in range(all_elements.count()):
                            element_text = all_elements.nth(i).text_content()
                            # 检查元素文本是否只包含"写文章"，不包含其他内容
                            if element_text.strip() == "写文章":
                                print(f"✅ 找到并点击了'写文章'按钮（文本过滤）: {element_text}")
                                all_elements.nth(i).click()
                                break
                        else:
                            raise Exception("未找到正确的'写文章'按钮")
            page_zhihu_editor = page_zhihu_info.value
            
            # 点击"文档"按钮打开导入模态框
            print("点击'文档'按钮以弹出导入菜单")
            # 使用更精确的CSS选择器定位"文档"按钮
            try:
                # 方法1：通过包含"文档"文本的span元素定位
                page_zhihu_editor.locator("span.css-8atqhb:has-text('文档')").click()
                print("✅ 通过span.css-8atqhb定位成功")
            except Exception as e1:
                print(f"⚠️ 方法1失败: {e1}")
                try:
                    # 方法2：通过按钮的aria-label属性定位
                    page_zhihu_editor.locator("button[aria-label='文档']").click()
                    print("✅ 通过aria-label定位成功")
                except Exception as e2:
                    print(f"⚠️ 方法2失败: {e2}")
                    try:
                        # 方法3：通过包含特定class的按钮定位
                        page_zhihu_editor.locator("button.ToolbarButton:has-text('文档')").click()
                        print("✅ 通过ToolbarButton class定位成功")
                    except Exception as e3:
                        print(f"⚠️ 方法3失败: {e3}")
                        # 方法4：兜底方案，使用原来的方式
                        page_zhihu_editor.get_by_role("button", name="文档").click()
                        print("✅ 使用兜底方案定位成功")
            
            # 等待弹窗出现，使用更稳定的定位方式
            print("等待弹窗出现...")
            try:
                # 方法1：等待弹窗容器出现
                page_zhihu_editor.wait_for_selector("[role='tooltip'], .Popover-content, [id*='Popover']", timeout=5000)
                print("✅ 弹窗容器已出现")
                
                # 方法2：尝试多种定位方式
                doc_button_clicked = False
                
                # 尝试通过弹窗内的文档按钮定位
                try:
                    # 使用更通用的选择器
                    popover_content = page_zhihu_editor.locator("[role='tooltip'], .Popover-content, [id*='Popover']").first
                    popover_content.get_by_role("button", name="文档").click()
                    print("✅ 通过弹窗容器找到并点击了'文档'按钮")
                    doc_button_clicked = True
                except Exception as e1:
                    print(f"⚠️  方法1失败: {e1}")
                    
                    # 尝试直接通过文本定位
                    try:
                        page_zhihu_editor.get_by_text("文档").nth(1).click()  # 第二个文档按钮
                        print("✅ 通过文本定位找到并点击了'文档'按钮")
                        doc_button_clicked = True
                    except Exception as e2:
                        print(f"⚠️  方法2失败: {e2}")
                        
                        # 尝试通过CSS选择器
                        try:
                            page_zhihu_editor.locator("button:has-text('文档')").nth(1).click()
                            print("✅ 通过CSS选择器找到并点击了'文档'按钮")
                            doc_button_clicked = True
                        except Exception as e3:
                            print(f"⚠️  方法3失败: {e3}")
                
                if not doc_button_clicked:
                    raise Exception("所有方法都无法找到弹窗中的'文档'按钮")
                    
            except Exception as e:
                print(f"❌ 无法找到弹窗或文档按钮: {e}")
                # 如果弹窗定位失败，尝试直接点击第二个文档按钮
                try:
                    page_zhihu_editor.get_by_text("文档").nth(1).click()
                    print("✅ 直接点击第二个'文档'按钮成功")
                except Exception as e2:
                    print(f"❌ 备用方法也失败: {e2}")
                    raise e2
            
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
            # 点击发布按钮并等待页面导航完成。注意：点击"发布"按钮后，新的网页会报错，实际上文章已经发布成功了。错误信息：{"error":{"message":"您当前请求存在异常，暂时限制本次访问。如有疑问，您可以通过手机摇一摇或登录后私信知乎小管家反馈。8131ab59c0a33a85e9efb02aaaf1b643","code":40362}}
            
            # print("点击发布按钮...")
            # page_zhihu_editor.wait_for_load_state("networkidle")
            # 等待页面基本加载完成
            print("等待文档基本加载完成...")
            page_zhihu_editor.wait_for_load_state("domcontentloaded", timeout=60000)
            print("文档页面基本加载完成！")
            page_zhihu_editor.get_by_role("button", name="发布").click()
            
            # # 等待页面跳转完成
            print("等待页面跳转完成...")
            page_zhihu_editor.wait_for_load_state("networkidle")
            print("页面跳转完成！")
            print("知乎文章发布成功！")

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
            print(f"📁 正在上传markdown文件（csdn的审核越来越严格，所以使用专门为csdn准备的markdown文件）: {final_51cto_markdown_path}")
            page_csdn_md_editor.get_by_text("导入 导入").set_input_files(final_51cto_markdown_path)
            page_csdn_md_editor.wait_for_timeout(10000)
            print("等待文档基本加载完成...")
            page_csdn_md_editor.wait_for_load_state("domcontentloaded", timeout=60000)
            print("文档页面基本加载完成！")
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
            # 注意：上传的图片文件不能超过5MB
            page_csdn_md_editor.locator(".cover-upload-box .el-upload__input").set_input_files(compressed_cover_image)
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
            file_chooser.set_files(final_51cto_markdown_path)
            
            page_51cto.wait_for_timeout(10000)
            print("等待文档基本加载完成...")
            page_51cto.wait_for_load_state("domcontentloaded", timeout=60000)
            print("文档页面基本加载完成！")
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
            print("🏷️  正在设置文章标签...")
            page_51cto.get_by_text("标签", exact=True).click()
            page_51cto.get_by_role("textbox", name="请设置标签，最多可设置5个，支持，；enter间隔").click()
            
            # 添加多个标签，51cto默认会自动填写三个话题标签，所以还可以手工填写两个(之前的代码已经清空了现有标签)。最多只能填写5个标签。
            for tag in cto_tags:
                page_51cto.get_by_role("textbox", name="请设置标签，最多可设置5个，支持，；enter间隔").fill(tag)
                page_51cto.get_by_role("textbox", name="请设置标签，最多可设置5个，支持，；enter间隔").press("Enter")
            
            # 设置文章摘要
            print("🏷️  正在设置文章摘要...")
            page_51cto.get_by_role("textbox", name="请填写文章摘要，最多可填写500").click()
            page_51cto.get_by_role("textbox", name="请填写文章摘要，最多可填写500").fill(summary)
            
            # 设置话题
            print("🏷️  正在设置话题...")
            page_51cto.get_by_role("textbox", name="请填写话题").click()
            page_51cto.get_by_text("#yyds干货盘点#").click()
            
            # 添加封面设置代码。注意：51CTO支持自动从正文中提取图片作为封面图（默认设置），如果要自己设置封面图，这里可以手动上传封面图
            # 先选择手动上传封面模式（而不是自动设置）
            # page_51cto.locator("input[name='imgtype'][value='1']").check()  # 选择手动上传模式

            # 或者使用更精确的选择器，注意，图片不能超过1.9MB，否则会报错
            # page_51cto.locator("input[type='file'].upload_input").set_input_files(cover_image)

            # 发布文章
            print("🏷️  正在发布文章...")
            page_51cto.get_by_role("button", name="发布", exact=True).click()
            # 验证是否发布成功
            try:
                # 不一定会出现"发布成功 - 待审核"文本，因为如果文档中没有检测到敏感词，则不会出现这个文本。
                page_51cto.get_by_text("发布成功 - 待审核").click()
                print("✅ 文章发布成功！")
            except Exception as e:
                print(f"ℹ️ 未找到'发布成功 - 待审核'文本，程序继续执行: {e}")

        ## 博客园，发布文章。
        ## 支持Markdown导入，自动提取图片，设置分类等
        if 'cnblogs' in target_platforms:
            print("正在发布到博客园...")
            # 获取博客园平台的话题标签
            cnblogs_tags = get_platform_tags(all_tags, 'cnblogs')
            print(f"🏷️  博客园话题标签: {cnblogs_tags}")
            
            page_cnblogs = browser_context.new_page()
            page_cnblogs.goto("https://www.cnblogs.com/")
            print("📝 已打开博客园首页")
            
            page_cnblogs.get_by_role("link", name="写随笔").click()
            print("📝 已点击写随笔按钮")
            
            # 切换到文章模式
            page_cnblogs.get_by_role("link", name="文章").click()
            print("📝 已切换到文章模式")
            
            # 导入文章 - 使用最稳定的定位器
            page_cnblogs.get_by_role("link", name="导入文章").click()
            print("📝 已点击导入文章按钮")
            
            # 上传Markdown文件 - 使用文件选择器处理方式
            print("📁 正在上传Markdown文件...")
            with page_cnblogs.expect_file_chooser() as fc_info:
                # 点击"选择文件"链接或拖拽区域来触发文件选择器
                page_cnblogs.get_by_role("link", name="选择文件").click()
            
            file_chooser = fc_info.value
            file_chooser.set_files(markdown_file)
            print(f"✅ 已选择文件: {markdown_file}")
            
            # 确认导入
            page_cnblogs.get_by_text("导入 1 个文件").click()
            print("📝 已确认导入文件")
            
            page_cnblogs.get_by_role("button", name="开始导入").click()
            print("🚀 正在开始导入...")
            
            page_cnblogs.get_by_role("button", name="完成").click()
            print("✅ 文件导入完成")
            
            print("等待文档基本加载完成...")
            page_cnblogs.wait_for_load_state("domcontentloaded", timeout=60000)
            print("文档页面基本加载完成！")
            
            # 编辑导入的文章
            print("📝 正在编辑导入的文章...")
            # 使用更灵活的匹配方式，因为title后面的时间标记是动态变化的
            # 尝试通过title定位元素，如果失败则使用markdown_filename
            try:
                page_cnblogs.get_by_role("row").filter(has_text=title).get_by_role("link").nth(1).click()
                print(f"✅ 通过title定位成功: {title}")
            except Exception as e:
                print(f"⚠️  通过title定位失败: {e}")
                if 'markdown_filename' in locals():
                    print(f"🔄 尝试使用markdown文件名定位: {markdown_filename}")
                    page_cnblogs.get_by_role("row").filter(has_text=markdown_filename).get_by_role("link").nth(1).click()
                    print(f"✅ 通过markdown文件名定位成功: {markdown_filename}")
                else:
                    print("❌ markdown_filename未定义，无法使用备用定位方式")
                    raise e
            print("📝 已进入文章编辑页面")
            
            # 设置文章分类
            print("🏷️  正在设置文章分类...")
            # page_cnblogs.locator("nz-tree-select div").click()
            page_cnblogs.get_by_role("checkbox", name="AI").check()
            print("✅ 已设置文章分类为AI")
            
            # 设置发布状态
            print("📝 正在设置发布状态...")
            page_cnblogs.get_by_role("checkbox", name="发布", exact=True).check()
            print("✅ 已设置为发布状态")
            
            # 提取文章中的图片
            print("🖼️  正在提取文章中的图片...")
            page_cnblogs.get_by_role("button", name="提取图片").click()
            
            # 检查是否有图片需要提取
            try:
                # 等待一下让页面响应
                page_cnblogs.wait_for_timeout(2000)
                
                # 检查是否出现"没有需要提取的图片"的提示
                no_images_element = page_cnblogs.get_by_text("没有需要提取的图片")
                if no_images_element.count() > 0:
                    print("⚠️  没有需要提取的图片")
                    no_images_element.click()
                else:
                    # 如果没有"没有需要提取的图片"提示，则点击"成功"
                    page_cnblogs.get_by_text("成功:", timeout=60000).click()
                    print("✅ 图片提取成功")
            except Exception as e:
                print(f"⚠️  图片提取过程中出现异常: {e}")
                # 尝试点击成功按钮
                try:
                    page_cnblogs.get_by_text("成功:").click()
                    print("✅ 图片提取成功")
                except:
                    print("⚠️  无法点击成功按钮，继续执行后续步骤")
            
            # 设置题图 - 使用文件选择器
            print("🖼️  正在设置题图...")
            page_cnblogs.get_by_text("插入题图").click()
            
            with page_cnblogs.expect_file_chooser() as fc_info2:
                page_cnblogs.get_by_role("button", name="选择要上传的图片").click()
            
            file_chooser2 = fc_info2.value
            file_chooser2.set_files(cover_image)
            print(f"✅ 已选择题图: {cover_image}")
            
            page_cnblogs.get_by_role("button", name="确定").click()
            print("✅ 题图设置完成")
            
            # 设置文章摘要
            print("📝 正在设置文章摘要...")
            page_cnblogs.locator("#summary").click()
            page_cnblogs.locator("#summary").fill(summary)
            print(f"✅ 已设置文章摘要: {summary[:50]}...")
            
            # 保存草稿
            # page_cnblogs.get_by_role("button", name="保存草稿").click()
            # 注意：实际发布需要手动点击发布按钮
            print("🚀 正在发布文章...")
            print("点击发布草稿按钮")
            page_cnblogs.get_by_role("button", name="发布草稿").click()
            print("点击保存成功按钮")
            try:
                save_success_elem = page_cnblogs.locator("#cdk-overlay-4").get_by_text("保存成功")
                if save_success_elem.count() > 0:
                    save_success_elem.click()
                    print("✅ 检测到并点击了'保存成功'按钮")
                else:
                    publish_success_elem = page_cnblogs.locator("#cdk-overlay-4").get_by_text("发布成功")
                    if publish_success_elem.count() > 0:
                        publish_success_elem.click()
                        print("✅ 检测到并点击了'发布成功'按钮")
                    else:
                        print("⚠️  未检测到'保存成功'或'发布成功'按钮，跳过点击")
            except Exception as e:
                print(f"⚠️  点击'保存成功'或'发布成功'按钮时出错: {e}")
            print("✅ 博客园文章发布成功！")

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
            page_xiaohongshu.get_by_role("textbox", name="填写标题会有更多赞哦～").fill(short_title)
            
            # 设置描述内容
            page_xiaohongshu.get_by_role("textbox").nth(1).click()
            # 先填入摘要和链接
            # 设置描述内容，使用type方法逐步输入以确保换行生效
            page_xiaohongshu.get_by_role("textbox").nth(1).click()
            page_xiaohongshu.get_by_role("textbox").nth(1).type(summary)
            page_xiaohongshu.get_by_role("textbox").nth(1).press("Enter")
            # 若加入链接，则会被核定违规
            # page_xiaohongshu.get_by_role("textbox").nth(1).type("详情请查阅此文章：")
            # page_xiaohongshu.get_by_role("textbox").nth(1).type(url)
            # page_xiaohongshu.get_by_role("textbox").nth(1).press("Enter")
            
            # 模拟人工操作添加话题标签，小红书笔记最多支持添加10个话题标签
            for tag in xiaohongshu_tags:
                page_xiaohongshu.get_by_role("textbox").nth(1).type("#")
                page_xiaohongshu.wait_for_timeout(1000)
                page_xiaohongshu.get_by_role("textbox").nth(1).type(tag)
                page_xiaohongshu.wait_for_timeout(1000)
                page_xiaohongshu.locator("#creator-editor-topic-container").get_by_text(f"#{tag}", exact=True).click()
                page_xiaohongshu.wait_for_timeout(1000)
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
            page_xiaohongshu.get_by_text('发布成功').click(timeout=60000)

        ## 抖音，发布图文（douyin_newspic）。
        ## 支持图片上传，设置标题、描述、合集等
        if 'douyin_newspic' in target_platforms:
            print("正在发布到抖音图文消息...")  
            # 获取抖音平台的话题标签
            douyin_tags = get_platform_tags(all_tags, 'douyin')
            print(f"🏷️  抖音话题标签: {douyin_tags}")
            
            page_douyin = browser_context.new_page()
            page_douyin.goto("https://creator.douyin.com/creator-micro/home?enter_from=dou_web", timeout=60000)
            page_douyin.get_by_text("发布图文").click()
            
            # 上传图文
            # page_douyin.get_by_role("button", name="上传图文").click()
            with page_douyin.expect_file_chooser() as fc_info3:
                page_douyin.get_by_role("button", name="上传图文").click()
            
            file_chooser3 = fc_info3.value
            file_chooser3.set_files(cover_image)
            
            # 设置作品标题
            page_douyin.get_by_role("textbox", name="添加作品标题").click()
            page_douyin.get_by_role("textbox", name="添加作品标题").fill(short_title)
            
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
            print("正在打开发布图文窗口...")
            with page_kuaishou.expect_popup() as page_new_newspic:
                page_kuaishou.get_by_text("发布图文", exact=True).click()
            page_kuaishou_newspic = page_new_newspic.value
            print("✅ 发布图文窗口打开成功")
            
            # 上传图片
            # page_kuaishou_newspic.get_by_role("button", name="上传图片").click()
            print("正在上传图片...")
            with page_kuaishou_newspic.expect_file_chooser() as fc_info4:
                page_kuaishou_newspic.get_by_role("button", name="上传图片").click()
            
            file_chooser4 = fc_info4.value
            file_chooser4.set_files(cover_image)

            # 验证是否上传了图片
            page_kuaishou_newspic.get_by_text(re.compile(r'\d+张图片上传成功')).click(timeout=120000)
            print("✅ 图片上传成功")
            # 快手图文没有标题
            # 设置描述内容
            print("正在设置描述内容...")
            page_kuaishou_newspic.locator("#work-description-edit").click()
            page_kuaishou_newspic.locator("#work-description-edit").fill(f"{summary}")
            page_kuaishou_newspic.locator("#work-description-edit").press("Enter")
            page_kuaishou_newspic.locator("#work-description-edit").type("详情请查阅此文章：")
            page_kuaishou_newspic.locator("#work-description-edit").type(url)
            page_kuaishou_newspic.locator("#work-description-edit").press("Enter")
            print("等待网络空闲")
            try:
                page_kuaishou_newspic.wait_for_load_state("networkidle", timeout=60000)
            except Exception as e:
                print(f"⚠️ 网络空闲等待超时，继续执行: {e}")
            print("正在添加话题标签...")
            # 添加话题标签，注意：快手最多支持添加4个话题标签
            # 快手添加话题标签很简单，直接输入标签名即可，不是一定要从下拉列表中选择
            for tag in kuaishou_tags:
                page_kuaishou_newspic.locator("#work-description-edit").type(f"#{tag} ")
            
            # 等待网络空闲状态
            try:
                page_kuaishou_newspic.wait_for_load_state("networkidle", timeout=60000)
            except Exception as e:
                print(f"⚠️ 快手图文消息等待网络空闲超时，继续执行: {e}")
            print("✅ 话题标签添加成功")
            # 发布
            print("正在发布快手图文...")
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
        # if 'mdnice' in target_platforms:
        #     page_mdnice.screenshot(path="test-results/screenshot_mdnice.png", full_page=True)
        # if 'wechat' in target_platforms:
        #     page_wechat.screenshot(path="test-results/screenshot_wechat.png", full_page=True)
        # if 'zhihu' in target_platforms:
        #     page_zhihu_editor.screenshot(path="test-results/screenshot_zhihu.png", full_page=True)
        # if 'csdn' in target_platforms:
        #     page_csdn.screenshot(path="test-results/screenshot_csdn.png", full_page=True)
        # if '51cto' in target_platforms:
        #     page_51cto.screenshot(path="test-results/screenshot_51cto.png", full_page=True)
        # if 'cnblogs' in target_platforms:
        #     page_cnblogs.screenshot(path="test-results/screenshot_cnblogs.png", full_page=True)
        # if 'xiaohongshu_newspic' in target_platforms:
        #     page_xiaohongshu.screenshot(path="test-results/screenshot_xiaohongshu.png", full_page=True)
        # if 'douyin_newspic' in target_platforms:
        #     page_douyin.screenshot(path="test-results/screenshot_douyin.png", full_page=True)
        # if 'kuaishou_newspic' in target_platforms:
        #     page_kuaishou.screenshot(path="test-results/screenshot_kuaishou.png", full_page=True)
        # if 'bilibili_newspic' in target_platforms:
        #     page_bilibili.screenshot(path="test-results/screenshot_bilibili.png", full_page=True)


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
    print("1. 基本运行（需要提供title参数）：")
    print("   pytest -s --headed --video on --screenshot on --tracing on ./test_social_media_automatic_publish.py \\")
    print("     --title '文章标题'")
    print()
    print("2. 自定义参数运行：")
    print("   pytest -s --headed ./test_social_media_automatic_publish.py \\")
    print("     --title '自定义标题' \\")
    print("     --author '自定义作者' \\")
    print("     --summary '自定义摘要' \\")
    print("     --url '原文链接' \\")
    print("     --markdown-file '/path/to/article.md' \\")
    print("     --cover-image 'cover.jpg' \\")
    print("     --short-title '短标题' \\")
    print("     --platforms 'wechat,zhihu'")
    print()
    print("参数说明：")
    print("--title              文章标题（必填）")
    print("--author             作者名称（必填）")
    print("--summary            文章摘要（可选，如不指定则使用豆包AI自动生成）")
    print("                     特殊值：'auto'、'doubao'、'豆包'、'ai' - 使用豆包AI自动生成")
    print("--url                原文链接（可选，如不指定则从钉钉文档自动获取）")
    print("--markdown-file      Markdown文件路径（可选，如不指定则从钉钉文档自动下载）")
    print("--user-data-dir      浏览器用户数据目录（可选，默认：chromium-browser-data）")
    print("--platforms          指定要发布到的平台（可选，默认发布到所有平台）")
    print("--cover-image        文章封面图片路径（可选，如不指定则使用Gemini自动生成）")
    print("--tags               话题标签（可选，用逗号分隔，如：AI,人工智能,大模型）")
    print("                     特殊值：'auto'、'doubao'、'豆包'、'ai' - 使用豆包AI自动生成")
    print("--short-title        短标题（可选，用于图文平台，如不指定则自动生成）")
    print("--backup-browser-data 是否备份浏览器数据（可选，true/false，默认true）")
    print()
    print("豆包AI自动生成summary的使用方法：")
    print("--summary auto                    # 使用豆包AI自动生成summary")
    print("--summary doubao                  # 使用豆包AI自动生成summary")
    print("--summary 豆包                    # 使用豆包AI自动生成summary")
    print("--summary ai                      # 使用豆包AI自动生成summary")
    print()
    print("豆包AI自动生成话题标签的使用方法：")
    print("--tags auto                       # 使用豆包AI自动生成话题标签")
    print("--tags doubao                     # 使用豆包AI自动生成话题标签")
    print("--tags 豆包                       # 使用豆包AI自动生成话题标签")
    print("--tags ai                         # 使用豆包AI自动生成话题标签")
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
    print("  --cover-image './cover.jpg' \\")
    print("  --short-title 'AutoGPT智能代理'")
    print()
    print("# 只发布到特定平台")
    print("pytest -s --headed ./test_social_media_automatic_publish.py \\")
    print("  --title '测试标题' \\")
    print("  --author '测试作者' \\")
    print("  --summary '测试摘要' \\")
    print("  --url 'https://test.com' \\")
    print("  --markdown-file './test.md' \\")
    print("  --cover-image './test_cover.jpg' \\")
    print("  --short-title '测试短标题' \\")
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
    print("  --short-title '快速测试' \\")
    print("  --platforms 'zhihu' \\")
    print("  --backup-browser-data false")
    print()
    print("作者：tornadoami")
    print("版本：1.0.0")
    print("更新日期：2025年")
    print("=" * 80)
    print("参数说明：")
    print("--title              文章标题（必填）")
    print("--author             作者名称（必填）")
    print("--summary            文章摘要（可选，如不指定则使用豆包AI自动生成）")
    print("                     特殊值：'auto'、'doubao'、'豆包'、'ai' - 使用豆包AI自动生成")
    print("--url                原文链接（可选，如不指定则从钉钉文档自动获取）")
    print("--markdown-file      Markdown文件路径（可选，如不指定则从钉钉文档自动下载）")
    print("--user-data-dir      浏览器用户数据目录（可选，默认：chromium-browser-data）")
    print("--platforms          指定要发布到的平台（可选，默认发布到所有平台）")
    print("--cover-image        文章封面图片路径（可选，如不指定则使用Gemini自动生成）")
    print("--tags               话题标签（可选，用逗号分隔，如：AI,人工智能,大模型）")
    print("                     特殊值：'auto'、'doubao'、'豆包'、'ai' - 使用豆包AI自动生成")
    print("--short-title        短标题（可选，用于图文平台，如不指定则自动生成）")
    print("--backup-browser-data 是否备份浏览器数据（可选，true/false，默认true）")
    print()
    print("豆包AI自动生成summary的使用方法：")
    print("--summary auto                    # 使用豆包AI自动生成summary")
    print("--summary doubao                  # 使用豆包AI自动生成summary")
    print("--summary 豆包                    # 使用豆包AI自动生成summary")
    print("--summary ai                      # 使用豆包AI自动生成summary")
    print()
    print("环境要求：")
    print("- 如果使用豆包AI功能，需要安装: pip install pyperclip")
    print("- 如果使用豆包AI功能，需要先登录豆包AI账号")