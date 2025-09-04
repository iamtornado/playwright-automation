"""
Gemini图片生成测试脚本 - 修复文件上传问题
"""

import pytest
import sys
import os
import time
from datetime import datetime
from playwright.sync_api import sync_playwright, expect

def test_gemini_image_generation():
    """
    测试Gemini图片生成功能 - 修复文件上传
    """
    print("=" * 80)
    print("Gemini图片生成测试脚本 - 修复文件上传问题")
    print("=" * 80)
    
    # 配置参数
    debug_port = "9222"
    downloads_dir = os.path.join(os.getcwd(), "generated_images")
    os.makedirs(downloads_dir, exist_ok=True)
    
    # 测试文件路径
    markdown_file = "D:/Users/14266/Downloads/远程批量加域（wsman协议和传统的协议RPC）.md"
    
    # 图片生成提示词
    prompt_text = "根据我提供的markdown文件，请生成合适的文章封面。图片的比例为16:9"
    
    print(f"🔗 连接到Chrome实例 (端口: {debug_port})")
    print(f"📁 图片保存目录: {downloads_dir}")
    print(f"📄 使用的Markdown文件: {markdown_file}")
    print(f"💭 图片生成提示: {prompt_text}")
    print()
    
    try:
        with sync_playwright() as playwright:
            # 连接到现有Chrome实例
            browser = playwright.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
            
            print(f"✅ 成功连接到Chrome实例")
            
            if not browser.contexts:
                print("❌ 没有找到浏览器上下文，请确保Chrome中打开了Gemini页面")
                return
            
            context = browser.contexts[0]
            pages = context.pages
            
            if not pages:
                print("❌ 没有找到标签页，请在Chrome中打开Gemini页面")
                return
            
            # 使用当前活跃页面
            page = pages[-1]
            print(f"📖 使用标签页: {page.title()}")
            print(f"🌐 当前URL: {page.url}")
            
            # 设置下载事件监听
            downloaded_files = []
            
            def handle_download(download):
                """处理下载事件"""
                try:
                    original_filename = download.suggested_filename
                    print(f"📥 检测到图片下载: {original_filename}")
                    
                    if original_filename:
                        name_part, ext_part = os.path.splitext(original_filename)
                    else:
                        name_part = "gemini_generated_image"
                        ext_part = ".png"
                    
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename_with_timestamp = f"{name_part}_{timestamp}{ext_part}"
                    file_path = os.path.join(downloads_dir, filename_with_timestamp)
                    
                    download.save_as(file_path)
                    downloaded_files.append(file_path)
                    
                    print(f"✅ 图片已保存到: {file_path}")
                    
                except Exception as e:
                    print(f"❌ 下载处理失败: {e}")
            
            page.on("download", handle_download)
            
            print()
            print("🎨 开始执行Gemini图片生成流程...")
            print("-" * 60)
            
            try:
                # 1. 点击工具按钮
                print("1️⃣ 点击工具按钮...")
                page.get_by_role("button", name="工具").click()
                page.wait_for_timeout(1000)
                
                # 2. 选择Imagen生成图片
                print("2️⃣ 选择Imagen生成图片...")
                page.get_by_role("button", name="使用 Imagen 生成图片").click()
                page.wait_for_timeout(2000)
                
                # 3. 打开文件上传菜单
                print("3️⃣ 打开文件上传菜单...")
                page.get_by_role("button", name="打开文件上传菜单").click()
                page.wait_for_timeout(1000)
                
                # # 4. 点击文件上传按钮
                # print("4️⃣ 选择文件上传...")
                # page.locator("[data-test-id=\"local-image-file-uploader-button\"]").click()
                # page.wait_for_timeout(1000)
                with page.expect_file_chooser() as fc_info:
                    page.locator("[data-test-id=\"local-image-file-uploader-button\"]").click()
            
                file_chooser = fc_info.value
                file_chooser.set_files(markdown_file)
                # # 5. 文件上传 - 关键修复：使用正确的方法
                # print(f"5️⃣ 上传Markdown文件...")
                # if os.path.exists(markdown_file):
                #     upload_success = False
                    
                    # # 方法1：直接对隐藏的input设置文件（强制方式 + UI状态处理）
                    # try:
                    #     print("   📂 方法1：直接设置隐藏的文件输入框...")
                    #     
                    #     # 找到隐藏的文件输入框并强制设置文件
                    #     file_input = page.locator("input[type='file'][name='Filedata']")
                    #     if file_input.count() > 0:
                    #         # 使用JavaScript强制设置文件
                    #         file_input.set_input_files(markdown_file)
                    #         page.wait_for_timeout(2000)
                    #         print("   ✅ 方法1成功：直接设置文件输入框")
                    #         
                    #         # 关键修复：处理文件选择器窗口关闭
                    #         print("   🔄 处理文件选择器窗口状态...")
                    #         
                    #         # 方法1a：按ESC键关闭文件选择器
                    #         try:
                    #             page.keyboard.press("Escape")
                    #             page.wait_for_timeout(500)
                    #             print("   ✅ 已按ESC键关闭文件选择器")
                    #         except:
                    #             pass
                    #         
                    #         # 方法1b：点击页面其他区域
                    #         try:
                    #             # 点击页面空白区域，确保焦点离开文件选择器
                    #             page.click("body", position={"x": 400, "y": 200})
                    #             page.wait_for_timeout(500)
                    #             print("   ✅ 已点击页面空白区域")
                    #         except:
                    #             pass
                    #         
                    #         # 方法1c：使用JavaScript关闭可能的模态对话框
                    #         try:
                    #             close_dialog_js = """
                    #             // 尝试关闭可能的模态对话框
                    #             const dialogs = document.querySelectorAll('[role="dialog"], .dialog, .modal, .overlay');
                    #             dialogs.forEach(dialog => {
                    #                 if (dialog.style.display !== 'none') {
                    #                     dialog.style.display = 'none';
                    #                 }
                    #             });
                    #             
                    #             // 尝试点击关闭按钮
                    #             const closeButtons = document.querySelectorAll('[aria-label*="关闭"], [aria-label*="Close"], .close-button, [data-test-id*="close"]');
                    #             closeButtons.forEach(btn => {
                    #                 if (btn.offsetParent !== null) { // 如果元素可见
                    #                     btn.click();
                    #                 }
                    #             });
                    #             
                    #             // 移除可能的遮罩层
                    #             const overlays = document.querySelectorAll('.overlay, .backdrop, .mask');
                    #             overlays.forEach(overlay => {
                    #                 if (overlay.style.display !== 'none') {
                    #                     overlay.style.display = 'none';
                    #                 }
                    #             });
                    #             
                    #             return true;
                    #             """
                    #             
                    #             page.evaluate(close_dialog_js)
                    #             page.wait_for_timeout(500)
                    #             print("   ✅ 已执行JavaScript关闭对话框")
                    #         except:
                    #             pass
                    #         
                    #         # 方法1d：查找并点击具体的关闭按钮
                    #         try:
                    #             close_button_selectors = [
                    #                 "[aria-label='关闭']",
                    #                 "[aria-label='Close']",
                    #                 "button:has-text('关闭')",
                    #                 "button:has-text('Close')",
                    #                 "button:has-text('×')",
                    #                 ".close-button",
                    #                 "[data-test-id*='close']",
                    #                 ".modal-close",
                    #                 ".dialog-close"
                    #             ]
                    #             
                    #             for selector in close_button_selectors:
                    #                 try:
                    #                     close_btn = page.locator(selector)
                    #                     if close_btn.count() > 0 and close_btn.first.is_visible():
                    #                         close_btn.first.click()
                    #                         page.wait_for_timeout(300)
                    #                         print(f"   ✅ 已点击关闭按钮: {selector}")
                    #                         break
                    #                 except:
                    #                     continue
                    #                     
                    #         except:
                    #             pass
                    #         
                    #         # 方法1e：等待文件上传完成的指示并处理UI状态
                    #         try:
                    #             print("   ⏳ 等待文件处理完成...")
                    #             
                    #             # 等待文件名出现或其他上传完成的标志
                    #             try:
                    #                 page.wait_for_selector("text=远程批量加域", timeout=8000)
                    #                 print("   ✅ 检测到文件名显示，上传完成")
                    #             except:
                    #                 # 如果没有检测到文件名，尝试检测其他上传完成的标志
                    #                 try:
                    #                     # 检查是否有"上传成功"或类似的提示
                    #                     success_indicators = [
                    #                         "text=上传成功",
                    #                         "text=Upload successful",
                    #                         "text=文件已上传",
                    #                         "[data-test-id*='upload-success']",
                    #                         ".upload-success"
                    #                     ]
                    #                     
                    #                     for indicator in success_indicators:
                    #                         try:
                    #                             page.wait_for_selector(indicator, timeout=2000)
                    #                             print(f"   ✅ 检测到上传成功标志: {indicator}")
                    #                             break
                    #                         except:
                    #                             continue
                    #                     else:
                    #                         print("   ℹ️  未检测到明确的上传完成标志，但继续执行...")
                    #                 except:
                    #                     print("   ℹ️  文件处理状态未知，但继续执行...")
                    #             
                    #             # 最后再次尝试关闭任何残留的对话框
                    #             page.keyboard.press("Escape")
                    #             page.wait_for_timeout(500)
                    #             
                    #         except:
                    #             pass
                    #         
                    #         upload_success = True
                    #     else:
                    #         print("   ❌ 方法1失败：未找到文件输入框")
                    #         
                    # except Exception as e:
                    #     print(f"   ❌ 方法1失败: {e}")
                    
                    # # 方法2：使用文件选择器（通过可见按钮触发）
                    # if not upload_success:
                    #     try:
                    #         print("   📂 方法2：通过可见按钮触发文件选择器...")
                    #         
                    #         # 尝试不同的可见按钮来触发文件选择器
                    #         trigger_buttons = [
                    #             "[data-test-id=\"local-image-file-uploader-button\"]",
                    #             "[data-test-id=\"uploader-images-files-button-advanced\"] button",
                    #             "button:has-text('选择文件')",
                    #             "button:has-text('上传文件')",
                    #             "button:has-text('Browse')",
                    #             "button:has-text('Choose')",
                    #             ".file-upload-button",
                    #             ".upload-button"
                    #         ]
                    #         
                    #         for button_selector in trigger_buttons:
                    #             try:
                    #                 print(f"     🎯 尝试按钮: {button_selector}")
                    #                 button = page.locator(button_selector)
                    #                 
                    #                 if button.count() > 0 and button.first.is_visible():
                    #                     print(f"     ✅ 找到可见按钮: {button_selector}")
                    #                     
                    #                     # 使用文件选择器
                    #                     with page.expect_file_chooser(timeout=10000) as fc_info:
                    #                         button.first.click()
                    #                     
                    #                     file_chooser = fc_info.value
                    #                     file_chooser.set_files(markdown_file)
                    #                     
                    #                     print("   ✅ 方法2成功：文件选择器上传")
                    #                     upload_success = True
                    #                     break
                    #                     
                    #             except Exception as e:
                    #                 print(f"     ❌ 按钮 {button_selector} 失败: {e}")
                    #                 continue
                    #                 
                    #     except Exception as e:
                    #         print(f"   ❌ 方法2失败: {e}")
                    
                    # 方法3：使用拖拽方式（如果支持）
                    # if not upload_success:
                    #     try:
                    #         print("   📂 方法3：尝试拖拽上传...")
                            
                    #         # 查找拖拽区域
                    #         drop_zones = [
                    #             ".upload-drop-zone",
                    #             ".file-drop-zone",
                    #             "[data-filedrop-id]",
                    #             ".drag-drop-area"
                    #         ]
                            
                    #         for zone_selector in drop_zones:
                    #             try:
                    #                 drop_zone = page.locator(zone_selector)
                    #                 if drop_zone.count() > 0:
                    #                     print(f"     🎯 找到拖拽区域: {zone_selector}")
                                        
                    #                     # 模拟拖拽文件
                    #                     drop_zone.first.set_input_files(markdown_file)
                    #                     print("   ✅ 方法3成功：拖拽上传")
                    #                     upload_success = True
                    #                     break
                                        
                    #             except Exception as e:
                    #                 print(f"     ❌ 拖拽区域 {zone_selector} 失败: {e}")
                    #                 continue
                                    
                    #     except Exception as e:
                    #         print(f"   ❌ 方法3失败: {e}")
                    
                    # # 方法4：JavaScript直接操作（最后的手段）
                    # if not upload_success:
                    #     try:
                    #         print("   📂 方法4：JavaScript直接操作...")
                    #         
                    #         # 使用JavaScript直接操作文件输入
                    #         js_code = f"""
                    #         const fileInput = document.querySelector('input[type="file"][name="Filedata"]');
                    #         if (fileInput) {{
                    #             // 创建一个File对象
                    #             const file = new File(['file content'], '{os.path.basename(markdown_file)}', {{
                    #                 type: 'text/markdown'
                    #             }});
                    #             
                    #             // 创建FileList
                    #             const dt = new DataTransfer();
                    #             dt.items.add(file);
                    #             fileInput.files = dt.files;
                    #             
                    #             // 触发change事件
                    #             const event = new Event('change', {{ bubbles: true }});
                    #             fileInput.dispatchEvent(event);
                    #             
                    #             return true;
                    #         }}
                    #         return false;
                    #         """
                    #         
                    #         result = page.evaluate(js_code)
                    #         if result:
                    #             print("   ✅ 方法4成功：JavaScript操作")
                    #             upload_success = True
                    #         else:
                    #             print("   ❌ 方法4失败：JavaScript操作失败")
                    #             
                    #     except Exception as e:
                    #         print(f"   ❌ 方法4失败: {e}")
                    
                    # 检查上传结果
                #     if upload_success:
                #         print("✅ 文件上传成功")
                        
                #         # 等待文件处理完成
                #         print("   🔄 等待文件处理完成...")
                #         page.wait_for_timeout(5000)
                        
                #         # 检查是否有文件处理完成的指示
                #         try:
                #             # 等待文件名出现
                #             page.wait_for_selector("text=远程批量加域", timeout=10000)
                #             print("   ✅ 检测到文件名显示，处理完成")
                #         except:
                #             print("   ℹ️  未检测到文件名，但继续执行...")
                            
                #     else:
                #         print("❌ 所有上传方法都失败了")
                #         print("请手动上传文件，然后按回车继续...")
                #         input("按回车键继续...")
                        
                # else:
                #     print(f"❌ 文件不存在: {markdown_file}")
                #     return
                
                # 6. 输入提示词
                print("6️⃣ 输入图片生成提示...")
                
                try:
                    textbox = page.get_by_role("textbox", name="在此处输入提示")
                    if textbox.count() > 0:
                        print("   🎯 找到提示输入框")
                        # textbox.click()
                        # textbox.set_input_files(markdown_file)
                        page.wait_for_timeout(500)
                        textbox.fill("")
                        page.wait_for_timeout(200)
                        textbox.fill(prompt_text)
                        print("   ✅ 提示词输入成功")
                    else:
                        print("   🔍 使用键盘输入方式...")
                        page.keyboard.type(prompt_text)
                        print("   ✅ 键盘输入成功")
                        
                except Exception as e:
                    print(f"   ❌ 提示词输入失败: {e}")
                
                page.wait_for_timeout(1000)
                page.wait_for_load_state("networkidle")
                # 7. 发送请求
                print("7️⃣ 发送图片生成请求...")
                try:
                    send_button = page.get_by_role("button", name="发送")
                    if send_button.count() > 0:
                        send_button.click()
                        print("✅ 已点击发送按钮")
                    else:
                        page.keyboard.press("Enter")
                        print("✅ 已按回车键发送")
                except Exception as e:
                    print(f"⚠️  发送失败，尝试回车: {e}")
                    page.keyboard.press("Enter")
                
                # 8. 等待图片生成完成
                print("8️⃣ 等待图片生成完成...")
                print("   ⏳ 这可能需要几十秒时间，请耐心等待...")
                
                try:
                    page.wait_for_selector("[data-test-id=\"download-generated-image-button\"]", timeout=120000)
                    print("✅ 图片生成完成，下载按钮已出现")
                except:
                    print("⚠️  等待超时，但继续尝试下载...")
                
                # 9. 下载生成的图片 - 简化处理
                print("9️⃣ 下载生成的图片...")
                
                try:
                    # 简单直接的下载方式
                    page.wait_for_timeout(5000)
                    page.wait_for_load_state("networkidle")
                    with page.expect_download(timeout=30000) as download_info:
                        page.locator("[data-test-id=\"download-generated-image-button\"]").click()
                    
                    download = download_info.value
                    print("✅ 下载开始")
                    page.wait_for_timeout(5000)
                    
                except Exception as e:
                    print(f"❌ 下载失败: {e}")
                    print("请手动点击下载按钮")
                
                print("-" * 60)
                print("🎉 Gemini图片生成流程完成！")
                
                # 显示下载结果
                print("\n📋 下载结果:")
                if downloaded_files:
                    for i, file_path in enumerate(downloaded_files, 1):
                        print(f"{i}. {os.path.basename(file_path)}")
                        print(f"   📁 路径: {file_path}")
                        if os.path.exists(file_path):
                            print(f"   📊 大小: {os.path.getsize(file_path)} 字节")
                            print(f"   ✅ 状态: 下载成功")
                        else:
                            print(f"   ❌ 状态: 文件不存在")
                        print()
                else:
                    print("⚠️  没有检测到下载文件，请检查downloads目录")
                
                print(f"📁 所有图片保存在: {downloads_dir}")
                
            except Exception as e:
                print(f"❌ 执行过程中出错: {e}")
                
    except ConnectionRefusedError:
        print("❌ 连接失败：无法连接到Chrome实例")
        
    except Exception as e:
        print(f"❌ 发生错误: {e}")

def main():
    """主函数"""
    test_gemini_image_generation()

if __name__ == "__main__":
    main()
