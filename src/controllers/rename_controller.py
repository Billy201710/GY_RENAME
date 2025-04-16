#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import asyncio
from PySide6.QtCore import QObject, Signal, Slot, QThreadPool, QRunnable, QObject

from models.rename_model import RenameModel
from utils.ai_client import AIClient

class RenameController(QObject):
    """
    重命名控制器类，处理文件重命名相关操作
    """
    
    # 定义信号
    example_updated = Signal(str, object)  # 示例更新信号，参数为文件名和新数据
    analysis_started = Signal()  # 分析开始信号
    analysis_completed = Signal(dict)  # 分析完成信号，参数为分析结果
    analysis_failed = Signal(str)  # 分析失败信号，参数为错误消息
    analysis_result_updated = Signal(dict)  # 分析结果更新信号，参数为重命名映射
    rename_started = Signal()  # 重命名开始信号
    rename_completed = Signal(dict)  # 重命名完成信号，参数为结果信息
    rename_failed = Signal(str)  # 重命名失败信号，参数为错误消息
    
    def __init__(self, config_manager, parent=None):
        """
        初始化重命名控制器
        
        Args:
            config_manager: 配置管理器实例
            parent: 父对象
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.rename_model = RenameModel(parent=self)
        self.ai_client = AIClient(config_manager, parent=self)
        
        # 连接AI客户端信号
        self.ai_client.analysis_started.connect(self._on_analysis_started)
        self.ai_client.analysis_completed.connect(self._on_analysis_completed)
        self.ai_client.analysis_failed.connect(self._on_analysis_failed)
        
        # 连接模型信号
        self.rename_model.exampleUpdated.connect(self._on_example_updated)
        self.rename_model.currentHistoryChanged.connect(self._on_current_history_changed)
    
    @Slot(str)
    def edit_example(self, file_name):
        """
        编辑重命名示例
        
        Args:
            file_name (str): 文件名
            
        Returns:
            tuple: (成功标志, 结果或错误消息)
        """
        # 只需记录这个文件名已被选为示例
        # 文本实际编辑由FileListWidget中的文本编辑框处理
        # 添加示例记录（初始值为原始文件名，等待用户编辑后更新）
        result = self.rename_model.add_example(file_name, file_name)
        
        if result:
            return True, {"original_name": file_name, "new_name": file_name}
        else:
            return False, "准备编辑示例失败"
    
    @Slot(list, list)
    def analyze_naming_pattern(self, original_files, example_files):
        """
        分析命名模式
        
        Args:
            original_files (list): 原始文件列表，每个元素是一个字典，包含name和path属性
            example_files (list): 示例文件列表，每个元素是一个字典，包含原始名称和新名称
            
        Returns:
            bool: 如果成功启动分析返回True，否则返回False
        """
        # 检查是否有足够的文件
        if not original_files:
            self.analysis_failed.emit("没有原始文件可供分析")
            return False
        
        if not example_files:
            self.analysis_failed.emit("没有命名示例，请至少为一个文件提供重命名示例")
            return False
        
        # 启动分析
        self.ai_client.start_analysis(original_files, example_files)
        
        return True
    
    @Slot()
    def go_to_previous_analysis(self):
        """
        转到上一个分析结果
        
        Returns:
            bool: 如果成功转到上一个返回True，否则返回False
        """
        history = self.rename_model.go_to_previous()
        return history is not None
    
    @Slot()
    def go_to_next_analysis(self):
        """
        转到下一个分析结果
        
        Returns:
            bool: 如果成功转到下一个返回True，否则返回False
        """
        history = self.rename_model.go_to_next()
        return history is not None
    
    @Slot()
    def apply_rename(self):
        """
        应用重命名
        
        Returns:
            dict: 包含success, count和可能的error字段的结果字典
        """
        # 获取当前重命名映射
        rename_map = self.rename_model.get_current_rename_map()
        
        if not rename_map:
            return {"success": False, "error": "没有可用的重命名映射"}
        
        try:
            # 发出重命名开始信号
            self.rename_started.emit()
            
            # 跟踪成功计数
            success_count = 0
            
            # 执行重命名
            for original_name, new_name in rename_map.items():
                # 获取文件路径
                file_path = self._get_file_path(original_name)
                
                if not file_path or not os.path.exists(file_path):
                    continue
                
                # 获取目标路径
                dir_path = os.path.dirname(file_path)
                new_path = os.path.join(dir_path, new_name)
                
                # 如果目标文件已存在，添加后缀
                if os.path.exists(new_path) and file_path != new_path:
                    base, ext = os.path.splitext(new_name)
                    i = 1
                    while os.path.exists(new_path):
                        new_name = f"{base}_{i}{ext}"
                        new_path = os.path.join(dir_path, new_name)
                        i += 1
                
                # 执行重命名
                shutil.move(file_path, new_path)
                success_count += 1
            
            # 发出重命名完成信号
            result = {"success": True, "count": success_count}
            self.rename_completed.emit(result)
            
            return result
        
        except Exception as e:
            # 发出重命名失败信号
            error_message = f"重命名失败: {str(e)}"
            self.rename_failed.emit(error_message)
            
            return {"success": False, "error": error_message}
    
    def _get_file_path(self, file_name):
        """
        获取文件路径
        
        Args:
            file_name (str): 文件名
            
        Returns:
            str: 文件路径，如果不存在返回None
        """
        # 这里需要从文件控制器或其他地方获取文件路径
        # 示例实现，实际应用中需要根据具体情况修改
        from PySide6.QtWidgets import QApplication
        
        # 获取主窗口
        main_window = QApplication.activeWindow()
        
        if main_window:
            # 尝试获取文件控制器
            file_controller = getattr(main_window, 'file_controller', None)
            
            if file_controller:
                # 获取文件数据
                file_data = file_controller.get_file(file_name)
                
                if file_data:
                    return file_data.get('path')
        
        return None
    
    @Slot()
    def clear_examples(self):
        """
        清空所有示例
        """
        self.rename_model.clear_examples()
    
    @Slot()
    def clear_analysis_results(self):
        """
        清空所有分析结果
        """
        self.rename_model.clear_history()
    
    def get_example_files(self):
        """
        获取示例文件列表
        
        Returns:
            list: 示例文件列表，每个元素是一个字典，包含original_name和new_name
        """
        return self.rename_model.get_example_list()
    
    def get_current_analysis_result(self):
        """
        获取当前分析结果
        
        Returns:
            dict: 当前分析结果，是一个从原始文件名到新文件名的映射
        """
        return self.rename_model.get_current_rename_map()
    
    def get_previous_analysis_result(self):
        """
        获取上一个分析结果
        
        Returns:
            dict: 上一个分析结果，是一个从原始文件名到新文件名的映射，如果没有则返回None
        """
        # 转到上一个历史记录
        if self.rename_model.go_to_previous():
            return self.rename_model.get_current_rename_map()
        return None
    
    def get_next_analysis_result(self):
        """
        获取下一个分析结果
        
        Returns:
            dict: 下一个分析结果，是一个从原始文件名到新文件名的映射，如果没有则返回None
        """
        # 转到下一个历史记录
        if self.rename_model.go_to_next():
            return self.rename_model.get_current_rename_map()
        return None
    
    # 私有方法，处理信号
    def _on_example_updated(self, original_name, new_data):
        """
        示例更新事件处理
        
        Args:
            original_name (str): 原始文件名
            new_data (dict): 新数据
        """
        # 转发信号
        self.example_updated.emit(original_name, new_data)
    
    def _on_analysis_started(self):
        """
        分析开始事件处理
        """
        # 转发信号
        self.analysis_started.emit()
    
    def _on_analysis_completed(self, result):
        """
        分析完成事件处理
        
        Args:
            result (dict): 分析结果
        """
        # 添加到历史记录
        self.rename_model.add_history(result)
        
        # 转发信号
        self.analysis_completed.emit(result)
    
    def _on_analysis_failed(self, error_message):
        """
        分析失败事件处理
        
        Args:
            error_message (str): 错误消息
        """
        # 转发信号
        self.analysis_failed.emit(error_message)
    
    def _on_current_history_changed(self, history):
        """
        当前历史记录变更事件处理
        
        Args:
            history (RenameHistory): 当前历史记录
        """
        if history:
            # 获取重命名映射
            rename_map = history.get_rename_map()
            
            # 发出信号
            self.analysis_result_updated.emit(rename_map)