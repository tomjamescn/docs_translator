# 代码风格和约定

docs_translator 项目采用以下代码风格和约定：

## 代码风格

- 使用 [NumPy 风格](https://numpydoc.readthedocs.io/en/latest/format.html)的文档字符串
- 使用 4 个空格进行缩进（不使用制表符）
- 每行代码最多 88 个字符
- 使用双引号表示字符串
- 使用 type hints 进行类型注解

## 文档字符串格式

使用 NumPy 风格的文档字符串格式：

```python
"""简短描述。

详细描述（可选）。

Parameters
----------
param1 : type
    参数1的描述
param2 : type, optional
    参数2的描述

Returns
-------
type
    返回值的描述

Raises
------
ExceptionType
    异常的描述
"""
```

## 命名约定

- 类名：使用 `CamelCase`
- 函数和变量：使用 `snake_case`
- 常量：使用 `UPPER_SNAKE_CASE`
- 模块名：使用 `snake_case`

## 导入顺序

1. 标准库导入
2. 相关第三方导入
3. 本地应用/库特定导入

每组导入之间应有一个空行
