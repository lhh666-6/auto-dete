# 公共 Retail 参考流程比较

这是 KAIS 拒稿后新增的离线补强材料。入口是 [RESULTS.md](RESULTS.md)；实验规则在 [PROTOCOL.md](PROTOCOL.md)。原投稿稿件和冻结实验账本不改动。

六条未用于先前比较、按完整动作序列去重的公共流程，四种受控纠正/授权场景，两种实现，共48条路线。ToolGate 正常业务配置与作者新增持久化桥合并记作 **T-configured**；C 调用原合同后端。后缀调用原生 Retail 工具，比较完整世界终态。没有模型、人工参与者或官方任务奖励评估。

## 已保存证据

- `inputs/`：六条原任务、参考执行、初态、参考终态、24个场景输入及选择规则。
- `FREEZE.json`：运行前固定的110个来源/输入/实现文件，以及3个受保护投稿文件。
- `runs/20261020T123319655459Z/`：本轮唯一执行；每路保存实际 SQLite、逐尝试记录、原生工具草稿、全部后缀及完整终态。
- 运行目录 `RUN.json`：48条完成、0工程错误、0网络尝试；385个运行产物的哈希。
- `SCORE.json`、`SCORE-rows.csv`：独立只读评分。原始严格评分为 T 23 PASS/1 FAIL、C 24 PASS；唯一失败为首个公共工具导入的两条日志，完整业务终态全部通过。
- `DIAGNOSTIC-ADJUDICATION.md`：单独核查该日志问题；原评分和冻结源码保留，不以事后解释覆盖原结果。

## 离线复核现有结果

在本项目根目录使用本轮已有环境：

```powershell
& research/kais-toolgate-public-reference-2026-10-20/.venv/Scripts/python.exe -B research/kais-toolgate-public-reference-2026-10-20/public_score.py research/kais-toolgate-public-reference-2026-10-20/runs/20261020T123319655459Z --verify
```

这个命令只读取已有证据并验证已保存评分一致。由于原评分保留上述一个日志 FAIL，退出码仍为1；应检查 JSON 中唯一失败原因及裁决文件，不能将退出码自动解释成合同违规。已有评分不一致时脚本拒绝覆盖。

## 重新执行

完整仓库、固定依赖和原来源可用时：

```powershell
& research/kais-toolgate-public-reference-2026-10-20/.venv/Scripts/python.exe research/kais-toolgate-public-reference-2026-10-20/run_public.py run
```

每次建立新的运行目录，不覆盖旧数据；随后用评分器读取新目录。不要重复执行 `prepare_public.py` 或 `freeze` 来覆盖已有输入。

当前冻结清单含原工作区绝对路径，并依赖相邻 `kais-toolgate-feasibility-2026-10-20` 与 `kais-external-baseline-sprint-2026-10-15` 的固定来源。因此本目录不是独立、任意路径可解压的发布包。另一环境复核时，应保持完整证据目录，按相对目录映射原哈希，另存环境验证回执，保留原冻结清单。依赖精确版本见 `requirements-lock.txt`。
