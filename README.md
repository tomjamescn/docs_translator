# docs_translator

## 简介
这是一个对开源项目的文档进行翻译的工具，能够使用openai兼容的api对开源项目的文档目录，支持两类主要文档格式：
- Sphinx文档系统
- Markdown文档系统

## 功能特点

- 自动检测文档类型（Markdown或Sphinx）
- 保留原始文档的格式和结构
- 不翻译代码块，保持代码的完整性
- 自动复制静态资源（如图片、CSS等）
- 支持自定义目标语言
- 支持自定义OpenAI兼容的API端点
- 提供命令行界面和Python API

## 安装

使用pip安装：

```bash
pip install docs-translator
```

或者从源码安装：

```bash
git clone https://github.com/username/docs_translator.git
cd docs_translator
pip install -e .
```

### 使用 Conda 创建环境（推荐）

```bash
# 创建conda环境
conda create -n docs_translator python=3.8
# 激活环境
conda activate docs_translator
# 安装包
pip install docs-translator
```

或者从源码安装到 Conda 环境：

```bash
git clone https://github.com/username/docs_translator.git
cd docs_translator
conda create -n docs_translator python=3.8
conda activate docs_translator
pip install -e .
```

## 使用方法

### 命令行界面

```bash
# 基本用法
docs-translator 源文档目录 输出目录

# 指定文档类型
docs-translator 源文档目录 输出目录 --doc-type markdown

# 指定目标语言
docs-translator 源文档目录 输出目录 --target-lang zh-CN

# 指定API密钥和模型
docs-translator 源文档目录 输出目录 --api-key your_api_key --model gpt-4
```

### Python API

```python
from docs_translator.api import translate_docs

# 基本用法
translate_docs(
    source_dir="源文档目录",
    output_dir="输出目录",
    api_key="your_api_key"
)

# 高级用法
translate_docs(
    source_dir="源文档目录",
    output_dir="输出目录",
    doc_type="sphinx",  # 或 "markdown", "auto"
    target_lang="zh-CN",
    api_key="your_api_key",
    api_base="https://your-api-endpoint/v1",
    model="gpt-4"
)
```

## 配置说明

- `api_key`: OpenAI API密钥，可以通过命令行参数`--api-key`或环境变量`OPENAI_API_KEY`设置
- `api_base`: API的基础URL，可以通过命令行参数`--api-base`或环境变量`OPENAI_API_BASE`设置
- `model`: 使用的模型名称，默认为"gpt-3.5-turbo"

## 开发

### 安装开发依赖

```bash
pip install -e ".[dev]"
```

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black src tests
isort src tests
```

### 运行Linting

```bash
ruff src tests
```

## 许可证

MIT