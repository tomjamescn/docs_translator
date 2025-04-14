# 项目结构

docs_translator 是一个用于翻译开源项目文档的工具，支持 Sphinx 和 Markdown 文档系统。以下是项目的主要结构：

## 核心模块

- `src/docs_translator/__init__.py`: 包定义和版本信息
- `src/docs_translator/translator.py`: 翻译器实现，包括基础翻译器和 OpenAI 翻译器
- `src/docs_translator/processor.py`: 文档处理器，协调解析器和翻译器的工作
- `src/docs_translator/cli.py`: 命令行接口
- `src/docs_translator/api.py`: Python API 接口

## 解析器模块

- `src/docs_translator/parsers/base.py`: 解析器基类
- `src/docs_translator/parsers/markdown.py`: Markdown 文档解析器
- `src/docs_translator/parsers/sphinx.py`: Sphinx 文档解析器
- `src/docs_translator/parsers/__init__.py`: 导出模块接口

## 测试

- `tests/test_translator.py`: 单元测试

## 文档和示例

- `docs/markdown_sample/`: Markdown 文档示例
- `docs/sphinx_sample/`: Sphinx 文档示例

## 构建和配置文件

- `setup.py`: 项目安装配置
- `pyproject.toml`: 项目构建配置
- `.github/workflows/tests.yml`: GitHub Actions 测试工作流
