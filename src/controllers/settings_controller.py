#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PySide6.QtCore import QObject, Signal, Slot, QSettings

from models.settings_model import SettingsModel

class SettingsController(QObject):
    """
    设置控制器类，处理应用程序设置相关操作
    """
    
    # 定义信号
    settings_updated = Signal(dict)  # 设置更新信号，参数为新设置
    
    def __init__(self, config_manager, parent=None):
        """
        初始化设置控制器
        
        Args:
            config_manager: 配置管理器实例
            parent: 父对象
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.settings_model = SettingsModel(parent=self)
        
        # 连接模型信号
        self.settings_model.settingsChanged.connect(self._on_settings_changed)
        
        # 加载设置
        self._load_settings()
    
    def _load_settings(self):
        """
        加载设置
        """
        # 获取设置文件路径
        settings_path = self._get_settings_file_path()
        
        # 尝试从文件加载
        if os.path.exists(settings_path):
            self.settings_model.load_from_file(settings_path)
        
        # 如果配置管理器中有设置，优先使用
        api_key = self.config_manager.get_config('api_key')
        api_url = self.config_manager.get_config('api_url')
        api_model = self.config_manager.get_config('api_model')
        
        if api_key:
            self.settings_model.set_setting('api.key', api_key)
        
        if api_url:
            self.settings_model.set_setting('api.url', api_url)
        
        if api_model:
            self.settings_model.set_setting('api.model', api_model)
    
    def _get_settings_file_path(self):
        """
        获取设置文件路径
        
        Returns:
            str: 设置文件路径
        """
        # 使用QSettings获取配置目录
        q_settings = QSettings()
        org_name = q_settings.organizationName()
        app_name = q_settings.applicationName()
        
        # 如果组织名或应用名为空，使用默认值
        if not org_name:
            org_name = "GY"
        if not app_name:
            app_name = "GY_Rename"
        
        # 根据平台确定配置目录
        if os.name == 'nt':  # Windows
            config_dir = os.path.join(os.environ['APPDATA'], org_name, app_name)
        elif os.name == 'posix':  # macOS/Linux
            config_dir = os.path.expanduser(f"~/.config/{org_name}/{app_name}")
        else:
            # 默认使用当前目录
            config_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'config')
        
        # 确保目录存在
        os.makedirs(config_dir, exist_ok=True)
        
        # 返回设置文件路径
        return os.path.join(config_dir, 'settings.json')
    
    @Slot(dict)
    def update_settings(self, settings):
        """
        更新设置
        
        Args:
            settings (dict): 新设置
            
        Returns:
            bool: 如果成功更新返回True，否则返回False
        """
        # 更新模型
        result = self.settings_model.update_settings(settings)
        
        if result:
            # 保存设置
            self._save_settings()
            
            # 更新配置管理器
            self._update_config_manager()
        
        return result
    
    def _save_settings(self):
        """
        保存设置
        
        Returns:
            bool: 如果成功保存返回True，否则返回False
        """
        settings_path = self._get_settings_file_path()
        return self.settings_model.save_to_file(settings_path)
    
    def _update_config_manager(self):
        """
        更新配置管理器
        """
        # 获取API设置
        api_key = self.settings_model.get_setting('api.key', '')
        api_url = self.settings_model.get_setting('api.url', '')
        api_model = self.settings_model.get_setting('api.model', '')
        
        # 更新配置管理器
        config = {
            'api_key': api_key,
            'api_url': api_url,
            'api_model': api_model,
            'first_run': self.settings_model.get_setting('app.first_run', True)
        }
        
        self.config_manager.update_config(config)
    
    @Slot(str)
    def set_api_key(self, api_key):
        """
        设置API密钥
        
        Args:
            api_key (str): API密钥
            
        Returns:
            bool: 如果成功设置返回True，否则返回False
        """
        result = self.settings_model.set_setting('api.key', api_key)
        
        if result:
            # 保存设置
            self._save_settings()
            
            # 更新配置管理器
            self.config_manager.update_config({'api_key': api_key})
        
        return result
    
    @Slot(str)
    def set_api_url(self, api_url):
        """
        设置API URL
        
        Args:
            api_url (str): API URL
            
        Returns:
            bool: 如果成功设置返回True，否则返回False
        """
        result = self.settings_model.set_setting('api.url', api_url)
        
        if result:
            # 保存设置
            self._save_settings()
            
            # 更新配置管理器
            self.config_manager.update_config({'api_url': api_url})
        
        return result
    
    @Slot(str)
    def set_api_model(self, api_model):
        """
        设置API模型
        
        Args:
            api_model (str): API模型
            
        Returns:
            bool: 如果成功设置返回True，否则返回False
        """
        result = self.settings_model.set_setting('api.model', api_model)
        
        if result:
            # 保存设置
            self._save_settings()
            
            # 更新配置管理器
            self.config_manager.update_config({'api_model': api_model})
        
        return result
    
    @Slot()
    def set_first_run_completed(self):
        """
        设置首次运行完成标志
        
        Returns:
            bool: 如果成功设置返回True，否则返回False
        """
        result = self.settings_model.set_first_run_completed()
        
        if result:
            # 保存设置
            self._save_settings()
            
            # 更新配置管理器
            self.config_manager.update_config({'first_run': False})
        
        return result
    
    def get_settings(self):
        """
        获取所有设置
        
        Returns:
            dict: 设置字典
        """
        return self.settings_model.get_settings()
    
    def get_setting(self, key_path, default=None):
        """
        获取指定设置项
        
        Args:
            key_path (str): 设置项路径
            default: 默认值
            
        Returns:
            如果存在返回设置值，否则返回默认值
        """
        return self.settings_model.get_setting(key_path, default)
    
    def is_api_configured(self):
        """
        检查API是否已配置
        
        Returns:
            bool: 如果API已配置返回True，否则返回False
        """
        return self.settings_model.is_api_configured()
    
    def is_first_run(self):
        """
        检查是否首次运行应用
        
        Returns:
            bool: 如果是首次运行返回True，否则返回False
        """
        return self.settings_model.is_first_run()
    
    # 私有方法，处理信号
    def _on_settings_changed(self, settings):
        """
        设置变更事件处理
        
        Args:
            settings (dict): 新设置
        """
        # 转发信号
        self.settings_updated.emit(settings)