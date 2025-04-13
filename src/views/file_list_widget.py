#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QHBoxLayout, QAbstractItemView, QMenu, QMessageBox
)
from PySide6.QtCore import Qt, Signal, QMimeData, QUrl
from PySide6.QtGui import QDrag, QMouseEvent, QContextMenuEvent

class FileListWidget(QWidget):
    """
    文件列表控件类，用于显示文件列表和相关操作
    """
    
    # 定义信号
    files_dropped = Signal(list)  # 文件拖放信号，参数为文件路径列表
    edit_button_clicked = Signal(str)  # 编辑按钮点击信号，参数为文件名
    
    def __init__(self, title="文件列表", accept_drops=False, with_edit_button=False, parent=None):
        """
        初始化文件列表控件
        
        Args:
            title (str): 列表标题
            accept_drops (bool): 是否接受拖放
            with_edit_button (bool): 是否显示编辑按钮
            parent: 父窗口
        """
        super().__init__(parent)
        
        self.title = title
        self.accept_drops = accept_drops
        self.with_edit_button = with_edit_button
        
        # 存储文件列表的字典 {file_name: file_data}
        self.files = {}
        
        # 创建UI
        self._create_ui()
    
    def _create_ui(self):
        """
        创建UI组件
        """
        # 创建主布局
        main_layout = QVBoxLayout(self)
        
        # 创建标题标签
        title_label = QLabel(self.title)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("font-weight: bold; font-size: 16px;")
        
        # 创建文件列表控件
        self.file_list = QListWidget()
        self.file_list.setDragEnabled(True)
        self.file_list.setAcceptDrops(self.accept_drops)
        self.file_list.setDropIndicatorShown(self.accept_drops)
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        
        # 如果接受拖放，连接相关事件
        if self.accept_drops:
            self.setAcceptDrops(True)
            self.file_list.setDragDropMode(QAbstractItemView.DropOnly)
        
        # 添加标题和列表到主布局
        main_layout.addWidget(title_label)
        main_layout.addWidget(self.file_list)
        
        # 设置边距和间距
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
    
    def add_files(self, files):
        """
        添加文件到列表
        
        Args:
            files (list): 文件列表，每个元素是一个字典，包含name和path属性
        """
        for file_data in files:
            file_name = file_data.get('name', '')
            
            # 如果文件已存在，跳过
            if file_name in self.files:
                continue
            
            # 存储文件数据
            self.files[file_name] = file_data
            
            # 创建列表项
            item = QListWidgetItem(file_name)
            item.setData(Qt.UserRole, file_data)
            
            # 如果需要编辑按钮，创建自定义小部件
            if self.with_edit_button:
                # 创建小部件
                item_widget = QWidget()
                layout = QHBoxLayout(item_widget)
                
                # 创建标签和按钮
                label = QLabel(file_name)
                edit_button = QPushButton("Edit")
                edit_button.setMaximumWidth(60)
                
                # 连接按钮信号
                edit_button.clicked.connect(lambda checked, name=file_name: self.edit_button_clicked.emit(name))
                
                # 添加到布局
                layout.addWidget(label)
                layout.addWidget(edit_button)
                layout.setContentsMargins(5, 2, 5, 2)
                
                # 设置列表项和小部件
                self.file_list.addItem(item)
                self.file_list.setItemWidget(item, item_widget)
                
                # 调整项高度
                item.setSizeHint(item_widget.sizeHint())
            else:
                # 直接添加文本项
                self.file_list.addItem(item)
    
    def update_file(self, file_name, new_data):
        """
        更新文件数据
        
        Args:
            file_name (str): 文件名
            new_data (dict): 新的文件数据
        """
        # 如果文件不存在，添加它
        if file_name not in self.files:
            self.add_files([new_data])
            return
        
        # 更新存储的数据
        self.files[file_name].update(new_data)
        
        # 查找并更新列表项
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            item_data = item.data(Qt.UserRole)
            
            if item_data.get('name') == file_name:
                # 如果有自定义部件
                if self.with_edit_button:
                    widget = self.file_list.itemWidget(item)
                    if widget:
                        label = widget.findChild(QLabel)
                        if label and 'new_name' in new_data:
                            label.setText(new_data['new_name'])
                else:
                    # 直接更新文本
                    if 'new_name' in new_data:
                        item.setText(new_data['new_name'])
                
                # 更新项数据
                item.setData(Qt.UserRole, self.files[file_name])
                break
    
    def update_files(self, file_data_map):
        """
        批量更新文件数据
        
        Args:
            file_data_map (dict): 文件数据映射，键为文件名，值为新数据
        """
        for file_name, new_data in file_data_map.items():
            # 如果只是字符串，转换为字典
            if isinstance(new_data, str):
                new_data = {'new_name': new_data}
            
            self.update_file(file_name, new_data)
    
    def get_files(self):
        """
        获取所有文件数据
        
        Returns:
            list: 文件数据列表
        """
        return list(self.files.values())
    
    def get_file(self, file_name):
        """
        获取指定文件的数据
        
        Args:
            file_name (str): 文件名
            
        Returns:
            dict: 文件数据，如果不存在返回None
        """
        return self.files.get(file_name)
    
    def clear(self):
        """
        清空文件列表
        """
        self.files.clear()
        self.file_list.clear()
    
    def dragEnterEvent(self, event):
        """
        拖动进入事件处理
        """
        if self.accept_drops and event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event):
        """
        拖放事件处理
        """
        if self.accept_drops and event.mimeData().hasUrls():
            # 获取文件URL
            urls = event.mimeData().urls()
            
            # 提取文件路径
            file_paths = []
            for url in urls:
                if url.isLocalFile():
                    file_paths.append(url.toLocalFile())
            
            # 如果有文件，发出信号
            if file_paths:
                self.files_dropped.emit(file_paths)
            
            event.acceptProposedAction()
    
    def contextMenuEvent(self, event):
        """
        上下文菜单事件处理
        
        允许右键菜单删除文件项
        """
        # 获取点击位置的项
        item = self.file_list.itemAt(self.file_list.mapFrom(self, event.pos()))
        
        if item:
            # 创建上下文菜单
            menu = QMenu(self)
            
            # 添加删除动作
            delete_action = menu.addAction("删除")
            delete_action.triggered.connect(lambda: self._delete_item(item))
            
            # 显示菜单
            menu.exec(event.globalPos())
    
    def _delete_item(self, item):
        """
        删除列表项
        
        Args:
            item: 要删除的列表项
        """
        # 获取文件名
        file_data = item.data(Qt.UserRole)
        file_name = file_data.get('name', '')
        
        # 从存储中删除
        if file_name in self.files:
            del self.files[file_name]
        
        # 从列表中删除
        row = self.file_list.row(item)
        self.file_list.takeItem(row)