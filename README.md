# Docs Translator

Docs Translator 是一个用于自动翻译技术文档的工具，支持 Sphinx 文档和 Markdown 文档的批量翻译。

## 功能特点

- 支持 Sphinx 文档项目的翻译，使用 sphinx-intl 工作流
- 支持 Markdown 文档的翻译
- 使用 OpenAI 兼容的 API 接口进行高质量翻译
- 保持原文档的格式和结构
- 批量翻译功能，提高处理效率
- 实时显示翻译进度和统计信息
- 翻译缓存机制，避免重复翻译相同内容
- 缓存管理工具，支持清理、导入导出和查看统计

## 安装

```bash
pip install docs-translator
```

或从源代码安装：

```bash
git clone https://github.com/yourusername/docs-translator.git
cd docs-translator
pip install -e .
```

## 使用方法

### 命令行使用

```bash
# 翻译 Sphinx 文档(使用 sphinx-intl)
docs-translator /path/to/sphinx/docs /path/to/output --doc-type sphinx-intl --target-lang zh-CN

# 翻译 Markdown 文档
docs-translator /path/to/markdown/docs /path/to/output --doc-type markdown --target-lang zh-CN

# 自动检测文档类型并翻译
docs-translator /path/to/docs /path/to/output --target-lang zh-CN

# 使用缓存和批量翻译选项
docs-translator /path/to/docs /path/to/output --use-cache --cache-dir /custom/cache/dir --batch-size 20
```

#### 报错信息收集
> 由于sphinx有很多插件，默认不安装，所以在翻译的时候会报错，这时需要安装对应插件
```
# 2025-04-25 04:15:32,828 - docs_translator.parsers.sphinx_intl - ERROR - sphinx-build命令失败:
# Extension error:
# Could not import extension sphinxcontrib.autodoc_pydantic (exception: No module named 'sphinxcontrib.autodoc_pydantic')

pip install autodoc-pydantic
```

### 作为库使用

```python
from docs_translator.translator import OpenAITranslator
from docs_translator.sphinx_intl_processor import SphinxIntlProcessor
from docs_translator.parsers.sphinx_intl import SphinxIntlParser

# 初始化翻译器
translator = OpenAITranslator(
    api_key="your_openai_api_key",
    api_base="https://api.openai.com/v1",  # 或其他兼容的API地址
    model="gpt-3.5-turbo",                 # 或其他支持的模型
    use_cache=True                         # 启用翻译缓存
)

# 初始化解析器
parser = SphinxIntlParser("/path/to/sphinx/docs")

# 初始化处理器
processor = SphinxIntlProcessor(
    parser=parser,
    translator=translator,
    output_dir="/path/to/output",
    target_lang="zh_CN",
    batch_size=10                          # 批量翻译大小
)

# 执行翻译处理
processor.process()
```

## 翻译缓存功能

该项目支持翻译缓存机制，可以避免重复翻译相同的内容，大幅提高翻译效率和节省API调用费用。

### 缓存特点

- 自动保存已翻译的内容到本地缓存
- 在多次运行之间保持缓存，持久化保存
- 缓存命中时跳过API调用，节省时间和费用
- 提供详细的缓存使用统计信息
- 支持缓存管理工具，可清理、导出和导入缓存

### 缓存配置

缓存默认已启用，可以通过以下方式配置：

```python
# 在创建翻译器时配置缓存
translator = OpenAITranslator(
    api_key="your_api_key",
    use_cache=True,                        # 是否启用缓存
    cache_dir="/custom/cache/directory"    # 自定义缓存目录（可选）
)

# 在创建处理器时配置缓存统计显示
processor = SphinxIntlProcessor(
    parser=parser,
    translator=translator,
    output_dir=output_dir,
    show_cache_stats=True                  # 是否显示缓存统计
)
```

### 缓存管理工具

项目提供了专用的缓存管理命令行工具，使用方法如下：

```bash
# 查看缓存信息和统计
docs-translator-cache info

# 清空缓存内容（保留文件）
docs-translator-cache clear

# 删除缓存文件
docs-translator-cache delete

# 导出缓存到文件
docs-translator-cache export /path/to/export.json

# 从文件导入缓存
docs-translator-cache import /path/to/import.json

# 导入并与现有缓存合并
docs-translator-cache import /path/to/import.json --merge

# 压缩缓存（删除重复项）
docs-translator-cache compact

# 指定自定义缓存目录
docs-translator-cache info --cache-dir /custom/cache/directory

# 查看详细帮助
docs-translator-cache --help
```

### 缓存存储位置

默认情况下，缓存存储在用户家目录的 `.docs_translator/cache` 文件夹下的 `translation_cache.json` 文件中。

## 批量翻译优化

项目支持批量翻译功能，可以一次性翻译多个文本片段，提高翻译效率：

- 可配置的批量大小，根据API限制和需求调整
- 详细的进度显示和时间统计
- 支持批量API调用（如果API支持）
- 自动回退机制，当批量翻译失败时自动降级到逐条翻译

## 注意事项

1. 使用前请确保您有有效的OpenAI API密钥或兼容的替代API
2. 对于大型文档项目，建议适当调整批量大小以优化效率
3. 默认缓存会持续增长，可使用缓存管理工具定期清理或压缩

## 许可证

[待补充]

## 贡献

欢迎提交问题报告和拉取请求！

