# ToolGate 关系配置可行性与 P0 联合结果

2026-10-20。**在八项开发控制中，T-configured 与 C 各通过 8/8：四次合法提交、四次拒绝，逐项业务写入结果持平。** ToolGate 的正常前置/后置回调可以表达本轮映射的纠正执行关系。这个结果支持正常配置的可行性，不支持 C 具有独有表达能力，也不构成统计等效结论。

本文依据已保存运行 `20261020T121403449662Z` 的[总评分](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/runs/20261020T121403449662Z/SCORE.json)、[逐项评分](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/runs/20261020T121403449662Z/SCORE-rows.csv)、[协议](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/PROTOCOL.md)和[P0 联合分析](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/P0-JOINT-RESULTS.md)整理，没有为编写本文重跑实验。主线之外新增防御场景为 **0**。

## 四个层次的比较

“原文提出了什么”与“框架能否经配置表达”是两个问题。本次验证原始代码接口和局部执行，不复现 ToolGate 论文的完整实验，也不据此判定论文全部保证。

| 原文/原生保证 | 正常配置能力 | 作者新增持久化桥 | 观察结果 |
|---|---|---|---|
| **ToolGate：**固定提交 `976ad3f5528f89e248cbdf55840347b445934155` 的原 `ToolGatePipeline` 执行 pre → tool → post → symbolic-state update；源码提供前置与后置 Python 回调。源码没有随附本任务的现成纠正授权政策。 | 本轮在正常回调中独立配置目标、前驱、候选实例与授权值关系，并检查完整后继及未变字段/来源。没有调用 C verifier。**T-configured 与 T+relation 是同一个条件**；通过这些接口配置业务关系不属于框架能力突破。 | 本项目新增候选、授权、版本、来源和转换记录；纯草稿工具不提前写外部状态。作者提供的 SQLite 桥在事务内读取前驱、运行原 pipeline，post 通过后才提交。 | 8/8 通过，4 次合法提交、4 次无新增业务提交。与 C 的八项观察相同。 |
| **C：**复用冻结的 `stores.Store("full", ...)`，实际准入由原 `ReviewForms` 与 `SqlAlchemyFormRepository` 执行。该路线的原持久后端参与执行。 | 适配器构建相同语义的输入，保留提议、授权值、审查/执行实例、前驱与字段来源；未重写 C 准入判定。C 的其他证据和生产者元数据不在共享比较投影内。 | C 使用已冻结的持久后端；本轮适配器负责构造控制输入与保存证据。ToolGate 路线新增的 SQLite 桥不能归为 ToolGate 原生特性，也不能据其存在推断整个 C 合同已被等价覆盖。 | 8/8 通过，4 次合法提交、4 次无新增业务提交。本轮没有发现 C 相对于配置后 ToolGate 的差异。 |

ToolGate 源码和接口可由[来源清单](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/UPSTREAM-SOURCE.json)、[原 pipeline](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/vendor/ToolGate/toolgate/pipeline/pipeline.py)、[原合同定义](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/vendor/ToolGate/toolgate/contracts/contract.py)核查；新增部分分别见[ToolGate 适配器](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/toolgate_adapter.py)和[C 适配器](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/contract_adapter.py)。

## 八项开发控制

| 控制 | 业务情景 | T-configured | C | ToolGate 实际检查位置 |
|---|---|---|---|---|
| D01 | 原提议直接获批 | 提交；通过 | 提交；通过 | pre、工具、post 各 1 次 |
| D02 | 提议经纠正，执行授权值 | 提交；通过 | 提交；通过 | pre、工具、post 各 1 次 |
| D03 | 新预览实例已存在，仍执行原被审实例 | 提交；通过 | 提交；通过 | pre、工具、post 各 1 次 |
| D04 | 新实例经重新授权后执行 | 提交；通过 | 提交；通过 | pre、工具、post 各 1 次 |
| D05 | 新实例沿用旧实例授权 | 拒绝；通过 | 拒绝；通过 | pre 拒绝；工具与 post 均 0 次 |
| D06 | 审查后前驱已被独立事务推进 | 拒绝；通过 | 拒绝；通过 | pre 拒绝；工具与 post 均 0 次 |
| D07 | 草稿使用原提议而非纠正后的授权值 | 拒绝；通过 | 拒绝；通过 | 工具生成草稿后，post 拒绝 |
| D08 | 草稿改写未获授权的 `batch` 字段 | 拒绝；通过 | 拒绝；通过 | 工具生成草稿后，post 拒绝 |

“通过”表示符合预先保存的控制预期，不能把拒绝项称为任务完成。D06 的拒绝保留了已经提交的独立更新；“无新增业务提交”指本次尝试没有再写入目标版本。候选登记本身不计为业务提交。独立评分器还核查成功记录的完整后继、实例/授权关联，以及未变字段的值和来源。

[运行回执](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/runs/20261020T121403449662Z/RUN.json)记录 16 条完成、工程错误 0、网络尝试 0，并确认冻结来源及受保护文件未变；[环境记录](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/runs/20261020T121403449662Z/environment.json)记录 hosted model calls 为 0。本轮使用脚本 reasoner 和固定单工具检索，没有测试模型自主选择或续行。

## P0：六个效用差异应怎样解释

P0 对既有三项公共任务 × 11 情景 × N/E/C 的 99 条记录进行离线复算，共 33 个配对。E 与 C 在全部 33 对的 `I_target`、`U_boundary` 上相同。N 的 U=1 为 30，E/C 各为 24；**六个差异不能合称六次安全收益或六次合法任务损失。**

| 差异组 | 实际证据 | 可以作出的解释 |
|---|---|---|
| 3 组 stale | 授权前驱为 1，独立更新已提交为 2；N 从 2 写到 3 并覆盖更新，E/C 保持版本 2。 | 新增新鲜性义务下，三组过期请求确被阻止，独立更新得到保留。没有后续新授权恢复，原地址目标未完成；没有证据将其称为合法请求误拒。 |
| 3 组 swap | E/C 实际执行的候选身份不同且没有新授权；N 原生接口没有同等业务候选身份，harness 在提交后添加观测 ID。 | E/C 在新增身份映射下拒绝成立；**N 的身份违规仍为 unknown**。不能将旁路标签当作原生候选替换成功，更不能把这三组计为已证实防止了 N 的身份违规。 |

P0 中 N 的 `I_target` 为 6 通过、12 违规、15 未知；E/C 各 33 通过。N 的 15 个未知均有完整实验记录与实际版本提交，未知来自缺少可核查的业务候选/来源关系，并非数据丢失。原生图仍有提议、人工编辑与调用关联。证据更完整产生的可观察性提升，不能自动换算成防止违规。

P0 的合法控制中，E/C 各自 approve、edit、stale_recovery 的新授权提交均为 3/3 达到边界目标且 I=1。恢复由脚本执行。P0 也未运行完整任务 evaluator，因此其 U 是边界目标指标，不是完整公共任务成功率。详情与逐差异证据保留在[P0 联合分析](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/P0-JOINT-RESULTS.md)。

## 结论范围

这八项控制说明：纠正执行关系在 ToolGate 正常回调中可配置、可运行，并在已保存输入上与 C 得到相同业务效果。此前是否提出该关系，需要独立文献判断；可配置性既不能证明此前已经提出，也不能因此前未提出而否定框架表达能力。

本轮没有开发集外比较、端到端 ToolGate 论文复现、完整公共 benchmark、统计等效检验或独有能力证据。SQLite 桥的事务属于作者适配，post 拒绝的是尚未外部提交的草稿；没有验证任意副作用回滚或并发新鲜性保证。D08 仅检查未授权字段改动，没有开展伪造来源或证据攻击。后续公共工作流实验的结果需按自己的冻结输入和评分单独报告，不能由本轮推定。
