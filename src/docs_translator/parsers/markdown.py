"""Markdown文档解析器实现。

这个模块提供了用于解析Markdown文档的解析器。
"""

import os
import re
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseParser


class MarkdownParser(BaseParser):
    """Markdown文档解析器。
    
    这个解析器能够解析Markdown格式的文档，并将其分解为可翻译的片段。
    
    Parameters
    ----------
    root_dir : str
        Markdown文档的根目录
    file_extensions : List[str], optional
        要处理的文件扩展名列表，默认为['.md', '.markdown']
    
    Attributes
    ----------
    root_dir : str
        Markdown文档的根目录
    file_extensions : List[str]
        要处理的文件扩展名列表
    """
    
    def __init__(self, root_dir: str, file_extensions: Optional[List[str]] = None):
        """初始化Markdown解析器。
        
        Parameters
        ----------
        root_dir : str
            Markdown文档的根目录
        file_extensions : List[str], optional
            要处理的文件扩展名列表，默认为['.md', '.markdown']
        """
        super().__init__(root_dir)
        self.file_extensions = file_extensions or ['.md', '.markdown']
    
    def get_all_files(self) -> List[str]:
        """获取所有需要翻译的Markdown文件路径。
        
        Returns
        -------
        List[str]
            需要翻译的Markdown文件的相对路径列表
        """
        markdown_files = []
        
        for root, _, files in os.walk(self.root_dir):
            for file in files:
                if any(file.endswith(ext) for ext in self.file_extensions):
                    rel_path = os.path.relpath(os.path.join(root, file), self.root_dir)
                    markdown_files.append(rel_path)
        
        return markdown_files
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """解析Markdown文件，将其分解为可翻译的片段。
        
        Parameters
        ----------
        file_path : str
            要解析的Markdown文件路径
            
        Returns
        -------
        List[Dict[str, Any]]
            文件中解析出的片段列表，每个片段为一个字典，
            包含'content'、'type'和'position'字段
        """
        full_path = os.path.join(self.root_dir, file_path)
        
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        segments = []
        position = 0
        
        # 分隔代码块和非代码块
        pattern = r'(```[^\n]*\n.*?```|`.*?`)'
        parts = re.split(pattern, content, flags=re.DOTALL)
        
        for part in parts:
            if not part:
                continue
                
            # 检查是否为代码块
            if part.startswith('```') and part.endswith('```'):
                segments.append({
                    'content': part,
                    'type': 'code_block',
                    'position': position
                })
            # 检查是否为内联代码
            elif part.startswith('`') and part.endswith('`'):
                segments.append({
                    'content': part,
                    'type': 'inline_code',
                    'position': position
                })
            # 普通文本
            else:
                # 进一步分割文本为段落
                paragraphs = re.split(r'(\n{2,})', part)
                for para in paragraphs:
                    if para.strip():
                        segments.append({
                            'content': para,
                            'type': 'text',
                            'position': position
                        })
                        position += 1
            
            position += 1
        
        return segments
    
    def build_file(self, file_path: str, translated_segments: List[Dict[str, Any]]) -> str:
        """根据翻译后的片段重建Markdown文件内容。
        
        Parameters
        ----------
        file_path : str
            原始Markdown文件路径
        translated_segments : List[Dict[str, Any]]
            翻译后的片段列表
            
        Returns
        -------
        str
            重建后的Markdown文件内容
        """
        # 按位置排序片段
        sorted_segments = sorted(translated_segments, key=lambda x: x['position'])
        
        # 组合所有片段
        content = ''.join(segment['content'] for segment in sorted_segments)
        
        return content
