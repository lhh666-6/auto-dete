# CK 与本文执行门：离线对象映射与准入探针

制定于 2026-10-14，在本探针的留档运行前锁定；仅用于投稿后探索性返修准备。冻结时间和逐文件哈希见 `freeze.json`。不是预注册研究、生产系统 benchmark、完整 CK 复现或新的 Agent 实验。

## 问题与范围

问题：在保留各自原生保护的情况下，CK 作者公开的有限状态模型与本文原有 Host，能否对共同可表达的正常、证据过期、前驱变化情形作出一致的准入决定？另外，四角色中哪些关系不能在 CK 现有抽象接口中直接测量？

本轮遵循原总方案八类场景，但缩为**共同准入行为探针**。独立真实业务规则尚未取得，因此不运行应用优越性评分，不声称完成完整 B2/B3 或外部系统 benchmark。没有新模型调用、付费服务、真人参与、生产数据或对提交版及冻结队列的修改。

分析单位为确定性构造场景，不是抽样任务。无随机分配、统计检验、功效分析或自然风险率估计；一次覆盖全部指定场景，再从另一目录离线重建核对语义输出。协议来自已有执行方案及本轮源码映射。代理在 API 核对阶段已做 16 条 Host 内存可运行性检查及 CK 部分原生调用检查（其中 Host 的证据场景为 E2 新候选配旧授权，与本协议不同）；其未留档的行级结果不作为本轮数值证据。冻结只锁定复核规则，不能宣称结果未知、盲测或前瞻性预注册。预期差异完全可能为零。

## 原生产物与映射

CK 原文件为 `reviews/kais-execution-plan-2026-10-14/baseline-audit/sources/ck-bounded-model.txt`，固定提交 `74841530988f1324bd927da15519486509372917`，SHA-256 `af28a28f195493009a53cce1aeca43c7fc4937871688ad1e9160ed3412b4fece`。保持字节及代码不变，通过 `runpy` 调用 `State`、`Request`、`submit`。不运行 `main` 的完整状态空间探索。模型作者明确指出其不是存储实现、conformance suite 或性能 benchmark。

本文使用 `research/agent-policy-phase2-formal-2026-10-07/src/phase2/kernel.py` 的原有 `Host`，分别使用 context 和 bound 政策，保留证据、值、前驱、来源、幂等及授权消费行为；通过公开工具参数入口执行。仅新建内存 fixture，不导入或改写正式任务清单、runner、scorer、结果。

| 对象 / 义务 | 本文 Host | CK 原模型及适配层 | 本轮解释 |
|---|---|---|---|
| 原提议与授权值 | `source_proposal_value` / `authorized_value`，提交值单独校验 | 外部描述放入不透明 `core_digest`；操作值映射为符号 `ops_token` | CK 不解析业务纠正关系；Accept/Correction 不是两种 CK 原生分支 |
| 被审阅 / 被执行候选 | grant 中 reviewed ID、commit 中 candidate ID | 没有独立的人工审阅候选 ID；pid 是提案身份，root 是状态抽象 | 两个同内容新实例格子记 `not_representable`，不执行、不计为接受或漏拦截 |
| 新鲜前驱 | candidate context 中版本对当前 head | 原生 `expected_head` 对 `State.head` | 可比较粗粒度准入决定；外部推进在 CK 中用一次合法独立 `submit` 产生 |
| 证据更新 | E1/E2 实际字节、哈希、locator 及当前证据引用 | 由适配层计算 E1/E2 引用相等，传入 `commit_bound_valid` 和 `final_bound_valid` | CK 原生检查 supplied freshness predicate；不声称复现证据获取/签名/字节验证 |
| 候选绑定 | 证书及 context / ID | 原生 derived root 对 sealed candidate root | 专门检查 root 改变控制；不能将其混同同内容新实例 |
| 完整后继 / 来源 | 读取真实 pre/post 字段及来源 | 符号 root 和 accepted-unit schema，`successor_well_formed` 抽象判据 | CK 的最终业务值、字段来源、四角色审计为 `null` / 未测，不用外部台账冒充原生保证 |
| 拒绝与重试 | 保存拒绝回执；新幂等键可再尝试，授权消费保持 | pid 有稳定 disposition；相同 pid/digest 返回旧结果；合法恢复使用新 pid | 分别保留语义，不在同 pid 上擦除拒绝 |

CK 的其他权限、认证、覆盖、生命周期、效果和后继保护保留默认合法输入，并用单故障控制确认有代表性的保护仍工作。不向任何方法提供最终判分 oracle。所谓“中立事实”是输出格式中立，不等于已建立外部业务规范。

## 固定输入与八格设计

全新构造单记录，字段 quantity，基线值 7；原提议值 20。Accept 授权 20，Correction 授权 21。另有未改字段 reference_note 和 business_context，携带来源。E1/E2 支持相同提议值，但版本、文字和 locator 不同。所有场景采用 Host 的 E family 以使证据版本约束生效，不推断其他业务必须使用该规则。CK 的 Accept/Correction 操作符号分别为 1/2，不能从 modulo-29 root 解码业务值或推断密码学安全。

每种模式以下四格，各执行 context、bound、CK 三条记录；共 24 条计划记录，其中 CK 两条不可表达，预期最多 22 条实际场景执行。不能把 24 条称为 24 个可比试验。

1. `normal`：取得有效候选与授权，按授权提交。
2. `new_instance`：授权 c1 后以同上下文新建 c2，原授权不变，提交 c2。CK 跳过，原因如上。
3. `evidence_changed`：授权后发布 E2，初次提交仍使用 E1 候选。
4. `predecessor_changed`：授权后发生独立合法 head 推进，初次提交仍指向旧 head。

初次提交不混入其他故障。记录响应、实际是否改变权威业务状态/产生新效果、提交前后版本和可观测事实。拒绝允许写诊断和 disposition：状态不变只指业务 head/root/authority/effects 等，不指整个存储无变化。

## 预定控制与续行

- 每个可执行格子原样重放初次请求：检验无第二次状态变化及稳定响应。
- 证据/前驱拒绝后，Host 重新提案并授权当前候选；CK 重新准备新 pid、当前 head、当前证据和新 seal，保留原拒绝及有效 effect ID。脚本只给出一个合法恢复见证，不声称 Agent 自发恢复、恢复最优或人力成本相同。
- 新实例被 bound 拒绝后，用新请求键复用已审阅 c1；另用独立副本检查给 c2 新授权后可以合法提交。context 若已提交则不回滚再造拒绝。
- CK 独立负控制：candidate root 不匹配、最终新鲜度失效、后继无效、自我扩权、已用 pid 换 core、已用 pid 换 attempt、新 pid 重用已消费 effect。均走原生 submit，不补写 gate。
- 本文两个政策各检查 Correction 时误交原提议值会被拒绝；这是已有授权值检查的控制，不宣称新发现。

## 输出、失败与可说的结论

逐条保留初次、重放、恢复的原始工具响应或 CK Request/Result 状态，以及规范化事实。CK 无法观测的业务值、审阅实例和来源记 `null`，不是 0 分。原生有效性检查与本文实例关系分开，无总分、无完整性排行榜、无吞吐或延迟排名。

统计仅为覆盖数、粗粒度决定的一致性及控制是否符合协议。无可区分的差异也是有效结果。任何异常保留 error/unknown，退出非零并保存已取得记录，不删除失败；修复须记录，不能把执行后的变更冒称预先冻结。

本轮允许的结论：公开模型在给定输入和明确适配下如何处理共同准入状态，及哪个原研究问题仍不可比较。禁止的结论：本文优于 CK、CK 不支持实例绑定/纠错/来源、CK 接受未授权替换、业务安全等价、在线效用等价、已补齐真实应用基线。

后续门槛：只有找到明确而未被近邻已有机制覆盖的可检验义务，或一个真实应用中的不同代价/效果，才继续 CK＋契约或在线试验。当前探针不能自动开启 API 采集。

来源：[CK 原文 §2.2、§3、§5](https://arxiv.org/html/2608.11632v1)、[固定源码](https://github.com/openkedge/pci/blob/74841530988f1324bd927da15519486509372917/src/transactional_continuity_kernel/bounded_model.py)、[前轮来源审计](../../reviews/kais-execution-plan-2026-10-14/baseline-audit/BASELINE_AUDIT.md)。
