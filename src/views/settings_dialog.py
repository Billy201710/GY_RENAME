#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QComboBox, QDialogButtonBox,
    QMessageBox
)
from PySide6.QtCore import Qt

class SettingsDialog(QDialog):
    """
    设置对话框类，用于配置AI API参数
    """
    
    def __init__(self, config_manager, first_run=False, parent=None):
        """
        初始化设置对话框
        
        Args:
            config_manager: 配置管理器实例
            first_run (bool): 是否首次运行
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.config_manager = config_manager
        self.first_run = first_run
        
        # 设置窗口属性
        self.setWindowTitle("AI API设置")
        self.resize(500, 300)
        
        # 创建UI
        self._create_ui()
        
        # 加载当前配置
        self._load_config()
        
        # 如果是首次运行，显示欢迎消息
        if self.first_run:
            self._show_welcome_message()
    
    def _create_ui(self):
        """
        创建UI组件
        """
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建表单布局
        form_layout = QFormLayout()
        
        # API密钥
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("输入您的API密钥")
        form_layout.addRow("API密钥:", self.api_key_edit)
        
        # API URL
        self.api_url_edit = QLineEdit()
        self.api_url_edit.setPlaceholderText("例如: https://api.openai.com/v1/chat/completions")
        form_layout.addRow("API URL:", self.api_url_edit)
        
        # 模型选择
        self.api_model_combobox = QComboBox()
        self.api_model_combobox.addItems([
            "gpt-4", 
            "gpt-4-turbo", 
            "gpt-3.5-turbo",
            "claude-3-sonnet-20240229",
            "gemini-pro"
        ])
        self.api_model_combobox.setEditable(True)
        form_layout.addRow("AI模型:", self.api_model_combobox)
        
        # 添加表单到主布局
        main_layout.addLayout(form_layout)
        
        # 添加描述标签
        description_label = QLabel(
            "请输入您的AI API密钥和URL。这些信息将用于调用AI服务来分析文件命名模式。"
            "您的API密钥将安全地存储在本地配置中，不会发送给任何第三方。"
        )
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: gray;")
        main_layout.addWidget(description_label)
        
        # 添加按钮
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
        # 设置间距和边距
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)
    
    def _load_config(self):
        """
        从配置管理器加载配置
        """
        config = self.config_manager.get_config()
        
        # 设置API密钥
        if 'api_key' in config:
            self.api_key_edit.setText(config['api_key'])
        
        # 设置API URL
        if 'api_url' in config:
            self.api_url_edit.setText(config['api_url'])
        else:
            # 设置默认URL
            self.api_url_edit.setText("https://api.openai.com/v1/chat/completions")
        
        # 设置模型
        if 'api_model' in config and config['api_model']:
            index = self.api_model_combobox.findText(config['api_model'])
            if index >= 0:
                self.api_model_combobox.setCurrentIndex(index)
            else:
                self.api_model_combobox.setCurrentText(config['api_model'])
        else:
            # 设置默认模型
            self.api_model_combobox.setCurrentText("gpt-3.5-turbo")
    
    def _show_welcome_message(self):
        """
        显示欢迎消息
        """
        QMessageBox.information(
            self,
            "欢迎使用GY_Rename",
            "欢迎使用GY_Rename批量文件重命名工具！\n\n"
            "首次使用前，请配置AI API参数，以便应用能够调用AI服务来分析文件命名模式。\n\n"
            "如果您没有API密钥，可以前往相应的AI服务提供商网站申请。"
        )
    
    def accept(self):
        """
        确认按钮处理
        """
        # 检查必填字段
        if not self.api_key_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入API密钥")
            return
        
        if not self.api_url_edit.text().strip():
            QMessageBox.warning(self, "警告", "请输入API URL")
            return
        
        # 保存配置
        config = {
            'api_key': self.api_key_edit.text().strip(),
            'api_url': self.api_url_edit.text().strip(),
            'api_model': self.api_model_combobox.currentText().strip()
        }
        
        self.config_manager.update_config(config)
        
        # 调用父类的accept方法
        super().accept()