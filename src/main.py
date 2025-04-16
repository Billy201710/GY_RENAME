#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from PySide6.QtWidgets import QApplication, QLabel, QHBoxLayout, QWidget
from PySide6.QtCore import QDir
from PySide6.QtGui import QPixmap

# 确保能够引用项目内模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.append(parent_dir)

from views.main_window import MainWindow
from utils.config_manager import ConfigManager

def main():
    """
    应用程序主入口
    """
    # 创建应用实例
    app = QApplication(sys.argv)
    app.setApplicationName("GY_Rename")
    app.setOrganizationName("GY")
    
    # 初始化配置管理器
    config_manager = ConfigManager()
    
    # 创建并显示主窗口
    main_window = MainWindow(config_manager)
    main_window.show()
    
    # 测试代码 - 已注释掉
    """
    from views.settings_dialog import SettingsDialog
    from PySide6.QtWidgets import QDialogButtonBox
    
    dialog = SettingsDialog(config_manager)
    
    # 直接设置确定和取消按钮的样式
    ok_button = dialog.button_box.button(QDialogButtonBox.Ok)
    if ok_button:
        ok_button.setStyleSheet("background-color: #2E8B57; color: white; font-weight: bold;")
    
    cancel_button = dialog.button_box.button(QDialogButtonBox.Cancel)
    if cancel_button:
        cancel_button.setStyleSheet("background-color: #cd5c5c; color: white; font-weight: bold;")
    
    dialog.show()
    """
    
    # 运行应用主循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()