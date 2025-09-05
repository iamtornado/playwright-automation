# craXcel，一个可以移除Excel密码的开源工具

![craXcel，一个可以移除Excel密码的开源工具封面图.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/jP2lRYj1WWbd6O8g/img/ab4c2003-eee3-4cd1-8744-f495b2d74244.png)

# 阅读原文

建议阅读原文，始终查看最新文档版本，获得最佳阅读体验：[《craXcel，一个可以移除Excel密码的开源工具》](https://docs.dingtalk.com/i/nodes/GZLxjv9VGqAl6KAPs7naPKy686EDybno)

[https://docs.dingtalk.com/i/nodes/GZLxjv9VGqAl6KAPs7naPKy686EDybno?iframeQuery=utm\_source=portal&utm\_medium=portal\_recent](https://docs.dingtalk.com/i/nodes/GZLxjv9VGqAl6KAPs7naPKy686EDybno?iframeQuery=utm_source=portal&utm_medium=portal_recent)

# 声明

严禁非法使用！

# 官网（github网址）

[petemc89/craXcel: Command line application to unlock Microsoft Office password protected files.](https://github.com/petemc89/craXcel)

# 简介

Python command line application to unlock Microsoft Office password protected files.

Supported applications

As of V2.0:

Microsoft Excel (workbook, worksheet, vba)

.xlsx

.xlsm

Microsoft Word (modify, format, vba)

.docx

.docm

Microsoft Powerpoint (modify, vba)

.pptx

.pptm

Others may work, but have not been tested.

# 安装

根据实践，我发现Python的版本不能过高，可以确定的是Python 3.11是可以正常使用craXcel的

## ubuntu

### 安装Python 3.11

ubuntu server 24.04系统内置的Python版本是3.12

首先要安装Python 3.11，详情请看此文：[《Python》](https://docs.dingtalk.com/i/nodes/3NwLYZXWynR79aRKiv5Aal2RVkyEqBQm)

### 克隆仓库

```shell
git clone https://github.com/petemc89/craXcel.git
cd craXcel/
```

### 然后创建虚拟环境

有两种方法，

第一种方法：使用uv（推荐）

```shell
uv venv --python 3.11
source .venv/bin/activate
```

第二种方法：用Python的venv模块

```shell
python3.11 -m venv .venv311
source .venv311/bin/activate

pip install --upgrade pip
```

### 安装必备模块

```shell
用uv安装
uv pip install -r requirements.txt

#pip install -r requirements.txt
```

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/jP2lRYj1WWbd6O8g/img/346a8fec-48c9-4e6e-a9ce-99ef01bdec02.png)

# 移除Excel工作表或工作簿密码

```shell
uv run python craxcel.py /home/ubuntu/日常工作.xlsx
#或：
python3.11 craxcel.py /home/ubuntu/日常工作.xlsx
```

操作成功后，解密的Excel文件默认存放在unlocked目录中

![image.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/jP2lRYj1WWbd6O8g/img/28cb1e14-cd1e-40a5-bebb-16192a3049ff.png)

# 特别说明

根据实践，我发现Python的版本不能过高，可以确定的是Python 3.11是可以正常使用craXcel

Python 3.12和3.13是不行的，在安装必备模块时会报错。

craXcel不支持移除Excel文件本身的密码，例如如果文件被ipguard软件加密了，则没法通过craXcel进行解密。

# [**关于作者和DreamAI**](https://alidocs.dingtalk.com/i/nodes/Amq4vjg890AlRbA6Td9ZvlpDJ3kdP0wQ?utm_scene=team_space)

[https://docs.dingtalk.com/i/nodes/Amq4vjg890AlRbA6Td9ZvlpDJ3kdP0wQ?iframeQuery=utm\_source=portal&utm\_medium=portal\_recent](https://docs.dingtalk.com/i/nodes/Amq4vjg890AlRbA6Td9ZvlpDJ3kdP0wQ?iframeQuery=utm_source=portal&utm_medium=portal_recent)

# 关注微信公众号“AI发烧友”，获取更多IT开发运维实用工具与技巧，还有很多AI技术文档！

![梦幻智能logo-01（无水印）.png](https://alidocs.oss-cn-zhangjiakou.aliyuncs.com/res/eLbnj1PrDP6GwlaN/img/c394abcb-ec2a-4f4c-94d5-33f7d43882bd.png?x-oss-process=image/crop,x_167,y_517,w_1264,h_484/ignore-error,1)