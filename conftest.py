import pytest
import os
import shutil
import glob
from datetime import datetime

def pytest_addoption(parser):
    parser.addoption("--title", type=str, 
                     default='autogpt，一款可持续运行并自主执行任务的智能代理平台，帮助用户高效自动化各类工作流程',
                     help='文章标题')
    parser.addoption("--author", type=str, default='tornadoami', help='作者名称')
    parser.addoption("--summary", type=str, 
                     default='本文介绍 AutoGPT，一款可自主执行任务的智能代理平台，含无缝集成等核心功能，附官网与 GitHub 地址。还详解安装：需先装 docker 等工具，Linux 用脚本安装及解决克隆、镜像拉取失败办法',
                     help='文章摘要')
    parser.addoption("--url", type=str, 
                     default='https://alidocs.dingtalk.com/i/nodes/X6GRezwJlAMg6vMGskpZPGvD8dqbropQ?utm_scene=team_space',
                     help='原文链接')
    parser.addoption("--markdown-file", type=str, 
                     default='/home/ubuntu/autogpt，一款可持续运行并自主执行任务的智能代理平台，帮助用户高效自动化各类工作流程.md',
                     help='Markdown文件路径')
    parser.addoption("--user-data-dir", type=str, 
                     default='D:/tornadofiles/scripts_脚本/github_projects/playwright-automation/chromium-browser-data',
                     help='浏览器用户数据目录')
    parser.addoption("--platforms", type=str, 
                     default='all',
                     help='指定要发布到的平台，用逗号分隔，如：wechat,zhihu,csdn,51cto,cnblogs 或 all 表示所有平台')
    parser.addoption("--cover-image", type=str, 
                     default='cover.jpg',
                     help='文章封面图片路径')
    # 新增话题标签参数
    parser.addoption("--tags", type=str, 
                     default='AI,人工智能,大模型,LLM,机器学习,深度学习,开源,技术分享,自动化,ollama',
                     help='话题标签，用逗号分隔，如：AI,人工智能,大模型,LLM')

def cleanup_old_backups(max_backups=3):
    """清理旧的备份目录，只保留最近的指定数量的备份"""
    backup_pattern = "chromium-browser-data_backup_*"
    backup_dirs = glob.glob(backup_pattern)
    
    if len(backup_dirs) <= max_backups:
        print(f"📁 当前备份数量: {len(backup_dirs)}，无需清理")
        return
    
    # 按修改时间排序，最新的在前面
    backup_dirs.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    
    # 删除超出数量限制的旧备份
    dirs_to_delete = backup_dirs[max_backups:]
    
    for backup_dir in dirs_to_delete:
        try:
            shutil.rmtree(backup_dir)
            print(f"🗑️  已删除旧备份: {backup_dir}")
        except Exception as e:
            print(f"❌ 删除备份失败 {backup_dir}: {e}")
    
    print(f"✅ 备份清理完成，保留最近 {max_backups} 个备份")

def backup_browser_data():
    """备份chromium-browser-data目录"""
    source_dir = "chromium-browser-data"
    if os.path.exists(source_dir):
        # 先清理旧备份
        cleanup_old_backups(max_backups=3)
        
        # 创建带时间戳的备份目录名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = f"chromium-browser-data_backup_{timestamp}"
        
        try:
            # 复制目录
            shutil.copytree(source_dir, backup_dir)
            print(f"✅ 浏览器数据目录备份成功: {backup_dir}")
            
            # 备份完成后再次清理，确保不超过限制
            cleanup_old_backups(max_backups=3)
            
            return backup_dir
        except Exception as e:
            print(f"❌ 浏览器数据目录备份失败: {e}")
            return None
    else:
        print("⚠️  chromium-browser-data 目录不存在，跳过备份")
        return None

@pytest.fixture(scope="session", autouse=True)
def backup_browser_data_fixture():
    """自动执行的备份fixture"""
    print("🔄 开始备份浏览器数据目录...")
    backup_path = backup_browser_data()
    yield backup_path
    print(f"📦 浏览器数据备份完成: {backup_path}")

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, playwright):
    return {
        "geolocation": {"latitude": 22.558033372050147, "longitude": 113.46251764183725}, 
        "locale": "zh-CN", 
        "permissions": ["geolocation"], 
        "timezone_id": "Asia/Shanghai", 
        "viewport": {"width": 1920, "height": 1080}
    }
