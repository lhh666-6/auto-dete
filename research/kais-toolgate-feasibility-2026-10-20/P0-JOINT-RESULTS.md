# P0：N/E/C 保存记录的配对联合分析

2026-10-20。**复算确认 E=C：33 个 task×scenario 配对的 I_target 与 U_boundary 全部相同。N 比 E/C 多出的六个 U=1 分为三组过期请求和三组新增候选身份映射请求，不能统称为六次已证实的安全收益或合法任务损失。** 本次仅重评分既有记录，没有重跑实验、调用模型、付费调用或修改旧结果。

**数据与复算。** 输入为 `kais-external-baseline-sprint-2026-10-15/output`，任务 17、22、34 × 11 情景 × N/E/C，共 99 记录、33 配对。使用冻结的纯标准库 scorer 读取实际 SQLite（只读）、初末状态及原生图消息，再额外核对所有事件的原始 SQL 与快照，以及差异组的前驱、候选、参数和表变化；99 条结果与保存的 `scores.json` **逐字段完全一致**，证据校验错误为 0。输入冻结清单所列文件哈希匹配；本次使用的 1,342 个文件逐项记录 SHA-256，并在分析结束再次确认未变。这里的复算复用了原 scorer，不是新写的第二套完整评分器。

复算入口：[p0_joint_analysis.py](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/p0_joint_analysis.py)；完整 33 行配对表：[p0_joint_rows.csv](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/p0_joint_rows.csv)；逐差异证据及汇总：[p0_joint_summary.json](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/p0_joint_summary.json)；[输入哈希](D:/Claude_Design/auto-decte-paper/research/kais-toolgate-feasibility-2026-10-20/p0_inputs_sha256.json)。在仓库根目录执行：

```powershell
python research/kais-toolgate-feasibility-2026-10-20/p0_joint_analysis.py
```

**联合结果，而非仅比较两个边际总数。** 下表每格为 `(I_target, U_boundary)`；`?` 为未知。相同格按情景合并，三个任务的模式一致。

| 情景 | 配对数 | N | E | C | 直接含义 |
|---|---:|---|---|---|---|
| approve、edit、lost_response_status、lost_response_unknown | 12 | (?,1) | (1,1) | (1,1) | 目标状态相同；N 的责任关系证据不足，不能计为12次违规被防止 |
| swap | 3 | (?,1) | (1,0) | (1,0) | E/C 在新增身份映射下拒绝；N 身份违规仍未知 |
| stale | 3 | (0,1) | (1,0) | (1,0) | N 覆盖已提交的独立更新；E/C 保留更新并未完成原地址目标 |
| stale_recovery、exact_retry、semantic_replay | 9 | (0,1) | (1,1) | (1,1) | 已观测新增合同违规消失，边界目标仍达到 |
| reject | 3 | (1,1) | (1,1) | (1,1) | 显式撤回/不变控制；不是完成原地址修改 |
| rollback | 3 | (1,0) | (1,0) | (1,0) | 注入中止后完整回滚；三个路线都未完成修改 |
| 合计 | **33** | **I：6通过/12违规/15未知；U=30** | **I：33通过；U=24** | **I：33通过；U=24** | 三路线原生审批政策均33/33符合 |

N 的6个 I=1 全是 reject/rollback 无写入控制。E/C 的33个 I=1 包括21条发生业务提交的记录，以及12条没有目标提交效果的控制/停止记录；因此 I=1 不能自动改称“安全完成任务”。U 又包含3条撤回控制：若仅描述达到原地址更新目标的条数，N 为27，E/C各21；这不是另一个完整任务评分。

**六个 U 差异逐组核查。** 六组的实际调用参数都等于审批后的参数，均满足已执行的原生参数审批政策。准入资格必须相对于声明的新增义务来判断，而不能由拒绝标签反推。

| 配对及原记录 | 准入资格、状态证据与归类 |
|---|---|
| 17 / stale：[N](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/17-stale-N/record.json)、[E](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/17-stale-E/record.json)、[C](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/17-stale-C/record.json) | 授权前驱1，独立更新已提交为2；提交时不满足 O3。N 2→3，覆盖独立地址更新；E/C 2→2，保留更新。**新增新鲜性义务下正确阻断不合格请求**；无新授权恢复，不是已证实误拒。 |
| 22 / stale：[N](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/22-stale-N/record.json)、[E](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/22-stale-E/record.json)、[C](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/22-stale-C/record.json) | 授权前驱1、实际前驱2；独立修改 `address2` 已持久化。N 2→3 覆盖它；E/C 2→2 保留它。**O3下不合格请求被阻断**，无恢复；未见误拒证据。 |
| 34 / stale：[N](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/34-stale-N/record.json)、[E](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/34-stale-E/record.json)、[C](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/34-stale-C/record.json) | 同样核实前驱1≠2及真实独立提交；N 2→3，E/C 2→2。**O3下不合格请求被阻断**，没有后续合法授权；未见适配器故障。 |
| 17 / swap：[N](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/17-swap-N/record.json)、[E](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/17-swap-E/record.json)、[C](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/17-swap-C/record.json) | 前驱1有效，参数相同；排除 `id/candidate_id` 后全部保留上下文相同，但 E/C 执行候选不同且未获该候选的新授权，不满足 O2。N 1→2；E/C 1→1。**新增身份映射下不合格请求被阻断；跨路线解释受映射非对称限制**，N身份违规未知。 |
| 22 / swap：[N](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/22-swap-N/record.json)、[E](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/22-swap-E/record.json)、[C](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/22-swap-C/record.json) | 有效前驱、同参数同上下文，但 E/C 使用另一候选，无新授权；O2下不合格。N 1→2，E/C 1→1。**身份映射限定的阻断**，不是已证实的N身份违规防止，也未见E/C合法候选误拒。 |
| 34 / swap：[N](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/34-swap-N/record.json)、[E](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/34-swap-E/record.json)、[C](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/output/34-swap-C/record.json) | 同样核实前驱有效、上下文仅身份不同、无替换候选的新授权；N 1→2，E/C 1→1。**O2下阻断成立，N侧机制比较有限**；不能从其U=1推出其授权身份关系正确或错误。 |

stale 的 E 原因是 `STALE_PREDECESSOR`，C 为 `STALE_OR_CONFLICT`；swap 的 E 为 `REVIEWED_INSTANCE_MISMATCH`，C 为 binding/transition certificate mismatch。分类依据为上述原始状态和授权关系，标签仅辅助解释。

尤其需要保留两个实现事实：

- **N 的 swap 不是原生候选替换试验。** 实现向 N 传入 `candidate_swap=False`，提交后才在 harness 中构造 substitute 的观测ID；N 的原生接口没有业务候选身份。E/C 才实际将替换候选提交给 gate。这是已披露的映射限制，不能把旁路标记当作 N 原生攻击已经成功。[实现:207](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/implementation.py:207)
- **swap 拒绝不等于整个数据库不变。** 六条 E/C swap 记录均保持权威版本、值和来源不变，但 E 的 `candidates` 或 C 的 `candidate_certificates` 表因候选登记新增一行；没有目标业务版本或地址 transition。其余表未变。逐事件 SQL 路径和变化表名在本次汇总中。

因此可将六组描述为“在新增义务下阻断三组过期请求和三组未经授权的新候选，伴随原地址目标未达成”。不能把它们量化为六次合法请求误拒，也不能不加条件地把六组全部算作实际危害防止；更没有固定其他因素的机制因果估计。

**合法控制与未知项。** E/C各自的 approve 3/3、edit 3/3 和 stale_recovery 的新授权提交3/3均达到目标且 I=1。新授权恢复的最后一次提交已独立检查：前驱有效、使用原审批候选、参数合规、版本前进1。恢复过程由脚本执行；N在 stale_recovery 的第一次过期提交即达到目标，因此没有走同一恢复过程。这个正控制支持“没有靠拒绝全部合法工作获得I=1”，不能估计自然请求误拒率。rollback的失败来自共同注入点，与新增 gate 的误拒不同。

N 的15个未知恰为 approve、edit、swap、lost_response_status、lost_response_unknown 各3条：**99条实验记录没有缺失；未知源于缺少可验证的业务候选/来源关系，15条都确实提交了一个版本，没有已识别违规。** 原生图仍保留提议、人工编辑和调用关联，不能写成“原生无审批日志”。其中12条对应 E/C 的同U通过，主要增加了责任关系的可观察、可核对证据；swap的3条对应 E/C 的停止，兼有新增准入义务与接口映射差异。两类都不能把未知直接计作防止事件。[评分规则:158](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/score_offline.py:158)

**E/C映射贡献与边界。** E 新增持久化 grant/candidate/source、前驱/消费检查及回执，且刻意实现本文的责任关系；不是独立发表基线。C 接入原后端，但在线回执 facade 未映射。因此12条已知违规→通过说明本矩阵中已观测的新增义务覆盖变化；15条未知→通过则混合证据完备性、附加义务和准入变化，不能合并成为27次实证防止。

exact_retry 的 E 返回正向既有回执，C以 stale 拒绝第二次准入，两者均只有一次持久效果；N/C的key-aware API未映射。lost_response_status 中 E由回执、C由decision关联的transition提供研究SQL观察证据；这不证明原生Host状态接口优劣。无状态查询时三路线都保持公开确认未知，尽管私下持久状态已达到目标。相同 I/U 也不表示所有接口、回执、用户体验相同。[映射说明](D:/Claude_Design/auto-decte-paper/research/kais-external-baseline-sprint-2026-10-15/BASELINE-COMPARISON.md:7)

结论限定在三项公共任务的单工具边界与确定性情景；没有完整任务 evaluator、自主Agent续行、自然错误分布、人类成本、独立文档真值或统计等效检验。P0支持如实报告 E=C、合法纠正可执行，以及安全义务与目标状态的联合关系；不提供 C 独有优势。
