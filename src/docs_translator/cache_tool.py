"""缓存管理工具模块。

这个模块提供了翻译缓存的管理功能，包括清理、重置、查看统计等。
"""

import os
import sys
import argparse
import logging
import json
from typing import Dict, List, Optional, Any

from .translation_cache import TranslationCache


logger = logging.getLogger(__name__)


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
        description="翻译缓存管理工具"
    )
    
    subparsers = parser.add_subparsers(
        dest="command",
        help="缓存管理命令"
    )
    
    # 查看缓存信息子命令
    info_parser = subparsers.add_parser(
        "info",
        help="显示缓存信息"
    )
    
    # 清空缓存子命令
    clear_parser = subparsers.add_parser(
        "clear",
        help="清空翻译缓存"
    )
    
    # 删除缓存子命令
    delete_parser = subparsers.add_parser(
        "delete",
        help="删除翻译缓存文件"
    )
    
    # 导出缓存子命令
    export_parser = subparsers.add_parser(
        "export",
        help="导出翻译缓存到文件"
    )
    export_parser.add_argument(
        "output_file",
        help="导出文件路径"
    )
    
    # 导入缓存子命令
    import_parser = subparsers.add_parser(
        "import",
        help="从文件导入翻译缓存"
    )
    import_parser.add_argument(
        "input_file",
        help="导入文件路径"
    )
    import_parser.add_argument(
        "--merge",
        action="store_true",
        help="与现有缓存合并，而非替换"
    )
    
    # 压缩缓存子命令
    compact_parser = subparsers.add_parser(
        "compact",
        help="压缩翻译缓存，删除重复项"
    )
    
    # 公共参数
    for subparser in [info_parser, clear_parser, delete_parser, export_parser, import_parser, compact_parser]:
        subparser.add_argument(
            "--cache-dir",
            help="缓存目录路径，默认为~/.docs_translator/cache"
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
    
    if not args.command:
        print("请指定要执行的命令。使用 --help 查看帮助。")
        return 1
    
    try:
        # 初始化缓存
        cache = TranslationCache(cache_dir=args.cache_dir)
        
        if args.command == "info":
            handle_info(cache)
            
        elif args.command == "clear":
            handle_clear(cache)
            
        elif args.command == "delete":
            handle_delete(cache)
            
        elif args.command == "export":
            handle_export(cache, args.output_file)
            
        elif args.command == "import":
            handle_import(cache, args.input_file, args.merge)
            
        elif args.command == "compact":
            handle_compact(cache)
            
        return 0
        
    except KeyboardInterrupt:
        print("\n操作已取消")
        return 130
    except Exception as e:
        logger.error(f"处理过程中出错: {str(e)}", exc_info=args.verbose)
        print(f"错误: {str(e)}")
        return 1


def handle_info(cache: TranslationCache) -> None:
    """处理info命令，显示缓存信息。
    
    Parameters
    ----------
    cache : TranslationCache
        缓存对象
    """
    stats = cache.get_stats()
    
    print("\n翻译缓存信息:")
    print(f"缓存文件: {stats['cache_file']}")
    print(f"缓存条目数量: {stats['cache_entries']}")
    
    if stats['cache_entries'] > 0:
        cache_file_size = os.path.getsize(stats['cache_file']) if os.path.exists(stats['cache_file']) else 0
        print(f"缓存文件大小: {format_size(cache_file_size)}")
        
        # 获取目标语言统计
        langs = cache.get_language_stats()
        print("\n目标语言分布:")
        for lang, count in langs.items():
            print(f"  {lang}: {count} 条目 ({count/stats['cache_entries']*100:.1f}%)")
    
    print("")


def handle_clear(cache: TranslationCache) -> None:
    """处理clear命令，清空缓存。
    
    Parameters
    ----------
    cache : TranslationCache
        缓存对象
    """
    confirm = input("确定要清空翻译缓存吗? 此操作不可撤销! (y/N): ")
    if confirm.lower() in ['y', 'yes']:
        old_stats = cache.get_stats()
        cache.clear()
        print(f"已清空翻译缓存，删除了 {old_stats['cache_entries']} 个条目")
    else:
        print("操作已取消")


def handle_delete(cache: TranslationCache) -> None:
    """处理delete命令，删除缓存文件。
    
    Parameters
    ----------
    cache : TranslationCache
        缓存对象
    """
    confirm = input("确定要删除翻译缓存文件吗? 此操作不可撤销! (y/N): ")
    if confirm.lower() in ['y', 'yes']:
        cache_file = cache.cache_path
        if os.path.exists(cache_file):
            os.remove(cache_file)
            print(f"已删除翻译缓存文件: {cache_file}")
        else:
            print(f"缓存文件不存在: {cache_file}")
    else:
        print("操作已取消")


def handle_export(cache: TranslationCache, output_file: str) -> None:
    """处理export命令，导出缓存到文件。
    
    Parameters
    ----------
    cache : TranslationCache
        缓存对象
    output_file : str
        导出文件路径
    """
    # 确保输出目录存在
    output_dir = os.path.dirname(output_file)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
    
    # 获取缓存数据
    data = cache.export_data()
    
    # 写入文件
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"已导出 {len(data)} 个缓存条目到: {output_file}")


def handle_import(cache: TranslationCache, input_file: str, merge: bool) -> None:
    """处理import命令，从文件导入缓存。
    
    Parameters
    ----------
    cache : TranslationCache
        缓存对象
    input_file : str
        导入文件路径
    merge : bool
        是否与现有缓存合并
    """
    if not os.path.exists(input_file):
        print(f"导入文件不存在: {input_file}")
        return
    
    try:
        # 读取导入文件
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 导入数据
        old_count = cache.get_stats()['cache_entries']
        new_count = cache.import_data(data, merge=merge)
        
        if merge:
            print(f"已合并导入 {new_count - old_count} 个新条目，当前缓存共有 {new_count} 个条目")
        else:
            print(f"已导入 {new_count} 个条目，替换了原有的 {old_count} 个条目")
    
    except Exception as e:
        print(f"导入缓存时出错: {str(e)}")


def handle_compact(cache: TranslationCache) -> None:
    """处理compact命令，压缩缓存。
    
    Parameters
    ----------
    cache : TranslationCache
        缓存对象
    """
    old_count = cache.get_stats()['cache_entries']
    new_count = cache.compact()
    
    if new_count < old_count:
        print(f"已压缩缓存，从 {old_count} 个条目减少到 {new_count} 个条目，删除了 {old_count - new_count} 个重复项")
    else:
        print(f"缓存已是最优状态，包含 {new_count} 个条目")


def format_size(size_bytes: int) -> str:
    """格式化文件大小显示。
    
    Parameters
    ----------
    size_bytes : int
        文件大小（字节）
        
    Returns
    -------
    str
        格式化后的大小字符串
    """
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


if __name__ == "__main__":
    sys.exit(main())