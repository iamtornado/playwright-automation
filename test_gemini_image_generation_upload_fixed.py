# -*- coding: utf-8 -*-
"""
Gemini图片生成测试脚本 - 完全参照录制脚本
"""

import os
from playwright.sync_api import sync_playwright

# 查找系统下载目录中的最新图片文件
import shutil
import glob

# 获取系统下载目录 - 使用注册表获取真实路径
def get_downloads_directory():
    """获取Windows系统中下载目录的实际路径"""
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
            downloads_reg = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
            # 展开环境变量
            downloads_reg_expanded = os.path.expandvars(downloads_reg)
            return downloads_reg_expanded
    except Exception:
        # 如果注册表方法失败，使用默认方法
        return os.path.join(os.path.expanduser("~"), "Downloads")

downloads_folder = get_downloads_directory()
print(f"系统下载目录: {downloads_folder}")

def test_gemini_image_generation():
    """
    测试Gemini图片生成功能 - 完全参照录制脚本
    """
    print("=" * 80)
    print("Gemini图片生成测试脚本 - 完全参照录制脚本")
    print("=" * 80)
    
    # 配置参数 - 与录制脚本完全一致
    debug_port = "9222"
    #无论downloads_dir如何设置，其实Chrome的下载目录都是浏览器本身设置的下载目录
    generated_images_dir = os.path.join(os.getcwd(), "generated_images")
    print(f"代码库中generated_images目录的绝对路径: {generated_images_dir}")
    downloads_dir = downloads_folder
    os.makedirs(downloads_dir, exist_ok=True)
    print(f"当前操作系统的实际下载目录: {downloads_dir}")
    
    # markdown文件路径
    markdown_file = os.getenv("MARKDOWN_FILE_PATH")
    # markdown_file = "D:/Users/14266/Downloads/远程批量加域（wsman协议和传统的协议RPC）.md"

    # 图片生成提示词
    prompt_text = "根据我提供的markdown文件，请生成合适的文章封面。图片的比例为16:9"
    
    print(f"连接到Chrome实例 (端口: {debug_port})")
    print(f"下载目录: {downloads_dir}")
    print()
    
    try:
        with sync_playwright() as playwright:
            # 连接到已运行的Chrome实例 - 与录制脚本完全一致
            browser = playwright.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
            
            print("成功连接到Chrome实例")
            print(f"发现 {len(browser.contexts)} 个浏览器上下文")
            
            # 使用现有的上下文，而不是创建新的 - 与录制脚本完全一致
            if browser.contexts:
                context = browser.contexts[0]  # 使用第一个现有上下文
                print("使用现有的浏览器上下文")
            else:
                print("没有找到现有上下文，这可能意味着Chrome没有打开任何标签页")
                print("请在Chrome中打开至少一个标签页，然后重新运行脚本")
                return
            
            print(f"发现 {len(context.pages)} 个标签页")
            
            # 使用现有的页面，或者创建新页面（但在同一个上下文中） - 与录制脚本完全一致
            if context.pages:
                # 使用最后一个活跃的页面
                page = context.pages[-1]
                print(f"使用现有标签页: {page.url}")
            else:
                # 在现有上下文中创建新页面
                page = context.new_page()
                print("在现有上下文中创建新标签页")
            
            # 设置页面的下载路径到指定目录
            try:
                # 为页面设置下载行为，强制下载到指定目录
                page.set_extra_http_headers({})  # 确保页面已初始化
                
                # 使用CDP命令设置下载路径
                client = page.context.new_cdp_session(page)
                client.send('Page.setDownloadBehavior', {
                    'behavior': 'allow',
                    'downloadPath': downloads_dir
                })
                print(f"✅ 已设置下载路径到: {downloads_dir}")
                
            except Exception as e:
                print(f"⚠️  设置下载路径失败: {e}")
                print("将使用默认下载处理方式")
            
            # 注意：由于使用CDP连接外部Chrome实例，下载事件监听可能不会正常工作
            # 因此采用等待下载完成后从系统下载目录查找文件的方式
            
            print()
            print("开始执行Gemini图片生成流程...")
            print("-" * 60)
            
            try:
                # 1. 点击工具按钮，注意gemini网页改版后，不需要点击工具按钮了
                # print("1. 点击工具按钮...")
                # page.locator("button.toolbox-drawer-button").click()
                # page.wait_for_timeout(1000)
                
                # 2. 选择Imagen生成图片
                print("2. 选择Imagen生成图片...")
                # 检查按钮是否已经被点击过了（通过检查按钮状态或页面元素变化）
                try:
                    image_button = page.get_by_role("button", name="🍌 图片")
                    if image_button.count() > 0:
                        # 检查按钮是否已经处于激活状态
                        button_classes = image_button.get_attribute("class") or ""
                        if "active" not in button_classes.lower() and "selected" not in button_classes.lower():
                            print("图片按钮未激活，正在点击...")
                            image_button.click()
                            page.wait_for_timeout(2000)
                        else:
                            print("图片按钮已经激活，跳过点击")
                    else:
                        print("未找到图片按钮")
                except Exception as e:
                    print(f"检查图片按钮状态失败: {e}")
                    # 如果检查失败，尝试直接点击
                    try:
                        page.get_by_role("button", name="🍌 图片").click()
                        page.wait_for_timeout(2000)
                    except Exception as e2:
                        print(f"点击图片按钮失败: {e2}")
                
                # 3. 打开文件上传菜单
                print("3. 打开文件上传菜单...")
                page.get_by_role("button", name="打开文件上传菜单").click()
                page.wait_for_timeout(1000)
                # 4. 点击文件上传按钮
                print("4. 选择文件上传...")
                # page.locator("[data-test-id=\"local-image-file-uploader-button\"]").click()
                # page.wait_for_timeout(1000)
                with page.expect_file_chooser() as fc_info:
                    page.locator("[data-test-id=\"local-image-file-uploader-button\"]").click()
                file_chooser = fc_info.value
                file_chooser.set_files(markdown_file)
                
                print("6. 输入图片生成提示...")
                
                # 输入图片生成提示
                try:
                    textbox = page.get_by_role("textbox", name="在此处输入提示")
                    if textbox.count() > 0:
                        print("找到提示输入框")
                        # textbox.click()
                        # textbox.set_input_files(markdown_file)
                        page.wait_for_timeout(500)
                        textbox.fill("")
                        page.wait_for_timeout(200)
                        textbox.fill(prompt_text)
                        print("提示词输入成功")
                    else:
                        print("使用键盘输入方式...")
                        page.keyboard.type(prompt_text)
                        print("键盘输入成功")
                        
                except Exception as e:
                    print(f"提示词输入失败: {e}")
                
                page.wait_for_timeout(1000)
                page.wait_for_load_state("networkidle")
                
                # 发送请求
                print("7. 发送图片生成请求...")
                try:
                    send_button = page.get_by_role("button", name="发送")
                    if send_button.count() > 0:
                        send_button.click()
                        print("已点击发送按钮")
                    else:
                        page.keyboard.press("Enter")
                        print("已按回车键发送")
                except Exception as e:
                    print(f"发送失败，尝试回车: {e}")
                    page.keyboard.press("Enter")
                
                # 8. 等待图片生成完成
                print("8. 等待图片生成完成...")
                print("这可能需要几十秒时间，请耐心等待...")

                # 等待图片下载按钮出现
                try:
                    print("等待图片下载按钮出现，等待时间120秒...")
                    page.wait_for_selector("[data-test-id=\"download-generated-image-button\"]", timeout=120000)
                    print("图片生成完成，下载按钮已出现")
                except Exception:
                    try:
                        print("等待超时，仍然没有出现下载图片的按钮，尝试再次发送提示词生成图片")
                        textbox.fill(prompt_text)
                        print("再次提示词输入成功")
                        print("再次点击发送按钮")
                        send_button.click()
                        print("已点击发送按钮")
                        print("再次等待图片下载按钮出现，等待时间120秒...")
                        page.wait_for_selector("[data-test-id=\"download-generated-image-button\"]", timeout=120000)
                        print("图片生成完成，下载按钮已出现")
                    except Exception:
                        print("再次等待超时，仍然没有出现下载图片的按钮，请尝试再次发送提示词生成图片")
                        # 暂停程序，等待用户手动操作
                        print("\n程序暂停，等待用户手动操作...")
                        page.pause()

                # 下载生成的图片
                print("9. 下载生成的图片...")

                try:
                    # 确保下载按钮存在且可见
                    download_button = page.locator("[data-test-id=\"download-generated-image-button\"]")
                    
                    # 等待按钮出现并可见
                    download_button.wait_for(state="visible", timeout=30000)
                    print("下载按钮已可见")
                    
                    # 滚动到按钮位置，确保完全可见
                    download_button.scroll_into_view_if_needed()
                    page.wait_for_timeout(1000)
                    
                    # 等待页面稳定
                    page.wait_for_load_state("networkidle")
                    page.wait_for_timeout(2000)
                    
                    # 点击下载按钮（不使用expect_download，因为CDP连接可能不支持）
                    print("点击下载按钮...")
                    download_button.click()
                    print("已点击下载按钮")
                    
                    # 等待下载完成 - 使用固定等待时间
                    print("等待30秒，使得下载完成...")
                    page.wait_for_timeout(30000)  # 等待30秒让下载完成
                    

                    
                    # 查找最新的图片文件
                    image_extensions = ['*.png', '*.jpg', '*.jpeg', '*.gif', '*.webp']
                    latest_image = None
                    latest_time = 0
                    
                    # 遍历所有支持的图片文件扩展名
                    for ext in image_extensions:
                        # 构建搜索模式，在下载目录中查找指定扩展名的文件
                        pattern = os.path.join(downloads_folder, ext)
                        # 使用glob模块查找匹配模式的所有文件
                        for file_path in glob.glob(pattern):
                            # 获取文件的创建时间
                            file_time = os.path.getctime(file_path)
                            # 如果当前文件比之前找到的文件更新，则更新最新文件记录
                            if file_time > latest_time:
                                latest_time = file_time
                                latest_image = file_path
                    
                    if latest_image and os.path.exists(latest_image) and os.path.getsize(latest_image) > 0:
                        print(f"✅ 找到最新下载的图片: {latest_image}")
                        print(f"文件大小: {os.path.getsize(latest_image)} 字节")
                        
                        # 直接复制文件到目标目录，保持原始文件名
                        target_path = os.path.join(generated_images_dir, os.path.basename(latest_image))

                        shutil.copy2(latest_image, target_path)
                        print(f"✅ 文件已复制到: {target_path}")
                        print(f"最终文件大小: {os.path.getsize(target_path)} 字节")
                    else:
                        print("⚠️  未在系统下载目录中找到有效图片文件")
                        
                        # 如果系统下载目录中没有文件，检查目标目录中是否有新文件
                        print("检查目标目录中是否有新下载的文件...")
                        if os.path.exists(downloads_dir):
                            image_files = [f for f in os.listdir(downloads_dir) 
                                         if f.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp'))]
                            if image_files:
                                # 找到最新的文件
                                latest_file = None
                                latest_time = 0
                                for img_file in image_files:
                                    full_path = os.path.join(downloads_dir, img_file)
                                    file_time = os.path.getctime(full_path)
                                    if file_time > latest_time:
                                        latest_time = file_time
                                        latest_file = full_path
                                
                                if latest_file and os.path.getsize(latest_file) > 0:
                                    print(f"✅ 目标目录中发现有效图片文件: {latest_file}")
                                    print(f"文件大小: {os.path.getsize(latest_file)} 字节")
                                else:
                                    print("⚠️  目标目录中的图片文件为空或无效")

                    # 验证最终结果
                    print("验证下载结果...")
                    if 'target_path' in locals() and os.path.exists(target_path) and os.path.getsize(target_path) > 0:
                        print("✅ 图片下载成功！")
                        print(f"文件路径: {target_path}")
                        print(f"文件大小: {os.path.getsize(target_path)} 字节")
                    elif 'latest_file' in locals() and latest_file and os.path.exists(latest_file) and os.path.getsize(latest_file) > 0:
                        print("✅ 图片下载成功！")
                        print(f"文件路径: {latest_file}")
                        print(f"文件大小: {os.path.getsize(latest_file)} 字节")
                    else:
                        print("❌ 图片下载失败或文件为空")
                        if 'target_path' in locals():
                            print(f"目标路径: {target_path}")
                            if os.path.exists(target_path):
                                print(f"文件存在但大小为: {os.path.getsize(target_path)} 字节")
                            else:
                                print("文件不存在")
                        
                except Exception as e:
                    print(f"下载过程出错: {e}")
                    import traceback
                    traceback.print_exc()
                
                print("-" * 60)
                print("Gemini图片生成流程完成！")
                print(f"下载的文件保存在: {generated_images_dir}")
                print("提示：生成的代码可以直接用于自动化测试")
                
            except Exception as e:
                print(f"执行过程中出错: {e}")
                
            # 注意：不要关闭browser，因为那是外部的Chrome实例 - 与录制脚本完全一致
                
    except ConnectionRefusedError:
        print("连接失败：无法连接到Chrome实例")
        
    except Exception as e:
        print(f"发生错误: {e}")

def main():
    """主函数"""
    test_gemini_image_generation()

if __name__ == "__main__":
    test_gemini_image_generation()