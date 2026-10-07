# Phase 2 实验结果快照

快照时间：**2026-10-07 10:10:02（北京时间）**。

原正式批次已结束，128 tasks × 2 configs × 2 policies = 512 个计划臂，失败和 unknown 均保留。本轮额度恢复补采仍在进行：117 个计划配对中，本快照只纳入 **45 个已终止配对 / 90 个策略臂**。已终止包含失败；正在写入的轨迹没有收入压缩包。

## 内容

- `formal-results-complete.zip`：原正式批次原始轨迹、状态数据库、提供方响应、账本。
- `quota-recovery-terminal-pairs.zip`：补采已终止配对及独立快照账本；每个原任务保留对应关系。
- `original-formal-analysis/`：原批次四张结果表、配对效应、全部失败分类、分析摘要和图。
- `recovery-terminal-arm-outcomes.csv`：补采当前逐臂描述性结果。
- `snapshot-summary.json`：进度、分母、分组计数和压缩包 SHA-256。
- `source-collection-status.json`：采样时原账本，含当时运行中的任务元数据；这部分没有打包未稳定的原始文件。
- 每个 ZIP 中的 `SNAPSHOT-MEMBERS.json`：逐文件 SHA-256；已验证 CRC 和全部成员哈希。

## 离线复算

在本仓库根目录解压 `formal-results-complete.zip`，其中路径以 `research/` 开始。安装正式包的固定依赖后运行：

```powershell
python research/agent-policy-phase2-formal-2026-10-07/analyze_formal.py --output fresh-formal-analysis --figures
```

这只做离线评分，不调用模型。补采代码与 freeze 位于 `research/agent-policy-phase2-quota-recovery-2026-10-07/`。本快照的补采数据尚未覆盖完整队列，只用于检查和描述，不能当成最终推断。保留原批次分析；任何合并视图必须明确标注原批次与补采来源。

原冻结协议、任务、模型别名、工具、评分器和配对顺序不因上传改变。原始运行日志保留已观察到的额度故障。调用凭据不在包内。共同作者读取结果即可；恢复或另行采集需协调批次，避免多人重复采集。
