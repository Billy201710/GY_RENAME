#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from PySide6.QtCore import QObject, Signal, Slot
from PySide6.QtWidgets import QFileDialog

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
            paths (list): 文件路径列表，可以是字符串列表或QUrl列表，
                          也可以是包含path和is_folder属性的字典列表
            
        Returns:
            list: 添加的文件数据列表
        """
        file_dicts = []
        
        # 处理每个路径
        for path_item in paths:
            try:
                # 初始化变量
                path = None
                is_folder = False
                
                # 如果是字典，直接获取信息
                if isinstance(path_item, dict):
                    path = path_item.get('path', '')
                    is_folder = path_item.get('is_folder', False)
                    # 字典可能已经包含所有需要的信息
                    if 'name' in path_item and 'path' in path_item:
                        file_dicts.append(path_item)
                        # 添加到模型
                        self.file_model.add_file(path_item['path'], path_item['name'], is_folder=is_folder)
                        continue
                # 如果是QUrl，转换为本地路径
                elif hasattr(path_item, 'toLocalFile'):
                    path = path_item.toLocalFile()
                else:
                    path = path_item
                
                # 如果路径为空，跳过
                if not path:
                    continue
                
                # 判断是否是文件夹
                if is_folder or os.path.isdir(path):
                    # 添加文件夹本身
                    folder_name = os.path.basename(path)
                    file_item = {
                        'name': folder_name,
                        'path': path,
                        'is_folder': True
                    }
                    file_dicts.append(file_item)
                    # 添加到模型
                    self.file_model.add_file(path, folder_name, is_folder=True)
                    
                # 如果是文件
                elif os.path.isfile(path):
                    # 获取文件名和路径
                    name = os.path.basename(path)
                    
                    # 添加到模型
                    file_item = self.file_model.add_file(path, name, is_folder=False)
                    
                    # 如果成功添加，添加到结果列表
                    if file_item:
                        file_dicts.append(file_item.to_dict())
            except Exception as e:
                print(f"添加文件/文件夹时出错: {str(e)}")
                continue
        
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
    
    def browse_files(self):
        """
        打开文件浏览对话框，选择文件
        
        Returns:
            list: 选择的文件数据列表
        """
        # 获取之前使用的目录，如果不存在则使用用户目录
        last_dir = self.config_manager.get_last_directory() or os.path.expanduser("~")
        
        # 打开文件对话框
        file_paths, _ = QFileDialog.getOpenFileNames(
            None,
            "选择文件",
            last_dir,
            "所有文件 (*.*)"
        )
        
        # 如果选择了文件，保存目录
        if file_paths:
            dir_path = os.path.dirname(file_paths[0])
            self.config_manager.set_last_directory(dir_path)
            
            # 添加文件
            return self.add_files(file_paths)
        
        return []