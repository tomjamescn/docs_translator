# 推荐的命令

以下是 docs_translator 项目开发过程中常用的命令：

## 安装开发依赖

```bash
pip install -e ".[dev]"
```

## 代码格式化

```bash
# 格式化代码
black src tests

# 排序导入
isort src tests
```

## 代码检查

```bash
# 运行 linter
ruff src tests

# 类型检查（可选）
mypy src
```

## 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_translator.py

# 带覆盖率报告
pytest --cov=src
```

## 构建和分发

```bash
# 构建分发包
python -m build

# 安装本地开发版本
pip install -e .
```

## Windows 系统命令

在 Windows 系统上，以下是一些常用的开发命令：

```bash
# 查看目录内容
dir
dir /a  # 显示隐藏文件

# 创建目录
mkdir dirname

# 删除文件/目录
del filename
rmdir dirname
rmdir /s /q dirname  # 递归删除目录及其内容

# 环境变量设置
set OPENAI_API_KEY=your_api_key
```

## 运行文档翻译器命令行工具

```bash
# 基本用法
docs-translator source_dir output_dir

# 设置 API 密钥
set OPENAI_API_KEY=your_api_key
docs-translator source_dir output_dir

# 指定文档类型和目标语言
docs-translator source_dir output_dir --doc-type markdown --target-lang zh-CN
```
