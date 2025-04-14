"""核心翻译功能模块。

这个模块提供了基础的翻译功能，支持使用OpenAI兼容API。
"""

import os
import json
import logging
from typing import Dict, List, Optional, Union, Any

import requests

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
    """
    
    def __init__(
        self, 
        api_key: str, 
        api_base: Optional[str] = "https://api.openai.com/v1", 
        model: str = "gpt-3.5-turbo"
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
        """
        self.api_key = api_key
        self.api_base = api_base
        self.model = model
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        }
    
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
        raise NotImplementedError("子类必须实现translate方法")


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
    """
    
    def translate(self, text: str, target_lang: str = "zh-CN") -> str:
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
