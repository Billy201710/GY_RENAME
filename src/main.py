#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QDir

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
    
    # 运行应用主循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()