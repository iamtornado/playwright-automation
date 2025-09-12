# 钉钉文档编辑器调试脚本

本目录包含了专门用于调试钉钉文档编辑器聚焦问题的独立测试脚本。

## 脚本说明

### 1. test_dingtalk_editor_debug.py
**功能**: 全面的钉钉文档编辑器聚焦调试
**特点**:
- 尝试多种聚焦方法
- 记录详细的调试信息
- 收集iframe元素统计
- 保存调试截图和追踪文件

**使用方法**:
```bash
pytest -s --headed ./test_dingtalk_editor_debug.py --title '文章标题'
```

### 2. test_dingtalk_simple_focus.py
**功能**: 简单的聚焦方法测试
**特点**:
- 测试4种不同的聚焦方法
- 输出简洁的测试结果
- 适合快速验证

**使用方法**:
```bash
pytest -s --headed ./test_dingtalk_simple_focus.py --title '文章标题'
```

### 3. test_dingtalk_iframe_analysis.py
**功能**: iframe内容深度分析
**特点**:
- 分析iframe内的DOM结构
- 统计各种元素类型和属性
- 保存iframe的HTML内容
- 提供详细的元素信息

**使用方法**:
```bash
pytest -s --headed ./test_dingtalk_iframe_analysis.py --title '文章标题'
```

## 调试步骤

### 第一步：基础聚焦测试
运行简单聚焦测试，快速验证基本功能：
```bash
pytest -s --headed ./test_dingtalk_simple_focus.py --title '测试文章'
```

### 第二步：iframe内容分析
如果聚焦失败，运行iframe分析脚本：
```bash
pytest -s --headed ./test_dingtalk_iframe_analysis.py --title '测试文章'
```

### 第三步：全面调试
运行完整调试脚本，获取详细信息：
```bash
pytest -s --headed ./test_dingtalk_editor_debug.py --title '测试文章'
```

## 输出文件

调试过程中会生成以下文件：

### test-results/ 目录
- `dingtalk_editor_debug.png` - 调试截图
- `dingtalk_editor_debug_trace.zip` - 追踪文件
- `dingtalk_simple_focus.png` - 简单测试截图
- `dingtalk_iframe_analysis.png` - 分析截图
- `dingtalk_iframe_content.html` - iframe HTML内容

## 调试信息解读

### 聚焦方法测试结果
- ✅ 成功 - 方法有效
- ❌ 失败 - 方法无效，会显示错误信息
- ⚠️ 警告 - 方法部分有效或需要进一步检查

### 元素统计信息
- 总元素数量：iframe中的元素总数
- 元素类型统计：各种HTML标签的数量
- 特殊属性统计：具有特定属性的元素数量
- 编辑器元素：可能的编辑器相关元素

## 常见问题排查

### 1. 聚焦失败
**可能原因**:
- iframe未完全加载
- 编辑器元素选择器不正确
- 页面结构发生变化

**解决方法**:
- 检查iframe加载状态
- 更新元素选择器
- 分析iframe HTML内容

### 2. 元素找不到
**可能原因**:
- 页面结构变化
- 选择器过时
- 元素动态生成

**解决方法**:
- 使用iframe分析脚本检查DOM结构
- 更新选择器
- 添加等待时间

### 3. 组合键失败
**可能原因**:
- 焦点不在正确位置
- 浏览器不支持该组合键
- 页面阻止了键盘事件

**解决方法**:
- 确保先正确聚焦
- 尝试其他键盘操作
- 检查页面事件处理

## 建议的调试流程

1. **运行简单测试** - 快速验证基本功能
2. **分析iframe内容** - 了解页面结构
3. **运行全面调试** - 获取详细信息
4. **分析输出文件** - 找出问题原因
5. **修改主脚本** - 根据调试结果优化代码

## 注意事项

1. 确保已登录钉钉文档
2. 测试前关闭其他浏览器窗口
3. 保存好调试输出文件
4. 根据调试结果调整主脚本的聚焦逻辑

## 联系支持

如果调试后仍有问题，请提供：
- 调试脚本的完整输出
- 生成的截图文件
- iframe HTML内容文件
- 具体的错误信息
