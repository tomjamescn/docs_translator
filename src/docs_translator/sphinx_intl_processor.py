"""基于sphinx-intl的文档处理器模块。

这个模块提供了基于sphinx-intl处理Sphinx文档的专用处理器。
"""

import os
import logging
import subprocess
import tempfile
import shutil
import glob
import time
import sys
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
    batch_size : int, optional
        批量翻译时每批处理的数量，默认为10
    show_cache_stats : bool, optional
        是否在处理结束时显示缓存统计，默认为True
        
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
    batch_size : int
        批量处理大小
    show_cache_stats : bool
        是否显示缓存统计
    """
    
    def __init__(
        self, 
        parser: SphinxIntlParser, 
        translator: BaseTranslator, 
        output_dir: str,
        target_lang: str = "zh_CN",
        batch_size: int = 10,
        show_cache_stats: bool = True
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
        batch_size : int, optional
            批量翻译大小，默认为10
        show_cache_stats : bool, optional
            是否显示缓存统计，默认为True
        """
        self.parser = parser
        self.translator = translator
        self.output_dir = os.path.abspath(output_dir)
        self.target_lang = target_lang
        self.batch_size = batch_size
        self.show_cache_stats = show_cache_stats
        
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
            start_time = time.time()
            
            # 1. 提取消息到.pot文件
            logger.info("步骤1: 提取消息到.pot文件")
            print("步骤1: 提取消息到.pot文件")
            if not self._extract_messages():
                logger.error("提取消息失败，停止处理")
                print("提取消息失败，停止处理")
                return
            
            # 2. 生成.po文件
            logger.info(f"步骤2: 为目标语言 {self.target_lang} 生成.po文件")
            print(f"步骤2: 为目标语言 {self.target_lang} 生成.po文件")
            if not self._generate_po_files():
                logger.error("生成.po文件失败，停止处理")
                print("生成.po文件失败，停止处理")
                return
            
            # 3. 翻译.po文件
            logger.info("步骤3: 翻译.po文件")
            print("步骤3: 翻译.po文件")
            if not self._translate_po_files():
                logger.error("翻译.po文件失败，停止处理")
                print("翻译.po文件失败，停止处理")
                return
            
            # 4. 构建翻译后的文档
            logger.info(f"步骤4: 构建翻译后的文档到 {self.output_dir}")
            print(f"步骤4: 构建翻译后的文档到 {self.output_dir}")
            if not self._build_translated_docs():
                logger.error("构建翻译后的文档失败，停止处理")
                print("构建翻译后的文档失败，停止处理")
                return
            
            # 显示缓存统计
            if self.show_cache_stats and hasattr(self.translator, 'get_cache_stats'):
                stats = self.translator.get_cache_stats()
                print("\n翻译缓存统计:")
                print(f"- 缓存命中: {stats.get('hits', 0)}次")
                print(f"- 缓存未命中: {stats.get('misses', 0)}次")
                print(f"- 缓存条目总数: {stats.get('cache_entries', 0)}个")
                print(f"- 节省的API调用: {stats.get('saved_calls', 0)}次")
                print(f"- 预估节省费用: ${stats.get('estimated_saving_usd', 0):.3f}")
                print(f"- 缓存文件: {stats.get('cache_file', '')}")
            
            total_time = time.time() - start_time
            logger.info(f"文档翻译处理完成，总用时: {total_time:.1f}秒")
            print(f"\n文档翻译处理完成，总用时: {total_time:.1f}秒")
            
        except Exception as e:
            logger.error(f"处理过程中发生错误: {str(e)}")
            print(f"处理过程中发生错误: {str(e)}")
    
    def _extract_messages(self) -> bool:
        """提取消息到.pot文件。
        
        Returns
        -------
        bool
            操作是否成功
        """
        print("正在提取消息...")
        result = self.parser.extract_messages()
        if result:
            print("消息提取成功")
        return result
    
    def _generate_po_files(self) -> bool:
        """生成.po文件。
        
        Returns
        -------
        bool
            操作是否成功
        """
        print(f"正在为 {self.target_lang} 生成.po文件...")
        result = self.parser.generate_po_files(self.target_lang)
        if result:
            print(".po文件生成成功")
        return result
    
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
                print(f"标准PO文件目录不存在: {po_dir}，尝试查找其他可能的目录...")
                
                # 尝试递归搜索找到所有.po文件
                po_files_paths = []
                for root, _, files in os.walk(locale_dir):
                    for file in files:
                        if file.endswith('.po'):
                            po_files_paths.append(os.path.join(root, file))
                
                if not po_files_paths:
                    # 如果没有找到任何.po文件，尝试运行sphinx-intl命令创建
                    logger.warning("没有找到任何.po文件，尝试重新运行sphinx-intl...")
                    print("没有找到任何.po文件，尝试重新运行sphinx-intl...")
                    if not self.parser.generate_po_files(self.target_lang):
                        logger.error("无法生成.po文件")
                        print("无法生成.po文件")
                        return False
                    
                    # 再次尝试寻找.po文件
                    for root, _, files in os.walk(locale_dir):
                        for file in files:
                            if file.endswith('.po'):
                                po_files_paths.append(os.path.join(root, file))
                
                if not po_files_paths:
                    logger.error("在尝试所有方法后仍未找到.po文件")
                    print("在尝试所有方法后仍未找到.po文件")
                    return False
                
                logger.info(f"找到 {len(po_files_paths)} 个.po文件需要翻译")
                print(f"找到 {len(po_files_paths)} 个.po文件需要翻译")
                
                # 翻译找到的所有.po文件
                for i, po_path in enumerate(po_files_paths):
                    print(f"[{i+1}/{len(po_files_paths)}] 翻译文件: {os.path.basename(po_path)}")
                    self._translate_po_file(po_path)
            else:
                # 标准目录存在，按原计划处理
                po_files = [f for f in os.listdir(po_dir) if f.endswith('.po')]
                logger.info(f"找到 {len(po_files)} 个.po文件需要翻译")
                print(f"找到 {len(po_files)} 个.po文件需要翻译")
                
                for i, po_file in enumerate(po_files):
                    po_path = os.path.join(po_dir, po_file)
                    print(f"[{i+1}/{len(po_files)}] 翻译文件: {po_file}")
                    self._translate_po_file(po_path)
            
            return True
            
        except Exception as e:
            logger.error(f"翻译.po文件时出错: {str(e)}")
            print(f"翻译.po文件时出错: {str(e)}")
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
            
            # 收集需要翻译的条目
            to_translate = []
            entries_to_update = []
            
            for entry in po:
                if entry.msgstr == "" and not entry.obsolete:
                    # 只收集未翻译且非过时的条目
                    to_translate.append(entry.msgid)
                    entries_to_update.append(entry)
            
            total_entries = len(to_translate)
            if total_entries == 0:
                print(f"文件 {os.path.basename(po_path)} 中没有需要翻译的条目")
                return
            
            print(f"文件 {os.path.basename(po_path)} 中有 {total_entries} 个条目需要翻译")
            
            # 批量翻译
            start_time = time.time()
            
            # 使用translator.batch_translate进行批量翻译
            # 这会自动处理缓存
            translated_texts = self.translator.batch_translate(
                to_translate, 
                self.target_lang, 
                self.batch_size
            )
            
            # 更新PO条目
            for entry, translated_text in zip(entries_to_update, translated_texts):
                entry.msgstr = translated_text
            
            # 保存翻译后的.po文件
            po.save(po_path)
            
            # 显示完成信息
            total_time = time.time() - start_time
            print(f"文件 {os.path.basename(po_path)} 翻译完成! 用时: {total_time:.1f} 秒, 平均速度: {total_entries/total_time:.2f} 条目/秒")
            
        except ImportError:
            # 如果没有polib，使用简单文本替换
            logger.warning("未找到polib库，使用简单替换方法")
            print("未找到polib库，使用简单替换方法")
            self._translate_po_file_simple(po_path)
        
        except Exception as e:
            logger.warning(f"翻译.po文件 {po_path} 时出错: {str(e)}")
            print(f"翻译.po文件 {os.path.basename(po_path)} 时出错: {str(e)}")
    
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
            
            # 准备批量翻译
            total_entries = len(matches)
            if total_entries == 0:
                print(f"文件 {os.path.basename(po_path)} 中没有需要翻译的条目")
                return
            
            print(f"文件 {os.path.basename(po_path)} 中有 {total_entries} 个条目需要翻译")
            
            # 批量翻译
            start_time = time.time()
            to_translate = []
            
            # 收集需要翻译的文本
            for msgid in matches:
                if msgid.strip() and msgid != "":
                    to_translate.append(msgid)
            
            # 使用translator.batch_translate进行批量翻译
            # 这会自动处理缓存
            all_translated = self.translator.batch_translate(
                to_translate, 
                self.target_lang, 
                self.batch_size
            )
            
            # 更新.po文件内容
            for msgid, translated in zip(to_translate, all_translated):
                # 对msgid和translated进行转义处理
                escaped_msgid = msgid.replace('"', '\\"')
                escaped_translated = translated.replace('"', '\\"')
                
                # 替换原文件中的内容
                pattern = f'msgid "{escaped_msgid}"\nmsgstr ""'
                replacement = f'msgid "{escaped_msgid}"\nmsgstr "{escaped_translated}"'
                content = content.replace(pattern, replacement)
            
            # 写回文件
            with open(po_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 显示完成信息
            total_time = time.time() - start_time
            print(f"文件 {os.path.basename(po_path)} 简单模式翻译完成! 用时: {total_time:.1f} 秒, 平均速度: {total_entries/total_time:.2f} 条目/秒")
            
        except Exception as e:
            logger.warning(f"使用简单方法翻译.po文件 {po_path} 时出错: {str(e)}")
            print(f"使用简单方法翻译.po文件 {os.path.basename(po_path)} 时出错: {str(e)}")
    
    def _build_translated_docs(self) -> bool:
        """构建翻译后的文档。
        
        Returns
        -------
        bool
            操作是否成功
        """
        print(f"正在构建翻译后的文档到 {self.output_dir}...")
        result = self.parser.build_translated_docs(self.target_lang, self.output_dir)
        if result:
            print("文档构建成功!")
        return result