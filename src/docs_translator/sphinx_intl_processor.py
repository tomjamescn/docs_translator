"""基于sphinx-intl的文档处理器模块。

这个模块提供了基于sphinx-intl处理Sphinx文档的专用处理器。
"""

import os
import logging
import subprocess
import tempfile
import shutil
import glob
from typing import Dict, List, Optional, Any, Tuple

from .parsers.sphinx_intl import SphinxIntlParser
from .translator import BaseTranslator

logger = logging.getLogger(__name__)


class SphinxIntlProcessor:
    """基于sphinx-intl的Sphinx文档处理器。
    
    这个类使用sphinx-intl处理Sphinx文档的翻译流程，适用于Sphinx文档项目。
    
    Parameters
    ----------
    parser : SphinxIntlParser
        Sphinx-intl解析器
    translator : BaseTranslator
        翻译器
    output_dir : str
        输出目录路径
    target_lang : str, optional
        目标语言，默认为"zh_CN"
        
    Attributes
    ----------
    parser : SphinxIntlParser
        Sphinx-intl解析器
    translator : BaseTranslator
        翻译器
    output_dir : str
        输出目录路径
    target_lang : str
        目标语言
    """
    
    def __init__(
        self, 
        parser: SphinxIntlParser, 
        translator: BaseTranslator, 
        output_dir: str,
        target_lang: str = "zh_CN"
    ):
        """初始化Sphinx-intl处理器。
        
        Parameters
        ----------
        parser : SphinxIntlParser
            Sphinx-intl文档解析器
        translator : BaseTranslator
            翻译器
        output_dir : str
            输出目录路径
        target_lang : str, optional
            目标语言，默认为"zh_CN"
        """
        self.parser = parser
        self.translator = translator
        self.output_dir = os.path.abspath(output_dir)
        self.target_lang = target_lang
        
        # 创建输出目录
        os.makedirs(self.output_dir, exist_ok=True)
    
    def process(self) -> None:
        """处理Sphinx文档的翻译。
        
        使用sphinx-intl工作流处理Sphinx文档翻译:
        1. 提取消息到.pot文件
        2. 生成.po文件
        3. 翻译.po文件
        4. 构建翻译后的文档
        """
        try:
            # 1. 提取消息到.pot文件
            logger.info("步骤1: 提取消息到.pot文件")
            if not self._extract_messages():
                logger.error("提取消息失败，停止处理")
                return
            
            # 2. 生成.po文件
            logger.info(f"步骤2: 为目标语言 {self.target_lang} 生成.po文件")
            if not self._generate_po_files():
                logger.error("生成.po文件失败，停止处理")
                return
            
            # 3. 翻译.po文件
            logger.info("步骤3: 翻译.po文件")
            if not self._translate_po_files():
                logger.error("翻译.po文件失败，停止处理")
                return
            
            # 4. 构建翻译后的文档
            logger.info(f"步骤4: 构建翻译后的文档到 {self.output_dir}")
            if not self._build_translated_docs():
                logger.error("构建翻译后的文档失败，停止处理")
                return
            
            logger.info("文档翻译处理完成")
            
        except Exception as e:
            logger.error(f"处理过程中发生错误: {str(e)}")
    
    def _extract_messages(self) -> bool:
        """提取消息到.pot文件。
        
        Returns
        -------
        bool
            操作是否成功
        """
        return self.parser.extract_messages()
    
    def _generate_po_files(self) -> bool:
        """生成.po文件。
        
        Returns
        -------
        bool
            操作是否成功
        """
        return self.parser.generate_po_files(self.target_lang)
    
    def _translate_po_files(self) -> bool:
        """翻译.po文件内容。
        
        Returns
        -------
        bool
            操作是否成功
        """
        try:
            # 找到所有的.po文件
            locale_dir = self.parser.locale_dir
            po_dir = os.path.join(locale_dir, self.target_lang, 'LC_MESSAGES')
            
            # 检查目录是否存在
            if not os.path.exists(po_dir):
                logger.warning(f"标准PO文件目录不存在: {po_dir}，尝试查找其他可能的目录...")
                
                # 尝试递归搜索找到所有.po文件
                po_files_paths = []
                for root, _, files in os.walk(locale_dir):
                    for file in files:
                        if file.endswith('.po'):
                            po_files_paths.append(os.path.join(root, file))
                
                if not po_files_paths:
                    # 如果没有找到任何.po文件，尝试运行sphinx-intl命令创建
                    logger.warning("没有找到任何.po文件，尝试重新运行sphinx-intl...")
                    if not self.parser.generate_po_files(self.target_lang):
                        logger.error("无法生成.po文件")
                        return False
                    
                    # 再次尝试寻找.po文件
                    for root, _, files in os.walk(locale_dir):
                        for file in files:
                            if file.endswith('.po'):
                                po_files_paths.append(os.path.join(root, file))
                
                if not po_files_paths:
                    logger.error("在尝试所有方法后仍未找到.po文件")
                    return False
                
                logger.info(f"找到 {len(po_files_paths)} 个.po文件需要翻译")
                
                # 翻译找到的所有.po文件
                for po_path in po_files_paths:
                    logger.info(f"翻译文件: {po_path}")
                    self._translate_po_file(po_path)
            else:
                # 标准目录存在，按原计划处理
                po_files = [f for f in os.listdir(po_dir) if f.endswith('.po')]
                logger.info(f"找到 {len(po_files)} 个.po文件需要翻译")
                
                for po_file in po_files:
                    po_path = os.path.join(po_dir, po_file)
                    logger.info(f"翻译文件: {po_path}")
                    self._translate_po_file(po_path)
            
            return True
            
        except Exception as e:
            logger.error(f"翻译.po文件时出错: {str(e)}")
            return False
    
    def _translate_po_file(self, po_path: str) -> None:
        """翻译单个.po文件。
        
        Parameters
        ----------
        po_path : str
            .po文件路径
        """
        try:
            import polib
            
            # 加载.po文件
            po = polib.pofile(po_path)
            
            # 逐条翻译
            for entry in po:
                if entry.msgstr == "" and not entry.obsolete:
                    # 只翻译未翻译且非过时的条目
                    try:
                        translated = self.translator.translate(
                            entry.msgid, 
                            self.target_lang
                        )
                        entry.msgstr = translated
                        logger.debug(f"已翻译: '{entry.msgid[:30]}...' -> '{translated[:30]}...'")
                    except Exception as e:
                        logger.warning(f"翻译条目时出错: {str(e)}")
                        # 继续处理其他条目
            
            # 保存翻译后的.po文件
            po.save(po_path)
            
            logger.info(f"翻译完成: {po_path}")
            
        except ImportError:
            # 如果没有polib，使用简单文本替换
            logger.warning("未找到polib库，使用简单替换方法")
            self._translate_po_file_simple(po_path)
        
        except Exception as e:
            logger.warning(f"翻译.po文件 {po_path} 时出错: {str(e)}")
    
    def _translate_po_file_simple(self, po_path: str) -> None:
        """使用简单文本处理方式翻译.po文件。
        
        当polib不可用时的备选方案。
        
        Parameters
        ----------
        po_path : str
            .po文件路径
        """
        try:
            with open(po_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析.po文件
            msgid_pattern = r'msgid "(.*?)"\nmsgstr ""'
            
            # 查找所有未翻译的字符串
            import re
            matches = re.findall(msgid_pattern, content, re.DOTALL)
            
            # 逐条翻译
            for msgid in matches:
                if msgid.strip() and msgid != "":
                    try:
                        # 对msgid进行转义处理
                        escaped_msgid = msgid.replace('"', '\\"')
                        # 翻译内容
                        translated = self.translator.translate(msgid, self.target_lang)
                        # 对翻译后的内容进行转义处理
                        escaped_translated = translated.replace('"', '\\"')
                        
                        # 替换原文件中的内容
                        pattern = f'msgid "{escaped_msgid}"\nmsgstr ""'
                        replacement = f'msgid "{escaped_msgid}"\nmsgstr "{escaped_translated}"'
                        content = content.replace(pattern, replacement)
                        
                        logger.debug(f"已翻译: '{msgid[:30]}...' -> '{translated[:30]}...'")
                    except Exception as e:
                        logger.warning(f"翻译条目时出错: {str(e)}")
                        # 继续处理其他条目
            
            # 写回文件
            with open(po_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"使用简单方法翻译完成: {po_path}")
            
        except Exception as e:
            logger.warning(f"使用简单方法翻译.po文件 {po_path} 时出错: {str(e)}")
    
    def _build_translated_docs(self) -> bool:
        """构建翻译后的文档。
        
        Returns
        -------
        bool
            操作是否成功
        """
        return self.parser.build_translated_docs(self.target_lang, self.output_dir)