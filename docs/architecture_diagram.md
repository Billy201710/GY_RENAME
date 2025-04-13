# GY_Rename 架构设计

## 系统架构图

```
                              +-------------------+
                              |    Application    |
                              +-------------------+
                                       |
                                       v
+---------------+            +-------------------+            +---------------+
|               |            |                   |            |               |
|     Views     |<---------->|    Controllers    |<---------->|     Models    |
|               |            |                   |            |               |
+---------------+            +-------------------+            +---------------+
       |                              |                              |
       v                              v                              v
+---------------+            +-------------------+            +---------------+
| - MainWindow  |            | - FileController  |            | - FileModel   |
| - FileListWid.|            | - RenameController|            | - RenameModel |
| - SettingsDlg.|            | - SettingsControl.|            | - SettingsModel|
+---------------+            +-------------------+            +---------------+
                                       |
                                       v
                              +-------------------+
                              |      Utilities    |
                              | - ConfigManager   |
                              | - AIClient        |
                              | - FileOperations  |
                              +-------------------+
                                       |
                                       v
                              +-------------------+
                              |    External API   |
                              |  (AI Service API) |
                              +-------------------+
```

## 数据流图

```
+-------------+     +-------------+     +-------------+     +-------------+
|             |     |             |     |             |     |             |
| 用户界面交互 | --> | 控制器处理   | --> | 模型数据更新 | --> | 视图更新显示 |
|             |     |             |     |             |     |             |
+-------------+     +-------------+     +-------------+     +-------------+
                          |
                          v
                    +-------------+
                    |             |
                    | AI API 调用 |
                    |             |
                    +-------------+
                          |
                          v
                    +-------------+
                    |             |
                    | 文件系统操作 |
                    |             |
                    +-------------+
```

## 组件交互流程

### 重命名流程

1. **文件加载**:
   用户 → MainWindow → FileController → FileModel → FileListWidget显示

2. **命名示例提供**:
   用户 → FileListWidget → RenameController → RenameModel → 更新示例视图

3. **AI分析**:
   用户 → MainWindow → RenameController → AIClient → AI API → 分析结果 → RenameModel → 更新分析视图

4. **执行重命名**:
   用户 → MainWindow → RenameController → FileOperations → 文件系统 → RenameController → 更新完成通知

## 核心类说明

### 模型层 (Models)

- **FileModel**: 管理文件集合，提供文件添加、移除、更新等操作
- **RenameModel**: 管理重命名历史记录和示例，提供添加历史、导航历史、管理示例等功能
- **SettingsModel**: 管理应用程序设置，提供设置读取、更新和保存功能

### 视图层 (Views)

- **MainWindow**: 主窗口，提供整体布局和用户交互界面
- **FileListWidget**: 文件列表控件，显示文件列表，支持拖放和编辑
- **SettingsDialog**: 设置对话框，用于配置AI API参数

### 控制器层 (Controllers)

- **FileController**: 处理文件相关操作，包括添加、移除、获取文件等
- **RenameController**: 处理重命名相关操作，包括编辑示例、分析命名模式、应用重命名等
- **SettingsController**: 处理设置相关操作，包括更新设置、保存设置等

### 工具类 (Utilities)

- **ConfigManager**: 配置管理器，负责管理应用程序配置
- **AIClient**: AI客户端，负责与AI API的通信
- **FileOperations**: 文件操作工具类，提供文件操作相关功能

## 设计模式应用

- **MVC模式**: 将应用程序分为模型、视图和控制器三层，降低耦合度，提高可维护性
- **观察者模式**: 通过信号槽机制实现组件间的松耦合通信
- **单例模式**: 配置管理器采用单例模式，确保全局唯一实例
- **策略模式**: 文件操作类提供不同的文件处理策略
- **命令模式**: 重命名操作采用命令模式，支持撤销/重做