"""提供简化的API接口。

此模块提供了简化的API，方便用户直接在Python代码中使用文档翻译功能。
"""

import os
from typing import Dict, List, Optional, Any

from .translator import OpenAITranslator, BaseTranslator
from .parsers import MarkdownParser, SphinxParser, BaseParser
from .processor import DocumentProcessor


def translate_docs(
    source_dir: str,
    output_dir: str,
    doc_type: str = "auto",
    target_lang: str = "zh-CN",
    api_key: Optional[str] = None,
    api_base: Optional[str] = None,
    model: str = "gpt-3.5-turbo"
) -> None:
    """翻译文档目录。
    
    这是一个简化的API，用于翻译整个文档目录。
    
    Parameters
    ----------
    source_dir : str
        源文档目录路径
    output_dir : str
        翻译输出目录路径
    doc_type : str, optional
        文档类型，可选值为"markdown"、"sphinx"或"auto"，默认为"auto"
    target_lang : str, optional
        目标语言，默认为"zh-CN"
    api_key : str, optional
        OpenAI兼容的API密钥，也可通过OPENAI_API_KEY环境变量设置
    api_base : str, optional
        API的基础URL，默认为OpenAI的API地址
    model : str, optional
        使用的模型名称，默认为"gpt-3.5-turbo"
        
    Raises
    ------
    ValueError
        如果未提供API密钥或源目录不存在
    """
    # 检查API密钥
    api_key = api_key or os.environ.get('OPENAI_API_KEY')
    if not api_key:
        raise ValueError("请提供OpenAI API密钥（通过api_key参数或OPENAI_API_KEY环境变量）")
    
    # 获取API基础URL
    api_base = api_base or os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
    
    # 检查源目录
    if not os.path.isdir(source_dir):
        raise ValueError(f"源目录不存在: {source_dir}")
    
    # 创建翻译器
    translator = OpenAITranslator(
        api_key=api_key,
        api_base=api_base,
        model=model
    )
    
    # 创建解析器
    if doc_type == "markdown":
        parser = MarkdownParser(source_dir)
    elif doc_type == "sphinx":
        parser = SphinxParser(source_dir)
    else:
        # 自动检测
        if _is_sphinx_project(source_dir):
            parser = SphinxParser(source_dir)
        else:
            parser = MarkdownParser(source_dir)
    
    # 创建文档处理器
    processor = DocumentProcessor(
        parser=parser,
        translator=translator,
        output_dir=output_dir,
        target_lang=target_lang
    )
    
    # 开始处理
    processor.process_all()


def _is_sphinx_project(directory: str) -> bool:
    """检查指定目录是否为Sphinx项目。
    
    Parameters
    ----------
    directory : str
        要检查的目录路径
        
    Returns
    -------
    bool
        如果是Sphinx项目则返回True，否则返回False
    """
    # 检查是否存在conf.py文件（Sphinx配置文件）
    conf_path = os.path.join(directory, 'conf.py')
    if os.path.exists(conf_path):
        return True
    
    # 检查source目录
    source_dir = os.path.join(directory, 'source')
    if os.path.isdir(source_dir):
        conf_path = os.path.join(source_dir, 'conf.py')
        if os.path.exists(conf_path):
            return True
    
    # 检查doc/docs目录
    for doc_dir in ['doc', 'docs']:
        dir_path = os.path.join(directory, doc_dir)
        if os.path.isdir(dir_path):
            conf_path = os.path.join(dir_path, 'conf.py')
            if os.path.exists(conf_path):
                return True
    
    return False
