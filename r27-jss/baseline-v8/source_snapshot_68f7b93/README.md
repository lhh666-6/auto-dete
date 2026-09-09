# 工业级产量数据采集 Demo

面向 Windows 10/11 的单机产量表单采集系统。首个版本优先保证在 OCR、AI
和向量检索关闭时，仍能完成导入、人工复核、查询、追溯和 XLSX 导出。

## 开发环境

```powershell
uv sync --extra dev
uv run python -m pytest -v
uv run python -m ruff check .
uv run streamlit run app/ui/main.py
```

复制 `.env.example` 为 `.env` 后可修改本地数据目录。不要将真实表单、员工数据、
录音、数据库、导出文件或密钥提交到 GitHub。

协作状态和接力操作见 [PROGRESS.md](PROGRESS.md)。

## 当前功能

- 图片证据导入、SHA-256 去重和条件录音绑定
- 人工确认、更正、不可变版本和审计事件
- 图像质量、二维码分类、透视校正、数字候选和 OMR
- 确定性业务规则、精确查询和完整追溯
- 四工作表 XLSX 导出和导出后更正提醒
- 默认关闭的 AI 建议 Adapter 与本地相似异常检索

OCR、OMR 和 AI 输出均为候选，不会覆盖人工确认事实。AI 关闭时核心流程仍可运行。

## 本地运行与恢复

运行数据默认位于 `data/`：SQLite 数据库、证据、导出文件需要一起备份。恢复时先关闭
应用，将完整备份恢复到同一数据根目录，再启动应用并通过追溯页抽查表单、证据和导出批次。
原始证据不得覆盖；重新采集必须生成新的证据记录。

## GitHub 接力

```powershell
git switch main
git pull --ff-only
git switch -c phase-N-description
uv sync --extra dev
uv run python -m pytest -q
```

每个阶段必须同步更新 `PROGRESS.md`，写明验证命令、结果、提交号、已知问题和下一位操作。
真实业务数据、录音、数据库、导出文件和密钥不得提交。
