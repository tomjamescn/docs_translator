"""Sphinx-intl集成的Sphinx文档解析器实现。

这个模块提供了基于sphinx-intl的Sphinx文档解析和翻译功能。
"""

import os
import re
import subprocess
import tempfile
import shutil
import logging
from typing import Dict, List, Optional, Any, Tuple

from .base import BaseParser

logger = logging.getLogger(__name__)


class SphinxIntlParser(BaseParser):
    """基于sphinx-intl的Sphinx文档解析器。
    
    这个解析器利用sphinx-intl和Sphinx的gettext构建器处理Sphinx文档的国际化翻译。
    
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
    pot_dir : str
        存储.pot文件的目录路径
    locale_dir : str
        存储翻译文件的目录路径
    """
    
    def __init__(self, root_dir: str, config_path: Optional[str] = None):
        """初始化Sphinx-intl解析器。
        
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
        
        # 设置pot和locale目录
        self.pot_dir = os.path.join(self.root_dir, "_build", "gettext")
        self.locale_dir = os.path.join(self.root_dir, "locale")
        
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
    
    def _get_source_dir(self) -> str:
        """获取Sphinx源文件目录。
        
        Returns
        -------
        str
            源文件目录路径
        """
        # 如果conf.py在source目录中，则返回source目录
        if self.config_path and os.path.dirname(self.config_path) != self.root_dir:
            return os.path.dirname(self.config_path)
        
        # 检查常见源目录
        source_dir = os.path.join(self.root_dir, 'source')
        if os.path.isdir(source_dir):
            return source_dir
        
        # 默认使用根目录
        return self.root_dir
    
    def get_all_files(self) -> List[str]:
        """获取所有需要翻译的Sphinx文档文件路径。
        
        Returns
        -------
        List[str]
            需要翻译的文件的相对路径列表
        """
        doc_files = []
        
        # 确定文档目录
        source_dir = self._get_source_dir()
        
        for root, _, files in os.walk(source_dir):
            for file in files:
                if any(file.endswith(ext) for ext in self.file_extensions):
                    rel_path = os.path.relpath(os.path.join(root, file), self.root_dir)
                    doc_files.append(rel_path)
        
        return doc_files
    
    def extract_messages(self) -> bool:
        """提取需要翻译的消息到.pot文件。
        
        使用Sphinx的gettext构建器提取消息。
        
        Returns
        -------
        bool
            操作是否成功
        """
        try:
            # 确定源目录和构建目录
            source_dir = self._get_source_dir()
            
            # 确保pot_dir目录存在
            os.makedirs(self.pot_dir, exist_ok=True)
            
            # 构建sphinx-build命令
            cmd = [
                "sphinx-build",
                "-b", "gettext",
                source_dir,
                self.pot_dir
            ]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            # 执行命令
            result = subprocess.run(
                cmd, 
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"sphinx-build命令失败: {result.stderr}")
                return False
                
            logger.info("提取消息完成")
            return True
            
        except Exception as e:
            logger.error(f"提取消息失败: {str(e)}")
            return False
    
    def parse_file(self, file_path: str) -> List[Dict[str, Any]]:
        """解析Sphinx文档文件，将其分解为可翻译的片段。
        
        由于使用sphinx-intl，这个方法的实现方式与传统解析不同。
        它会读取原始文件，并返回原始内容作为一个片段，稍后在翻译过程中
        会通过sphinx-intl和.po文件处理。
        
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
            # RST文件，返回整个文件作为一个片段
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return [{
                'content': content,
                'type': 'file',
                'position': 0,
                'path': file_path
            }]
    
    def build_file(self, file_path: str, translated_segments: List[Dict[str, Any]]) -> str:
        """根据翻译后的片段重建文件内容。
        
        对于RST文件，由于我们处理的是整个文件，
        所以直接返回翻译后的内容。
        
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
            # 对于RST文件，直接返回翻译内容
            return translated_segments[0]['content']
    
    def generate_po_files(self, target_lang: str) -> bool:
        """为目标语言生成.po文件。
        
        Parameters
        ----------
        target_lang : str
            目标语言代码，例如"zh_CN"
            
        Returns
        -------
        bool
            操作是否成功
        """
        try:
            # 创建locale目录
            os.makedirs(self.locale_dir, exist_ok=True)
            
            # 构建sphinx-intl命令
            cmd = [
                "sphinx-intl", "update",
                "-p", self.pot_dir,
                "-d", self.locale_dir,
                "-l", target_lang
            ]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            # 执行命令
            result = subprocess.run(
                cmd, 
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"sphinx-intl命令失败: {result.stderr}")
                return False
                
            logger.info("生成.po文件完成")
            return True
            
        except Exception as e:
            logger.error(f"生成.po文件失败: {str(e)}")
            return False
    
    def build_translated_docs(self, target_lang: str, output_dir: str) -> bool:
        """构建翻译后的文档。
        
        Parameters
        ----------
        target_lang : str
            目标语言代码，例如"zh_CN"
        output_dir : str
            输出目录路径
            
        Returns
        -------
        bool
            操作是否成功
        """
        try:
            # 确定源目录
            source_dir = self._get_source_dir()
            
            # 构建sphinx-build命令
            cmd = [
                "sphinx-build",
                "-b", "html",
                "-D", f"language={target_lang}",
                "-D", f"locale_dirs={self.locale_dir}",
                source_dir,
                output_dir
            ]
            
            logger.info(f"执行命令: {' '.join(cmd)}")
            
            # 执行命令
            result = subprocess.run(
                cmd, 
                capture_output=True,
                text=True,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"构建文档命令失败: {result.stderr}")
                return False
                
            logger.info("构建翻译文档完成")
            return True
            
        except Exception as e:
            logger.error(f"构建翻译文档失败: {str(e)}")
            return False