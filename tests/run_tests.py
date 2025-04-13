#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import unittest

# 添加父目录到路径以便导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# 导入测试模块
from test_config_manager import TestConfigManager
from test_file_model import TestFileModel
from test_file_operations import TestFileOperations

if __name__ == '__main__':
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试用例
    test_suite.addTest(unittest.makeSuite(TestConfigManager))
    test_suite.addTest(unittest.makeSuite(TestFileModel))
    test_suite.addTest(unittest.makeSuite(TestFileOperations))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 输出结果摘要
    print("\n测试结果摘要:")
    print(f"运行测试用例: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    
    # 设置退出码
    sys.exit(len(result.failures) + len(result.errors))