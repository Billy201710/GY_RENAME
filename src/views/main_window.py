#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QToolBar, QMessageBox,
    QSplitter, QStatusBar, QApplication, QSizePolicy, QToolButton
)
from PySide6.QtCore import Qt, Slot, QSize, QFile, QTextStream, QPoint
from PySide6.QtGui import QIcon, QAction, QPixmap, QMouseEvent
from PySide6.QtWidgets import QSpacerItem

from views.file_list_widget import FileListWidget
from views.settings_dialog import SettingsDialog
from controllers.file_controller import FileController
from controllers.rename_controller import RenameController
from controllers.settings_controller import SettingsController

class MainWindow(QMainWindow):
    """
    应用程序主窗口类
    """
    
    def __init__(self, config_manager, parent=None):
        """
        初始化主窗口
        
        Args:
            config_manager: 配置管理器实例
            parent: 父窗口
        """
        super().__init__(parent)
        self.config_manager = config_manager
        
        # 初始化控制器
        self.file_controller = FileController(config_manager)
        self.rename_controller = RenameController(config_manager)
        self.settings_controller = SettingsController(config_manager)
        
        # 设置窗口属性
        self.setWindowTitle("GY_Rename - AI批量重命名工具")
        self.resize(1200, 800)
        
        # 加载应用图标
        app_icon_path = os.path.join("assets", "icons", "normal", "app_icon.png")
        if os.path.exists(app_icon_path):
            self.setWindowIcon(QIcon(app_icon_path))
        
        # 移除系统标题栏，使用自定义标题栏
        self.setWindowFlags(Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint | Qt.WindowCloseButtonHint | Qt.FramelessWindowHint)
        
        # 窗口置顶状态
        self.always_on_top = False
        
        # 用于窗口拖动
        self.dragging = False
        self.drag_position = QPoint()
        
        # 加载应用样式
        self._load_style_sheet()
        
        # 创建UI组件
        self._create_ui()
        self._create_actions()
        self._create_custom_title_bar()  # 创建自定义标题栏
        self._create_status_bar()
        self._create_connections()
        
        # 检查首次运行，显示设置对话框
        if self.config_manager.is_first_run():
            self._show_first_run_dialog()
    
    def _load_style_sheet(self):
        """
        加载应用样式表
        """
        style_file_path = os.path.join("assets", "styles", "app_style.qss")
        
        if os.path.exists(style_file_path):
            style_file = QFile(style_file_path)
            if style_file.open(QFile.ReadOnly | QFile.Text):
                stream = QTextStream(style_file)
                style_sheet = stream.readAll()
                self.setStyleSheet(style_sheet)
                style_file.close()
    
    def _create_ui(self):
        """
        创建UI组件
        """
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        self.main_layout = QVBoxLayout(central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)
        
        # 创建文件列表区域的分割器
        self.file_lists_splitter = QSplitter(Qt.Horizontal)
        self.file_lists_splitter.setHandleWidth(1)  # 减小分割器手柄宽度
        self.file_lists_splitter.setStyleSheet("QSplitter::handle { background-color: #121212; }")
        
        # 创建三个文件列表容器
        original_container = QWidget()
        original_container.setObjectName("originalFilesContainer")
        example_container = QWidget()
        example_container.setObjectName("exampleFilesContainer")
        analysis_container = QWidget()
        analysis_container.setObjectName("analysisFilesContainer")
        
        # 为每个容器创建布局
        original_layout = QVBoxLayout(original_container)
        example_layout = QVBoxLayout(example_container)
        analysis_layout = QVBoxLayout(analysis_container)
        
        # 设置布局参数 - 去除边距使界面更紧凑
        for layout in [original_layout, example_layout, analysis_layout]:
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(0)
        
        # 创建三个文件列表区域的表头 - 使用原型图样式
        original_header = self._create_original_files_header()
        example_header = self._create_example_files_header()
        analysis_header = self._create_analysis_files_header()
        
        # 创建三个文件列表
        self.original_files_widget = FileListWidget("", accept_drops=True)
        self.example_files_widget = FileListWidget("", with_edit_button=True)
        self.analysis_files_widget = FileListWidget("")
        # 设置分析结果列表为结果列表，使文本显示为绿色
        self.analysis_files_widget.set_as_result_list(True)
        
        # 添加表头和列表到各自布局
        original_layout.addWidget(original_header)
        original_layout.addWidget(self.original_files_widget, 1)
        
        example_layout.addWidget(example_header)
        example_layout.addWidget(self.example_files_widget, 1)
        
        analysis_layout.addWidget(analysis_header)
        analysis_layout.addWidget(self.analysis_files_widget, 1)
        
        # 将三个容器添加到分割器
        self.file_lists_splitter.addWidget(original_container)
        self.file_lists_splitter.addWidget(example_container)
        self.file_lists_splitter.addWidget(analysis_container)
        
        # 设置分割器初始大小
        self.file_lists_splitter.setSizes([400, 400, 400])
        
        # 创建底部按钮区域
        bottom_container = self._create_bottom_button_area()
        
        # 将分割器和底部按钮添加到主布局
        self.main_layout.addWidget(self.file_lists_splitter, 1)
        self.main_layout.addWidget(bottom_container)
    
    def _create_actions(self):
        """
        创建动作
        """
        # 命名分析按钮
        self.analyze_action = QAction(QIcon("assets/icons/normal/refresh.png"), "命名分析", self)
        self.analyze_action.setStatusTip("基于示例分析命名模式")
        
        # 后退按钮
        self.back_action = QAction(QIcon("assets/icons/normal/back.png"), "后退", self)
        self.back_action.setStatusTip("查看上一个分析结果")
        
        # 前进按钮
        self.forward_action = QAction(QIcon("assets/icons/normal/forward.png"), "前进", self)
        self.forward_action.setStatusTip("查看下一个分析结果")
        
        # 设置按钮
        self.settings_action = QAction(QIcon("assets/icons/normal/setting.png"), "设置", self)
        self.settings_action.setStatusTip("打开设置对话框") # 设置按钮提示
        
        # 刷新按钮
        self.refresh_action = QAction(QIcon("assets/icons/normal/refresh.png"), "刷新", self)
        self.refresh_action.setStatusTip("刷新文件列表")
        
        # 固定按钮
        self.pin_action = QAction(QIcon("assets/icons/normal/pin.png"), "窗口置顶", self)
        self.pin_action.setStatusTip("将窗口固定在最前方显示")
        self.pin_action.setCheckable(True)
    
    def _create_custom_title_bar(self):
        """
        创建自定义标题栏
        """
        # 创建标题栏容器
        title_bar = QWidget()
        title_bar.setObjectName("titleBar")
        title_bar.setFixedHeight(36)
        title_bar_layout = QHBoxLayout(title_bar)
        title_bar_layout.setContentsMargins(8, 0, 8, 0)
        title_bar_layout.setSpacing(4)
        
        
        # 添加应用图标
        app_icon_label = QLabel()
        app_icon_label.setPixmap(QPixmap("assets/icons/normal/app_icon.png").scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        app_icon_label.setObjectName("appIconLabel")
        title_bar_layout.addWidget(app_icon_label)
        
        # 添加标题文本
        app_title_label = QLabel("GY_ReNAME")
        app_title_label.setObjectName("appTitleLabel")
        title_bar_layout.addWidget(app_title_label)
        
        # 添加伸缩空间
        title_bar_layout.addStretch(1)
        
        # 添加窗口操作按钮
        # Pin按钮
        self.pin_button = QPushButton()
        self.pin_button.setObjectName("pinButton")
        self.pin_button.setIcon(QIcon("assets/icons/normal/pin.png"))
        self.pin_button.setFixedSize(28, 28)
        self.pin_button.setCheckable(True)
        self.pin_button.setToolTip("窗口置顶")
        title_bar_layout.addWidget(self.pin_button)
        
        # 最小化按钮
        min_button = QPushButton()
        min_button.setObjectName("minButton")
        min_button.setIcon(QIcon("assets/icons/normal/minimize.png"))
        min_button.setFixedSize(28, 28)
        min_button.setToolTip("最小化")
        min_button.clicked.connect(self.showMinimized)
        title_bar_layout.addWidget(min_button)
        
        # 最大化/还原按钮
        self.max_restore_button = QPushButton()
        self.max_restore_button.setObjectName("maxRestoreButton")
        self.max_restore_button.setIcon(QIcon("assets/icons/normal/Maximize.png"))
        self.max_restore_button.setFixedSize(28, 28)
        self.max_restore_button.setToolTip("最大化")
        self.max_restore_button.clicked.connect(self._on_max_restore_clicked)
        title_bar_layout.addWidget(self.max_restore_button)
        
        # 关闭按钮
        close_button = QPushButton()
        close_button.setObjectName("closeButton")
        close_button.setIcon(QIcon("assets/icons/normal/close.png"))
        close_button.setFixedSize(28, 28)
        close_button.setToolTip("关闭")
        close_button.clicked.connect(self.close)
        title_bar_layout.addWidget(close_button)
        
        # 将标题栏添加到主布局
        self.main_layout.insertWidget(0, title_bar)
        
        # 连接置顶按钮信号
        self.pin_button.clicked.connect(self._on_pin_button_clicked)
    
    def _create_status_bar(self):
        """
        创建状态栏
        """
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        # 添加永久消息
        self.status_bar.showMessage("就绪")
    
    def _create_connections(self):
        """
        创建信号连接
        """
        # 文件相关连接
        self.original_files_widget.files_dropped.connect(self.file_controller.add_files)
        self.file_controller.files_added.connect(self.original_files_widget.add_files)
        self.file_controller.files_added.connect(self._update_step1_completed)
        
        # 重命名相关连接
        self.example_files_widget.edit_button_clicked.connect(self.rename_controller.edit_example)
        self.rename_controller.example_updated.connect(self.example_files_widget.update_file)
        self.rename_controller.example_updated.connect(self._update_step2_completed)
        self.rename_controller.analysis_result_updated.connect(self.analysis_files_widget.update_files)
        self.rename_controller.analysis_result_updated.connect(self._update_step3_completed)
        
        # 状态更新连接
        self.rename_controller.analysis_started.connect(lambda: self.status_bar.showMessage("正在分析..."))
        self.rename_controller.analysis_completed.connect(lambda: self.status_bar.showMessage("分析完成"))
        self.rename_controller.analysis_failed.connect(lambda msg: self.status_bar.showMessage(f"分析失败: {msg}"))
        self.rename_controller.rename_started.connect(lambda: self.status_bar.showMessage("正在重命名..."))
        self.rename_controller.rename_completed.connect(lambda: self.status_bar.showMessage("重命名完成"))
        self.rename_controller.rename_failed.connect(lambda msg: self.status_bar.showMessage(f"重命名失败: {msg}"))
        
        # 按钮连接
        self.analyze_button.clicked.connect(self._on_analyze_action)
        self.confirm_button.clicked.connect(self._on_confirm_clicked)
        self.clear_button.clicked.connect(self._on_clear_clicked)
        
        # Pin按钮连接
        self.pin_button.clicked.connect(self._on_pin_button_clicked)
    
    def _show_first_run_dialog(self):
        """
        显示首次运行对话框
        """
        dialog = SettingsDialog(self.config_manager, first_run=True, parent=self)
        if dialog.exec():
            self.config_manager.set_first_run_completed()
    
    def _show_settings_dialog(self):
        """
        显示设置对话框
        """
        dialog = SettingsDialog(self.config_manager, parent=self)
        dialog.exec()
    
    @Slot()
    def _on_analyze_action(self):
        """
        分析按钮点击处理
        """
        # 获取原始文件和示例文件
        original_files = self.file_controller.get_files()
        example_files = self.rename_controller.get_example_files()
        
        # 检查是否有足够的文件
        if not original_files:
            QMessageBox.warning(self, "警告", "没有原始文件可供分析，请先添加文件。")
            return
        
        if not example_files:
            QMessageBox.warning(self, "警告", "没有命名示例，请至少为一个文件提供重命名示例。")
            return
        
        # 执行分析
        self.rename_controller.analyze_naming_pattern(original_files, example_files)
    
    @Slot()
    def _on_confirm_clicked(self):
        """
        分析按钮点击处理 (原确认按钮)
        """
        # 获取当前分析结果
        analysis_result = self.rename_controller.get_current_analysis_result()
        
        if not analysis_result:
            QMessageBox.warning(self, "警告", "没有分析结果可供确认，请先进行命名分析。")
            return
        
        # 询问用户确认
        reply = QMessageBox.question(
            self, 
            "确认重命名", 
            "确定要按照当前分析结果重命名全部文件吗？此操作无法撤销。",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 执行重命名
            result = self.rename_controller.apply_rename()
            
            if result.get("success"):
                QMessageBox.information(self, "成功", f"成功重命名 {result.get('count', 0)} 个文件。")
            else:
                QMessageBox.critical(self, "错误", f"重命名过程中发生错误: {result.get('error', '未知错误')}")
    
    @Slot()
    def _on_clear_clicked(self):
        """
        清空按钮点击处理
        """
        # 询问用户确认
        reply = QMessageBox.question(
            self, 
            "确认清空", 
            "确定要清空所有文件列表吗？",
            QMessageBox.Yes | QMessageBox.No, 
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # 清空文件列表
            self.file_controller.clear_files()
            self.rename_controller.clear_examples()
            self.rename_controller.clear_analysis_results()
            
            # 更新UI
            self.original_files_widget.clear()
            self.example_files_widget.clear()
            self.analysis_files_widget.clear()
            
            # 重置箭头状态
            self._reset_arrow_states()
            
            # 更新状态栏
            self.status_bar.showMessage("已清空所有文件列表")
    
    @Slot()
    def _reset_arrow_states(self):
        """
        重置箭头状态
        """
        # 恢复箭头颜色为默认
        self.arrow_label1.setStyleSheet("font-size: 32px; color: #a0a0a0; padding: 10px 0; font-weight: bold;")
        self.arrow_label2.setStyleSheet("font-size: 32px; color: #a0a0a0; padding: 10px 0; font-weight: bold;")
        # 重置文本确保一致性
        self.arrow_label1.setText("➔")
        self.arrow_label2.setText("➔")
    
    @Slot()
    def _on_refresh_action(self):
        """
        刷新按钮点击处理
        """
        # 获取当前文件列表
        current_files = self.file_controller.get_files()
        
        if not current_files:
            self.status_bar.showMessage("没有文件可供刷新")
            return
        
        # 清空文件列表
        self.original_files_widget.clear()
        
        # 重新添加文件
        self.original_files_widget.add_files(current_files)
        
        # 更新状态栏
        self.status_bar.showMessage("文件列表已刷新")
    
    @Slot(bool)
    def _on_pin_button_clicked(self, checked):
        """
        置顶按钮点击处理
        """
        self._on_pin_action(checked)
        # 更新工具栏中的pin action状态
        self.pin_action.setChecked(checked)
    
    @Slot()
    def _on_max_restore_clicked(self):
        """
        最大化/还原按钮点击处理
        """
        if self.isMaximized():
            self.showNormal()
            self.max_restore_button.setIcon(QIcon("assets/icons/normal/Maximize.png"))
            self.max_restore_button.setToolTip("最大化")
        else:
            self.showMaximized()
            self.max_restore_button.setIcon(QIcon("assets/icons/normal/unmaximize.png"))
            self.max_restore_button.setToolTip("还原")
    
    @Slot(bool)
    def _on_pin_action(self, checked):
        """
        固定按钮点击处理
        
        Args:
            checked (bool): 是否选中
        """
        # 设置窗口标志
        flags = self.windowFlags()
        
        if checked:
            # 设置窗口置顶
            self.setWindowFlags(flags | Qt.WindowStaysOnTopHint)
            self.pin_button.setIcon(QIcon("assets/icons/active/pin.png"))
            self.pin_action.setIcon(QIcon("assets/icons/active/pin.png"))
            self.status_bar.showMessage("窗口已固定在最前方")
        else:
            # 取消窗口置顶
            self.setWindowFlags(flags & ~Qt.WindowStaysOnTopHint)
            self.pin_button.setIcon(QIcon("assets/icons/normal/pin.png"))
            self.pin_action.setIcon(QIcon("assets/icons/normal/pin.png"))
            self.status_bar.showMessage("窗口已取消固定")
        
        # 重新显示窗口
        self.show()

    def mousePressEvent(self, event: QMouseEvent):
        """
        鼠标按下事件处理
        """
        # 只处理左键点击
        if event.button() == Qt.LeftButton:
            # 判断是否点击在标题栏区域
            title_bar = self.findChild(QWidget, "titleBar")
            if title_bar and title_bar.geometry().contains(event.pos()):
                self.dragging = True
                self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
        
        # 调用父类方法
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        """
        鼠标移动事件处理
        """
        if self.dragging and not self.isMaximized():
            self.move(event.globalPosition().toPoint() - self.drag_position)
        
        # 调用父类方法
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """
        鼠标释放事件处理
        """
        if event.button() == Qt.LeftButton:
            self.dragging = False
        
        # 调用父类方法
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event: QMouseEvent):
        """
        鼠标双击事件处理
        """
        # 判断是否在标题栏上双击
        title_bar = self.findChild(QWidget, "titleBar")
        if title_bar and title_bar.geometry().contains(event.pos()):
            self._on_max_restore_clicked()
        
        # 调用父类方法
        super().mouseDoubleClickEvent(event)

    def _create_original_files_header(self):
        """创建原始文件区域的表头 - 符合原型图样式"""
        header_widget = QWidget() # 表头容器
        header_widget.setObjectName("originalFilesHeader") # 表头容器名称
        
        header_layout = QHBoxLayout(header_widget) # 表头布局
        header_layout.setContentsMargins(20,0,0,0) # 表头布局内边距
        
        # 创建表头标题区域
        title_container = QWidget()
        title_container.setObjectName("titleContainer") # 标题容器
        title_layout = QHBoxLayout(title_container) # 标题布局
        title_layout.setContentsMargins(0, 0, 0, 0) # 标题布局内边距

        # 创建设置按钮
        setting_button = QToolButton()
        setting_button.setIcon(QIcon("assets/icons/normal/setting.png"))
        setting_button.setCursor(Qt.PointingHandCursor) # 设置鼠标悬停为手型
        # 把图标设置为36*36
        setting_button.setIconSize(QSize(36, 36))
        setting_button.setFixedSize(36, 36)
        setting_button.setObjectName("settingButton")
        setting_button.setToolTip("设置")
        # todo: 设置按钮点击事件
        setting_button.clicked.connect(self._show_settings_dialog)
                
        # 步骤标签
        step_label = QLabel("原始文件")
        step_label.setObjectName("stepLabel")
        step_label.setStyleSheet("font-size: 36px; color: #7E7E80; font-weight: bold;")

        # 添加步骤指示图标
        step_icon = QLabel()
        step_icon.setPixmap(QPixmap("assets/icons/normal/step_1.png"))
        step_icon.setObjectName("stepIcon")
        step_icon.setFixedSize(36, 36)
        
        # 创建一个包装容器来确保图标和文字对齐
        alignment_container = QWidget()
        alignment_layout = QHBoxLayout(alignment_container)
        alignment_layout.setContentsMargins(0, 0, 0, 0)
        alignment_layout.setSpacing(10)
        alignment_layout.addWidget(step_label)
        alignment_layout.addWidget(step_icon)
        alignment_layout.addStretch()
        
        # 设置垂直对齐方式
        alignment_layout.setAlignment(step_label, Qt.AlignVCenter)
        alignment_layout.setAlignment(step_icon, Qt.AlignVCenter)
        
        # 创建步骤指示器容器
        step_container = QWidget()
        step_container.setObjectName("stepContainer")
        step_layout = QHBoxLayout(step_container)
        step_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加箭头图标
        arrow_icon = QLabel("➔")
        arrow_icon.setAlignment(Qt.AlignCenter)
        arrow_icon.setObjectName("arrowIcon")
        arrow_icon.setStyleSheet("font-size: 32px; color: #a0a0a0; font-weight: bold;")
        arrow_icon.setAlignment(Qt.AlignRight) # 使箭头图标右对齐
        
        # 保存箭头引用
        self.arrow_label1 = arrow_icon
        
        # 添加到步骤容器布局
        step_layout.addWidget(arrow_icon)
        
        # 添加标题区域和步骤指示器到主布局
        header_layout.addWidget(setting_button)
        header_layout.addWidget(alignment_container) 
        header_layout.addWidget(step_container) 
        
        # 定义header_layout中每个元素的宽度占比
        header_layout.setStretch(0, 1) # 设置按钮占据1个单位
        header_layout.setStretch(1, 4) # 标题区域占据4个单位
        header_layout.setStretch(2, 1) # 步骤指示器占据1个单位
        header_layout.setSpacing(20) # 设置间距
        
        return header_widget

    def _create_example_files_header(self):
        """创建示例文件区域的表头 - 符合原型图样式"""
        header_widget = QWidget()
        header_widget.setObjectName("exampleFilesHeader")
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        
        # 创建左侧空白占位区域
        left_spacer = QWidget()
        left_spacer.setObjectName("leftSpacer")
        
        # 创建表头标题区域
        title_container = QWidget()
        title_container.setObjectName("titleContainer")
        title_layout = QHBoxLayout(title_container)
        title_layout.setContentsMargins(0, 0, 0, 0)
        
        # 步骤标签
        step_label = QLabel("命名示范")
        step_label.setObjectName("stepLabel")
        step_label.setStyleSheet("font-size: 36px; color: #CBA057; font-weight: bold;")
        
        # 添加步骤指示图标
        step_icon = QLabel()
        step_icon.setPixmap(QPixmap("assets/icons/normal/step_2.png"))
        step_icon.setObjectName("stepIcon")
        step_icon.setFixedSize(36, 36)  # 设置固定大小与第一个标题一致
        
        # 创建一个包装容器来确保图标和文字对齐
        alignment_container = QWidget()
        alignment_layout = QHBoxLayout(alignment_container)
        alignment_layout.setContentsMargins(0, 0, 0, 0)
        alignment_layout.setSpacing(10)
        alignment_layout.addWidget(step_label)
        alignment_layout.addWidget(step_icon)
        alignment_layout.addStretch()
        
        # 设置垂直对齐方式
        alignment_layout.setAlignment(step_label, Qt.AlignVCenter)
        alignment_layout.setAlignment(step_icon, Qt.AlignVCenter)
        
        # 创建步骤指示器容器
        step_container = QWidget()
        step_container.setObjectName("stepContainer")
        step_layout = QHBoxLayout(step_container)
        step_layout.setContentsMargins(0, 0, 0, 0)
        
        # 添加箭头图标
        arrow_icon = QLabel("➔")
        arrow_icon.setAlignment(Qt.AlignCenter)
        arrow_icon.setObjectName("arrowIcon")
        arrow_icon.setStyleSheet("font-size: 32px; color: #a0a0a0; font-weight: bold;")
        arrow_icon.setAlignment(Qt.AlignRight)  # 使箭头图标右对齐
        
        # 保存箭头引用
        self.arrow_label2 = arrow_icon
        
        # 添加到步骤容器布局
        step_layout.addWidget(arrow_icon)
        
        # 添加左侧占位区域、标题区域和步骤指示器到主布局
        header_layout.addWidget(left_spacer)
        header_layout.addWidget(alignment_container)
        header_layout.addWidget(step_container)
        
        # 定义header_layout中每个元素的宽度占比
        header_layout.setStretch(0, 1)  # 左侧占位区域占据1个单位
        header_layout.setStretch(1, 4)  # 标题区域占据4个单位

        # 创建一个spacer
        spacer = QSpacerItem(20, 20)
        # 添加标题区域和步骤指示器到主布局
        header_layout.addWidget(title_container)
        header_layout.addWidget(step_container)
        
        return header_widget

    def _create_analysis_files_header(self):
        """创建分析结果区域的表头 - 符合原型图样式"""
        header_widget = QWidget()
        header_widget.setObjectName("analysisFilesHeader")
        
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(0, 0, 0, 0)
        header_layout.setSpacing(0)  # 设置主布局间距为0
        
        # 创建左侧占位区域，确保按钮区域位于水平中央
        left_spacer = QWidget()
        left_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # 创建命名分析按钮区域 - 使用水平布局而不是QHBoxLayout
        button_container = QWidget()
        button_container.setObjectName("buttonContainer")
        
        # 使用QHBoxLayout但完全移除所有边距和间距
        button_layout = QHBoxLayout(button_container)
        button_layout.setSpacing(0)  # 设置按钮之间的间距为0
        button_layout.setContentsMargins(0, 0, 0, 0)  # 移除内边距
        
        # 后退按钮
        back_btn = QToolButton()
        back_btn.setIcon(QIcon("assets/icons/normal/back.png"))
        back_btn.setObjectName("navigationButton")
        # 设置图标大小
        back_btn.setIconSize(QSize(36, 36))
        back_btn.setFixedWidth(48)
        back_btn.setFixedHeight(48)
        back_btn.setToolTip("查看上一个分析结果")
        back_btn.setCursor(Qt.PointingHandCursor) # 设置鼠标悬停为手型
        back_btn.clicked.connect(self._on_back_action)
        
        # 分析命名按钮
        self.analyze_button = QPushButton("命名分析")
        self.analyze_button.setStyleSheet("font-size: 26px; margin: 0; padding: 0;")
        self.analyze_button.setObjectName("analyzeButton")
        self.analyze_button.setCursor(Qt.PointingHandCursor) # 设置鼠标悬停为手型
        self.analyze_button.setFixedWidth(185)
        self.analyze_button.setFixedHeight(48)
        self.analyze_button.clicked.connect(self._on_analyze_action)
        
        # 前进按钮
        forward_btn = QToolButton()
        forward_btn.setIcon(QIcon("assets/icons/normal/forward.png"))
        forward_btn.setObjectName("navigationButton")
        # 设置图标大小
        forward_btn.setIconSize(QSize(36, 36))
        forward_btn.setFixedWidth(48)
        forward_btn.setFixedHeight(48)
        forward_btn.setToolTip("查看下一个分析结果")
        forward_btn.setCursor(Qt.PointingHandCursor) # 设置鼠标悬停为手型
        forward_btn.clicked.connect(self._on_forward_action)
        
        # 添加到按钮布局并控制总宽度不超过300px
        button_layout.addWidget(back_btn)
        button_layout.addWidget(self.analyze_button)
        button_layout.addWidget(forward_btn)
        
        # 设置按钮容器的固定宽度为300px
        button_container.setFixedWidth(290)
        
        # 确保按钮布局中的元素不会超出容器
        button_layout.setStretch(0, 1)  # 后退按钮
        button_layout.setStretch(1, 4)  # 分析命名按钮
        button_layout.setStretch(2, 1)  # 前进按钮              
        
        # 创建步骤指示器容器
        step_container = QWidget()
        step_container.setObjectName("stepContainer")
        step_layout = QHBoxLayout(step_container)
        step_layout.setContentsMargins(5, 5, 10, 5)
        
        # 添加步骤指示图标
        step_icon = QLabel()
        step_icon.setPixmap(QPixmap("assets/icons/normal/step_3.png"))
        step_icon.setAlignment(Qt.AlignCenter)
        step_icon.setObjectName("stepIcon")
        
        # 添加到步骤容器布局
        step_layout.addWidget(step_icon)
        
        # 创建右侧占位区域，确保按钮区域位于水平中央
        right_spacer = QWidget()
        right_spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        
        # 添加左侧占位区域、按钮区域、步骤指示器和右侧占位区域到主布局
        header_layout.addWidget(left_spacer)
        header_layout.addWidget(button_container)
        header_layout.addWidget(step_container)
        header_layout.addWidget(right_spacer)
        # 设置左右占位区域的伸缩比例相等，确保按钮区域居中
        header_layout.setStretch(0, 1)  # 左侧占位区域占据1个单位
        header_layout.setStretch(1, 4)  # 按钮区域占据4个单位
        header_layout.setStretch(2, 1)  # 步骤指示器占据1个单位
        header_layout.setStretch(3, 1)  # 右侧占位区域占据1个单位
        return header_widget

    def _create_bottom_button_area(self):
        """创建底部按钮区域 - 符合原型图样式"""
        # 底部按钮容器
        bottom_container = QWidget()
        bottom_container.setObjectName("bottomContainer")
        
        # 创建布局
        bottom_layout = QHBoxLayout(bottom_container)
        bottom_layout.setContentsMargins(0, 0, 0, 0)
        bottom_layout.setSpacing(0)  # 设置按钮之间的间距为0
        
        # 确认按钮容器
        confirm_container = QWidget()
        confirm_container.setObjectName("confirmContainer")
        confirm_layout = QHBoxLayout(confirm_container)
        confirm_layout.setContentsMargins(0, 5, 0, 5)  # 移除左右边距
        
        # 确认按钮（包含步骤图标）
        confirm_button = QPushButton()
        confirm_button.setObjectName("confirmButton")
        confirm_button.setCursor(Qt.PointingHandCursor) # 设置鼠标悬停为手型
        # 给按钮添加8个像素的圆角
        confirm_button.setStyleSheet("border-radius: 8px;")
        
        # 创建确认按钮的内部布局
        confirm_inner = QHBoxLayout(confirm_button)
        confirm_inner.setContentsMargins(10, 5, 10, 5)
        confirm_inner.setSpacing(10)
        
        # 步骤指示图标
        step_icon = QLabel()
        step_icon.setPixmap(QPixmap("assets/icons/normal/step_4.png"))
        step_icon.setAlignment(Qt.AlignCenter)
        
        # 按钮文字
        button_text = QLabel("确认")
        button_text.setObjectName("confirmButtonText")
        button_text.setStyleSheet("font-size: 28px; color: #F7F7F7;")
        button_text.setAlignment(Qt.AlignCenter)
        
        # 添加到内部布局
        confirm_inner.addWidget(button_text, 1)
        confirm_inner.addWidget(step_icon)
        
        # 添加确认按钮到确认容器
        confirm_layout.addWidget(confirm_button)
        
        # 保存按钮引用
        self.confirm_button = confirm_button
        
        # 连接确认按钮点击信号
        confirm_button.clicked.connect(self._on_confirm_clicked)
        
        # 清空按钮容器
        clear_container = QWidget()
        clear_container.setObjectName("clearContainer")
        clear_layout = QHBoxLayout(clear_container)
        clear_layout.setContentsMargins(0, 5, 0, 5)  # 移除左右边距
        
        # 清空按钮（包含步骤图标）
        clear_button = QPushButton()
        clear_button.setObjectName("clearButton")
        clear_button.setStyleSheet("border-radius: 8px;")
        clear_button.setCursor(Qt.PointingHandCursor) # 设置鼠标悬停为手型
        # 创建清空按钮的内部布局
        clear_inner = QHBoxLayout(clear_button)
        clear_inner.setContentsMargins(10, 5, 10, 5)
        clear_inner.setSpacing(10)
        
        # 步骤指示图标
        step_icon = QLabel()
        step_icon.setPixmap(QPixmap("assets/icons/normal/step_5.png"))
        step_icon.setAlignment(Qt.AlignCenter)
        
        # 按钮文字
        button_text = QLabel("清空列表")
        button_text.setObjectName("clearButtonText")
        button_text.setStyleSheet("font-size: 28px; color: #F7F7F7;")
        button_text.setAlignment(Qt.AlignCenter)
        
        # 添加到内部布局
        clear_inner.addWidget(button_text, 1)
        clear_inner.addWidget(step_icon)
        
        # 添加清空按钮到清空容器
        clear_layout.addWidget(clear_button)
        
        # 保存按钮引用
        self.clear_button = clear_button
        
        # 连接清空按钮点击信号
        clear_button.clicked.connect(self._on_clear_clicked)
        
        # 添加按钮容器到底部布局，并确保它们之间没有间距
        bottom_layout.addWidget(confirm_container, 1)
        bottom_layout.addWidget(clear_container, 1)
        
        return bottom_container

    def _on_add_original_files(self):
        """处理添加原始文件的操作"""
        files = self.file_controller.browse_files()
        if files:
            self.original_files_widget.add_files(files)
            self.status_bar.showMessage(f"已添加 {len(files)} 个原始文件")
    
    def _on_clear_original_files(self):
        """清空原始文件列表"""
        self.original_files_widget.clear()
        self.file_controller.clear_files()
        # 重置第一个箭头状态
        self.arrow_label1.setStyleSheet("font-size: 32px; color: #a0a0a0; padding: 10px 0; font-weight: bold;")
        self.status_bar.showMessage("已清空原始文件列表")
    
    def _on_add_example_files(self):
        """处理添加示例文件的操作"""
        # 这里通常是从原始文件中选择
        files = self.file_controller.get_files()
        if not files:
            QMessageBox.warning(self, "警告", "请先添加原始文件")
            return
        
        # 设置示例文件
        self.example_files_widget.add_files(files)
        self.status_bar.showMessage("已添加示例文件")
    
    def _on_clear_example_files(self):
        """清空示例文件列表"""
        self.example_files_widget.clear()
        self.rename_controller.clear_examples()
        # 重置第二个箭头状态
        self.arrow_label2.setStyleSheet("font-size: 32px; color: #a0a0a0; padding: 10px 0; font-weight: bold;")
        self.status_bar.showMessage("已清空示例文件列表")
    
    def _on_analyze_button_clicked(self):
        """分析按钮点击处理"""
        self._on_analyze_action()

    def _on_back_action(self):
        """查看上一个分析结果"""
        # 获取上一个分析结果
        result = self.rename_controller.get_previous_analysis_result()
        if result:
            # 更新分析结果列表
            self.analysis_files_widget.update_files(result)
            self.status_bar.showMessage("已显示上一个分析结果")
        else:
            self.status_bar.showMessage("没有更早的分析结果")
    
    def _on_forward_action(self):
        """查看下一个分析结果"""
        # 获取下一个分析结果
        result = self.rename_controller.get_next_analysis_result()
        if result:
            # 更新分析结果列表
            self.analysis_files_widget.update_files(result)
            self.status_bar.showMessage("已显示下一个分析结果")
        else:
            self.status_bar.showMessage("没有更新的分析结果")

    def _update_step1_completed(self, files=None):
        """
        更新步骤1完成状态
        """
        if files and len(files) > 0:
            self.arrow_label1.setText("➔")
            self.arrow_label1.setStyleSheet("font-size: 32px; color: #4CAF50; padding: 10px 0; font-weight: bold;")
    
    def _update_step2_completed(self, *args):
        """
        更新步骤2完成状态
        """
        examples = self.rename_controller.get_example_files()
        if examples and len(examples) > 0:
            self.arrow_label2.setText("➔")
            self.arrow_label2.setStyleSheet("font-size: 32px; color: #4CAF50; padding: 10px 0; font-weight: bold;")
    
    def _update_step3_completed(self, *args):
        """
        更新步骤3完成状态
        """
        # 可以在此处添加额外的视觉效果，表示分析完成
        pass