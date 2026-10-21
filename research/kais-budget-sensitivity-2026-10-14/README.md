# KAIS 预算敏感性补证

这是投稿后独立开展的探索性研究：24个归档审查检查点 × context/bound × 4096/393216输出预算，共96条计划续行。旧prefix是复用输入，只有suffix为新采集；结果不替换原论文的任何队列。

- 本轮已完成96/96条续行；[结果报告](RESULTS.md)汇总四条件结果及解释边界。
- 设计与解释边界：[PROTOCOL.md](PROTOCOL.md)
- 任务及运行次序：`allocation.json`
- 原始记录：`live/<task>/<low|high>/<context|bound>/`
- 独立离线分析：`analysis.py`，输出`analysis.json`、`summary.json`、`cells.csv`和`pairs.csv`
- 保护与冻结：`protection-before.json`、`freeze.json`及最终验证产物
- [最终独立核查](../../reviews/kais-budget-sensitivity-2026-10-14/final-audit.md)：全部96臂、389份请求/响应及24组配对核对通过；`protection-after.json`记录14,597个原文件未改变。

环境：Python 3.11、jsonschema。运行以下命令只做本地测试、核查或分析，不调用模型：

```text
python -B test_run.py
python -B test_analysis.py
python -B run.py verify
python -B run.py status
python -B analysis.py
```

`python -B run.py live`会调用付费模型，按冻结顺序继续尚未终止的条件；不应为得到不同结果重复已终止条件。原始响应、截断、失败及未知状态都应保留。离线复核不需要凭据。
