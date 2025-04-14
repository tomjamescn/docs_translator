"""unittest测试模块。

此模块包含文档翻译工具的单元测试。
"""

import os
import unittest
from unittest.mock import MagicMock, patch

from docs_translator.translator import BaseTranslator, OpenAITranslator
from docs_translator.parsers.base import BaseParser
from docs_translator.parsers.markdown import MarkdownParser
from docs_translator.parsers.sphinx import SphinxParser
from docs_translator.processor import DocumentProcessor


class TestBaseTranslator(unittest.TestCase):
    """测试BaseTranslator类。"""
    
    def test_init(self):
        """测试初始化。"""
        translator = BaseTranslator(api_key="test_key", api_base="test_base", model="test_model")
        self.assertEqual(translator.api_key, "test_key")
        self.assertEqual(translator.api_base, "test_base")
        self.assertEqual(translator.model, "test_model")
    
    def test_translate_abstract(self):
        """测试抽象方法translate。"""
        translator = BaseTranslator(api_key="test_key")
        with self.assertRaises(NotImplementedError):
            translator.translate("test text")


class TestOpenAITranslator(unittest.TestCase):
    """测试OpenAITranslator类。"""
    
    @patch('requests.post')
    def test_translate(self, mock_post):
        """测试translate方法。"""
        # 模拟请求响应
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "choices": [
                {
                    "message": {
                        "content": "测试翻译文本"
                    }
                }
            ]
        }
        mock_post.return_value = mock_response
        
        # 创建翻译器并调用translate方法
        translator = OpenAITranslator(api_key="test_key")
        result = translator.translate("Test text", target_lang="zh-CN")
        
        # 验证结果
        self.assertEqual(result, "测试翻译文本")
        
        # 验证请求
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertIn("headers", kwargs)
        self.assertIn("json", kwargs)
        self.assertEqual(kwargs["json"]["messages"][1]["content"], "Test text")


class TestMarkdownParser(unittest.TestCase):
    """测试MarkdownParser类。"""
    
    def setUp(self):
        """设置测试环境。"""
        # 创建临时测试目录和文件
        self.test_dir = os.path.join(os.path.dirname(__file__), "test_md")
        os.makedirs(self.test_dir, exist_ok=True)
        
        # 创建测试Markdown文件
        self.test_file = os.path.join(self.test_dir, "test.md")
        with open(self.test_file, "w", encoding="utf-8") as f:
            f.write("# Test Heading\n\nTest paragraph.\n\n```python\nprint('Hello')\n```\n")
        
        # 创建解析器
        self.parser = MarkdownParser(self.test_dir)
    
    def tearDown(self):
        """清理测试环境。"""
        # 删除测试文件和目录
        if os.path.exists(self.test_file):
            os.unlink(self.test_file)
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
    
    def test_get_all_files(self):
        """测试get_all_files方法。"""
        files = self.parser.get_all_files()
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0], "test.md")
    
    def test_parse_file(self):
        """测试parse_file方法。"""
        segments = self.parser.parse_file("test.md")
        self.assertEqual(len(segments), 3)
        
        # 检查段落
        self.assertEqual(segments[0]["type"], "text")
        self.assertEqual(segments[0]["content"], "# Test Heading\n\nTest paragraph.")
        
        # 检查代码块
        self.assertEqual(segments[2]["type"], "code_block")
        self.assertEqual(segments[2]["content"], "```python\nprint('Hello')\n```")
    
    def test_build_file(self):
        """测试build_file方法。"""
        segments = [
            {"content": "# 测试标题\n\n测试段落。", "type": "text", "position": 0},
            {"content": "```python\nprint('Hello')\n```", "type": "code_block", "position": 1}
        ]
        
        content = self.parser.build_file("test.md", segments)
        self.assertEqual(content, "# 测试标题\n\n测试段落。```python\nprint('Hello')\n```")


if __name__ == "__main__":
    unittest.main()
