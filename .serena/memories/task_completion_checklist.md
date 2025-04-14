# 任务完成检查表

在完成每个任务后，请按照以下检查表确保工作质量：

## 代码质量检查

- [ ] 代码格式化
  ```bash
  black src tests
  isort src tests
  ```

- [ ] 代码检查
  ```bash
  ruff src tests
  ```

- [ ] 运行测试
  ```bash
  pytest
  ```

## 文档和注释

- [ ] 所有新函数和类都有适当的文档字符串（NumPy 风格）
- [ ] 必要时添加了内联注释
- [ ] 更新了 README.md（如果需要）

## 版本控制

- [ ] 所有更改都已提交到 Git
  ```bash
  git add .
  git commit -m "描述性提交信息"
  ```

- [ ] 更新版本号（如果适用）
  - 在 `src/docs_translator/__init__.py` 中更新 `__version__`
  - 在 `setup.py` 中更新版本号

## 最终检查

- [ ] 代码可以正常运行且无明显 bug
- [ ] 没有引入新的警告或错误
- [ ] 所有功能按预期工作
