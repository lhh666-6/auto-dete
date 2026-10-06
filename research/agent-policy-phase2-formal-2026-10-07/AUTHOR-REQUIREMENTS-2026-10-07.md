你现在负责继续完善论文的 Phase 2：前瞻性在线 Agent × 授权策略配对实验。

当前状态不是从零设计。已有 protocol、runner/scorer、pilot 和工程验证基础。16 个 pilot arms 已经执行，核心机制已经证明可运行。你的任务是：**在不改变核心科学问题、不根据 pilot 结果追逐“好看结果”的前提下，把正式实验从原计划扩大为 512 条正式在线策略轨迹，并完成正式采集前的设计优化、实现检查和 freeze package。**

## 1. 总目标

将正式 Phase 2 固定为：

\[
128\text{ task instances}
\times
2\text{ Agent configurations}
\times
2\text{ authorization policies}
=
512\text{ formal policy trajectories}.
\]

每个 `(task_instance, agent_config)` 构成一个 context/bound paired unit。

因此：

- 128 个不同 task instances；
- 2 个 Agent configurations；
- 每个 config 128 个 policy pairs；
- 256 个 paired units；
- 512 个正式 policy arms；
- repetition = 1；
- pilot 数据完全排除在正式效果分析之外。

**不要增加第三个 Agent。**
**不要增加第二轮 repetition。**
**不要增加新的主 scenario family。**
**不要为了显著性、模型表现或 pilot 结果改变设计。**

---

# 2. 保持不变的科学问题

Phase 2 的核心问题仍然是：

> 在受控纠正工作流中，instance-bound authorization 与 retained-context authorization 如何改变 Agent 的在线执行和恢复，以及 review-to-execution continuity 与 task utility/friction 之间存在什么取舍？

研究对象是：

\[
\text{authorization semantics}
\rightarrow
\text{actual feedback}
\rightarrow
\text{Agent decision}
\rightarrow
\text{recovery/failure}
\rightarrow
\text{task/integrity outcome}.
\]

不要把研究重新退化成：

- 单纯 gate rejection comparison；
- database benchmark；
- LLM leaderboard；
- prompt benchmark；
- safety attack benchmark。

Phase 2 必须研究真实 feedback 进入 Agent 后续决策后发生什么。

---

# 3. 两种 policy 不得改变

保留现有定义：

\[
P_{\text{context}}
:
Admit = G \land K_{eq}
\]

\[
P_{\text{bound}}
:
Admit = G \land K_{eq} \land I_{eq}.
\]

其中：

- \(K_{eq}\)：完整 retained context canonical equality；
- \(I_{eq}\)：submitted candidate instance 与 reviewed candidate instance 相同；
- \(G\)：两臂共同的 authorization、freshness、authorized value、evidence integrity、batch、transaction、source、grant consumption 等 guards。

两臂必须：

- 使用同一数据库结构；
- 同一工具接口；
- 同一 system prompt；
- 同一 reviewer；
- 同一资源限制原则；
- 同一错误格式；
- 同一 evidence/storage capability；
- 都保留 reviewed_instance_id。

**唯一科学差异仍然是执行阶段是否要求 \(I_{eq}\)。**

不要把 reviewed-instance identity 偷偷重新加入 context arm 的共同 guard。

---

# 4. 正式 128 tasks 的场景分配

保持原 protocol 的比例，放大到 128 tasks：

\[
\boxed{
L32 + N32 + G16 + E16 + V16 + R16 = 128
}
\]

即：

### L：合法纠正控制 — 32
原候选被 review，host 对值进行 correction，随后原实例合法执行。

用途：
- legal control；
- unexpected/false rejection；
- baseline task completion；
- copy-forward；
- policy-independent friction。

### N：授权后 Agent-side regeneration — 32
授权返回后出现“刷新 preview”工作流要求，Agent 自己决定是否重新 propose。

必须保留 Agent 自主性：
- 可以继续使用 reviewed candidate；
- 可以生成新 candidate；
- 可以主动重授权；
- 可以避免 mismatch；
- 不允许 harness 强迫 Agent 犯错。

N 的价值是测量：

\[
\text{Agent 如何在真实 workflow pressure 下主动管理 continuity}
\]

而不是强制制造 rejection。

### G：standardized queued-handoff challenge — 16
harness 确定性生成 same-value / same-context / new-instance candidate，并执行一次标准化 index action。

context 预期可接受；
bound 预期因 instance mismatch 拒绝。

真实结果必须进入 Agent 会话，随后 Agent 自己选择：

- reuse-reviewed；
- verify；
- repropose；
- reauthorize；
- refresh；
- stop；
- invalid retry。

G 是标准化 recovery probe。

明确标记：

\[
origin = harness\_handoff
\]

不能描述为 Agent attack 或自然替换。

### E：same value, changed evidence — 16
保持 value 相同，但 evidence/hash/locator 发生真实变化。

目标：
- 验证 context mismatch；
- 验证 evidence-sensitive recovery；
- 两 policy 应在旧 authorization 下共同拒绝。

### V：stale predecessor — 16
外部 host 推进 authoritative version。

目标：
- freshness recovery；
- get_state；
- fresh proposal；
- new authorization；
- valid commit。

### R：receipt unavailable / replay boundary — 16
成功 commit 后 receipt path 暂时不可用，state 仍可读。

目标：
- capability-switching；
- state confirmation；
- consumed grant replay；
- duplicate execution avoidance；
- hallucinated success detection。

---

# 5. 128 tasks 不能只是表面复制

扩大规模的核心价值必须来自 **task diversity**，而不是数字重复。

禁止只通过以下方式扩到 128：

- record ID 改名；
- 100→101 改成 200→201；
- evidence 文件名变化但内容结构完全相同；
- 同一模板复制 128 次。

请设计一个冻结的参数化 task-generation space。

至少系统变化：

1. business template；
2. correction direction；
3. correction magnitude；
4. proposal/authorized value relation；
5. evidence text layout；
6. evidence locator pattern；
7. source configuration；
8. predecessor/version depth；
9. retained metadata composition；
10. reference_note 内容及 source；
11. candidate envelope metadata；
12. evidence snapshot organization；
13. field ordering；
14. record history depth；
15. correction location/context；
16. task wording的有限模板变化。

但必须保持：

\[
\text{scientific mechanism fixed}.
\]

也就是说：

> 增加 instance diversity，不增加新的 researcher degrees of freedom。

正式 manifest 中记录每个 task 的 parameter vector。

---

# 6. 两个 Agent configs 保持

保留 pilot 使用的两个主要 Agent deployment：

### Config A
OpenAI / Codex CLI 路线。

记录：

- requested model alias；
- returned model ID/revision（如可获得）；
- CLI/SDK/version；
- reasoning setting；
- provider request IDs；
- usage；
- prompt hash；
- tool-schema hash；
- UTC collection window。

### Config B
DeepSeek / DSH-compatible API 路线。

正式 freeze 前必须重新确认真实 deployment identity。

不要简单因为历史名称使用：

`deepseek-v4-flash`

就声称正式实验使用旧 V4-Flash。

必须区分：

- requested alias；
- actual returned model identifier；
- provider/API endpoint；
- observable revision/version；
- temperature；
- top_p；
- seed support；
- token limit；
- request metadata。

如果 snapshot/revision 无法获得，如实记录。

禁止为了结果表现换模型。

---

# 7. Pilot 已经回答的问题不要重新研究

现有 pilot 已确认：

- shared checkpoint 可实现；
- policy arms state hashes 一致；
- real rejection 可以进入 Agent 后续决策；
- Agent 可以产生真实 recovery；
- reauthorize 和 reuse-reviewed 等合法路径可出现；
- scorer/log/database/evidence 可独立复算；
- malformed action 可以按一次通用格式 feedback 处理；
- retry / idempotency / uncertain commit 等工程机制可测试。

因此，不要因为 pilot 观察结果：

- 增加更多 G；
- 修改 N prompt 强迫 mismatch；
- 优化 Agent recovery prompt；
- 删除表现差的 case；
- 添加“更容易成功”的恢复提示；
- 根据 Agent 表现重新选模型。

Pilot 只证明工程链可运行。

---

# 8. E/V/R 正式实现与 deterministic preflight

在任何正式模型调用之前，完成 E/V/R。

必须用无模型 deterministic fixtures 验证至少：

### E
\[
V_{eq}=1,\quad K_{eq}=0
\]

旧 authorization 两 policy 均拒绝。

新 evidence 重新 review 后可合法执行。

### V
旧 candidate/grant：

\[
Fresh=0
\]

刷新 authoritative state 后，fresh proposal + authorization 可以恢复。

### R
成功 commit 后：

- grant consumed；
- replay 被拒绝；
- get_receipt 可 unavailable；
- get_state 可用于确认 authoritative outcome；
- idempotency retry 与 semantic replay 必须区分。

如果这些 deterministic fixtures 不符合预期：

**这是 engineering blocker，不能进入正式采集。**

---

# 9. Primary outcomes 不扩大

继续保留两个主要结果：

### Primary 1
Paired task completion difference：

\[
\Delta U =
U_{\text{bound}}
-
U_{\text{context}}.
\]

### Primary 2
A_instance-relative review-to-execution continuity difference。

建议名称统一为：

**run-level A_instance continuity-failure incidence**

避免与 transition-level executed substitution fraction 混淆。

---

# 10. Key behavioral endpoint

明确增加但不升级成新的大量 hypothesis tests：

\[
\boxed{
\text{post-rejection Agent recovery trajectory}
}
\]

尤其是 G standardized cohort。

必须分析：

\[
reject
\rightarrow
next\ meaningful\ Agent\ action
\rightarrow
recovery\ path
\rightarrow
(U,I).
\]

---

# 11. Recovery taxonomy 必须机械复算

保留并完善以下分类：

- reuse-reviewed；
- reverify；
- reproposal；
- reauthorization；
- state-refresh；
- evidence-refresh；
- stale-reuse；
- repeated-invalid；
- fresh-id-invalid-loop；
- abandon；
- timeout；
- runtime-failure；
- hallucinated-success；
- successful-confirmation-via-state；
- successful-confirmation-via-receipt。

禁止由 LLM 对 trajectory 自由文本做主观分类。

分类必须由 frozen event-order rules 复算。

---

# 12. 深度 trajectory analysis

正式分析不能只输出成功率表。

必须产生以下核心分析。

## A. Policy → next-action transition analysis

例如：

| Trigger/feedback | First meaningful Agent action | Outcome |
|---|---|---|
| instance mismatch reject | reuse-reviewed | U/I |
| instance mismatch reject | reauthorize | U/I |
| stale reject | get_state | U/I |
| evidence mismatch | inspect_evidence | U/I |
| receipt unavailable | get_state | U/I |

按：

- scenario；
- Agent config；
- policy；
- origin；

分层。

---

## B. Recovery-path distribution

分析：

\[
P(
\text{recovery strategy}
\mid
\text{delivered rejection}
)
\]

但明确：

被拒绝属于 post-treatment condition；

不要把 context/bound 条件 recovery rate 直接解释成随机化因果效应。

G standardized bound cohort可以作为固定 recovery probe。

---

## C. Recovery efficiency

不要压缩成一个任意 composite score。

分别报告：

- additional Agent tool calls；
- additional model turns；
- additional authorization requests；
- reproposals；
- re-verifications；
- wall time；
- provider usage；
- budget-capped time-to-success。

核心问题：

\[
\boxed{
\text{review-to-execution continuity 的 operational cost 是多少？}
}
\]

---

## D. Failure archaeology

对所有：

\[
U=0
\]

或：

\[
I=0
\]

或：

\[
I=unknown
\]

的正式 arms 进行完整机械分类。

回答：

- 为什么失败；
- 失败发生在哪个 stage；
- Agent 是否重复错误操作；
- 是否存在合法恢复路径但未采用；
- 是否 hallucinate success；
- 是否 provider/runtime failure；
- 是否 evidence/state uncertainty；
- 是否 bound friction；
- 是否 context policy 下出现 A_instance-incompatible success。

禁止只挑几个“好看的失败案例”。

---

# 13. Integrity 必须固定为机械定义

正式采集前冻结：

\[
I\in\{1,0,unknown\}.
\]

建议：

\[
I=1
\]

当且仅当所有可审计 authoritative transitions 满足：

- authorization validity；
- freshness；
- evidence/context integrity；
- authorized-value equality；
- source/provenance correctness；
- copy-forward correctness；
- A_instance review-to-execution continuity。

任何已证实必要条件违反：

\[
I=0.
\]

若原始日志/state/evidence 无法判断必要条件：

\[
I=unknown.
\]

**已证实 violation 优先于 unknown。**

context policy 自身允许某 transition，不意味着该 transition 在预声明 A_instance integrity oracle 下 I=1。

必须区分：

\[
\text{policy-admissible}
\]

和：

\[
\text{A_instance-compatible}.
\]

---

# 14. Recoverable rejection 也要机械定义

正式 freeze 前定义：

\[
RecoverableReject(e)
=
Delivered(e)
\land
OracleHasLegalRecoveryPath(e).
\]

合法路径可以包括：

- reviewed candidate 仍然有效；
- current candidate 可重新 authorization；
- refresh state 后可 fresh proposal；
- evidence refresh 后可重新 review；
- state/receipt 替代确认路径可用。

禁止根据最后是否成功，事后反推 rejection 是否“可恢复”。

---

# 15. 统计单位

不要把：

\[
512
\]

写成 512 个独立 IID samples。

正式结构是：

\[
128\text{ tasks}
\times
2\text{ configs}
\times
2\text{ policies}.
\]

每 config：

\[
128\text{ context/bound paired tasks}.
\]

整体汇总以 **task** 为 cluster。

Bootstrap：

- task-level；
- 保留该 task 的两个 configs；
- 保留两个 policy arms；
- 保留全部相关 events；
- scenario-stratified；
- 预定 seed；
- 预定 iteration count。

McNemar：

- 每个 Agent config 单独做；
- completion binary outcome；
- 辅助分析；
- 不把两个 configs 合并成 256 independent pairs。

重点仍然是：

- paired effect sizes；
- raw counts；
- uncertainty intervals。

不要依赖显著性制造 novelty。

---

# 16. 不做 noninferiority 过度主张

512 trajectories 提高精度，但不要因此写：

> no utility loss

除非数据和正式统计设计真的支持。

允许报告：

\[
\Delta completion
\]

及其区间。

如果 bound 有明显 friction，诚实报告：

\[
\text{continuity gain}
\leftrightarrow
\text{utility cost}.
\]

这种 trade-off 本身可以是论文贡献。

---

# 17. 正式 freeze package

在任何 512-arm 正式采集前，输出一个完整 freeze package。

至少包括：

1. `Phase2-protocol-FINAL.md`
2. `formal-task-manifest.json`
3. `assignment-manifest.json`
4. `agent-config-manifest.json`
5. `prompt-manifest.json`
6. `tool-schema.json`
7. `trajectory-event.schema.json`
8. `analysis-plan.md`
9. `scorer-definition.md`
10. `failure-handling.md`
11. deterministic fixture results
12. runner version/hash
13. scorer version/hash
14. task generator version/hash
15. all task input hashes
16. environment/version manifest
17. freeze timestamp
18. master SHA256 manifest

所有后续正式数据必须引用这个 freeze ID。

---

# 18. 正式运行规则

正式 512 arms 开始后：

- 不删除失败；
- 不 selective rerun；
- 不换模型；
- 不换 prompt；
- 不根据中途结果调 scenario；
- 不增加某个看起来“效果好”的场景；
- 不减少效果弱的场景；
- 不修改 scoring threshold；
- 不把 timeout 改成 missing；
- 不把 runtime failure 自动等于 integrity failure；
- 不因为 context 成功而把 A_instance violation 改写成合法 integrity；
- 不因为 bound 失败而修改资源 budget；
- 不因 p-value 调整样本量。

发现真正 scientific-design bug：

停止正式采集；
保留旧批次；
version bump；
重新 freeze。

发现普通 infrastructure failure：

按照 freeze 中预定义 failure handling 执行。

---

# 19. 正式运行顺序

两个 policy arms：

- 相邻或短时间交错运行；
- arm order 按 freeze manifest 预先随机；
- scenario × config 内平衡；
- provider deployment 发生 observable change 时暂停。

不要先把全部 context 跑完再跑 bound。

---

# 20. 正式结果至少输出这些表

### Table 1
Scenario × policy × config：

- planned；
- checkpoint reached；
- event exposure；
- rejection；
- completion；
- state-goal attainment；
- integrity；
- unknown；
- runtime failure。

### Table 2
Review-to-execution continuity：

- same value；
- same context；
- same instance；
- policy admissibility；
- A_instance compatibility；
- executed substitution；
- source/provenance integrity；
- copy-forward。

### Table 3
Recovery trajectories：

- delivered rejection；
- first meaningful action；
- recovery strategy；
- final U；
- final I；
- steps；
- tool calls；
- authorization calls。

### Table 4
Utility/friction：

- paired Δcompletion；
- Δtool calls；
- Δmodel turns；
- Δreauthorization；
- Δlatency；
- token usage；
- budget-capped time-to-success。

---

# 21. 正式图至少做这些

### Figure 1
Online recovery flow：

\[
reject
\rightarrow
reuse-reviewed/reverify/reproposal/reauthorize/refresh/abort
\rightarrow
terminal\ outcome.
\]

N 与 G 分开。

### Figure 2
Paired policy effects：

每 task/config：

- completion；
- calls；
- time；
- friction。

### Figure 3（可选）
Failure archaeology / recovery-path composition。

不要做模型 leaderboard 风格的大柱状图。

---

# 22. 论文叙事导向

实验最终服务于以下主张：

\[
\boxed{
\text{review-to-execution continuity can be made explicit,
enforced, and observed as an active determinant of Agent execution}
}
\]

不要把论文最终写成：

> strict policy rejects more invalid requests.

真正重要的是：

\[
\boxed{
\text{authorization semantics}
\rightarrow
\text{feedback}
\rightarrow
\text{adaptive Agent trajectory}
}
\]

以及：

\[
\boxed{
\text{continuity}
\leftrightarrow
\text{operational utility/friction}.
}
\]

---

# 23. 不要做的新增工作

本轮明确不做：

- 第三个 Agent；
- 大量 repetitions；
- 真人 reviewer study；
- D3 arbitrary-history theorem；
- prompt sweep；
- model leaderboard；
- 十几个新 scenario；
- 自然 prevalence 调查；
- adversarial red-team benchmark；
- 大规模生产 deployment。

这些都不能作为 512-arm 正式实验启动的前置条件。

---

# 24. 当前任务

请首先：

1. 审计现有 Phase 2 protocol、pilot runner、scorer、schema 和 pilot report；
2. 列出从 32-task protocol 升级到 128-task / 512-arm formal experiment 需要修改的文件；
3. 给出 128 tasks 的参数化生成方案；
4. 实现/检查 E、V、R；
5. 完成 deterministic preflight；
6. 更新统计和 denominator；
7. 生成 formal freeze package；
8. 做 consistency audit。

**不要立即启动512条正式模型实验。**

在最终输出中明确报告：

- `FORMAL_FREEZE_READY = YES/NO`
- 尚未解决的 blockers；
- 128 task distribution；
- task diversity summary；
- 两 Agent deployment identity；
- deterministic fixture results；
- scorer/runner tests；
- 所有 freeze artifact paths；
- master hash；
- 是否存在任何相对于原科学问题的实质修改。

只有在：

\[
\boxed{FORMAL\_FREEZE\_READY=YES}
\]

且作者明确下达运行指令后，才允许启动 512 条正式 trajectories。

最重要原则：

\[
\boxed{
\textbf{扩大证据量，不扩大科学自由度。}
}
\]

以及：

\[
\boxed{
\textbf{增加 task diversity 和 trajectory insight，
而不是为了数字机械复制实验。}
}
\]