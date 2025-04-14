"""文档处理器模块。

这个模块提供了文档处理的核心功能。
"""

import os
import shutil
import logging
from typing import Dict, List, Optional, Any
from tqdm import tqdm

from .parsers.base import BaseParser
from .translator import BaseTranslator

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """文档处理器。
    
    这个类协调解析器和翻译器，处理整个文档翻译流程。
    
    Parameters
    ----------
    parser : BaseParser
        文档解析器
    translator : BaseTranslator
        翻译器
    output_dir : str
        输出目录路径
    target_lang : str, optional
        目标语言，默认为"zh-CN"
        
    Attributes
    ----------
    parser : BaseParser
        文档解析器
    translator : BaseTranslator
        翻译器
    output_dir : str
        输出目录路径
    target_lang : str
        目标语言
    """
    
    def __init__(
        self, 
        parser: BaseParser, 
        translator: BaseTranslator, 
        output_dir: str,
        target_lang: str = "zh-CN"
    ):
        """初始化文档处理器。
        
        Parameters
        ----------
        parser : BaseParser
            文档解析器
        translator : BaseTranslator
            翻译器
        output_dir : str
            输出目录路径
        target_lang : str, optional
            目标语言，默认为"zh-CN"
        """
        self.parser = parser
        self.translator = translator
        self.output_dir = os.path.abspath(output_dir)
        self.target_lang = target_lang
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
    
    def process_all(self) -> None:
        """处理所有文档文件。
        """
        # 获取所有需要翻译的文件
        files = self.parser.get_all_files()
        logger.info(f"找到 {len(files)} 个需要翻译的文件")
        
        # 复制静态资源
        self._copy_static_files()
        
        # 处理每个文件
        for file_path in tqdm(files, desc="翻译进度"):
            try:
                self._process_file(file_path)
            except Exception as e:
                logger.error(f"处理文件 {file_path} 时出错: {str(e)}")
    
    def _process_file(self, file_path: str) -> None:
        """处理单个文件。
        
        Parameters
        ----------
        file_path : str
            要处理的文件路径（相对于源目录）
        """
        logger.debug(f"开始处理文件: {file_path}")
        
        # 解析文件
        segments = self.parser.parse_file(file_path)
        logger.debug(f"文件 {file_path} 被分解为 {len(segments)} 个片段")
        
        # 翻译文本片段
        translated_segments = []
        for segment in segments:
            if segment['type'] in ['code_block', 'inline_code']:
                # 不翻译代码块
                translated_segments.append(segment)
            else:
                # 翻译文本
                try:
                    translated_content = self.translator.translate(
                        segment['content'], 
                        self.target_lang
                    )
                    translated_segment = segment.copy()
                    translated_segment['content'] = translated_content
                    translated_segments.append(translated_segment)
                except Exception as e:
                    logger.warning(f"翻译片段时出错: {str(e)}")
                    # 使用原始内容
                    translated_segments.append(segment)
        
        # 重建文件内容
        translated_content = self.parser.build_file(file_path, translated_segments)
        
        # 写入输出文件
        output_path = os.path.join(self.output_dir, file_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(translated_content)
        
        logger.debug(f"文件处理完成: {file_path}")
    
    def _copy_static_files(self) -> None:
        """复制静态资源文件。
        
        将非文档文件（如图片、CSS等）复制到输出目录。
        """
        # 源目录
        source_dir = self.parser.root_dir
        
        # 遍历源目录
        for root, _, files in os.walk(source_dir):
            # 计算相对路径
            rel_path = os.path.relpath(root, source_dir)
            
            # 创建目标目录
            if rel_path != '.':
                target_dir = os.path.join(self.output_dir, rel_path)
                os.makedirs(target_dir, exist_ok=True)
            else:
                target_dir = self.output_dir
            
            # 复制除了文档文件以外的文件
            for file in files:
                # 检查是否为需要翻译的文件类型
                if not self._is_document_file(file):
                    source_file = os.path.join(root, file)
                    target_file = os.path.join(target_dir, file)
                    
                    # 如果目标文件不存在或修改时间较旧，则复制
                    if (not os.path.exists(target_file) or 
                            os.path.getmtime(source_file) > os.path.getmtime(target_file)):
                        shutil.copy2(source_file, target_file)
                        logger.debug(f"复制静态文件: {os.path.join(rel_path, file)}")
    
    def _is_document_file(self, file_name: str) -> bool:
        """检查文件是否为需要翻译的文档文件。
        
        Parameters
        ----------
        file_name : str
            文件名
            
        Returns
        -------
        bool
            如果是文档文件则返回True，否则返回False
        """
        # 根据不同解析器类型判断
        if hasattr(self.parser, 'file_extensions'):
            return any(file_name.endswith(ext) for ext in self.parser.file_extensions)
        
        # 默认检查
        doc_extensions = ['.rst', '.md', '.markdown', '.txt']
        return any(file_name.endswith(ext) for ext in doc_extensions)
