#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import asyncio
import httpx
from PySide6.QtCore import QObject, Signal, Slot, QCoreApplication

class AIClient(QObject):
    """
    AI客户端类，负责与AI API的通信
    """
    
    # 定义信号
    analysis_started = Signal()
    analysis_completed = Signal(dict)
    analysis_failed = Signal(str)
    
    def __init__(self, config_manager, parent=None):
        """
        初始化AI客户端
        
        Args:
            config_manager: 配置管理器实例
            parent: 父对象
        """
        super().__init__(parent)
        self.config_manager = config_manager
        # 创建异步HTTP客户端，设置30秒超时
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def analyze_naming_pattern(self, original_files, example_files):
        """
        分析命名模式
        
        Args:
            original_files (list): 原始文件列表，每个元素是一个字典，包含name和path属性
            example_files (list): 示例文件列表，每个元素是一个字典，包含原始名称和新名称
            
        Returns:
            dict: 分析结果
        """
        # 发出分析开始信号
        self.analysis_started.emit()
        
        try:
            # 获取API配置
            api_key = self.config_manager.get_config('api_key')
            api_url = self.config_manager.get_config('api_url')
            api_model = self.config_manager.get_config('api_model')
            
            if not api_key or not api_url:
                raise ValueError("未配置API密钥或URL")
            
            # 构建请求数据
            payload = {
                "model": api_model or "deepseek-chat",
                "messages": [
                    {
                        "role": "system",
                        "content": "你是一个专门用于分析文件命名模式的AI助手。根据用户提供的原始文件名和重命名示例，你需要识别命名模式并应用于所有文件。"
                    },
                    {
                        "role": "user",
                        "content": self._build_prompt(original_files, example_files)
                    }
                ],
                "temperature": 0.3,  # 较低的温度以获得更一致的结果
                "response_format": {"type": "json_object"}  # 使用DeepSeek的JSON输出功能
            }
            
            # 发送API请求
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
            
            response = await self.client.post(
                api_url,
                headers=headers,
                json=payload
            )
            
            # 检查响应状态
            response.raise_for_status()
            result = response.json()
            
            # 处理DeepSeek API返回结果
            processed_result = self._process_api_response(result, original_files)
            
            # 发出分析完成信号
            self.analysis_completed.emit(processed_result)
            
            return processed_result
            
        except Exception as e:
            error_message = f"分析失败: {str(e)}"
            self.analysis_failed.emit(error_message)
            return {"error": error_message}
    
    def _build_prompt(self, original_files, example_files):
        """
        构建AI提示词
        
        Args:
            original_files (list): 原始文件列表
            example_files (list): 示例文件列表
            
        Returns:
            str: 构建的提示词
        """
        # 构建示例部分
        examples = ""
        for example in example_files:
            examples += f"原始文件名: {example['original_name']}\n"
            examples += f"新文件名: {example['new_name']}\n\n"
        
        # 构建待处理文件部分
        files_to_process = ""
        for file in original_files:
            files_to_process += f"- {file['name']}\n"
        
        # 完整提示词
        prompt = f"""
我需要你帮我分析文件重命名的模式，并将其应用于一组文件。

## 命名示例:
{examples}

## 需要处理的原始文件:
{files_to_process}

请分析这些示例的命名模式，并将相同的模式应用到所有需要处理的文件。对于每个文件，给出它应该被重命名的新名称。
返回格式要求：以JSON格式返回，每个文件一个对象，包含原始文件名(original_name)和新文件名(new_name)。
示例返回格式：
[
  {{"original_name": "file1.txt", "new_name": "renamed_file1.txt"}},
  {{"original_name": "file2.txt", "new_name": "renamed_file2.txt"}}
]
"""
        return prompt
    
    def _process_api_response(self, api_response, original_files):
        """
        处理API返回结果
        
        Args:
            api_response (dict): API返回的原始结果
            original_files (list): 原始文件列表
            
        Returns:
            dict: 处理后的结果
        """
        try:
            # 从API响应中提取文本内容
            content = api_response.get('choices', [{}])[0].get('message', {}).get('content', '')
            
            # 尝试从文本中提取JSON部分
            try:
                # 查找JSON开始和结束的位置
                start_index = content.find('[')
                end_index = content.rfind(']') + 1
                
                if start_index >= 0 and end_index > start_index:
                    json_str = content[start_index:end_index]
                    rename_data = json.loads(json_str)
                else:
                    raise ValueError("无法在响应中找到有效的JSON数据")
                
            except (json.JSONDecodeError, ValueError) as e:
                # 如果无法解析JSON，尝试使用正则表达式或其他方法提取文件名映射
                # 简单的实现可能不够健壮，这里仅作示例
                import re
                
                pattern = r'"original_name":\s*"([^"]+)",\s*"new_name":\s*"([^"]+)"'
                matches = re.findall(pattern, content)
                
                if matches:
                    rename_data = [
                        {"original_name": original, "new_name": new}
                        for original, new in matches
                    ]
                else:
                    raise ValueError(f"无法解析API响应: {str(e)}")
            
            # 确保所有原始文件都有对应的新名称
            result = {}
            for file in original_files:
                file_name = file['name']
                
                # 查找此文件的重命名结果
                rename_entry = next(
                    (item for item in rename_data if item['original_name'] == file_name),
                    None
                )
                
                if rename_entry:
                    # 如果找到重命名结果，使用它
                    result[file_name] = rename_entry['new_name']
                else:
                    # 如果没有找到，使用原始文件名
                    result[file_name] = file_name
            
            return {"rename_map": result, "raw_response": content}
            
        except Exception as e:
            return {
                "error": f"处理API响应时出错: {str(e)}",
                "raw_response": api_response
            }
    
    @Slot(list, list)
    def start_analysis(self, original_files, example_files):
        """
        启动异步分析任务
        
        Args:
            original_files (list): 原始文件列表
            example_files (list): 示例文件列表
        """
        asyncio.create_task(self.analyze_naming_pattern(original_files, example_files))
    
    def close(self):
        """
        关闭客户端
        """
        asyncio.create_task(self.client.aclose())