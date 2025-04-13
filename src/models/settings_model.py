#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import os
from PySide6.QtCore import QObject, Signal, Slot, Property

class SettingsModel(QObject):
    """
    设置模型类，管理应用程序设置
    """
    
    # 定义信号
    settingsChanged = Signal(dict)
    
    def __init__(self, parent=None):
        """
        初始化设置模型
        
        Args:
            parent: 父对象
        """
        super().__init__(parent)
        
        # 设置默认值
        self._settings = {
            'api': {
                'key': '',
                'url': 'https://api.openai.com/v1/chat/completions',
                'model': 'gpt-3.5-turbo'
            },
            'app': {
                'first_run': True,
                'theme': 'system',
                'max_history': 10
            },
            'rename': {
                'preview_before_apply': True,
                'backup_original_files': True,
                'backup_directory': 'backup'
            }
        }
    
    @Slot(dict)
    def update_settings(self, settings):
        """
        更新设置
        
        Args:
            settings (dict): 新设置，将与当前设置合并
            
        Returns:
            bool: 如果成功更新返回True，否则返回False
        """
        # 深度更新设置
        self._deep_update(self._settings, settings)
        
        # 发出信号
        self.settingsChanged.emit(self._settings)
        
        return True
    
    def _deep_update(self, target_dict, update_dict):
        """
        深度更新字典
        
        Args:
            target_dict (dict): 目标字典
            update_dict (dict): 更新字典
        """
        for key, value in update_dict.items():
            if isinstance(value, dict) and key in target_dict and isinstance(target_dict[key], dict):
                self._deep_update(target_dict[key], value)
            else:
                target_dict[key] = value
    
    def get_settings(self):
        """
        获取所有设置
        
        Returns:
            dict: 设置字典
        """
        return self._settings
    
    def get_setting(self, key_path, default=None):
        """
        获取指定设置项
        
        Args:
            key_path (str): 设置项路径，格式为"section.key"，例如"api.key"
            default: 默认值，当设置项不存在时返回
            
        Returns:
            如果存在返回设置值，否则返回默认值
        """
        # 解析路径
        keys = key_path.split('.')
        
        # 逐级查找
        value = self._settings
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        
        return value
    
    @Slot(str, object)
    def set_setting(self, key_path, value):
        """
        设置指定设置项
        
        Args:
            key_path (str): 设置项路径，格式为"section.key"，例如"api.key"
            value: 设置值
            
        Returns:
            bool: 如果成功设置返回True，否则返回False
        """
        # 解析路径
        keys = key_path.split('.')
        
        # 如果路径为空，返回失败
        if not keys:
            return False
        
        # 逐级查找
        target = self._settings
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]
        
        # 设置值
        target[keys[-1]] = value
        
        # 发出信号
        self.settingsChanged.emit(self._settings)
        
        return True
    
    def save_to_file(self, file_path):
        """
        保存设置到文件
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            bool: 如果成功保存返回True，否则返回False
        """
        try:
            # 确保目录存在
            dir_path = os.path.dirname(file_path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path)
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存设置失败: {str(e)}")
            return False
    
    def load_from_file(self, file_path):
        """
        从文件加载设置
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            bool: 如果成功加载返回True，否则返回False
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False
            
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                settings = json.load(f)
            
            # 更新设置
            self.update_settings(settings)
            
            return True
        except Exception as e:
            print(f"加载设置失败: {str(e)}")
            return False
    
    def is_first_run(self):
        """
        检查是否首次运行应用
        
        Returns:
            bool: 如果是首次运行返回True，否则返回False
        """
        return self.get_setting('app.first_run', True)
    
    def set_first_run_completed(self):
        """
        设置首次运行完成标志
        
        Returns:
            bool: 如果成功设置返回True，否则返回False
        """
        return self.set_setting('app.first_run', False)
    
    def is_api_configured(self):
        """
        检查API是否已配置
        
        Returns:
            bool: 如果API已配置返回True，否则返回False
        """
        api_key = self.get_setting('api.key', '')
        api_url = self.get_setting('api.url', '')
        return bool(api_key) and bool(api_url)