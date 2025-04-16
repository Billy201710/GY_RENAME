#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import json
import datetime
from PySide6.QtCore import QObject, Signal, Slot, Property

class RenameHistory(QObject):
    """
    重命名历史记录类，用于记录重命名操作和结果
    """
    
    def __init__(self, rename_map=None, timestamp=None, parent=None):
        """
        初始化重命名历史
        
        Args:
            rename_map (dict): 重命名映射，键为原始文件名，值为新文件名
            timestamp (datetime): 时间戳，如果为None则使用当前时间
            parent: 父对象
        """
        super().__init__(parent)
        self._rename_map = rename_map or {}
        self._timestamp = timestamp or datetime.datetime.now()
        self._raw_response = ""  # 原始AI响应
    
    def get_rename_map(self):
        """
        获取重命名映射
        
        Returns:
            dict: 重命名映射
        """
        return self._rename_map
    
    def set_rename_map(self, rename_map):
        """
        设置重命名映射
        
        Args:
            rename_map (dict): 重命名映射
        """
        self._rename_map = rename_map
    
    def get_timestamp(self):
        """
        获取时间戳
        
        Returns:
            datetime: 时间戳
        """
        return self._timestamp
    
    def get_raw_response(self):
        """
        获取原始AI响应
        
        Returns:
            str: 原始AI响应
        """
        return self._raw_response
    
    def set_raw_response(self, raw_response):
        """
        设置原始AI响应
        
        Args:
            raw_response (str): 原始AI响应
        """
        self._raw_response = raw_response
    
    def to_dict(self):
        """
        转换为字典
        
        Returns:
            dict: 字典表示
        """
        return {
            'rename_map': self._rename_map,
            'timestamp': self._timestamp.isoformat(),
            'raw_response': self._raw_response
        }
    
    @classmethod
    def from_dict(cls, data, parent=None):
        """
        从字典创建
        
        Args:
            data (dict): 字典数据
            parent: 父对象
            
        Returns:
            RenameHistory: 重命名历史对象
        """
        # 解析时间戳
        timestamp = None
        if 'timestamp' in data:
            try:
                timestamp = datetime.datetime.fromisoformat(data['timestamp'])
            except (ValueError, TypeError):
                timestamp = datetime.datetime.now()
        
        # 创建对象
        history = cls(
            rename_map=data.get('rename_map', {}),
            timestamp=timestamp,
            parent=parent
        )
        
        # 设置原始响应
        history.set_raw_response(data.get('raw_response', ''))
        
        return history

class RenameModel(QObject):
    """
    重命名模型类，管理重命名操作和历史记录
    """
    
    # 定义信号
    historyChanged = Signal(list)
    currentHistoryChanged = Signal(object)
    exampleUpdated = Signal(str, object)
    
    def __init__(self, parent=None):
        """
        初始化重命名模型
        
        Args:
            parent: 父对象
        """
        super().__init__(parent)
        self._history = []  # 历史记录列表
        self._current_index = -1  # 当前历史记录索引
        self._examples = {}  # 示例映射，键为原始文件名，值为新文件名
    
    @Slot(dict)
    def add_history(self, result):
        """
        添加历史记录
        
        Args:
            result (dict): 分析结果，包含rename_map和raw_response
            
        Returns:
            RenameHistory: 添加的历史记录
        """
        # 创建历史记录
        history = RenameHistory(
            rename_map=result.get('rename_map', {}),
            parent=self
        )
        
        # 设置原始响应
        history.set_raw_response(result.get('raw_response', ''))
        
        # 如果当前索引不是最后一个，移除后面的历史记录
        if self._current_index >= 0 and self._current_index < len(self._history) - 1:
            self._history = self._history[:self._current_index + 1]
        
        # 添加历史记录
        self._history.append(history)
        self._current_index = len(self._history) - 1
        
        # 发出信号
        self.historyChanged.emit(self._history)
        self.currentHistoryChanged.emit(history)
        
        return history
    
    @Slot()
    def clear_history(self):
        """
        清空历史记录
        """
        self._history.clear()
        self._current_index = -1
        
        # 发出信号
        self.historyChanged.emit([])
        self.currentHistoryChanged.emit(None)
    
    @Slot()
    def go_to_previous(self):
        """
        转到上一个历史记录
        
        Returns:
            RenameHistory: 上一个历史记录，如果没有上一个则返回None
        """
        if self._current_index > 0:
            self._current_index -= 1
            history = self._history[self._current_index]
            
            # 发出信号
            self.currentHistoryChanged.emit(history)
            
            return history
        
        return None
    
    @Slot()
    def go_to_next(self):
        """
        转到下一个历史记录
        
        Returns:
            RenameHistory: 下一个历史记录，如果没有下一个则返回None
        """
        if self._current_index < len(self._history) - 1:
            self._current_index += 1
            history = self._history[self._current_index]
            
            # 发出信号
            self.currentHistoryChanged.emit(history)
            
            return history
        
        return None
    
    def get_current_history(self):
        """
        获取当前历史记录
        
        Returns:
            RenameHistory: 当前历史记录，如果没有则返回None
        """
        if 0 <= self._current_index < len(self._history):
            return self._history[self._current_index]
        
        return None
    
    def get_current_rename_map(self):
        """
        获取当前重命名映射
        
        Returns:
            dict: 当前重命名映射，如果没有则返回空字典
        """
        history = self.get_current_history()
        if history:
            return history.get_rename_map()
        
        return {}
    
    @Slot(str, str, bool)
    def add_example(self, original_name, new_name, emit_signal=True):
        """
        添加重命名示例
        
        Args:
            original_name (str): 原始文件名
            new_name (str): 新文件名
            emit_signal (bool): 是否发出信号
            
        Returns:
            bool: 如果成功添加返回True，否则返回False
        """
        if not original_name or not new_name:
            return False
        
        # 更新示例映射
        self._examples[original_name] = new_name
        
        # 发出信号（如果需要）
        if emit_signal:
            self.exampleUpdated.emit(original_name, {'new_name': new_name})
        
        return True
    
    @Slot(str)
    def remove_example(self, original_name):
        """
        移除重命名示例
        
        Args:
            original_name (str): 原始文件名
            
        Returns:
            bool: 如果成功移除返回True，否则返回False
        """
        if original_name in self._examples:
            # 移除示例
            del self._examples[original_name]
            
            # 发出信号
            self.exampleUpdated.emit(original_name, None)
            
            return True
        
        return False
    
    @Slot()
    def clear_examples(self):
        """
        清空所有示例
        """
        self._examples.clear()
    
    def get_examples(self):
        """
        获取所有示例
        
        Returns:
            dict: 示例映射
        """
        return self._examples
    
    def get_example_list(self):
        """
        获取示例列表
        
        Returns:
            list: 示例列表，每个元素是包含original_name和new_name的字典
        """
        example_list = []
        for original_name, new_name in self._examples.items():
            example_list.append({
                'original_name': original_name,
                'new_name': new_name
            })
        return example_list
    
    def save_to_file(self, file_path):
        """
        保存模型到文件
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            bool: 如果成功保存返回True，否则返回False
        """
        try:
            # 准备数据
            data = {
                'history': [h.to_dict() for h in self._history],
                'current_index': self._current_index,
                'examples': self._examples
            }
            
            # 写入文件
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            return True
        except Exception as e:
            print(f"保存模型失败: {str(e)}")
            return False
    
    def load_from_file(self, file_path):
        """
        从文件加载模型
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            bool: 如果成功加载返回True，否则返回False
        """
        try:
            # 读取文件
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 清空当前数据
            self._history.clear()
            self._examples.clear()
            
            # 加载历史记录
            for h_data in data.get('history', []):
                history = RenameHistory.from_dict(h_data, parent=self)
                self._history.append(history)
            
            # 设置当前索引
            self._current_index = data.get('current_index', -1)
            
            # 加载示例
            self._examples.update(data.get('examples', {}))
            
            # 发出信号
            self.historyChanged.emit(self._history)
            
            # 发出当前历史记录变更信号
            current_history = self.get_current_history()
            self.currentHistoryChanged.emit(current_history)
            
            return True
        except Exception as e:
            print(f"加载模型失败: {str(e)}")
            return False