#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QPushButton, QLabel, QToolBar, QAction, QMessageBox,
    QSplitter
)
from PySide6.QtCore import Qt, Slot, QSize
from PySide6.QtGui import QIcon, QAction

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
        
        # 创建UI组件
        self._create_ui()
        self._create_actions()
        self._create_toolbar()
        self._create_connections()
        
        # 检查首次运行，显示设置对话框
        if self.config_manager.is_first_run():
            self._show_first_run_dialog()
    
    def _create_ui(self):
        """
        创建UI组件
        """
        # 创建中央部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 创建主布局
        main_layout = QVBoxLayout(central_widget)
        
        # 创建文件列表区域的分割器
        self.file_lists_splitter = QSplitter(Qt.Horizontal)
        
        # 创建三个文件列表
        self.original_files_widget = FileListWidget("原始文件", accept_drops=True)
        self.example_files_widget = FileListWidget("命名示范", with_edit_button=True)
        self.analysis_files_widget = FileListWidget("命名分析")
        
        # 添加文件列表到分割器
        self.file_lists_splitter.addWidget(self.original_files_widget)
        self.file_lists_splitter.addWidget(self.example_files_widget)
        self.file_lists_splitter.addWidget(self.analysis_files_widget)
        
        # 设置分割器初始大小
        self.file_lists_splitter.setSizes([400, 400, 400])
        
        # 创建底部按钮区域
        bottom_layout = QHBoxLayout()
        
        # 创建底部按钮
        self.confirm_button = QPushButton("确认")
        self.clear_button = QPushButton("清空列表")
        
        # 添加按钮到底部布局
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.confirm_button)
        bottom_layout.addWidget(self.clear_button)
        
        # 将分割器和底部按钮添加到主布局
        main_layout.addWidget(self.file_lists_splitter, 1)
        main_layout.addLayout(bottom_layout)
    
    def _create_actions(self):
        """
        创建动作
        """
        # 分析按钮
        self.analyze_action = QAction(QIcon("assets/icons/analyze.png"), "命名分析", self)
        self.analyze_action.setStatusTip("分析文件命名模式")
        
        # 后退按钮
        self.back_action = QAction(QIcon("assets/icons/back.png"), "后退", self)
        self.back_action.setStatusTip("查看上一个分析结果")
        
        # 前进按钮
        self.forward_action = QAction(QIcon("assets/icons/forward.png"), "前进", self)
        self.forward_action.setStatusTip("查看下一个分析结果")
        
        # 设置按钮
        self.settings_action = QAction(QIcon("assets/icons/settings.png"), "设置", self)
        self.settings_action.setStatusTip("打开设置对话框")
    
    def _create_toolbar(self):
        """
        创建工具栏
        """
        # 创建工具栏
        self.toolbar = QToolBar("主工具栏")
        self.toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(self.toolbar)
        
        # 添加动作到工具栏
        self.toolbar.addAction(self.back_action)
        self.toolbar.addAction(self.analyze_action)
        self.toolbar.addAction(self.forward_action)
        self.toolbar.addSeparator()
        self.toolbar.addAction(self.settings_action)
    
    def _create_connections(self):
        """
        创建信号连接
        """
        # 文件相关连接
        self.original_files_widget.files_dropped.connect(self.file_controller.add_files)
        self.file_controller.files_added.connect(self.original_files_widget.add_files)
        
        # 重命名相关连接
        self.example_files_widget.edit_button_clicked.connect(self.rename_controller.edit_example)
        self.rename_controller.example_updated.connect(self.example_files_widget.update_file)
        self.rename_controller.analysis_result_updated.connect(self.analysis_files_widget.update_files)
        
        # 按钮动作连接
        self.analyze_action.triggered.connect(self._on_analyze_action)
        self.back_action.triggered.connect(self.rename_controller.go_to_previous_analysis)
        self.forward_action.triggered.connect(self.rename_controller.go_to_next_analysis)
        self.settings_action.triggered.connect(self._show_settings_dialog)
        
        # 底部按钮连接
        self.confirm_button.clicked.connect(self._on_confirm_clicked)
        self.clear_button.clicked.connect(self._on_clear_clicked)
    
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
        确认按钮点击处理
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