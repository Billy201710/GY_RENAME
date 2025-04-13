#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PySide6.QtCore import QObject, Signal, Slot

from models.file_model import FileModel, FileItem

class FileController(QObject):
    """
    文件控制器类，处理文件相关操作
    """
    
    # 定义信号
    files_added = Signal(list)  # 文件添加信号，参数为文件数据列表
    file_removed = Signal(str)  # 文件移除信号，参数为文件名
    files_cleared = Signal()    # 文件清空信号
    
    def __init__(self, config_manager, parent=None):
        """
        初始化文件控制器
        
        Args:
            config_manager: 配置管理器实例
            parent: 父对象
        """
        super().__init__(parent)
        self.config_manager = config_manager
        self.file_model = FileModel(parent=self)
        
        # 连接模型信号
        self.file_model.fileAdded.connect(self._on_file_added)
        self.file_model.fileRemoved.connect(self._on_file_removed)
        self.file_model.filesChanged.connect(self._on_files_changed)
    
    @Slot(list)
    def add_files(self, paths):
        """
        添加文件
        
        Args:
            paths (list): 文件路径列表，可以是字符串列表或QUrl列表
            
        Returns:
            list: 添加的文件数据列表
        """
        file_dicts = []
        
        # 处理每个路径
        for path in paths:
            # 如果是QUrl，转换为本地路径
            if hasattr(path, 'toLocalFile'):
                path = path.toLocalFile()
            
            # 检查是否是文件
            if os.path.isfile(path):
                # 获取文件名和路径
                name = os.path.basename(path)
                
                # 添加到模型
                file_item = self.file_model.add_file(path, name)
                
                # 如果成功添加，添加到结果列表
                if file_item:
                    file_dicts.append(file_item.to_dict())
            
            # 如果是目录，获取目录中的所有文件
            elif os.path.isdir(path):
                for root, _, files in os.walk(path):
                    for file in files:
                        file_path = os.path.join(root, file)
                        # 添加到模型
                        file_item = self.file_model.add_file(file_path)
                        # 如果成功添加，添加到结果列表
                        if file_item:
                            file_dicts.append(file_item.to_dict())
        
        # 如果有文件添加，发出信号
        if file_dicts:
            self.files_added.emit(file_dicts)
        
        return file_dicts
    
    @Slot(str)
    def remove_file(self, name):
        """
        移除文件
        
        Args:
            name (str): 文件名
            
        Returns:
            bool: 如果成功移除返回True，否则返回False
        """
        return self.file_model.remove_file(name)
    
    @Slot()
    def clear_files(self):
        """
        清空所有文件
        """
        self.file_model.clear()
        self.files_cleared.emit()
    
    def get_files(self):
        """
        获取所有文件数据
        
        Returns:
            list: 文件数据字典列表
        """
        return self.file_model.get_file_dicts()
    
    def get_file(self, name):
        """
        获取指定文件的数据
        
        Args:
            name (str): 文件名
            
        Returns:
            dict: 文件数据字典，如果不存在返回None
        """
        file_item = self.file_model.get_file(name)
        if file_item:
            return file_item.to_dict()
        return None
    
    # 私有方法，处理模型信号
    def _on_file_added(self, file_item):
        """
        文件添加事件处理
        
        Args:
            file_item (FileItem): 添加的文件项
        """
        pass
    
    def _on_file_removed(self, name):
        """
        文件移除事件处理
        
        Args:
            name (str): 移除的文件名
        """
        # 转发信号
        self.file_removed.emit(name)
    
    def _on_files_changed(self, files):
        """
        文件列表变更事件处理
        
        Args:
            files (list): 当前文件项列表
        """
        pass