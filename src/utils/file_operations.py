#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import shutil
import datetime
import tempfile
from pathlib import Path

class FileOperations:
    """
    文件操作工具类，提供文件操作相关的静态方法
    """
    
    @staticmethod
    def rename_file(source_path, new_name):
        """
        重命名文件
        
        Args:
            source_path (str): 源文件路径
            new_name (str): 新文件名（不含路径）
            
        Returns:
            tuple: (成功标志, 新路径或错误消息)
        """
        try:
            # 检查源文件是否存在
            if not os.path.exists(source_path):
                return False, f"源文件不存在: {source_path}"
            
            # 获取目标路径
            dir_path = os.path.dirname(source_path)
            new_path = os.path.join(dir_path, new_name)
            
            # 检查目标文件是否已存在
            if os.path.exists(new_path) and source_path != new_path:
                return False, f"目标文件已存在: {new_path}"
            
            # 执行重命名
            shutil.move(source_path, new_path)
            
            return True, new_path
        except Exception as e:
            return False, f"重命名失败: {str(e)}"
    
    @staticmethod
    def batch_rename(rename_map):
        """
        批量重命名文件
        
        Args:
            rename_map (dict): 重命名映射，键为源文件路径，值为新文件名
            
        Returns:
            tuple: (成功标志, 成功计数, 错误列表)
        """
        success_count = 0
        errors = []
        
        # 执行重命名
        for source_path, new_name in rename_map.items():
            success, result = FileOperations.rename_file(source_path, new_name)
            
            if success:
                success_count += 1
            else:
                errors.append((source_path, result))
        
        return success_count > 0, success_count, errors
    
    @staticmethod
    def create_backup(file_path, backup_dir=None):
        """
        创建文件备份
        
        Args:
            file_path (str): 文件路径
            backup_dir (str, optional): 备份目录，如果为None则使用临时目录
            
        Returns:
            tuple: (成功标志, 备份路径或错误消息)
        """
        try:
            # 检查源文件是否存在
            if not os.path.exists(file_path):
                return False, f"源文件不存在: {file_path}"
            
            # 确定备份目录
            if backup_dir is None:
                backup_dir = tempfile.gettempdir()
            
            # 确保备份目录存在
            os.makedirs(backup_dir, exist_ok=True)
            
            # 生成备份文件名
            file_name = os.path.basename(file_path)
            timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            backup_name = f"{file_name}.{timestamp}.bak"
            backup_path = os.path.join(backup_dir, backup_name)
            
            # 执行备份
            shutil.copy2(file_path, backup_path)
            
            return True, backup_path
        except Exception as e:
            return False, f"备份失败: {str(e)}"
    
    @staticmethod
    def restore_from_backup(backup_path, original_path=None):
        """
        从备份恢复文件
        
        Args:
            backup_path (str): 备份文件路径
            original_path (str, optional): 原始文件路径，如果为None则从备份文件名推断
            
        Returns:
            tuple: (成功标志, 恢复路径或错误消息)
        """
        try:
            # 检查备份文件是否存在
            if not os.path.exists(backup_path):
                return False, f"备份文件不存在: {backup_path}"
            
            # 如果未指定原始路径，尝试从备份文件名推断
            if original_path is None:
                file_name = os.path.basename(backup_path)
                # 假设备份文件名格式为 "原始文件名.时间戳.bak"
                original_name = file_name.split('.', 1)[0]
                original_path = os.path.join(os.path.dirname(backup_path), original_name)
            
            # 执行恢复
            shutil.copy2(backup_path, original_path)
            
            return True, original_path
        except Exception as e:
            return False, f"恢复失败: {str(e)}"
    
    @staticmethod
    def batch_backup(file_paths, backup_dir=None):
        """
        批量备份文件
        
        Args:
            file_paths (list): 文件路径列表
            backup_dir (str, optional): 备份目录，如果为None则使用临时目录
            
        Returns:
            tuple: (成功标志, 备份路径字典, 错误列表)
        """
        backup_paths = {}
        errors = []
        
        # 执行备份
        for file_path in file_paths:
            success, result = FileOperations.create_backup(file_path, backup_dir)
            
            if success:
                backup_paths[file_path] = result
            else:
                errors.append((file_path, result))
        
        return len(backup_paths) > 0, backup_paths, errors
    
    @staticmethod
    def get_supported_file_types():
        """
        获取支持的文件类型
        
        Returns:
            list: 支持的文件扩展名列表
        """
        # 根据实际情况定义支持的文件类型
        return ['*']  # 支持所有文件类型
    
    @staticmethod
    def get_file_size(file_path):
        """
        获取文件大小
        
        Args:
            file_path (str): 文件路径
            
        Returns:
            tuple: (成功标志, 文件大小（字节）或错误消息)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                return False, f"文件不存在: {file_path}"
            
            # 获取文件大小
            size = os.path.getsize(file_path)
            
            return True, size
        except Exception as e:
            return False, f"获取文件大小失败: {str(e)}"
    
    @staticmethod
    def format_file_size(size_bytes):
        """
        格式化文件大小
        
        Args:
            size_bytes (int): 文件大小（字节）
            
        Returns:
            str: 格式化后的文件大小（带单位）
        """
        # 定义单位
        units = ['B', 'KB', 'MB', 'GB', 'TB']
        
        # 计算单位索引
        unit_index = 0
        while size_bytes >= 1024 and unit_index < len(units) - 1:
            size_bytes /= 1024
            unit_index += 1
        
        # 格式化输出
        return f"{size_bytes:.2f} {units[unit_index]}"
    
    @staticmethod
    def is_valid_filename(filename):
        """
        检查文件名是否有效
        
        Args:
            filename (str): 文件名
            
        Returns:
            bool: 如果文件名有效返回True，否则返回False
        """
        try:
            # 尝试创建路径对象
            path = Path(filename)
            
            # 检查是否包含非法字符
            if os.name == 'nt':  # Windows
                # Windows文件名不能包含以下字符: \ / : * ? " < > |
                invalid_chars = '\\/:"*?<>|'
                if any(c in filename for c in invalid_chars):
                    return False
            else:  # Unix/Linux/MacOS
                # Unix文件名不能包含斜杠
                if '/' in filename:
                    return False
            
            # 检查文件名长度
            if len(path.name) > 255:
                return False
            
            return True
        except Exception:
            return False
    
    @staticmethod
    def sanitize_filename(filename):
        """
        净化文件名，移除非法字符
        
        Args:
            filename (str): 原始文件名
            
        Returns:
            str: 净化后的文件名
        """
        # 如果文件名为空，返回默认名称
        if not filename:
            return "unnamed_file"
        
        # 移除非法字符
        if os.name == 'nt':  # Windows
            # Windows文件名不能包含以下字符: \ / : * ? " < > |
            invalid_chars = '\\/:"*?<>|'
            for c in invalid_chars:
                filename = filename.replace(c, '_')
        else:  # Unix/Linux/MacOS
            # Unix文件名不能包含斜杠
            filename = filename.replace('/', '_')
        
        # 去除首尾空白
        filename = filename.strip()
        
        # 限制长度
        if len(filename) > 255:
            base, ext = os.path.splitext(filename)
            filename = base[:255 - len(ext)] + ext
        
        # 如果文件名为空，返回默认名称
        if not filename:
            return "unnamed_file"
        
        return filename