#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PySide6.QtCore import QObject, Signal, Property, Slot

class FileItem(QObject):
    """
    文件项类，表示单个文件
    """
    
    # 定义信号
    nameChanged = Signal(str)
    pathChanged = Signal(str)
    
    def __init__(self, name="", path="", is_folder=False, parent=None):
        """
        初始化文件项
        
        Args:
            name (str): 文件名
            path (str): 文件路径
            is_folder (bool): 是否为文件夹
            parent: 父对象
        """
        super().__init__(parent)
        self._name = name
        self._path = path
        self._original_name = name  # 保存原始文件名，用于恢复
        self.is_folder = is_folder
    
    # 文件名属性
    def _get_name(self):
        return self._name
    
    def _set_name(self, name):
        if self._name != name:
            self._name = name
            self.nameChanged.emit(name)
    
    name = Property(str, _get_name, _set_name, notify=nameChanged)
    
    # 文件路径属性
    def _get_path(self):
        return self._path
    
    def _set_path(self, path):
        if self._path != path:
            self._path = path
            self.pathChanged.emit(path)
    
    path = Property(str, _get_path, _set_path, notify=pathChanged)
    
    # 原始文件名属性
    def get_original_name(self):
        return self._original_name
    
    # 重置为原始文件名
    @Slot()
    def reset_to_original(self):
        self.name = self._original_name
    
    # 转换为字典
    def to_dict(self):
        """
        转换为字典
        
        Returns:
            dict: 包含文件信息的字典
        """
        return {
            'name': self._name,
            'path': self._path,
            'original_name': self._original_name,
            'is_folder': self.is_folder
        }
    
    # 从字典创建
    @classmethod
    def from_dict(cls, data, parent=None):
        """
        从字典创建文件项
        
        Args:
            data (dict): 文件信息字典
            parent: 父对象
            
        Returns:
            FileItem: 文件项实例
        """
        item = cls(
            name=data.get('name', ''),
            path=data.get('path', ''),
            is_folder=data.get('is_folder', False),
            parent=parent
        )
        item._original_name = data.get('original_name', item._name)
        return item

class FileModel(QObject):
    """
    文件模型类，管理文件集合
    """
    
    # 定义信号
    filesChanged = Signal(list)
    fileAdded = Signal(object)
    fileRemoved = Signal(str)
    fileUpdated = Signal(str, object)
    
    def __init__(self, parent=None):
        """
        初始化文件模型
        
        Args:
            parent: 父对象
        """
        super().__init__(parent)
        self._files = {}  # 存储文件，键为文件名
    
    @Slot(str, str)
    def add_file(self, path, name=None, is_folder=False):
        """
        添加文件
        
        Args:
            path (str): 文件路径
            name (str, optional): 文件名，如果为None则使用路径中的文件名
            is_folder (bool): 是否为文件夹
            
        Returns:
            FileItem: 添加的文件项，如果文件已存在则返回None
        """
        # 如果未指定文件名，使用路径中的文件名
        if name is None:
            name = os.path.basename(path)
        
        # 检查文件是否已存在
        if name in self._files:
            return None
        
        # 创建新文件项
        file_item = FileItem(name=name, path=path, is_folder=is_folder, parent=self)
        
        # 添加到文件集合
        self._files[name] = file_item
        
        # 发出信号
        self.fileAdded.emit(file_item)
        self.filesChanged.emit(list(self._files.values()))
        
        return file_item
    
    @Slot(list)
    def add_files(self, paths):
        """
        批量添加文件
        
        Args:
            paths (list): 文件路径列表
            
        Returns:
            list: 添加的文件项列表
        """
        added_files = []
        
        for path in paths:
            if os.path.isfile(path):
                file_item = self.add_file(path)
                if file_item:
                    added_files.append(file_item)
        
        return added_files
    
    @Slot(str)
    def remove_file(self, name):
        """
        移除文件
        
        Args:
            name (str): 文件名
            
        Returns:
            bool: 如果成功移除返回True，否则返回False
        """
        if name in self._files:
            # 移除文件项
            file_item = self._files.pop(name)
            
            # 发出信号
            self.fileRemoved.emit(name)
            self.filesChanged.emit(list(self._files.values()))
            
            return True
        
        return False
    
    @Slot()
    def clear(self):
        """
        清空所有文件
        """
        self._files.clear()
        self.filesChanged.emit([])
    
    @Slot(str, str)
    def update_file_name(self, old_name, new_name):
        """
        更新文件名
        
        Args:
            old_name (str): 旧文件名
            new_name (str): 新文件名
            
        Returns:
            bool: 如果成功更新返回True，否则返回False
        """
        # 检查旧文件名是否存在
        if old_name not in self._files:
            return False
        
        # 检查新文件名是否已存在
        if new_name in self._files and old_name != new_name:
            return False
        
        # 获取文件项
        file_item = self._files[old_name]
        
        # 更新文件名
        file_item.name = new_name
        
        # 更新字典键
        if old_name != new_name:
            self._files[new_name] = file_item
            del self._files[old_name]
        
        # 发出信号
        self.fileUpdated.emit(old_name, file_item)
        self.filesChanged.emit(list(self._files.values()))
        
        return True
    
    def get_file(self, name):
        """
        获取文件项
        
        Args:
            name (str): 文件名
            
        Returns:
            FileItem: 文件项，如果不存在返回None
        """
        return self._files.get(name)
    
    def get_files(self):
        """
        获取所有文件项
        
        Returns:
            list: 文件项列表
        """
        return list(self._files.values())
    
    def get_file_dicts(self):
        """
        获取所有文件的字典表示
        
        Returns:
            list: 文件字典列表
        """
        return [file_item.to_dict() for file_item in self._files.values()]
    
    def get_file_count(self):
        """
        获取文件数量
        
        Returns:
            int: 文件数量
        """
        return len(self._files)
    
    def has_file(self, name):
        """
        检查文件是否存在
        
        Args:
            name (str): 文件名
            
        Returns:
            bool: 如果文件存在返回True，否则返回False
        """
        return name in self._files