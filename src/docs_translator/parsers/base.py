"""基础解析器实现。

这个模块定义了所有文档解析器的基类。
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
import os
import logging

logger = logging.getLogger(__name__)


class BaseParser(ABC):
    """文档解析器基类。
    
    所有特定文档格式的解析器都应该继承这个类并实现其抽象方法。
    
    Parameters
    ----------
    root_dir : str
        文档目录的根路径
        
    Attributes
    ----------
    root_dir : str
        文档目录的根路径
    """
    
    def __init__(self, root_dir: str):
        """初始化解析器。
        
        Parameters
        ----------
        root_dir : str
            文档目录的根路径
        """
        self.root_dir = os.path.abspath(root_dir)
        if not os.path.isdir(self.root_dir):
            raise ValueError(f"目录不存在: {self.root_dir}")
    
    @abstractmethod
    def get_all_files(self) -> List[str]:
        """获取所有需要翻译的文件路径。
        
        Returns
        -------
        List[str]
            需要翻译的文件的相对路径列表
        """
        pass
    
    @abstractmethod
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """解析单个文件，将其分解为可翻译的片段。
        
        Parameters
        ----------
        file_path : str
            要解析的文件路径
            
        Returns
        -------
        List[Dict[str, Any]]
            文件中解析出的片段列表，每个片段为一个字典，
            至少包含'content'和'type'字段
        """
        pass
    
    @abstractmethod
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
        pass
