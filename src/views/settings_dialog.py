#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFormLayout, QComboBox, QDialogButtonBox,
    QMessageBox, QApplication
)
from PySide6.QtCore import Qt, QFile, QTextStream

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
        
        # 先加载全局样式表
        self._load_style_sheet()
        
        # 创建UI
        self._create_ui()
        
        # 应用特定样式
        self._apply_specific_styles()
        
        # 加载当前配置
        self._load_config()
        
        # 如果是首次运行，显示欢迎消息
        if self.first_run:
            self._show_welcome_message()
    
    def _load_style_sheet(self):
        """
        加载样式表，确保能找到样式表文件
        """
        # 尝试相对于应用根目录加载
        style_file_path = os.path.join("assets", "styles", "app_style.qss")
        
        # 如果当前目录是src，则返回上一级查找资源
        if os.path.basename(os.getcwd()) == "src":
            style_file_path = os.path.join("..", style_file_path)
        
        print(f"尝试加载样式表: {style_file_path}")
        
        if os.path.exists(style_file_path):
            style_file = QFile(style_file_path)
            if style_file.open(QFile.ReadOnly | QFile.Text):
                stream = QTextStream(style_file)
                style_sheet = stream.readAll()
                self.setStyleSheet(style_sheet)
                style_file.close()
                print("样式表加载成功")
            else:
                print(f"无法打开样式表文件: {style_file_path}")
        else:
            print(f"样式表文件不存在: {style_file_path}")
            # 尝试其他可能的路径
            alternative_paths = [
                os.path.join("src", "..", "assets", "styles", "app_style.qss"),
                os.path.join("..", "assets", "styles", "app_style.qss"),
                os.path.join("assets", "styles", "app_style.qss")
            ]
            
            for path in alternative_paths:
                print(f"尝试替代路径: {path}")
                if os.path.exists(path):
                    style_file = QFile(path)
                    if style_file.open(QFile.ReadOnly | QFile.Text):
                        stream = QTextStream(style_file)
                        style_sheet = stream.readAll()
                        self.setStyleSheet(style_sheet)
                        style_file.close()
                        print(f"样式表从替代路径加载成功: {path}")
                        break
    
    def _apply_specific_styles(self):
        """
        直接对关键组件应用样式，确保样式正确应用
        但仅应用必要的样式，不干扰QSS文件中设置的按钮样式
        """
        # 设置输入框样式
        input_style = """
            background-color: white;
            color: #000000;
            border: 1px solid #888888;
            border-radius: 4px;
            padding: 5px;
            selection-background-color: #4a86e8;
        """
        self.api_key_edit.setStyleSheet(input_style)
        self.api_url_edit.setStyleSheet(input_style)
        
        # 设置下拉框样式
        combobox_style = """
            background-color: white;
            color: #000000;
            border: 1px solid #888888;
            border-radius: 4px;
            padding: 5px;
            min-height: 25px;
        """
        self.api_provider_combobox.setStyleSheet(combobox_style)
        self.api_model_combobox.setStyleSheet(combobox_style)
        
        # 设置API信息标签样式
        self.api_info_label.setStyleSheet("""
            color: #2E8B57; 
            background-color: rgba(46, 139, 87, 0.1); 
            padding: 8px; 
            border-radius: 4px;
        """)
        
        # 重要：显式设置确定和取消按钮的样式，包括hover和pressed状态
        ok_button = self.button_box.button(QDialogButtonBox.Ok)
        if ok_button:
            # 正常状态下的按钮颜色
            ok_button.setStyleSheet("""
                background-color: #2E8B57; 
                color: white; 
                font-weight: bold;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                min-width: 80px;
            """)
            # 设置hover和press状态下的按钮颜色
            ok_button.installEventFilter(self)
            # 使用QSS样式表来设置hover和pressed状态
            ok_button.setStyleSheet("""
                QPushButton {
                    background-color: #2E8B57; 
                    color: white; 
                    font-weight: bold;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #267349;
                }
                QPushButton:pressed {
                    background-color: #1e5e39;
                }
            """)
            # 设置鼠标悬停时显示手型
            ok_button.setCursor(Qt.PointingHandCursor)
            
        cancel_button = self.button_box.button(QDialogButtonBox.Cancel)
        if cancel_button:
            cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #cd5c5c; 
                    color: white; 
                    font-weight: bold;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    min-width: 80px;
                }
                QPushButton:hover {
                    background-color: #d87070;
                }
                QPushButton:pressed {
                    background-color: #b04545;
                }
            """)
            # 设置鼠标悬停时显示手型
            cancel_button.setCursor(Qt.PointingHandCursor)
    
    def _create_ui(self):
        """
        创建UI组件
        """
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        
        # 添加标题
        title_label = QLabel("AI API设置")
        title_label.setObjectName("titleLabel")
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 创建表单布局
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight)
        form_layout.setFieldGrowthPolicy(QFormLayout.ExpandingFieldsGrow)
        form_layout.setSpacing(10)
        
        # API提供商选择
        self.api_provider_combobox = QComboBox()
        self.api_provider_combobox.setObjectName("apiProviderComboBox")
        self.api_provider_combobox.addItems([
            "DeepSeek API",
            "OpenAI API",
            "其他"
        ])
        self.api_provider_combobox.currentIndexChanged.connect(self._on_provider_changed)
        form_layout.addRow("API提供商:", self.api_provider_combobox)
        
        # API密钥
        self.api_key_edit = QLineEdit()
        self.api_key_edit.setObjectName("apiKeyEdit")
        self.api_key_edit.setEchoMode(QLineEdit.Password)
        self.api_key_edit.setPlaceholderText("输入您的API密钥")
        self.api_key_edit.setMinimumWidth(300)
        form_layout.addRow("API密钥:", self.api_key_edit)
        
        # API URL
        self.api_url_edit = QLineEdit()
        self.api_url_edit.setObjectName("apiUrlEdit")
        self.api_url_edit.setPlaceholderText("例如: https://api.deepseek.com")
        form_layout.addRow("API URL:", self.api_url_edit)
        
        # 模型选择
        self.api_model_combobox = QComboBox()
        self.api_model_combobox.setObjectName("apiModelComboBox")
        self.api_model_combobox.setEditable(True)
        form_layout.addRow("AI模型:", self.api_model_combobox)
        
        # 添加表单到主布局
        main_layout.addLayout(form_layout)
        
        # 添加描述标签
        description_label = QLabel(
            "请输入您的API密钥和URL。这些信息将用于调用AI服务来分析文件命名模式。"
            "您的API密钥将安全地存储在本地配置中，不会发送给任何第三方。"
        )
        description_label.setWordWrap(True)
        description_label.setObjectName("descriptionLabel")
        main_layout.addWidget(description_label)
        
        # 添加API说明
        self.api_info_label = QLabel()
        self.api_info_label.setWordWrap(True)
        self.api_info_label.setObjectName("apiInfoLabel")
        main_layout.addWidget(self.api_info_label)
        
        # 添加按钮
        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.setObjectName("dialogButtonBox")
        self.button_box.button(QDialogButtonBox.Ok).setText("确定")
        self.button_box.button(QDialogButtonBox.Cancel).setText("取消")
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        main_layout.addWidget(self.button_box)
        
        # 设置间距和边距
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 初始化默认API提供商
        self._on_provider_changed(0)  # DeepSeek API
    
    def _on_provider_changed(self, index):
        """
        API提供商变更处理
        
        Args:
            index (int): 提供商索引
        """
        # 清空模型选择下拉框
        self.api_model_combobox.clear()
        
        if index == 0:  # DeepSeek API
            # 设置默认URL
            self.api_url_edit.setText("https://api.deepseek.com")
            
            # 添加DeepSeek模型
            self.api_model_combobox.addItems([
                "deepseek-chat",
                "deepseek-reasoner"
            ])
            
            # 设置DeepSeek API说明
            self.api_info_label.setText(
                "DeepSeek API使用说明：\n"
                "1. 访问 https://platform.deepseek.com/api_keys 申请API密钥\n"
                "2. 默认API URL: https://api.deepseek.com\n"
                "3. 推荐模型: deepseek-chat (DeepSeek-V3)"
            )
            
        elif index == 1:  # OpenAI API
            # 设置默认URL
            self.api_url_edit.setText("https://api.openai.com/v1")
            
            # 添加OpenAI模型
            self.api_model_combobox.addItems([
                "gpt-3.5-turbo",
                "gpt-4"
            ])
            
            # 设置OpenAI API说明
            self.api_info_label.setText(
                "OpenAI API使用说明：\n"
                "1. 访问 https://platform.openai.com/api-keys 申请API密钥\n"
                "2. 默认API URL: https://api.openai.com/v1\n"
                "3. 推荐模型: gpt-3.5-turbo 或 gpt-4"
            )
            
        else:  # 其他
            # 清空URL
            self.api_url_edit.setText("")
            self.api_url_edit.setPlaceholderText("输入API基础URL")
            
            # 允许自定义模型名称
            self.api_model_combobox.setEditable(True)
            self.api_model_combobox.setPlaceholderText("输入模型名称")
            
            # 设置其他API说明
            self.api_info_label.setText(
                "其他API提供商使用说明：\n"
                "1. 请确保您输入的API URL是完整的基础URL\n"
                "2. 输入完整的模型名称\n"
                "3. 该应用程序使用与OpenAI兼容的API格式"
            )
        
        # 重新应用样式，确保动态更新后的组件样式正确
        self._apply_specific_styles()
    
    def _load_config(self):
        """
        从配置管理器加载配置
        """
        config = self.config_manager.get_config()
        
        # 设置API提供商
        provider = config.get('api_provider', 'DeepSeek API')
        index = self.api_provider_combobox.findText(provider)
        if index >= 0:
            self.api_provider_combobox.setCurrentIndex(index)
        
        # 设置API密钥
        if 'api_key' in config:
            self.api_key_edit.setText(config['api_key'])
        
        # 设置API URL
        if 'api_url' in config:
            self.api_url_edit.setText(config['api_url'])
        
        # 设置模型
        if 'api_model' in config and config['api_model']:
            # 确保模型列表已经根据供应商更新
            self._on_provider_changed(self.api_provider_combobox.currentIndex())
            
            index = self.api_model_combobox.findText(config['api_model'])
            if index >= 0:
                self.api_model_combobox.setCurrentIndex(index)
            else:
                self.api_model_combobox.setCurrentText(config['api_model'])
    
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
            'api_provider': self.api_provider_combobox.currentText().strip(),
            'api_key': self.api_key_edit.text().strip(),
            'api_url': self.api_url_edit.text().strip(),
            'api_model': self.api_model_combobox.currentText().strip()
        }
        
        self.config_manager.update_config(config)
        
        # 调用父类的accept方法
        super().accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    settings_dialog = SettingsDialog()
    settings_dialog.show()
    sys.exit(app.exec())
