#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# 添加父目录到路径以便导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.config_manager import ConfigManager

class TestConfigManager(unittest.TestCase):
    """
    配置管理器测试类
    """
    
    def setUp(self):
        """
        测试前设置
        """
        self.config_manager = ConfigManager()
    
    def test_get_config(self):
        """
        测试获取配置
        """
        # 默认值
        self.assertEqual(self.config_manager.get_config('api_key'), '')
        self.assertEqual(self.config_manager.get_config('non_existent_key', 'default'), 'default')
        
        # 整个配置
        config = self.config_manager.get_config()
        self.assertIsInstance(config, dict)
        self.assertIn('api_key', config)
    
    def test_update_config(self):
        """
        测试更新配置
        """
        # 更新配置
        new_config = {
            'api_key': 'test_key',
            'api_url': 'https://test.api.com',
            'api_model': 'test_model'
        }
        self.config_manager.update_config(new_config)
        
        # 验证更新
        self.assertEqual(self.config_manager.get_config('api_key'), 'test_key')
        self.assertEqual(self.config_manager.get_config('api_url'), 'https://test.api.com')
        self.assertEqual(self.config_manager.get_config('api_model'), 'test_model')
    
    def test_is_api_configured(self):
        """
        测试API配置检查
        """
        # 初始状态
        self.assertFalse(self.config_manager.is_api_configured())
        
        # 设置API配置
        self.config_manager.update_config({
            'api_key': 'test_key',
            'api_url': 'https://test.api.com'
        })
        
        # 验证状态
        self.assertTrue(self.config_manager.is_api_configured())
        
        # 清除API配置
        self.config_manager.update_config({
            'api_key': '',
            'api_url': 'https://test.api.com'
        })
        
        # 验证状态
        self.assertFalse(self.config_manager.is_api_configured())
    
    def test_first_run(self):
        """
        测试首次运行标志
        """
        # 初始状态
        self.assertTrue(self.config_manager.is_first_run())
        
        # 设置首次运行完成
        self.config_manager.set_first_run_completed()
        
        # 验证状态
        self.assertFalse(self.config_manager.is_first_run())

if __name__ == '__main__':
    unittest.main()