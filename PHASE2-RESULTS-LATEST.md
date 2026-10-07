# 当前 Phase 2 实验结果

**北京时间 2026-10-07 10:10 快照**，不是补采最终报告。

[打开结果快照和复算说明](research/phase2-results-snapshots/2026-10-07T021002Z/README.md)

| 数据 | 状态 | 已包含范围 |
|---|---|---|
| 原正式实验 | 已结束 | 128 tasks、256 pairs、512 个计划策略臂；保留全部失败和 unknown |
| A 配置额度恢复补采 | 采集中 | 117 个计划配对中已终止的 45 对 / 90 臂 |

补采的“已终止”包含失败。当前快照有一条 context 臂在账户额度耗尽时终止，记录保留。正在执行的轨迹没有纳入稳定结果 ZIP；后续采集不会自动更新这次快照。

## 直接查看

- [原正式实验分析摘要](research/phase2-results-snapshots/2026-10-07T021002Z/original-formal-analysis/analysis-summary.json)
- [原正式实验分组结果表](research/phase2-results-snapshots/2026-10-07T021002Z/original-formal-analysis/table1-outcomes.csv)
- [补采逐臂结果](research/phase2-results-snapshots/2026-10-07T021002Z/recovery-terminal-arm-outcomes.csv)
- [进度、统计分母和包哈希](research/phase2-results-snapshots/2026-10-07T021002Z/snapshot-summary.json)
- [原批次原始结果 ZIP](research/phase2-results-snapshots/2026-10-07T021002Z/formal-results-complete.zip)
- [补采已终止轨迹 ZIP](research/phase2-results-snapshots/2026-10-07T021002Z/quota-recovery-terminal-pairs.zip)
- [补采及恢复脚本](research/agent-policy-phase2-quota-recovery-2026-10-07/README.md)

原冻结包中的“采集尚未启动”是冻结时的历史说明，以本页和有时间戳的结果快照为当前进度入口。原冻结文件、评分器、提示词、任务与原始结果均未覆盖修改。补采与原批次独立保留；不得将中期补采计数作为最终推断或静默替换原始主分析。

复算只需按快照 README 解压原批次 ZIP 并运行已有 `analyze_formal.py`；不需要模型账号，也不会调用 API。快照中的 `build_snapshot.py` 是本地打包步骤的存档，重建快照需要原始工作目录里的分析导出，不能替代离线评分入口。
