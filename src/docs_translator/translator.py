"""核心翻译功能模块。

这个模块提供了基础的翻译功能，支持使用OpenAI兼容API。
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union, Any, Tuple

import requests
import time

from .translation_cache import TranslationCache

# 设置日志
logger = logging.getLogger(__name__)


class BaseTranslator:
    """翻译器基类。
    
    这个类提供了基本的翻译接口，所有具体的翻译器实现都应该继承这个类。
    
    Parameters
    ----------
    api_key : str
        OpenAI兼容的API密钥
    api_base : str, optional
        API的基础URL，默认为OpenAI的API地址
    model : str, optional
        使用的模型名称，默认为"gpt-3.5-turbo"
    use_cache : bool, optional
        是否使用翻译缓存，默认为True
    cache_dir : str, optional
        缓存目录，默认为None（使用默认目录）
    
    Attributes
    ----------
    api_key : str
        OpenAI兼容API密钥
    api_base : str
        API基础URL
    model : str
        使用的模型名称
    headers : Dict[str, str]
        请求头信息
    cache : TranslationCache
        翻译缓存对象
    use_cache : bool
        是否使用翻译缓存
    cache_stats : Dict
        缓存使用统计
    """
    
    def __init__(
        self, 
        api_key: str, 
        api_base: Optional[str] = "https://api.openai.com/v1", 
        model: str = "gpt-3.5-turbo",
        use_cache: bool = True,
        cache_dir: Optional[str] = None
    ):
        """初始化翻译器。
        
        Parameters
        ----------
        api_key : str
            OpenAI兼容的API密钥
        api_base : str, optional
            API的基础URL，默认为OpenAI的API地址
        model : str, optional
            使用的模型名称，默认为"gpt-3.5-turbo"
        use_cache : bool, optional
            是否使用翻译缓存，默认为True
        cache_dir : str, optional
            缓存目录，默认为None（使用默认目录）
        """
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
        
        # 缓存相关
        self.use_cache = use_cache
        self.cache = TranslationCache(cache_dir) if use_cache else None
        self.cache_stats = {
            "hits": 0,         # 缓存命中次数
            "misses": 0,       # 缓存未命中次数
            "saved_calls": 0,  # 节省的API调用次数
            "total_requests": 0  # 总请求次数
        }
        
        if self.use_cache:
            logger.info("已启用翻译缓存")
    
    def translate(self, text: str, target_lang: str = "zh-CN") -> str:
        """翻译文本到目标语言。
        
        Parameters
        ----------
        text : str
            要翻译的文本
        target_lang : str, optional
            目标语言，默认为"zh-CN"
            
        Returns
        -------
        str
            翻译后的文本
            
        Raises
        ------
        Exception
            如果翻译过程中出现错误
        """
        self.cache_stats["total_requests"] += 1
        
        # 检查缓存
        if self.use_cache:
            cached_translation = self.cache.get(text, target_lang)
            if cached_translation is not None:
                self.cache_stats["hits"] += 1
                logger.debug(f"缓存命中: {text[:30]}...")
                return cached_translation
            else:
                self.cache_stats["misses"] += 1
        
        # 子类必须实现_translate方法
        translated = self._translate(text, target_lang)
        
        # 保存到缓存
        if self.use_cache and translated:
            self.cache.set(text, target_lang, translated)
        
        return translated
    
    def _translate(self, text: str, target_lang: str) -> str:
        """实际执行翻译的方法，子类必须实现。
        
        Parameters
        ----------
        text : str
            要翻译的文本
        target_lang : str
            目标语言
            
        Returns
        -------
        str
            翻译后的文本
        """
        raise NotImplementedError("子类必须实现_translate方法")
    
    def batch_translate(self, texts: List[str], target_lang: str = "zh-CN", batch_size: int = 10) -> List[str]:
        """批量翻译多个文本到目标语言。
        
        Parameters
        ----------
        texts : List[str]
            要翻译的文本列表
        target_lang : str, optional
            目标语言，默认为"zh-CN"
        batch_size : int, optional
            每批处理的文本数量，默认为10
            
        Returns
        -------
        List[str]
            翻译后的文本列表，顺序与输入列表相同
            
        Raises
        ------
        Exception
            如果翻译过程中出现错误
        """
        # 创建结果数组
        results = [None] * len(texts)
        total = len(texts)
        self.cache_stats["total_requests"] += total
        
        # 首先检查缓存并填充已缓存的翻译
        uncached_texts = []
        uncached_indices = []
        
        if self.use_cache:
            cached_stats = {"before": self.cache.get_stats()["cache_entries"]}
            
            # 检查每个文本是否已缓存
            for i, text in enumerate(texts):
                cached = self.cache.get(text, target_lang)
                if cached is not None:
                    results[i] = cached
                    self.cache_stats["hits"] += 1
                else:
                    uncached_texts.append(text)
                    uncached_indices.append(i)
                    self.cache_stats["misses"] += 1
            
            logger.info(f"缓存命中率: {self.cache_stats['hits']}/{total} ({self.cache_stats['hits']/total*100:.1f}%)")
            print(f"缓存命中率: {self.cache_stats['hits']}/{total} ({self.cache_stats['hits']/total*100:.1f}%)")
            
            if not uncached_texts:
                logger.info(f"所有 {total} 个文本都已在缓存中，跳过API调用")
                print(f"所有 {total} 个文本都已在缓存中，跳过API调用")
                self.cache_stats["saved_calls"] += total
                return results
            
            self.cache_stats["saved_calls"] += (total - len(uncached_texts))
        else:
            # 不使用缓存，所有文本都需要翻译
            uncached_texts = texts
            uncached_indices = list(range(total))
        
        # 分批翻译未缓存的文本
        uncached_total = len(uncached_texts)
        logger.info(f"需要翻译 {uncached_total} 个未缓存的文本")
        print(f"需要翻译 {uncached_total} 个未缓存的文本")
        
        for i in range(0, uncached_total, batch_size):
            batch_texts = uncached_texts[i:i+batch_size]
            batch_indices = uncached_indices[i:i+batch_size]
            batch_size_actual = len(batch_texts)
            
            logger.info(f"翻译批次 {i//batch_size + 1}/{(uncached_total + batch_size - 1)//batch_size}: {i}-{min(i+batch_size_actual, uncached_total)}/{uncached_total}")
            print(f"翻译批次 {i//batch_size + 1}/{(uncached_total + batch_size - 1)//batch_size}: {i}-{min(i+batch_size_actual, uncached_total)}/{uncached_total}")
            
            # 翻译当前批次
            try:
                # 尝试使用批量API翻译
                batch_translated = self._batch_translate(batch_texts, target_lang)
                
                # 更新结果数组和缓存
                for idx, translated_text, original_text in zip(batch_indices, batch_translated, batch_texts):
                    results[idx] = translated_text
                    
                    # 保存到缓存
                    if self.use_cache and translated_text:
                        self.cache.set(original_text, target_lang, translated_text)
                
                # 显示示例
                if batch_translated:
                    src_preview = batch_texts[0][:30] + "..." if len(batch_texts[0]) > 30 else batch_texts[0]
                    tgt_preview = batch_translated[0][:30] + "..." if len(batch_translated[0]) > 30 else batch_translated[0]
                    print(f"  示例: '{src_preview}' -> '{tgt_preview}'")
                
            except Exception as e:
                logger.error(f"批量翻译出错: {str(e)}")
                print(f"批量翻译出错: {str(e)}")
                
                # 回退到逐条翻译
                print("回退到逐条翻译...")
                for j, (text, idx) in enumerate(zip(batch_texts, batch_indices)):
                    try:
                        translated = self.translate(text, target_lang)
                        results[idx] = translated
                    except Exception as inner_e:
                        logger.warning(f"单条翻译出错: {str(inner_e)}")
                        print(f"单条翻译出错: {str(inner_e)}")
                        # 如果翻译失败，使用原文
                        results[idx] = text
            
            # 添加短暂延迟以避免API限制
            if i + batch_size < uncached_total:
                time.sleep(0.5)
        
        # 显示缓存统计
        if self.use_cache:
            cached_stats["after"] = self.cache.get_stats()["cache_entries"]
            new_entries = cached_stats["after"] - cached_stats["before"]
            logger.info(f"翻译完成，新增 {new_entries} 个缓存条目")
            print(f"翻译完成，新增 {new_entries} 个缓存条目")
            
            # 保存缓存
            self.cache.save()
        
        # 确保所有结果都有值
        for i in range(len(results)):
            if results[i] is None:
                results[i] = texts[i]  # 使用原文作为后备
        
        return results
    
    def _batch_translate(self, texts: List[str], target_lang: str) -> List[str]:
        """批量翻译方法，子类可以重写以提供更高效的实现。
        
        Parameters
        ----------
        texts : List[str]
            要翻译的文本列表
        target_lang : str
            目标语言
            
        Returns
        -------
        List[str]
            翻译后的文本列表
        """
        # 默认实现是逐个翻译
        results = []
        for text in texts:
            try:
                translated = self._translate(text, target_lang)
                results.append(translated)
            except Exception as e:
                logger.error(f"批量翻译中单条文本失败: {str(e)}")
                # 发生错误时，插入原文作为占位符
                results.append(text)
        
        return results
    
    def get_cache_stats(self) -> Dict:
        """获取缓存使用统计。
        
        Returns
        -------
        Dict
            缓存使用统计
        """
        stats = self.cache_stats.copy()
        
        # 添加缓存条目数量
        if self.use_cache:
            stats.update(self.cache.get_stats())
            
            # 计算节省的API调用费用（假设每1000个token $0.01）
            # 这只是一个粗略估计
            saved_calls = stats["saved_calls"]
            estimated_saving = saved_calls * 0.01 / 1000 * 100  # 假设每个文本平均100个token
            stats["estimated_saving_usd"] = estimated_saving
        
        return stats


class OpenAITranslator(BaseTranslator):
    """使用OpenAI API的翻译器。
    
    这个类使用OpenAI兼容的API实现文本翻译功能。
    
    Parameters
    ----------
    api_key : str
        OpenAI兼容的API密钥
    api_base : str, optional
        API的基础URL，默认为OpenAI的API地址
    model : str, optional
        使用的模型名称，默认为"gpt-3.5-turbo"
    use_cache : bool, optional
        是否使用翻译缓存，默认为True
    cache_dir : str, optional
        缓存目录，默认为None（使用默认目录）
    """
    
    def _translate(self, text: str, target_lang: str = "zh-CN") -> str:
        """使用OpenAI API翻译文本到目标语言。
        
        Parameters
        ----------
        text : str
            要翻译的文本
        target_lang : str, optional
            目标语言，默认为"zh-CN"
            
        Returns
        -------
        str
            翻译后的文本
            
        Raises
        ------
        Exception
            如果翻译过程中出现错误
        """
        url = f"{self.api_base}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"你是一个专业的翻译助手。请将以下文本翻译成{target_lang}，"
                        "保持原文的格式和专业术语准确性。不要添加任何解释或额外内容。"
                    )
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            "temperature": 0.3
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            
            result = response.json()
            translated_text = result["choices"][0]["message"]["content"]
            
            return translated_text.strip()
        
        except Exception as e:
            logger.error(f"翻译失败: {str(e)}")
            raise Exception(f"翻译失败: {str(e)}")
    
    def _batch_translate(self, texts: List[str], target_lang: str = "zh-CN") -> List[str]:
        """使用单个API调用批量翻译多个文本。
        
        此方法适用于较短的多个文本，将它们组合成一个请求发送给API。
        
        Parameters
        ----------
        texts : List[str]
            要翻译的文本列表
        target_lang : str, optional
            目标语言，默认为"zh-CN"
            
        Returns
        -------
        List[str]
            翻译后的文本列表
        
        Raises
        ------
        Exception
            如果翻译过程中出现错误
        """
        if not texts:
            return []
        
        # 将多个文本组合成一个JSON格式的字符串
        combined_text = json.dumps(texts)
        url = f"{self.api_base}/chat/completions"
        
        payload = {
            "model": self.model,
            "messages": [
                {
                    "role": "system",
                    "content": (
                        f"你是一个专业的翻译助手。请将以下JSON格式的文本列表翻译成{target_lang}，"
                        "保持每个项目的格式和专业术语准确性。以相同的JSON格式返回翻译结果列表。"
                        "不要添加任何解释或额外内容，只返回翻译后的JSON列表。"
                    )
                },
                {
                    "role": "user",
                    "content": combined_text
                }
            ],
            "temperature": 0.3
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            translated_json = result["choices"][0]["message"]["content"]
            
            # 尝试解析返回的JSON
            try:
                translated_texts = json.loads(translated_json)
                
                # 确保返回了正确数量的翻译
                if len(translated_texts) != len(texts):
                    logger.warning(f"翻译数量不匹配: 预期 {len(texts)}, 实际 {len(translated_texts)}")
                    # 如果数量不匹配，使用普通的批量翻译方法
                    return super()._batch_translate(texts, target_lang)
                
                return translated_texts
                
            except json.JSONDecodeError:
                logger.warning("无法解析翻译返回的JSON，使用常规批量翻译方法")
                return super()._batch_translate(texts, target_lang)
            
        except Exception as e:
            logger.error(f"批量API翻译失败: {str(e)}")
            # 失败时回退到常规批量翻译方法
            return super()._batch_translate(texts, target_lang)