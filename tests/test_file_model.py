#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# 添加父目录到路径以便导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.models.file_model import FileModel, FileItem

class TestFileModel(unittest.TestCase):
    """
    文件模型测试类
    """
    
    def setUp(self):
        """
        测试前设置
        """
        self.file_model = FileModel()
    
    def test_file_item(self):
        """
        测试文件项
        """
        # 创建文件项
        file_item = FileItem(name="test.txt", path="/path/to/test.txt")
        
        # 测试初始值
        self.assertEqual(file_item.name, "test.txt")
        self.assertEqual(file_item.path, "/path/to/test.txt")
        self.assertEqual(file_item.get_original_name(), "test.txt")
        
        # 测试修改值
        file_item.name = "new_test.txt"
        self.assertEqual(file_item.name, "new_test.txt")
        
        # 测试重置
        file_item.reset_to_original()
        self.assertEqual(file_item.name, "test.txt")
        
        # 测试字典转换
        file_dict = file_item.to_dict()
        self.assertIsInstance(file_dict, dict)
        self.assertEqual(file_dict['name'], "test.txt")
        self.assertEqual(file_dict['path'], "/path/to/test.txt")
        self.assertEqual(file_dict['original_name'], "test.txt")
        
        # 测试从字典创建
        new_file_item = FileItem.from_dict(file_dict)
        self.assertEqual(new_file_item.name, "test.txt")
        self.assertEqual(new_file_item.path, "/path/to/test.txt")
        self.assertEqual(new_file_item.get_original_name(), "test.txt")
    
    def test_add_file(self):
        """
        测试添加文件
        """
        # 添加文件
        file_item = self.file_model.add_file("/path/to/test.txt", "test.txt")
        
        # 验证添加
        self.assertIsNotNone(file_item)
        self.assertEqual(file_item.name, "test.txt")
        self.assertEqual(file_item.path, "/path/to/test.txt")
        
        # 验证模型状态
        self.assertEqual(self.file_model.get_file_count(), 1)
        self.assertTrue(self.file_model.has_file("test.txt"))
        
        # 验证获取文件
        file_item = self.file_model.get_file("test.txt")
        self.assertIsNotNone(file_item)
        self.assertEqual(file_item.name, "test.txt")
        
        # 验证获取所有文件
        files = self.file_model.get_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "test.txt")
        
        # 验证获取文件字典
        file_dicts = self.file_model.get_file_dicts()
        self.assertEqual(len(file_dicts), 1)
        self.assertEqual(file_dicts[0]['name'], "test.txt")
    
    def test_remove_file(self):
        """
        测试移除文件
        """
        # 添加文件
        self.file_model.add_file("/path/to/test.txt", "test.txt")
        
        # 验证添加
        self.assertEqual(self.file_model.get_file_count(), 1)
        
        # 移除文件
        result = self.file_model.remove_file("test.txt")
        
        # 验证移除
        self.assertTrue(result)
        self.assertEqual(self.file_model.get_file_count(), 0)
        self.assertFalse(self.file_model.has_file("test.txt"))
        
        # 尝试移除不存在的文件
        result = self.file_model.remove_file("non_existent.txt")
        
        # 验证结果
        self.assertFalse(result)
    
    def test_clear(self):
        """
        测试清空文件
        """
        # 添加文件
        self.file_model.add_file("/path/to/test1.txt", "test1.txt")
        self.file_model.add_file("/path/to/test2.txt", "test2.txt")
        
        # 验证添加
        self.assertEqual(self.file_model.get_file_count(), 2)
        
        # 清空文件
        self.file_model.clear()
        
        # 验证清空
        self.assertEqual(self.file_model.get_file_count(), 0)
        self.assertFalse(self.file_model.has_file("test1.txt"))
        self.assertFalse(self.file_model.has_file("test2.txt"))
    
    def test_update_file_name(self):
        """
        测试更新文件名
        """
        # 添加文件
        self.file_model.add_file("/path/to/test.txt", "test.txt")
        
        # 更新文件名
        result = self.file_model.update_file_name("test.txt", "new_test.txt")
        
        # 验证更新
        self.assertTrue(result)
        self.assertFalse(self.file_model.has_file("test.txt"))
        self.assertTrue(self.file_model.has_file("new_test.txt"))
        
        # 验证文件信息
        file_item = self.file_model.get_file("new_test.txt")
        self.assertEqual(file_item.name, "new_test.txt")
        self.assertEqual(file_item.path, "/path/to/test.txt")  # 路径不变
        
        # 尝试更新不存在的文件
        result = self.file_model.update_file_name("non_existent.txt", "new_name.txt")
        
        # 验证结果
        self.assertFalse(result)
        
        # 尝试更新为已存在的文件名
        self.file_model.add_file("/path/to/test2.txt", "test2.txt")
        result = self.file_model.update_file_name("test2.txt", "new_test.txt")
        
        # 验证结果
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()