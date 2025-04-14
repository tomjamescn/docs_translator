"""命令行接口模块。

这个模块提供了文档翻译工具的命令行接口。
"""

import argparse
import os
import sys
import logging
from typing import Dict, List, Optional, Any

from .translator import OpenAITranslator
from .parsers import MarkdownParser, SphinxParser
from .processor import DocumentProcessor
from . import __version__


def setup_logger(verbose: bool = False) -> logging.Logger:
    """设置日志记录器。
    
    Parameters
    ----------
    verbose : bool, optional
        是否启用详细日志，默认为False
        
    Returns
    -------
    logging.Logger
        配置好的日志记录器
    """
    log_level = logging.DEBUG if verbose else logging.INFO
    
    logger = logging.getLogger("docs_translator")
    logger.setLevel(log_level)
    
    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    
    # 设置格式
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # 添加处理器
    logger.addHandler(console_handler)
    
    return logger


def parse_args() -> argparse.Namespace:
    """解析命令行参数。
    
    Returns
    -------
    argparse.Namespace
        解析后的命令行参数
    """
    parser = argparse.ArgumentParser(
        description="翻译开源项目文档工具"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"docs_translator {__version__}"
    )
    
    parser.add_argument(
        "source_dir",
        help="源文档目录路径"
    )
    
    parser.add_argument(
        "output_dir",
        help="翻译输出目录路径"
    )
    
    parser.add_argument(
        "--doc-type",
        choices=["markdown", "sphinx", "auto"],
        default="auto",
        help="文档类型，默认为auto（自动检测）"
    )
    
    parser.add_argument(
        "--target-lang",
        default="zh-CN",
        help="目标语言，默认为zh-CN（简体中文）"
    )
    
    parser.add_argument(
        "--api-key",
        help="OpenAI兼容API密钥，也可通过OPENAI_API_KEY环境变量设置"
    )
    
    parser.add_argument(
        "--api-base",
        help="OpenAI兼容API基础URL，也可通过OPENAI_API_BASE环境变量设置"
    )
    
    parser.add_argument(
        "--model",
        default="gpt-3.5-turbo",
        help="使用的模型名称，默认为gpt-3.5-turbo"
    )
    
    parser.add_argument(
        "--verbose", "-v", 
        action="store_true",
        help="启用详细日志输出"
    )
    
    return parser.parse_args()


def main() -> int:
    """主程序入口。
    
    Returns
    -------
    int
        退出代码，0表示成功，非0表示错误
    """
    args = parse_args()
    logger = setup_logger(args.verbose)
    
    try:
        # 获取API密钥
        api_key = args.api_key or os.environ.get('OPENAI_API_KEY')
        if not api_key:
            logger.error("请提供OpenAI API密钥（通过--api-key参数或OPENAI_API_KEY环境变量）")
            return 1
        
        # 获取API基础URL
        api_base = args.api_base or os.environ.get('OPENAI_API_BASE', 'https://api.openai.com/v1')
        
        # 创建翻译器
        translator = OpenAITranslator(
            api_key=api_key,
            api_base=api_base,
            model=args.model
        )
        
        # 检查源目录
        if not os.path.isdir(args.source_dir):
            logger.error(f"源目录不存在: {args.source_dir}")
            return 1
        
        # 创建输出目录
        os.makedirs(args.output_dir, exist_ok=True)
        
        # 根据文档类型创建解析器
        if args.doc_type == "markdown" or (args.doc_type == "auto" and not _is_sphinx_project(args.source_dir)):
            parser = MarkdownParser(args.source_dir)
            logger.info("使用Markdown解析器")
        else:
            parser = SphinxParser(args.source_dir)
            logger.info("使用Sphinx解析器")
        
        # 创建文档处理器
        processor = DocumentProcessor(
            parser=parser,
            translator=translator,
            output_dir=args.output_dir,
            target_lang=args.target_lang
        )
        
        # 开始处理
        processor.process_all()
        
        logger.info(f"文档翻译完成，输出目录: {args.output_dir}")
        return 0
        
    except KeyboardInterrupt:
        logger.info("操作已取消")
        return 130
    except Exception as e:
        logger.error(f"处理过程中出错: {str(e)}", exc_info=args.verbose)
        return 1


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


if __name__ == "__main__":
    sys.exit(main())
