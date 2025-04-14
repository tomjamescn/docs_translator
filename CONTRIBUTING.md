# 项目贡献指南

欢迎为docs_translator项目做出贡献！请按照以下指南进行：

## 环境设置

1. Fork并克隆仓库：

```bash
git clone https://github.com/your-username/docs_translator.git
cd docs_translator
```

2. 创建并激活conda虚拟环境（推荐使用）：

```bash
# 创建conda环境
conda create -n docs_translator python=3.8
# 激活环境
conda activate docs_translator
```

3. 安装开发依赖：

```bash
pip install -e ".[dev]"
```

## 代码风格

本项目遵循[numpy风格](https://numpydoc.readthedocs.io/en/latest/format.html)的代码风格和文档规范：

- 使用4个空格进行缩进（不使用制表符）
- 使用双引号表示字符串
- 每行代码最多88个字符
- 函数、类和模块都应有文档字符串
- 使用numpy风格的文档字符串，包括Parameters、Returns、Raises等部分

## 提交代码前

在提交代码前，请确保：

1. 运行代码格式化工具：

```bash
black src tests
isort src tests
```

2. 运行linter检查代码问题：

```bash
ruff src tests
```

3. 运行类型检查（可选）：

```bash
mypy src
```

4. 运行单元测试，确保所有测试通过：

```bash
pytest
```

## 提交PR（Pull Request）

1. 在自己的fork上创建一个新分支
2. 在新分支上进行开发
3. 提交更改并推送到您的fork
4. 创建一个PR到主仓库

## 功能建议和问题报告

如果您想建议新功能或报告问题，请在GitHub上创建一个Issue，并提供尽可能详细的信息。