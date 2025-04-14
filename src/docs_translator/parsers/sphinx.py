"""Sphinx文档解析器实现。

这个模块提供了用于解析Sphinx文档的解析器。
"""

import os
import re
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseParser


class SphinxParser(BaseParser):
    """Sphinx文档解析器。
    
    这个解析器能够解析Sphinx格式的文档，支持reST和可能的Markdown文件。
    
    Parameters
    ----------
    root_dir : str
        Sphinx文档的根目录
    config_path : str, optional
        Sphinx配置文件(conf.py)的路径，默认为None，将自动查找
    
    Attributes
    ----------
    root_dir : str
        Sphinx文档的根目录
    config_path : str
        Sphinx配置文件的路径
    file_extensions : List[str]
        要处理的文件扩展名列表
    """
    
    def __init__(self, root_dir: str, config_path: Optional[str] = None):
        """初始化Sphinx解析器。
        
        Parameters
        ----------
        root_dir : str
            Sphinx文档的根目录
        config_path : str, optional
            Sphinx配置文件(conf.py)的路径，默认为None，将自动查找
        """
        super().__init__(root_dir)
        
        self.file_extensions = ['.rst', '.txt']
        
        # 查找conf.py文件
        if config_path:
            self.config_path = os.path.abspath(config_path)
        else:
            self.config_path = self._find_config()
        
        # 检查是否启用了Markdown支持
        if self.config_path and os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_content = f.read()
                if 'myst_parser' in config_content or 'recommonmark' in config_content:
                    self.file_extensions.extend(['.md', '.markdown'])
    
    def _find_config(self) -> Optional[str]:
        """查找Sphinx配置文件。
        
        Returns
        -------
        Optional[str]
            找到的配置文件路径，如果未找到则为None
        """
        # 首先检查root_dir下是否有conf.py
        conf_path = os.path.join(self.root_dir, 'conf.py')
        if os.path.exists(conf_path):
            return conf_path
        
        # 查找source目录
        source_dir = os.path.join(self.root_dir, 'source')
        if os.path.isdir(source_dir):
            conf_path = os.path.join(source_dir, 'conf.py')
            if os.path.exists(conf_path):
                return conf_path
        
        # 查找doc或docs目录
        for doc_dir in ['doc', 'docs']:
            dir_path = os.path.join(self.root_dir, doc_dir)
            if os.path.isdir(dir_path):
                conf_path = os.path.join(dir_path, 'conf.py')
                if os.path.exists(conf_path):
                    return conf_path
        
        return None
    
    def get_all_files(self) -> List[str]:
        """获取所有需要翻译的Sphinx文档文件路径。
        
        Returns
        -------
        List[str]
            需要翻译的文件的相对路径列表
        """
        doc_files = []
        
        # 确定文档目录
        doc_dirs = [self.root_dir]
        source_dir = os.path.join(self.root_dir, 'source')
        if os.path.isdir(source_dir):
            doc_dirs = [source_dir]
        
        for doc_dir in doc_dirs:
            for root, _, files in os.walk(doc_dir):
                for file in files:
                    if any(file.endswith(ext) for ext in self.file_extensions):
                        rel_path = os.path.relpath(os.path.join(root, file), self.root_dir)
                        doc_files.append(rel_path)
        
        return doc_files
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """解析Sphinx文档文件，将其分解为可翻译的片段。
        
        Parameters
        ----------
        file_path : str
            要解析的文件路径
            
        Returns
        -------
        List[Dict[str, Any]]
            文件中解析出的片段列表
        """
        full_path = os.path.join(self.root_dir, file_path)
        
        # 根据文件扩展名选择解析方法
        if file_path.endswith(('.md', '.markdown')):
            # 使用Markdown解析逻辑
            from .markdown import MarkdownParser
            md_parser = MarkdownParser(self.root_dir)
            return md_parser.parse_file(file_path)
        else:
            # RST解析逻辑
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            segments = []
            position = 0
            
            # 处理代码块
            code_pattern = r'(.. code-block::.*?(?:\n\s{4}.*?)+)'
            parts = re.split(code_pattern, content, flags=re.DOTALL)
            
            for part in parts:
                if not part:
                    continue
                
                # 检查是否为代码块
                if part.startswith('.. code-block::'):
                    segments.append({
                        'content': part,
                        'type': 'code_block',
                        'position': position
                    })
                    position += 1
                else:
                    # 处理指令块
                    directive_pattern = r'(\.\. [a-z-]+::.*?(?:\n\s{4}.*?)+)'
                    directive_parts = re.split(directive_pattern, part, flags=re.DOTALL)
                    
                    for d_part in directive_parts:
                        if not d_part:
                            continue
                        
                        if re.match(r'\.\. [a-z-]+::', d_part):
                            segments.append({
                                'content': d_part,
                                'type': 'directive',
                                'position': position
                            })
                        else:
                            # 分割为段落
                            paras = re.split(r'(\n{2,})', d_part)
                            for para in paras:
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
        """根据翻译后的片段重建文件内容。
        
        Parameters
        ----------
        file_path : str
            原始文件路径
        translated_segments : List[Dict[str, Any]]
            翻译后的片段列表
            
        Returns
        -------
        str
            重建后的文件内容
        """
        # 根据文件扩展名选择重建方法
        if file_path.endswith(('.md', '.markdown')):
            # 使用Markdown重建逻辑
            from .markdown import MarkdownParser
            md_parser = MarkdownParser(self.root_dir)
            return md_parser.build_file(file_path, translated_segments)
        else:
            # 排序并组合片段
            sorted_segments = sorted(translated_segments, key=lambda x: x['position'])
            content = ''.join(segment['content'] for segment in sorted_segments)
            
            return content
