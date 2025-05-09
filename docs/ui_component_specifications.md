# GY_Rename UI组件规范

## 概述

本文档详细描述了GY_Rename应用程序各UI组件的规格、样式和行为规范，确保开发过程中保持一致的设计风格和用户体验。

## 色彩方案

### 主色调
- **主色**：#2E8B57 (海绿色) - 用于重要按钮、强调元素
- **辅助色**：#D2B48C (棕褐色) - 用于次要按钮、工具栏
- **警示色**：#CD5C5C (印度红) - 用于警告、删除按钮
- **高亮色**：#E8C056 (金色) - 用于文件图标、原始文件列

### 状态颜色
- **正常状态**：使用原色
- **悬停状态**：亮度增加15%
- **禁用状态**：灰度化，透明度设为70%
- **选中状态**：主色的亮变体，加上细边框

### 文本颜色
- **主要文本**：#F0F0F0 (浅灰色，深色主题)/#333333 (深灰色，浅色主题)
- **次要文本**：#A0A0A0 (中灰色)
- **禁用文本**：#707070 (深灰色，深色主题)/#999999 (浅灰色，浅色主题)
- **链接文本**：#4AA0E8 (蓝色)

## 主窗口布局

### 整体尺寸
- **初始尺寸**：1200 x 800 像素
- **最小尺寸**：800 x 600 像素

### 工具栏
- **位置**：窗口顶部
- **高度**：48像素
- **按钮尺寸**：32 x 32像素
- **按钮间距**：8像素
- **主要按钮**：命名分析 (绿色)
- **次要按钮**：后退、前进、设置 (棕褐色)

### 三栏布局
- **分栏比例**：1:1:1 (初始状态)
- **分隔条**：2像素宽，#555555 (深灰色)
- **最小栏宽**：200像素
- **栏间距**：0 (使用分隔条)

### 底部操作栏
- **位置**：窗口底部
- **高度**：40像素
- **按钮尺寸**：100 x 32像素
- **按钮间距**：16像素
- **主要按钮**：确认 (右侧)
- **次要按钮**：清空列表 (右侧，确认按钮左侧)

## 文件列表组件

### 列表标题
- **高度**：32像素
- **背景色**：与列标识相同 (原始文件列:#E8C056, 命名示范列:#D2B48C, 命名分析列:#2E8B57)
- **文本**：粗体，16像素，白色
- **对齐**：居中

### 列表项
- **高度**：36像素 (固定高度)
- **文件图标**：左侧，24 x 24像素
- **文件名**：左对齐，常规字体，14像素
- **编辑按钮**：右侧，60 x 24像素 (仅命名示范列)
- **背景色**：交替行使用不同深度的背景色
- **选中状态**：主色的淡变体背景色，1像素边框

### 滚动条
- **宽度**：10像素
- **颜色**：主色的深变体
- **悬停颜色**：主色
- **圆角**：5像素

## 设置对话框

### 对话框尺寸
- **尺寸**：500 x 400像素
- **最小尺寸**：400 x 300像素

### 标签页
- **高度**：32像素
- **背景色**：主色
- **选中标签**：主色的亮变体
- **文本**：白色，14像素

### 表单布局
- **标签宽度**：120像素
- **标签对齐**：右对齐
- **控件间距**：10像素
- **分组边距**：15像素

### 按钮
- **尺寸**：80 x 32像素
- **确定按钮**：主色
- **取消按钮**：灰色
- **位置**：对话框底部右侧

## 交互反馈

### 按钮状态
- **正常**：标准颜色
- **悬停**：亮度增加，光标变为手型
- **按下**：亮度降低，轻微下沉效果
- **禁用**：灰度化，不可点击

### 拖放反馈
- **可放置区域**：显示轻微高亮边框
- **拖动过程**：显示半透明预览
- **成功放置**：短暂闪烁高亮效果
- **非法放置**：显示禁止图标

### 操作反馈
- **成功操作**：右下角临时显示成功提示 (绿色)
- **警告操作**：显示警告对话框，需用户确认
- **错误操作**：显示错误对话框，提供解决建议

## 进度指示

### 加载动画
- **尺寸**：32 x 32像素
- **位置**：居中显示
- **颜色**：主色
- **背景**：半透明遮罩

### 进度条
- **高度**：6像素
- **颜色**：主色
- **背景色**：#3A3A3A (深色)
- **动画**：平滑过渡

## 响应式设计

### 小屏幕适配 (<900px宽)
- **工具栏**：折叠部分按钮到菜单
- **三栏布局**：可切换为选项卡模式
- **按钮尺寸**：缩小到80%

### 大屏幕优化 (>1600px宽)
- **三栏布局**：保持合适比例，不过度拉伸
- **内容区域**：适当增加内边距
- **字体大小**：可选择性增大

## 辅助功能

### 键盘导航
- **Tab键**：在控件间切换焦点
- **快捷键**：主要功能提供键盘快捷键
- **焦点指示**：清晰的视觉焦点反馈

### 屏幕阅读器支持
- **文本替代**：所有图标提供文本描述
- **ARIA标签**：添加适当的ARIA属性
- **焦点顺序**：合理的Tab顺序

## 动画效果

### 过渡动画
- **持续时间**：200-300毫秒
- **缓动函数**：ease-in-out
- **应用场景**：面板切换、对话框显示/隐藏

### 反馈动画
- **持续时间**：150毫秒
- **缓动函数**：ease-out
- **应用场景**：按钮点击、项目选中