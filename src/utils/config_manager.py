#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
from PySide6.QtCore import QObject, QSettings, Signal

class ConfigManager(QObject):
    """
    配置管理器类，负责管理应用程序的配置信息，
    包括AI API密钥、API URL等设置项
    """
    
    # 定义配置变更信号
    config_changed = Signal(dict)
    
    def __init__(self, parent=None):
        """
        初始化配置管理器
        """
        super().__init__(parent)
        self.settings = QSettings()
        self.config = {}
        self.load_config()
    
    def load_config(self):
        """
        从存储中加载配置
        """
        # 加载API配置
        self.config['api_key'] = self.settings.value('api/key', '')
        self.config['api_url'] = self.settings.value('api/url', '')
        self.config['api_model'] = self.settings.value('api/model', '')
        
        # 加载应用设置
        self.config['first_run'] = self.settings.value('app/first_run', True, bool)
    
    def save_config(self):
        """
        保存配置到存储
        """
        # 保存API配置
        self.settings.setValue('api/key', self.config.get('api_key', ''))
        self.settings.setValue('api/url', self.config.get('api_url', ''))
        self.settings.setValue('api/model', self.config.get('api_model', ''))
        
        # 保存应用设置
        self.settings.setValue('app/first_run', self.config.get('first_run', True))
        
        # 触发配置变更信号
        self.config_changed.emit(self.config)
    
    def update_config(self, config_dict):
        """
        更新配置
        
        Args:
            config_dict (dict): 包含需要更新的配置项的字典
        """
        self.config.update(config_dict)
        self.save_config()
    
    def get_config(self, key=None, default=None):
        """
        获取配置项
        
        Args:
            key (str): 配置项键名
            default: 默认值，当配置项不存在时返回
            
        Returns:
            如果指定了key，返回对应的配置值；否则返回整个配置字典
        """
        if key:
            return self.config.get(key, default)
        return self.config
    
    def is_api_configured(self):
        """
        检查API是否已配置
        
        Returns:
            bool: 如果API已配置返回True，否则返回False
        """
        return bool(self.config.get('api_key')) and bool(self.config.get('api_url'))
    
    def is_first_run(self):
        """
        检查是否首次运行应用
        
        Returns:
            bool: 如果是首次运行返回True，否则返回False
        """
        return self.config.get('first_run', True)
    
    def set_first_run_completed(self):
        """
        设置首次运行完成标志
        """
        self.config['first_run'] = False
        self.save_config()