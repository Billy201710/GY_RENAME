#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QHBoxLayout, QAbstractItemView, QMenu, QMessageBox,
    QTextEdit, QFileDialog, QApplication, QSizePolicy
)
from PySide6.QtCore import Qt, Signal, QMimeData, QUrl, QSize, QEvent, QPoint
from PySide6.QtGui import QDrag, QMouseEvent, QContextMenuEvent, QPixmap, QFont, QKeyEvent, QCursor
import os
import subprocess
import platform

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
        self.is_result_list = False  # 标记是否为结果列表
        
        # 存储文件列表的字典 {file_name: file_data}
        self.files = {}
        
        # 存储同步的文件列表控件
        self.synced_lists = []
        
        # 创建UI
        self._create_ui()
        
        # 添加事件过滤器
        if self.accept_drops:
            self.file_list.viewport().installEventFilter(self)
            self.file_list.installEventFilter(self)
            
            # 允许双击空白区域选择文件
            self.file_list.mouseDoubleClickEvent = self._list_double_click_event
            
            # 显示提示标签
            self._update_placeholder_visibility()
    
    def _create_ui(self):
        """
        创建UI组件
        """
        # 创建主布局
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # 创建文件列表控件
        self.file_list = QListWidget()
        self.file_list.setDragEnabled(True)
        self.file_list.setAcceptDrops(self.accept_drops)
        self.file_list.setDropIndicatorShown(self.accept_drops)
        self.file_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.file_list.setAlternatingRowColors(True)
        self.file_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        
        # 设置滚动条样式
        self.file_list.setStyleSheet("""
            QListWidget { 
                padding: 0px; 
                background-color: #1E1E1E;
            }
            
            /* 垂直滚动条样式 */
            QScrollBar:vertical {
                background-color: #1E1E1E;
                width: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical {
                background-color: #3A3A3A;
                min-height: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:vertical:hover {
                background-color: #505050;
            }
            
            QScrollBar::handle:vertical:pressed {
                background-color: #606060;
            }
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                height: 0px;
                background: none;
            }
            
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
            
            /* 水平滚动条样式 */
            QScrollBar:horizontal {
                background-color: #1E1E1E;
                height: 12px;
                margin: 0px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal {
                background-color: #3A3A3A;
                min-width: 20px;
                border-radius: 6px;
            }
            
            QScrollBar::handle:horizontal:hover {
                background-color: #505050;
            }
            
            QScrollBar::handle:horizontal:pressed {
                background-color: #606060;
            }
            
            QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
                width: 0px;
                background: none;
            }
            
            QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {
                background: none;
            }
        """)
        
        self.file_list.setSpacing(2)  # 设置项目间距
        
        # 设置文件列表的键盘事件处理
        self.file_list.installEventFilter(self)
        
        # 如果接受拖放，连接相关事件
        if self.accept_drops:
            self.setAcceptDrops(True)
            self.file_list.setDragDropMode(QAbstractItemView.DropOnly)
            
            # 创建占位提示标签
            self.placeholder_label = QLabel(self)  # 直接设置父对象为self
            self.placeholder_label.setText("请从此处拖入或双击导入要重命名的文件/文件夹")
            self.placeholder_label.setAlignment(Qt.AlignCenter)
            self.placeholder_label.setStyleSheet("""
                QLabel {
                    color: #7E7E80;
                    font-size: 16px;
                    padding: 20px;
                    background-color: transparent;
                    border: 2px dashed #7E7E80;
                    border-radius: 10px;
                    margin: 20px;
                }
            """)
            self.placeholder_label.setWordWrap(True)
            
            # 让占位标签支持鼠标追踪，并安装事件过滤器
            self.placeholder_label.setMouseTracking(True)
            self.placeholder_label.installEventFilter(self)
            # 设置光标为手型，提示可点击
            self.placeholder_label.setCursor(Qt.PointingHandCursor)
        
        # 添加列表到主布局
        main_layout.addWidget(self.file_list)
        
        # 如果接受拖放，设置占位标签（但不添加到布局中）
        if self.accept_drops:
            # 调整占位标签的层叠顺序，使其显示在文件列表上方
            self.placeholder_label.raise_()
            # 初始时居中显示在文件列表区域
            self.placeholder_label.setGeometry(20, 20, self.width() - 40, self.height() - 40)
            # 确保在界面更新后调整标签的可见性
            QApplication.instance().processEvents()
            self._update_placeholder_visibility()
        
        # 设置右键菜单的样式
        self.setStyleSheet(self.styleSheet() + """
            QMenu {
                background-color: #2D2D2D;  /* 深灰色背景 */
                color: #F0F0F0;  /* 亮色文字 */
                border: 1px solid #3A3A3A;  /* 边框 */
                padding: 5px;
            }
            QMenu::item {
                padding: 5px 30px 5px 20px;  /* 内边距 */
                border: 1px solid transparent;  /* 透明边框 */
            }
            QMenu::item:selected {
                background-color: #3A5070;  /* 选中项背景色 */
                border: 1px solid #4A6080;  /* 选中项边框 */
            }
        """)
    
    def resizeEvent(self, event):
        """
        处理控件大小改变事件
        """
        super().resizeEvent(event)
        # 如果接受拖放且占位标签可见，调整占位标签大小
        if self.accept_drops and self.placeholder_label.isVisible():
            # 保留边距
            self.placeholder_label.setGeometry(20, 20, 
                                              self.width() - 40, 
                                              self.height() - 40)
    
    def _update_placeholder_visibility(self):
        """
        更新占位标签的可见性
        """
        if self.accept_drops:
            # 如果文件列表为空，显示占位标签
            if not self.files:
                self.placeholder_label.show()
                # 确保标签覆盖整个可视区域，但保留边距
                self.placeholder_label.setGeometry(20, 20, 
                                                  self.width() - 40, 
                                                  self.height() - 40)
            else:
                self.placeholder_label.hide()
    
    def _list_double_click_event(self, event):
        """
        处理列表双击事件，在空白区域双击打开文件选择对话框
        
        Args:
            event: 鼠标事件
        """
        # 检查是否在空白区域
        item = self.file_list.itemAt(event.position().toPoint())
        
        # 如果双击的是空白区域且是接受拖放的列表
        if not item and self.accept_drops:
            self._browse_files()
        else:
            # 调用默认的双击处理
            QListWidget.mouseDoubleClickEvent(self.file_list, event)
    
    def _browse_files(self):
        """
        打开文件浏览对话框选择文件
        """
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        
        # 打开文件对话框，支持多选
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "选择要重命名的文件",
            "",
            "所有文件 (*)",
            options=options
        )
        
        if file_paths:
            files = []
            for file_path in file_paths:
                try:
                    is_folder = os.path.isdir(file_path)
                    file_name = os.path.basename(file_path)
                    
                    files.append({
                        'name': file_name,
                        'path': file_path,
                        'is_folder': is_folder
                    })
                except Exception as e:
                    print(f"处理文件时出错: {str(e)}")
            
            # 添加到列表
            if files:
                self.add_files(files)
                self.files_dropped.emit(files)
                # 更新占位标签的可见性
                self._update_placeholder_visibility()
    
    def _browse_folders(self):
        """
        打开文件夹浏览对话框选择文件夹
        """
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly | QFileDialog.ShowDirsOnly
        
        # 打开文件夹对话框
        folder_path = QFileDialog.getExistingDirectory(
            self,
            "选择要重命名的文件夹",
            "",
            options=options
        )
        
        if folder_path:
            try:
                file_name = os.path.basename(folder_path)
                
                folder_data = {
                    'name': file_name,
                    'path': folder_path,
                    'is_folder': True
                }
                
                # 添加到列表
                self.add_files([folder_data])
                self.files_dropped.emit([folder_data])
            except Exception as e:
                print(f"处理文件夹时出错: {str(e)}")
    
    def add_files(self, files):
        """
        添加文件到列表
        
        Args:
            files (list): 文件列表，每个元素是一个字典，包含name和path属性
        """
        for file_data in files:
            try:
                file_name = file_data.get('name', '')
                
                # 如果文件已存在，跳过
                if file_name in self.files:
                    continue
                
                # 存储文件数据
                self.files[file_name] = file_data
                
                # 创建列表项
                item = QListWidgetItem()
                item.setData(Qt.UserRole, file_data)
                
                # 创建列表项小部件
                self._create_item_widget(item, file_data)
            except Exception as e:
                print(f"添加文件 '{file_data.get('name', '未知')}' 时出错: {str(e)}")
                continue
        
        # 更新占位标签的可见性
        if self.accept_drops:
            self._update_placeholder_visibility()
    
    def _create_item_widget(self, item, file_data):
        """
        创建列表项小部件
        
        Args:
            item: 列表项
            file_data: 文件数据
        """
        file_name = file_data.get('name', '')
        is_folder = file_data.get('is_folder', False)
        
        # 创建小部件
        item_widget = QWidget()
        # 设置鼠标悬停时显示手型光标 - 应用到整个项目
        item_widget.setCursor(Qt.PointingHandCursor)
        layout = QHBoxLayout(item_widget)
        
        # 确保各列表项高度一致 - 使用固定高度
        layout.setContentsMargins(10, 8, 10, 8)  # 统一的内边距
        layout.setSpacing(10)  # 统一的元素间距
        layout.setAlignment(Qt.AlignVCenter)  # 垂直居中对齐
        
        # 创建文件图标标签
        file_icon_label = QLabel()
        # 根据是否是文件夹设置不同的ObjectName
        file_icon_label.setObjectName("folderIcon" if is_folder else "fileIcon")
        
        # 根据文件类型选择不同的图标
        icon_path = "assets/icons/normal/folder.png" if is_folder else "assets/icons/normal/file.png"
        
        # 修改图标设置方式，防止图标拉伸
        pixmap = QPixmap(icon_path)
        pixmap = pixmap.scaled(20, 20, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        file_icon_label.setPixmap(pixmap)
        # 设置固定大小
        file_icon_label.setFixedSize(20, 20)
        layout.addWidget(file_icon_label)
        layout.setAlignment(file_icon_label, Qt.AlignVCenter)  # 图标垂直居中
        
        # 如果需要编辑按钮，创建自定义小部件
        if self.with_edit_button:
            # 使用QTextEdit代替QLabel
            text_edit = QTextEdit(file_name)
            text_edit.setReadOnly(True)
            text_edit.setFrameStyle(0)  # 无边框
            text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            text_edit.setFixedHeight(28)  # 设置固定高度
            text_edit.setTextInteractionFlags(Qt.NoTextInteraction)  # 禁止文本交互，解决点击问题
            # 设置鼠标悬停时显示手型光标
            text_edit.setCursor(Qt.PointingHandCursor)
            
            # 根据是否是文件夹设置不同的ObjectName和样式
            if is_folder:
                text_edit.setObjectName("folderNameEdit")
            else:
                text_edit.setObjectName("fileNameEdit")
            
            # 设置字体和样式
            font = QFont("Courier New", 10)  # 使用等宽字体，这种字体对特殊字符显示更好
            font.setStyleStrategy(QFont.PreferAntialias)  # 添加抗锯齿
            text_edit.setFont(font)
            # 为命名示范列设置#CBA057文字颜色
            text_edit.setStyleSheet("background-color: transparent; margin-left: 5px; padding: 2px; font-family: 'Courier New', monospace; border: none; color: #CBA057;")
            
            # 创建编辑按钮
            edit_button = QPushButton("Edit")
            edit_button.setObjectName("editButton")
            edit_button.setFixedWidth(120)
            # 设置编辑按钮样式：背景色#CBA057，字体颜色为白色
            edit_button.setStyleSheet("background-color: #CBA057; color: white; border-radius: 3px;")
            # 设置鼠标悬停时显示手型光标
            edit_button.setCursor(Qt.PointingHandCursor)
            
            # 连接按钮信号
            edit_button.clicked.connect(lambda checked, name=file_name: self.edit_button_clicked.emit(name))
            
            # 添加到布局
            layout.addWidget(text_edit, 1)  # 让文本编辑器占据剩余空间
            layout.addWidget(edit_button)
            layout.setAlignment(text_edit, Qt.AlignVCenter)  # 文本编辑器垂直居中
            
            # 安装事件过滤器，将点击事件传递给列表项
            text_edit.installEventFilter(self)
            
        else:
            # 使用QTextEdit代替QLabel
            text_edit = QTextEdit(file_name)
            text_edit.setReadOnly(True)
            text_edit.setFrameStyle(0)  # 无边框
            text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
            text_edit.setFixedHeight(28)  # 设置固定高度
            text_edit.setTextInteractionFlags(Qt.NoTextInteraction)  # 禁止文本交互，解决点击问题
            # 设置鼠标悬停时显示手型光标
            text_edit.setCursor(Qt.PointingHandCursor)
            
            # 设置字体和样式
            font = QFont("Courier New", 10)  # 使用等宽字体，这种字体对特殊字符显示更好
            font.setStyleStrategy(QFont.PreferAntialias)  # 添加抗锯齿
            text_edit.setFont(font)
            text_edit.setStyleSheet("background-color: transparent; margin-left: 5px; padding: 2px; font-family: 'Courier New', monospace; border: none;")
            
            # 如果是结果列表，设置特殊样式
            if self.is_result_list:
                text_edit.setObjectName("resultFileNameEdit")
                text_edit.setStyleSheet("background-color: transparent; margin-left: 5px; padding: 2px; font-family: 'Courier New', monospace; border: none; color: #4CAF50;")
            else:
                # 根据是否是文件夹设置不同的ObjectName
                if is_folder:
                    text_edit.setObjectName("folderNameEdit")
                    text_edit.setStyleSheet("background-color: transparent; margin-left: 5px; padding: 2px; font-family: 'Courier New', monospace; border: none; color: #f0c040;")
                else:
                    text_edit.setObjectName("fileNameEdit")
            
            # 添加到布局
            layout.addWidget(text_edit, 1)  # 让文本编辑器占据剩余空间
            layout.setAlignment(text_edit, Qt.AlignVCenter)  # 文本编辑器垂直居中
            
            # 安装事件过滤器，将点击事件传递给列表项
            text_edit.installEventFilter(self)
        
        # 设置列表项和小部件
        self.file_list.addItem(item)
        self.file_list.setItemWidget(item, item_widget)
        
        # 调整项高度 - 确保所有列表项高度一致
        # 使用固定高度，而不是根据内容自适应
        fixed_height = 48  # 固定高度值
        item.setSizeHint(QSize(item_widget.width(), fixed_height))
    
    def set_as_result_list(self, is_result=True):
        """
        设置为结果列表
        
        Args:
            is_result (bool): 是否为结果列表
        """
        self.is_result_list = is_result
    
    def update_file(self, file_name, new_data):
        """
        更新文件数据
        
        Args:
            file_name (str): 文件名
            new_data (dict): 新的文件数据
        """
        # 防止无限递归
        static_updating = getattr(self, '_updating_file', False)
        if static_updating:
            return
            
        self._updating_file = True
        
        try:
            # 如果文件不存在，添加它
            if file_name not in self.files:
                # 检查是否只需要添加Edit按钮
                if self.with_edit_button:
                    self.add_edit_button_only([new_data])
                else:
                    self.add_files([new_data])
                return
            
            # 更新存储的数据
            self.files[file_name].update(new_data)
            
            # 查找对应的列表项
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                item_data = item.data(Qt.UserRole)
                
                if item_data and item_data.get('name') == file_name:
                    # 更新item关联的数据
                    item.setData(Qt.UserRole, self.files[file_name])
                    
                    # 获取小部件
                    item_widget = self.file_list.itemWidget(item)
                    
                    if item_widget:
                        # 如果是编辑按钮模式且存在name，更新文本
                        if self.with_edit_button and 'name' in new_data:
                            # 查找文本编辑器
                            text_edit = None
                            for j in range(item_widget.layout().count()):
                                widget = item_widget.layout().itemAt(j).widget()
                                if isinstance(widget, QTextEdit):
                                    text_edit = widget
                                    break
                            
                            # 如果找到文本编辑器，更新文本
                            if text_edit and text_edit.toPlainText() != new_data.get('name'):
                                # 暂时断开信号避免循环
                                text_edit.blockSignals(True)
                                text_edit.setText(new_data.get('name'))
                                text_edit.blockSignals(False)
                    break
        finally:
            self._updating_file = False
    
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
        # 先清空其他同步列表
        for widget in self.synced_lists:
            # 避免循环调用
            widget.synced_lists = [w for w in widget.synced_lists if w != self]
            # 清空文件列表
            widget.files.clear()
            widget.file_list.clear()
            # 更新占位标签的可见性
            if widget.accept_drops:
                widget._update_placeholder_visibility()
            # 恢复同步列表引用
            if self not in widget.synced_lists:
                widget.synced_lists.append(self)
        
        # 清空自己的文件列表
        self.files.clear()
        self.file_list.clear()
        
        # 更新占位标签的可见性
        if self.accept_drops:
            self._update_placeholder_visibility()
    
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
            files = []
            is_folder_found = False
            is_file_found = False
            
            for url in event.mimeData().urls():
                try:
                    # 转换为本地路径并处理
                    file_path = url.toLocalFile()
                    # 判断是文件还是文件夹
                    is_folder = os.path.isdir(file_path)
                    if is_folder:
                        is_folder_found = True
                    else:
                        is_file_found = True
                    
                    file_name = os.path.basename(file_path)
                    
                    # 添加文件或文件夹到列表
                    files.append({
                        'name': file_name,
                        'path': file_path,
                        'is_folder': is_folder
                    })
                except Exception as e:
                    print(f"处理文件时出错: {str(e)}")
                    continue
            
            # 如果同时存在文件和文件夹，显示警告
            if is_folder_found and is_file_found:
                QMessageBox.warning(
                    self, 
                    "类型不一致",
                    "请不要在一次重命名中导入一种以上类型的文件",
                    QMessageBox.Ok
                )
                event.ignore()
                return
            
            # 如果有文件，添加到列表并发出信号
            if files:
                try:
                    self.add_files(files)
                    self.files_dropped.emit(files)
                    # 更新占位标签的可见性
                    self._update_placeholder_visibility()
                except Exception as e:
                    print(f"添加文件到列表时出错: {str(e)}")
            
            event.acceptProposedAction()
    
    def eventFilter(self, obj, event):
        """
        事件过滤器，处理事件
        
        Args:
            obj: 产生事件的对象
            event: 事件
        """
        # 处理鼠标进入和离开事件，用于显示和隐藏Edit按钮
        if event.type() == QEvent.Enter and self.with_edit_button:
            # 检查是否是列表项小部件
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                widget = self.file_list.itemWidget(item)
                
                if obj == widget:
                    # 查找Edit按钮并显示
                    for button in widget.findChildren(QPushButton, "editButton"):
                        button.setVisible(True)
                    return False  # 继续处理事件
        
        elif event.type() == QEvent.Leave and self.with_edit_button:
            # 检查是否是列表项小部件
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                widget = self.file_list.itemWidget(item)
                
                if obj == widget:
                    # 查找Edit按钮并隐藏
                    for button in widget.findChildren(QPushButton, "editButton"):
                        button.setVisible(False)
                    return False  # 继续处理事件
        
        # 处理文本编辑框的焦点丢失事件
        if isinstance(obj, QTextEdit) and event.type() == QEvent.FocusOut and obj.property("original_file_name"):
            original_file_name = obj.property("original_file_name")
            if original_file_name and original_file_name in self.files:
                new_text = obj.toPlainText()
                # 确保更新模型
                self._on_text_edited(original_file_name, new_text)
        
        # 处理Del键删除选中项
        if obj == self.file_list and event.type() == QEvent.KeyPress:
            # 转换为键盘事件并检查是否是Delete键
            if isinstance(event, QKeyEvent) and event.key() == Qt.Key_Delete:
                self._delete_selected_items()
                return True  # 事件已处理
        
        # 处理占位标签的双击事件
        if self.accept_drops and obj == self.placeholder_label:
            if event.type() == QEvent.MouseButtonDblClick:
                # 调用文件浏览对话框
                self._browse_files()
                return True  # 事件已处理
            elif event.type() == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
                # 单击也可以触发文件选择
                self._browse_files()
                return True  # 事件已处理
        
        # 过滤QTextEdit上的鼠标点击事件
        if isinstance(obj, QTextEdit) and event.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonDblClick]:
            # 找到对应的列表项
            for i in range(self.file_list.count()):
                item = self.file_list.item(i)
                widget = self.file_list.itemWidget(item)
                
                # 如果这个QTextEdit在当前小部件中
                if obj in widget.findChildren(QTextEdit):
                    # 单击选中项目
                    if event.type() == QEvent.MouseButtonPress:
                        # 如果不是右键点击
                        if event.button() != Qt.RightButton:
                            # 如果按下Ctrl键，切换选择状态
                            if event.modifiers() & Qt.ControlModifier:
                                item.setSelected(not item.isSelected())
                            # 否则，选择当前项并取消其他项的选择
                            else:
                                self.file_list.clearSelection()
                                item.setSelected(True)
                    
                    # 实现双击打开文件功能
                    if event.type() == QEvent.MouseButtonDblClick:
                        item_data = item.data(Qt.UserRole)
                        if item_data:
                            self._open_file(item_data)
                    
                    return False  # 不阻止事件继续传递，以便编辑功能正常工作
        
        # 其他事件由默认处理器处理
        return super().eventFilter(obj, event)
    
    def _open_file(self, file_data):
        """
        打开文件
        
        Args:
            file_data (dict): 文件数据
        """
        try:
            file_path = file_data.get('path', '')
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                return
            
            # 使用系统默认程序打开文件
            if platform.system() == 'Windows':
                os.startfile(file_path)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', file_path])
            else:  # Linux/Unix
                subprocess.run(['xdg-open', file_path])
                
        except Exception as e:
            print(f"打开文件时出错: {str(e)}")
    
    def _open_folder(self, file_path):
        """
        打开文件所在目录
        
        Args:
            file_path (str): 文件路径
        """
        try:
            if not os.path.exists(file_path):
                print(f"文件不存在: {file_path}")
                return
            
            # 获取文件所在目录
            folder_path = os.path.dirname(file_path)
            
            # 打开文件夹并选中文件
            if platform.system() == 'Windows':
                # 打开文件夹并选中文件
                subprocess.run(['explorer', '/select,', os.path.normpath(file_path)])
            elif platform.system() == 'Darwin':  # macOS
                # 在Finder中显示文件
                subprocess.run(['open', '-R', file_path])
            else:  # Linux/Unix
                # 打开文件夹
                subprocess.run(['xdg-open', folder_path])
                
        except Exception as e:
            print(f"打开文件夹时出错: {str(e)}")
    
    def contextMenuEvent(self, event):
        """
        上下文菜单事件处理
        
        显示右键菜单但不更改选择状态
        """
        # 保存当前的选择状态
        current_selection = []
        for i in range(self.file_list.count()):
            item = self.file_list.item(i)
            if item.isSelected():
                current_selection.append(i)
        
        # 获取鼠标位置下的项
        pos = self.file_list.mapFromGlobal(event.globalPos())
        clicked_item = self.file_list.itemAt(pos)
        
        # 创建上下文菜单
        menu = QMenu(self)
        
        # 如果是第一列且接受拖放
        if self.accept_drops:
            # 如果右键点击的是空白区域或没有项目
            if not clicked_item or not self.files:
                # 添加选择文件和文件夹的菜单项
                select_files_action = menu.addAction("选择文件")
                select_folder_action = menu.addAction("选择文件夹")
                
                # 显示菜单
                action = menu.exec(event.globalPos())
                
                # 处理菜单操作
                if action == select_files_action:
                    self._browse_files()
                elif action == select_folder_action:
                    self._browse_folders()
                
                return
        
        # 如果点击位置没有项，不显示菜单
        if not clicked_item:
            return
            
        # 只有当当前有选择时才显示菜单
        if not current_selection:
            # 如果没有选中项，选中当前点击的项
            clicked_item.setSelected(True)
        elif clicked_item not in [self.file_list.item(i) for i in current_selection]:
            # 如果点击的项不在当前选择中，保持当前选择不变
            # 不进行任何选择操作
            pass
        
        # 获取点击项的数据
        clicked_item_data = clicked_item.data(Qt.UserRole)
        file_path = clicked_item_data.get('path', '') if clicked_item_data else ''
        
        # 添加打开文件动作
        open_action = menu.addAction("打开文件")
        
        # 添加打开目录动作
        open_dir_action = menu.addAction("打开目录")
        
        # 添加清除动作
        menu.addSeparator()  # 添加分隔线
        clear_action = menu.addAction("清除")
        
        # 显示菜单
        action = menu.exec(event.globalPos())
        
        # 处理菜单动作
        if action == clear_action:
            # 删除所有选中的项
            self._delete_selected_items()
        elif action == open_action:
            # 打开选中的文件
            if clicked_item_data:
                self._open_file(clicked_item_data)
        elif action == open_dir_action:
            # 打开文件所在目录
            if file_path:
                self._open_folder(file_path)
    
    def _delete_selected_items(self):
        """
        删除所有选中的列表项（无确认提示）
        """
        # 获取选中的项
        selected_items = self.file_list.selectedItems()
        
        # 如果没有选中的项，返回
        if not selected_items:
            return
        
        # 收集要删除的索引
        indices_to_delete = [self.file_list.row(item) for item in selected_items]
        
        # 先在其他列表中删除相同索引的项
        for widget in self.synced_lists:
            # 确保其他列表具有足够的项目
            if widget.file_list.count() >= max(indices_to_delete) + 1:
                # 从最大索引开始删除，避免索引变化
                for index in sorted(indices_to_delete, reverse=True):
                    # 从列表中删除项目
                    item = widget.file_list.item(index)
                    if item:
                        # 获取文件名
                        file_data = item.data(Qt.UserRole)
                        if file_data:
                            file_name = file_data.get('name', '')
                            # 从存储中删除
                            if file_name in widget.files:
                                del widget.files[file_name]
                        # 从列表中删除
                        widget.file_list.takeItem(index)
                
                # 更新占位标签的可见性
                if widget.accept_drops:
                    widget._update_placeholder_visibility()
        
        # 删除当前列表中选中的项
        for item in selected_items:
            # 获取文件名
            file_data = item.data(Qt.UserRole)
            file_name = file_data.get('name', '')
            
            # 从存储中删除
            if file_name in self.files:
                del self.files[file_name]
            
            # 从列表中删除
            row = self.file_list.row(item)
            self.file_list.takeItem(row)
        
        # 更新占位标签的可见性
        if self.accept_drops:
            self._update_placeholder_visibility()
    
    def keyPressEvent(self, event):
        """
        处理键盘按键事件
        
        Args:
            event: 键盘事件
        """
        # 处理Delete键删除
        if event.key() == Qt.Key_Delete:
            self._delete_selected_items()
        else:
            # 其他键由父类处理
            super().keyPressEvent(event)

    def add_edit_button_only(self, files):
        """
        仅添加编辑按钮到列表（不显示文件名）
        
        Args:
            files (list): 文件列表，每个元素是一个字典，包含name和path属性
        """
        for file_data in files:
            try:
                file_name = file_data.get('name', '')
                
                # 如果文件已存在，跳过
                if file_name in self.files:
                    continue
                
                # 存储文件数据（但标记为未编辑状态）
                file_data['edited'] = False
                self.files[file_name] = file_data
                
                # 创建列表项
                item = QListWidgetItem()
                item.setData(Qt.UserRole, file_data)
                
                # 创建只包含编辑按钮的小部件
                self._create_edit_button_item(item, file_data)
            except Exception as e:
                print(f"添加编辑按钮 '{file_data.get('name', '未知')}' 时出错: {str(e)}")
                continue
        
        # 更新占位标签的可见性
        if self.accept_drops:
            self._update_placeholder_visibility()
            
    def _create_edit_button_item(self, item, file_data):
        """
        创建只包含编辑按钮的列表项小部件
        
        Args:
            item: 列表项
            file_data: 文件数据
        """
        file_name = file_data.get('name', '')
        
        # 创建小部件
        item_widget = QWidget()
        # 设置鼠标悬停时显示手型光标
        item_widget.setCursor(Qt.PointingHandCursor)
        # 强制布局更新
        item_widget.setAttribute(Qt.WA_DontShowOnScreen, False)
        
        layout = QHBoxLayout(item_widget)
        # 保持和其他列表项相同的内边距，确保对齐
        layout.setContentsMargins(10, 8, 10, 8)
        # 设置垂直居中
        layout.setAlignment(Qt.AlignCenter)
        
        # 创建编辑按钮
        edit_button = QPushButton("Edit")
        edit_button.setObjectName("editButton")
        # 设置最小宽度，确保按钮不会太小
        edit_button.setMinimumWidth(100)
        # 设置按钮策略，允许水平扩展
        edit_button.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        # 设置固定高度
        edit_button.setFixedHeight(30)
        # 设置鼠标悬停时显示手型光标
        edit_button.setCursor(Qt.PointingHandCursor)
        # 设置编辑按钮样式：背景色#CBA057，字体颜色为白色
        edit_button.setStyleSheet("background-color: #CBA057; color: white; border-radius: 3px;")
        
        # 保存原始文件名到按钮的属性中
        edit_button.setProperty("file_name", file_name)
        
        # 连接按钮信号到自定义槽，使用更安全的连接方式
        edit_button.clicked.connect(lambda: self._on_edit_button_clicked(file_name, item_widget))
        
        # 初始状态下隐藏编辑按钮
        edit_button.setVisible(False)
        
        # 添加到布局并让按钮填满可用空间
        layout.addWidget(edit_button, 1)
        
        # 强制布局刷新
        layout.invalidate()
        layout.activate()
        
        # 设置列表项和小部件
        self.file_list.addItem(item)
        self.file_list.setItemWidget(item, item_widget)
        
        # 调整项高度 - 确保所有列表项高度一致
        # 使用固定高度，与_create_item_widget中保持一致
        fixed_height = 48  # 固定高度值
        item.setSizeHint(QSize(item_widget.width(), fixed_height))
        
        # 强制更新布局，确保按钮正确显示
        item_widget.updateGeometry()
        edit_button.updateGeometry()
        
        # 安装事件过滤器，处理鼠标进入和离开事件
        item_widget.installEventFilter(self)
    
    def _on_edit_button_clicked(self, file_name, item_widget):
        """
        编辑按钮点击处理
        
        Args:
            file_name (str): 文件名
            item_widget (QWidget): 列表项小部件
        """
        # 通知控制器
        self.edit_button_clicked.emit(file_name)
        
        # 移除旧的布局中所有控件
        while item_widget.layout().count():
            item = item_widget.layout().takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        # 保持布局边距一致，确保对齐
        item_widget.layout().setContentsMargins(10, 8, 10, 8)
        
        # 创建文本编辑框
        text_edit = QTextEdit(file_name)
        text_edit.setObjectName("fileNameEdit")
        text_edit.setFrameStyle(0)  # 无边框
        text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        text_edit.setFixedHeight(28)  # 设置固定高度
        
        # 设置字体和样式
        font = QFont("Courier New", 10)
        font.setStyleStrategy(QFont.PreferAntialias)
        text_edit.setFont(font)
        text_edit.setStyleSheet("background-color: transparent; margin-left: 5px; padding: 2px; font-family: 'Courier New', monospace; border: none; color: #CBA057;")
        
        # 允许文本交互
        text_edit.setTextInteractionFlags(Qt.TextEditorInteraction)
        
        # 保存原始文件名
        text_edit.setProperty("original_file_name", file_name)
        
        # 添加到布局
        item_widget.layout().addWidget(text_edit)
        
        # 设置焦点到文本编辑框
        text_edit.setFocus()
        
        # 选中所有文本
        text_edit.selectAll()
        
        # 文本变更时保存到文件数据
        text_edit.textChanged.connect(lambda: self._on_text_edited(file_name, text_edit.toPlainText()))
        
        # 安装事件过滤器以处理焦点丢失事件
        text_edit.installEventFilter(self)
        
    def _on_text_edited(self, original_file_name, new_text):
        """
        文本编辑处理
        
        Args:
            original_file_name (str): 原始文件名
            new_text (str): 新文本
        """
        # 防止无限递归
        static_updating = getattr(self, '_updating_text', False)
        if static_updating:
            return
            
        self._updating_text = True
        
        try:
            # 更新存储的文件数据
            if original_file_name in self.files:
                self.files[original_file_name]['edited'] = True
                self.files[original_file_name]['new_name'] = new_text
                
                # 尝试更新重命名控制器
                from PySide6.QtWidgets import QApplication
                main_window = QApplication.activeWindow()
                
                if main_window and hasattr(main_window, 'rename_controller'):
                    # 从UI中获取重命名控制器
                    rename_controller = main_window.rename_controller
                    
                    # 更新重命名模型中的示例 - 不需要发信号
                    rename_controller.rename_model.add_example(original_file_name, new_text, emit_signal=False)
        finally:
            self._updating_text = False

    def sync_with(self, other_list_widgets):
        """
        与其他文件列表组件同步滚动和选择
        
        Args:
            other_list_widgets (list): 其他FileListWidget实例列表
        """
        self.synced_lists = [widget for widget in other_list_widgets if widget != self]
        
        # 断开旧连接，避免多次连接
        try:
            self.file_list.verticalScrollBar().valueChanged.disconnect(self._sync_scroll)
        except:
            pass  # 如果之前没有连接，会抛出异常，忽略它
            
        # 连接滚动信号
        self.file_list.verticalScrollBar().valueChanged.connect(self._sync_scroll)
        
        # 断开旧选择信号连接
        try:
            self.file_list.itemSelectionChanged.disconnect(self._sync_selection)
        except:
            pass  # 如果之前没有连接，忽略异常
            
        # 连接选择信号
        self.file_list.itemSelectionChanged.connect(self._sync_selection)
        
        # 确保初始同步
        self._sync_selection()
        scroll_value = self.file_list.verticalScrollBar().value()
        if scroll_value > 0:
            self._sync_scroll(scroll_value)
        
    def _sync_scroll(self, value):
        """
        同步滚动条位置
        
        Args:
            value (int): 滚动条位置值
        """
        # 防止无限递归
        if getattr(self, '_is_syncing_scroll', False):
            return
            
        self._is_syncing_scroll = True
        
        try:
            # 计算可见区域
            viewport_rect = self.file_list.viewport().rect()
            
            # 找到第一个可见项和偏移量
            first_visible_index = -1
            offset_percent = 0
            
            # 找到第一个完全可见的项
            for i in range(self.file_list.count()):
                item_rect = self.file_list.visualItemRect(self.file_list.item(i))
                # 如果项目在可见区域内
                if viewport_rect.contains(item_rect.topLeft()):
                    first_visible_index = i
                    # 计算第一个可见项相对于滚动条的偏移比例
                    scrollbar = self.file_list.verticalScrollBar()
                    total_range = scrollbar.maximum() - scrollbar.minimum()
                    if total_range > 0:
                        offset_percent = value / total_range
                    break
            
            # 如果没有找到可见项，使用滚动条的比例值
            if first_visible_index == -1:
                scrollbar = self.file_list.verticalScrollBar()
                total_range = scrollbar.maximum() - scrollbar.minimum()
                if total_range > 0:
                    offset_percent = value / total_range
                # 如果列表为空或者滚动到了底部，同步滚动条值即可
                for widget in self.synced_lists:
                    if widget.file_list.count() > 0:
                        target_value = int(offset_percent * (widget.file_list.verticalScrollBar().maximum() - widget.file_list.verticalScrollBar().minimum()))
                        widget.file_list.verticalScrollBar().setValue(target_value)
            else:
                # 同步到其他列表时，先将滚动条拉到相同比例位置，再滚动到对应项
                for widget in self.synced_lists:
                    if widget.file_list.count() > first_visible_index:
                        # 同步滚动条相对位置
                        target_scrollbar = widget.file_list.verticalScrollBar()
                        target_range = target_scrollbar.maximum() - target_scrollbar.minimum()
                        if target_range > 0:
                            target_value = int(offset_percent * target_range)
                            target_scrollbar.setValue(target_value)
                        
                        # 然后滚动到相同索引的项
                        widget.file_list.scrollToItem(
                            widget.file_list.item(first_visible_index),
                            QAbstractItemView.PositionAtTop
                        )
        
        finally:
            self._is_syncing_scroll = False
            
    def _sync_selection(self):
        """
        同步选择状态
        """
        # 获取当前选中项索引
        selected_indices = [self.file_list.row(item) for item in self.file_list.selectedItems()]
        
        # 同步到其他列表
        for widget in self.synced_lists:
            # 如果其他列表有相同数量的项，同步选择
            if widget.file_list.count() == self.file_list.count():
                widget.file_list.blockSignals(True)
                widget.file_list.clearSelection()
                for index in selected_indices:
                    if 0 <= index < widget.file_list.count():
                        widget.file_list.item(index).setSelected(True)
                widget.file_list.blockSignals(False)