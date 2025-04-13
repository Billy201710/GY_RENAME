#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest
import tempfile
import shutil

# 添加父目录到路径以便导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.utils.file_operations import FileOperations

class TestFileOperations(unittest.TestCase):
    """
    文件操作测试类
    """
    
    def setUp(self):
        """
        测试前设置
        """
        # 创建临时目录
        self.test_dir = tempfile.mkdtemp()
        
        # 创建测试文件
        self.test_file_path = os.path.join(self.test_dir, "test.txt")
        with open(self.test_file_path, "w") as f:
            f.write("Test content")
    
    def tearDown(self):
        """
        测试后清理
        """
        # 移除临时目录
        shutil.rmtree(self.test_dir)
    
    def test_rename_file(self):
        """
        测试重命名文件
        """
        # 重命名文件
        success, result = FileOperations.rename_file(self.test_file_path, "renamed.txt")
        
        # 验证结果
        self.assertTrue(success)
        renamed_path = os.path.join(self.test_dir, "renamed.txt")
        self.assertEqual(result, renamed_path)
        self.assertTrue(os.path.exists(renamed_path))
        self.assertFalse(os.path.exists(self.test_file_path))
        
        # 尝试重命名不存在的文件
        success, result = FileOperations.rename_file(self.test_file_path, "non_existent.txt")
        
        # 验证结果
        self.assertFalse(success)
        self.assertIn("不存在", result)
    
    def test_create_backup(self):
        """
        测试创建备份
        """
        # 创建备份
        success, result = FileOperations.create_backup(self.test_file_path, self.test_dir)
        
        # 验证结果
        self.assertTrue(success)
        self.assertTrue(os.path.exists(result))
        
        # 读取备份内容
        with open(result, "r") as f:
            content = f.read()
        
        # 验证内容
        self.assertEqual(content, "Test content")
        
        # 尝试备份不存在的文件
        non_existent_path = os.path.join(self.test_dir, "non_existent.txt")
        success, result = FileOperations.create_backup(non_existent_path, self.test_dir)
        
        # 验证结果
        self.assertFalse(success)
        self.assertIn("不存在", result)
    
    def test_get_file_size(self):
        """
        测试获取文件大小
        """
        # 获取文件大小
        success, size = FileOperations.get_file_size(self.test_file_path)
        
        # 验证结果
        self.assertTrue(success)
        self.assertEqual(size, len("Test content"))
        
        # 尝试获取不存在的文件大小
        non_existent_path = os.path.join(self.test_dir, "non_existent.txt")
        success, result = FileOperations.get_file_size(non_existent_path)
        
        # 验证结果
        self.assertFalse(success)
        self.assertIn("不存在", result)
    
    def test_format_file_size(self):
        """
        测试格式化文件大小
        """
        # 测试不同大小
        self.assertEqual(FileOperations.format_file_size(500), "500.00 B")
        self.assertEqual(FileOperations.format_file_size(1500), "1.46 KB")
        self.assertEqual(FileOperations.format_file_size(1500000), "1.43 MB")
        self.assertEqual(FileOperations.format_file_size(1500000000), "1.40 GB")
    
    def test_is_valid_filename(self):
        """
        测试文件名是否有效
        """
        # 测试有效文件名
        self.assertTrue(FileOperations.is_valid_filename("valid_file.txt"))
        self.assertTrue(FileOperations.is_valid_filename("valid-file.txt"))
        self.assertTrue(FileOperations.is_valid_filename("valid file.txt"))
        
        # 测试无效文件名
        if os.name == 'nt':  # Windows
            self.assertFalse(FileOperations.is_valid_filename("invalid/file.txt"))
            self.assertFalse(FileOperations.is_valid_filename("invalid:file.txt"))
            self.assertFalse(FileOperations.is_valid_filename("invalid*file.txt"))
            self.assertFalse(FileOperations.is_valid_filename("invalid?file.txt"))
            self.assertFalse(FileOperations.is_valid_filename('invalid"file.txt'))
            self.assertFalse(FileOperations.is_valid_filename("invalid<file.txt"))
            self.assertFalse(FileOperations.is_valid_filename("invalid>file.txt"))
            self.assertFalse(FileOperations.is_valid_filename("invalid|file.txt"))
    
    def test_sanitize_filename(self):
        """
        测试净化文件名
        """
        # 测试净化
        if os.name == 'nt':  # Windows
            self.assertEqual(FileOperations.sanitize_filename("invalid/file.txt"), "invalid_file.txt")
            self.assertEqual(FileOperations.sanitize_filename("invalid:file.txt"), "invalid_file.txt")
            self.assertEqual(FileOperations.sanitize_filename("invalid*file.txt"), "invalid_file.txt")
            self.assertEqual(FileOperations.sanitize_filename("invalid?file.txt"), "invalid_file.txt")
            self.assertEqual(FileOperations.sanitize_filename('invalid"file.txt'), "invalid_file.txt")
            self.assertEqual(FileOperations.sanitize_filename("invalid<file.txt"), "invalid_file.txt")
            self.assertEqual(FileOperations.sanitize_filename("invalid>file.txt"), "invalid_file.txt")
            self.assertEqual(FileOperations.sanitize_filename("invalid|file.txt"), "invalid_file.txt")
        
        # 测试空文件名
        self.assertEqual(FileOperations.sanitize_filename(""), "unnamed_file")
        self.assertEqual(FileOperations.sanitize_filename("   "), "unnamed_file")
        
        # 测试长文件名
        long_name = "a" * 300
        self.assertTrue(len(FileOperations.sanitize_filename(long_name)) <= 255)

if __name__ == '__main__':
    unittest.main()