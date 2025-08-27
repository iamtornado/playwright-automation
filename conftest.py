import pytest

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
