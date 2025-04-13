# GY_Rename - AI批量重命名工具

GY_Rename是一款基于人工智能的批量文件重命名工具，通过示例学习的方式，帮助用户快速、高效地完成文件批量重命名任务。该工具适用于Windows和macOS平台，采用PySide6和Python开发，界面直观友好，操作简单便捷。

## 项目功能

- **AI智能分析**：通过少量的命名示例，AI自动学习用户的命名规则并应用到所有文件
- **三栏式布局**：原始文件、命名示范、命名分析三栏式设计，清晰直观
- **操作历史**：支持操作回退和前进，轻松调整命名结果
- **批量预览**：重命名执行前可预览所有变更，避免误操作
- **多平台支持**：同时支持Windows和macOS系统
- **拖拽操作**：支持文件拖拽导入，操作便捷
- **API参数配置**：提供AI模型接口参数配置，灵活适应不同场景

## 安装说明

### 环境要求
- Python 3.8+
- PySide6
- 网络连接（用于AI API调用）

### 安装步骤
1. 克隆或下载本仓库
```bash
git clone https://github.com/yourusername/GY_Rename.git
cd GY_Rename
```

2. 安装依赖项
```bash
pip install -r requirements.txt
```

3. 运行应用
```bash
python src/main.py
```

## 使用指南

1. **首次使用设置**：
   - 首次打开软件时，会提示输入AI大模型的API Key及相关参数
   - 完成设置后，参数将被安全存储，后续使用无需重复输入

2. **基本操作流程**：
   - 将需要重命名的文件拖入"原始文件"列表
   - 在"命名示范"列点击"Edit"按钮，为部分文件提供重命名示例
   - 点击界面顶部的"命名分析"按钮，系统将自动分析命名规则
   - 查看"命名分析"列中的预览结果
   - 满意后点击"确认"按钮执行重命名，或继续调整示例后重新分析

3. **高级功能**：
   - 使用回退/前进按钮查看不同版本的命名分析结果
   - 通过设置按钮（齿轮图标）随时调整AI API参数
   - 使用"清空列表"按钮清除当前操作，开始新的重命名任务

## 项目开发规划

### 阶段一：基础架构搭建（项目初始化）
- [x] 创建项目基本结构
- [x] 实现MVC架构设计
- [x] 配置开发环境和依赖管理
- [x] 设计数据模型
- [x] 创建核心类和接口

### 阶段二：用户界面开发
- [ ] 实现主窗口和三栏式布局
  - [ ] 设计并实现主窗口布局和基本结构
  - [ ] 实现可调整的三栏式布局
  - [ ] 创建并应用统一的应用风格
  - [ ] 实现工具栏和状态栏
- [ ] 开发文件拖拽功能
  - [ ] 实现文件拖入功能
  - [ ] 支持多文件选择与拖放
  - [ ] 添加拖放视觉反馈
  - [ ] 处理不同文件类型识别
- [ ] 创建设置对话框
  - [ ] 设计并实现API设置界面
  - [ ] 创建首次运行向导
  - [ ] 实现设置项的保存与加载
  - [ ] 添加设置验证功能
- [ ] 实现文件列表组件
  - [ ] 创建自定义文件列表控件
  - [ ] 实现编辑按钮功能
  - [ ] 添加列表项的上下文菜单
  - [ ] 支持大量文件的高效显示
- [ ] 设计操作按钮和工具栏
  - [ ] 设计并实现所有操作按钮
  - [ ] 添加按钮状态反馈
  - [ ] 实现底部操作栏和确认按钮
  - [ ] 添加进度指示和状态反馈

### 阶段三：AI集成与核心功能实现
- [ ] 集成AI API调用接口
- [ ] 实现命名规则分析算法
- [ ] 开发示例学习逻辑
- [ ] 实现批量重命名预览功能
- [ ] 添加操作历史管理

### 阶段四：功能完善与性能优化
- [ ] 添加错误处理和异常管理
- [ ] 实现异步处理AI请求
- [ ] 优化大量文件处理性能
- [ ] 添加进度指示器
- [ ] 完善日志记录系统

### 阶段五：测试与发布
- [ ] 编写单元测试和集成测试
- [ ] 进行跨平台兼容性测试
- [ ] 用户界面和用户体验测试
- [ ] 创建安装包和发布脚本
- [ ] 撰写用户文档和帮助指南

## 项目结构

```
GY_Rename/
│
├── docs/                  # 文档目录
│   ├── api_guide.md       # API使用指南
│   └── user_manual.md     # 用户手册
│
├── src/                   # 源代码目录
│   ├── controllers/       # 控制器
│   │   ├── file_controller.py
│   │   ├── rename_controller.py
│   │   └── settings_controller.py
│   │
│   ├── models/            # 数据模型
│   │   ├── file_model.py
│   │   ├── rename_model.py
│   │   └── settings_model.py
│   │
│   ├── views/             # 视图
│   │   ├── main_window.py
│   │   ├── file_list_widget.py
│   │   ├── settings_dialog.py
│   │   └── rename_preview_widget.py
│   │
│   ├── utils/             # 工具函数
│   │   ├── ai_client.py
│   │   ├── file_operations.py
│   │   └── config_manager.py
│   │
│   └── main.py            # 程序入口
│
├── tests/                 # 测试代码目录
│   ├── test_file_operations.py
│   ├── test_rename_logic.py
│   └── test_ai_integration.py
│
├── assets/                # 资源文件目录
│   ├── icons/
│   └── styles/
│
├── requirements.txt       # 项目依赖
└── README.md              # 项目说明
```

## 技术栈

- **编程语言**：Python 3.8+
- **GUI框架**：PySide6
- **网络请求**：httpx（异步HTTP客户端）
- **数据存储**：SQLite（本地配置和历史记录）
- **异步处理**：asyncio
- **单元测试**：pytest

## 贡献指南

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m 'Add some amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用MIT许可证 - 详见 [LICENSE](LICENSE) 文件

## 联系方式

- 项目维护者: Your Name
- 邮箱: your.email@example.com
- 项目链接: [https://github.com/yourusername/GY_Rename](https://github.com/yourusername/GY_Rename)