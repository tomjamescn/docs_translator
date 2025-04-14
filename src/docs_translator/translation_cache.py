"""翻译缓存模块。

这个模块提供翻译缓存功能，避免重复翻译相同的内容。
"""

import os
import json
import hashlib
import logging
from typing import Dict, Optional, List, Tuple

logger = logging.getLogger(__name__)


class TranslationCache:
    """翻译缓存类。
    
    这个类提供了翻译结果的缓存功能，可以避免重复翻译相同的内容。
    
    Parameters
    ----------
    cache_dir : str, optional
        缓存文件存储目录，默认为用户家目录下的.docs_translator/cache
    cache_file : str, optional
        缓存文件名，默认为translation_cache.json
    
    Attributes
    ----------
    cache_dir : str
        缓存文件存储目录
    cache_file : str
        缓存文件名
    cache_path : str
        完整的缓存文件路径
    cache : Dict
        内存中的缓存数据
    """
    
    def __init__(
        self, 
        cache_dir: Optional[str] = None, 
        cache_file: str = "translation_cache.json"
    ):
        """初始化翻译缓存。
        
        Parameters
        ----------
        cache_dir : str, optional
            缓存文件存储目录，默认为用户家目录下的.docs_translator/cache
        cache_file : str, optional
            缓存文件名，默认为translation_cache.json
        """
        if cache_dir is None:
            # 默认使用用户家目录下的.docs_translator/cache目录
            home_dir = os.path.expanduser("~")
            cache_dir = os.path.join(home_dir, ".docs_translator", "cache")
        
        self.cache_dir = cache_dir
        self.cache_file = cache_file
        self.cache_path = os.path.join(self.cache_dir, self.cache_file)
        self.cache = {}
        
        # 确保缓存目录存在
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 加载现有缓存
        self._load_cache()
        
        logger.info(f"翻译缓存初始化，缓存文件: {self.cache_path}")
    
    def _load_cache(self) -> None:
        """从文件加载缓存数据。"""
        if os.path.exists(self.cache_path):
            try:
                with open(self.cache_path, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"已加载翻译缓存，包含 {len(self.cache)} 个条目")
            except Exception as e:
                logger.warning(f"加载翻译缓存失败: {str(e)}，将使用空缓存")
                self.cache = {}
        else:
            logger.info("缓存文件不存在，将使用空缓存")
            self.cache = {}
    
    def _save_cache(self) -> None:
        """将缓存数据保存到文件。"""
        try:
            with open(self.cache_path, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            logger.info(f"已保存翻译缓存，包含 {len(self.cache)} 个条目")
        except Exception as e:
            logger.warning(f"保存翻译缓存失败: {str(e)}")
    
    def _generate_key(self, text: str, target_lang: str) -> str:
        """为翻译生成缓存键。
        
        Parameters
        ----------
        text : str
            要翻译的文本
        target_lang : str
            目标语言
            
        Returns
        -------
        str
            缓存键
        """
        # 使用原文和目标语言的组合生成唯一哈希值
        combined = f"{text}|{target_lang}"
        return hashlib.md5(combined.encode('utf-8')).hexdigest()
    
    def get(self, text: str, target_lang: str) -> Optional[str]:
        """获取缓存的翻译结果。
        
        Parameters
        ----------
        text : str
            要翻译的文本
        target_lang : str
            目标语言
            
        Returns
        -------
        Optional[str]
            缓存的翻译结果，如果缓存未命中则返回None
        """
        key = self._generate_key(text, target_lang)
        return self.cache.get(key)
    
    def set(self, text: str, target_lang: str, translated_text: str) -> None:
        """设置翻译结果到缓存。
        
        Parameters
        ----------
        text : str
            要翻译的文本
        target_lang : str
            目标语言
        translated_text : str
            翻译后的文本
        """
        key = self._generate_key(text, target_lang)
        self.cache[key] = translated_text
        
        # 定期保存缓存，避免频繁IO
        if len(self.cache) % 100 == 0:
            self._save_cache()
    
    def batch_get(self, texts: List[str], target_lang: str) -> Tuple[List[str], List[int]]:
        """批量获取缓存的翻译结果。
        
        Parameters
        ----------
        texts : List[str]
            要翻译的文本列表
        target_lang : str
            目标语言
            
        Returns
        -------
        Tuple[List[str], List[int]]
            已缓存的翻译结果列表和对应的原始索引列表
        """
        cached_translations = []
        cached_indices = []
        
        for i, text in enumerate(texts):
            cached = self.get(text, target_lang)
            if cached is not None:
                cached_translations.append(cached)
                cached_indices.append(i)
        
        return cached_translations, cached_indices
    
    def batch_set(self, texts: List[str], target_lang: str, translated_texts: List[str]) -> None:
        """批量设置翻译结果到缓存。
        
        Parameters
        ----------
        texts : List[str]
            要翻译的文本列表
        target_lang : str
            目标语言
        translated_texts : List[str]
            翻译后的文本列表
        """
        for text, translated in zip(texts, translated_texts):
            self.set(text, target_lang, translated)
        
        # 批量设置后保存缓存
        self._save_cache()
    
    def save(self) -> None:
        """强制保存缓存到文件。"""
        self._save_cache()
    
    def get_stats(self) -> Dict:
        """获取缓存统计信息。
        
        Returns
        -------
        Dict
            缓存统计信息，包括缓存条目数量等
        """
        return {
            "cache_entries": len(self.cache),
            "cache_file": self.cache_path
        }
    
    def clear(self) -> None:
        """清空缓存。"""
        self.cache = {}
        self._save_cache()
        logger.info("翻译缓存已清空")
    
    def __del__(self):
        """析构函数，确保缓存被保存。"""
        self._save_cache()