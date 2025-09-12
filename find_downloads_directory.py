# -*- coding: utf-8 -*-
"""
Windows系统下载目录查找脚本
查找Windows系统中"下载"目录的实际路径
"""

import os
import winreg
import ctypes
from pathlib import Path

def get_downloads_directory():
    """
    获取Windows系统中下载目录的实际路径
    返回多个可能的路径列表
    """
    download_paths = []
    
    print("=" * 60)
    print("Windows系统下载目录查找工具")
    print("=" * 60)
    
    # 方法1: 使用环境变量
    print("1️⃣ 检查环境变量...")
    if 'USERPROFILE' in os.environ:
        default_downloads = os.path.join(os.environ['USERPROFILE'], 'Downloads')
        download_paths.append(('环境变量 USERPROFILE', default_downloads))
        print(f"   USERPROFILE: {default_downloads}")
    
    if 'HOMEDRIVE' in os.environ and 'HOMEPATH' in os.environ:
        home_downloads = os.path.join(os.environ['HOMEDRIVE'], os.environ['HOMEPATH'], 'Downloads')
        download_paths.append(('环境变量 HOMEDRIVE+HOMEPATH', home_downloads))
        print(f"   HOMEDRIVE+HOMEPATH: {home_downloads}")
    
    # 方法2: 使用Python的os.path.expanduser
    print("\n2️⃣ 使用Python os.path.expanduser...")
    expanduser_downloads = os.path.join(os.path.expanduser("~"), "Downloads")
    download_paths.append(('os.path.expanduser', expanduser_downloads))
    print(f"   expanduser: {expanduser_downloads}")
    
    # 方法3: 使用Windows注册表
    print("\n3️⃣ 检查Windows注册表...")
    try:
        # 检查用户配置文件路径
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders") as key:
            try:
                downloads_reg = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
                # 展开环境变量
                downloads_reg_expanded = os.path.expandvars(downloads_reg)
                download_paths.append(('注册表 Downloads', downloads_reg_expanded))
                print(f"   注册表 Downloads: {downloads_reg_expanded}")
            except FileNotFoundError:
                print("   注册表中未找到Downloads项")
    except Exception as e:
        print(f"   注册表访问失败: {e}")
    
    # 方法4: 使用Windows API
    print("\n4️⃣ 使用Windows API...")
    try:
        # 使用ctypes调用Windows API
        CSIDL_PERSONAL = 0x0005  # My Documents
        CSIDL_PROFILE = 0x0028   # User profile
        
        # 获取用户文档目录
        buf = ctypes.create_unicode_buffer(ctypes.wintypes.MAX_PATH)
        if ctypes.windll.shell32.SHGetFolderPathW(None, CSIDL_PERSONAL, None, 0, buf):
            documents_path = buf.value
            api_downloads = os.path.join(os.path.dirname(documents_path), "Downloads")
            download_paths.append(('Windows API', api_downloads))
            print(f"   Windows API: {api_downloads}")
    except Exception as e:
        print(f"   Windows API调用失败: {e}")
    
    # 方法5: 使用pathlib
    print("\n5️⃣ 使用pathlib...")
    try:
        home = Path.home()
        pathlib_downloads = home / "Downloads"
        download_paths.append(('pathlib', str(pathlib_downloads)))
        print(f"   pathlib: {pathlib_downloads}")
    except Exception as e:
        print(f"   pathlib失败: {e}")
    
    # 方法6: 检查常见的重定向位置
    print("\n6️⃣ 检查常见的重定向位置...")
    common_paths = [
        "D:\\Downloads",
        "D:\\Users\\Downloads", 
        "E:\\Downloads",
        "F:\\Downloads",
        "C:\\Users\\Public\\Downloads",
    ]
    
    # 添加当前用户名到D盘路径
    if 'USERNAME' in os.environ:
        username = os.environ['USERNAME']
        common_paths.extend([
            f"D:\\Users\\{username}\\Downloads",
            f"E:\\Users\\{username}\\Downloads",
            f"F:\\Users\\{username}\\Downloads",
        ])
    
    for path in common_paths:
        if os.path.exists(path):
            download_paths.append(('常见重定向位置', path))
            print(f"   发现: {path}")
    
    # 验证所有路径
    print("\n" + "=" * 60)
    print("路径验证结果:")
    print("=" * 60)
    
    valid_paths = []
    for method, path in download_paths:
        if os.path.exists(path):
            # 检查是否是目录
            if os.path.isdir(path):
                # 检查是否有写权限
                try:
                    test_file = os.path.join(path, "test_write_permission.tmp")
                    with open(test_file, 'w') as f:
                        f.write("test")
                    os.remove(test_file)
                    status = "✅ 存在且可写"
                    valid_paths.append((method, path))
                except Exception as e:
                    status = f"⚠️  存在但无写权限: {e}"
            else:
                status = "❌ 存在但不是目录"
        else:
            status = "❌ 不存在"
        
        print(f"{method:20} | {path}")
        print(f"{'':20} | {status}")
        print()
    
    # 推荐最佳路径
    print("=" * 60)
    print("推荐使用:")
    print("=" * 60)
    
    if valid_paths:
        # 优先选择注册表路径
        registry_path = None
        for method, path in valid_paths:
            if method == '注册表 Downloads':
                registry_path = path
                break
        
        if registry_path:
            print(f"🎯 最佳选择 (注册表): {registry_path}")
        else:
            print(f"🎯 最佳选择: {valid_paths[0][1]}")
        
        print(f"\n📝 在代码中使用:")
        print(f"downloads_dir = r\"{valid_paths[0][1]}\"")
    else:
        print("❌ 未找到有效的下载目录")
        print("建议手动检查下载目录位置")
    
    return valid_paths

def main():
    """主函数"""
    try:
        valid_paths = get_downloads_directory()
        
        if valid_paths:
            print(f"\n✅ 找到 {len(valid_paths)} 个有效的下载目录")
        else:
            print("\n❌ 未找到任何有效的下载目录")
            
    except Exception as e:
        print(f"\n❌ 程序执行出错: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
