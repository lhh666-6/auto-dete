# Auto-Decte novelty 重构设计：Correction-Aware Authoritative-State Admission

Date: 2026-08-31

Target manuscript: R21 JSS revision

Status: approved conceptual design; manuscript implementation pending

## 1. Objective

将论文的 novelty 从“authorization、freshness、provenance、atomic commit 等机制的组合”重构为一条层级化研究论证：

\[
\boxed{
\text{Correction-aware abstraction}
\rightarrow
\text{Failure-distinguishability characterization}
\rightarrow
\text{Formal/transactional realization}
\rightarrow
\text{Behavioral validation}
}
\]

论文不再声称首次提出 update admission、transaction boundary、governed write 或 authorized mutation。核心贡献改为：识别并刻画一种更窄的软件边界——一个不可信、已持久化的 AI candidate，如何通过与其绑定的人类授权决定，产生完整 authoritative successor，同时保留 candidate 作为非权威历史证据。

## 2. Novelty decision

### 2.1 What is not novel

以下机制或术语已被相邻工作单独或组合覆盖，不能作为独立 priority claim：

- transaction boundary；
- update admission 或 Admission Gateway；
- source-supported update validation；
- authorized mutation；
- predecessor/version binding；
- provenance-preserving history；
- policy-gated commit；
- stale/supersession detection；
- ordinary transactional atomicity。

因此，禁止使用以下主张：

- “the first transaction boundary for AI/agent updates”；
- “the first governed admission mechanism”；
- “the first authorized persistent mutation protocol”；
- “the first use of provenance, freshness, or predecessor binding”；
- “a universally minimal admission schema”。

### 2.2 What remains defensible

Auto-Decte 的可防守空间是以下关系及其结构性刻画：

\[
\boxed{
\text{exact persisted AI candidate}
\rightarrow
\text{candidate-bound human authorization}
\rightarrow
\text{explicit authorized value}
\rightarrow
\text{atomic complete-record successor}
\rightarrow
\text{total per-field source attribution}
}
\]

其中最具识别度的语义是 Correction：

\[
x_c \neq x_a,
\]

即 machine-proposed value 与 human-authorized value 可以不同，二者必须同时保留且不能互相覆盖。

## 3. Nearest-neighbor collision boundary

### 3.1 MutMem

MutMem 研究已具有持久状态的 memory property 如何被 cryptographically authorized mutation：transition 绑定 old/new weight、terminal provenance node、signer epoch 和 no-fork predecessor，并由 housekeeper 授权。

Auto-Decte 不以这些机制本身为 novelty。剩余差异是：

- MutMem 的主要 mutation object 是既有 memory 的 retrieval weight；
- 授权主体是 operational housekeeper，而不是 candidate-bound human review decision；
- 公开模型未展示 machine candidate value 与 distinct human-authorized value 的双值 Correction；
- 未展示 complete multi-field authoritative successor 与 total field-source map 的联合语义。

Primary source: <https://arxiv.org/html/2608.02843>

### 3.2 MemTxn

MemTxn 已明确提出 answer-model-external transaction boundary、source-supported update admission、conflict-conditioned visibility 和 complete-state recovery。它已经占据“首次把 agent-memory update 放入 transaction/admission boundary”的主张空间。

Auto-Decte 的剩余差异是：

- MemTxn 以 source-support predicate 决定 proposal activation；
- 公开模型未展示 attributable human authorization of the exact candidate；
- 未展示 Correction 中 \(x_c\neq x_a\)；
- 未展示 successor-wide total field-source attribution；
- 其公开边界明确不保证 semantic role binding 和 concurrency。

Primary source: <https://arxiv.org/html/2607.27834>

### 3.3 SuperLocalMemory 4.0

SuperLocalMemory 4.0 已包含 Admission Gateway、immutable ActorContext、policy registry、generation fence、canonical transaction 和 projection completion manifest。因此 admission、governed write 和 transactional projection completion 不能单独作为 Auto-Decte novelty。

Auto-Decte 的剩余差异是：

- 公开正文未展示 candidate-bound live human approval；
- 部分 activation 明确是 configuration-gated，而非 live human/RBAC approval；
- parent-version lineage 和 generation tracking 在相关路径中未报告；
- 未展示 dual-value Correction；
- 未展示 complete authoritative-record successor 的 total per-field source relation。

Primary source: <https://arxiv.org/html/2608.08253>

### 3.4 When Stale Constraints Go Unchecked

该工作研究 immutable historical provenance、source supersession 与有限 verification budget 下的 stale-consistent agent decision。它为 freshness distinction 提供强 empirical motivation，但没有提出 candidate-bound authoritative commit contract。

Primary source: <https://arxiv.org/html/2608.25553>

### 3.5 MemTX is a separate work

项目当前引用的 `MemTX: Transactional Belief Commit for Stateful Agent Memory`（arXiv:2607.23929）与 `MemTxn: A Transaction Boundary for Source-Supported Updates and Complete-State Recovery in Agent Memory`（arXiv:2607.27834）是两篇不同论文。最终 Related Work 必须分别引用和比较，禁止名称或贡献归属混淆。

## 4. Core abstraction

### 4.1 Authority-relevant history

定义 authority-relevant history：

\[
h=S_0\xrightarrow{e_1}S_1\xrightarrow{e_2}\cdots\xrightarrow{e_n}S_n,
\]

其中事件至少覆盖：

- evidence persistence；
- candidate persistence；
- human review decision；
- authorization construction；
- admission attempt；
- authoritative successor commit 或 rejection/stutter；
- reverse-trace reconstruction 或 trace failure。

该 history abstraction 不要求某一种数据库 schema；它描述 admission mechanism 为了作出决定和重建结果必须能够观察的语义信息。

### 4.2 Admission relation

Admission 定义为：

\[
\operatorname{Admit}(c,a,S_v)=S_{v+1},
\]

subject to：

\[
\operatorname{Bind}(a,c)
\land
\operatorname{Fresh}(c,S_v)
\land
\operatorname{Authorized}(a)
\land
\operatorname{Complete}(S_v,S_{v+1})
\land
\operatorname{Attributed}(S_{v+1}).
\]

Admission 不应定义为 `Admit(c)=fact`，也不应声称 candidate 本身获得 authoritative status。Correction 中，candidate value 并未成为 authoritative fact。准确语义是：

> Admission transforms a candidate-bound authorization into an authoritative successor while retaining the candidate as non-authoritative historical evidence.

### 4.3 Mutation versus admission

Authorized mutation 修改一个已经处于 authoritative state 中的对象：

\[
\operatorname{Mutate}(o_v,\alpha)=o_{v+1}.
\]

Correction-aware admission 则处理两个不同来源的事实角色：

- machine candidate 提供 proposal origin；
- human authorization 提供 committed-value authority；
- trusted admission transaction 构造完整 successor。

因此核心区分不是“使用了不同术语”，而是 authority origin、proposal origin 和 committed value 可以分离。

## 5. Dual-value attribution semantics

定义：

\[
\operatorname{proposal}(c)=x_c,
\]

\[
\operatorname{authorize}(a)=x_a,
\]

\[
\operatorname{commit}(S_{v+1},f)=x_a,
\]

\[
\operatorname{origin}(S_{v+1},f)=c.
\]

Accept：

\[
x_c=x_a.
\]

Correction：

\[
x_c\neq x_a.
\]

该语义同时保留两类不可互相替代的陈述：

1. 机器实际提出了什么；
2. 人类明确授权什么进入 authoritative state。

最终 committed value 的 authority 来自 authorization；其 admission history 的 candidate origin 仍指向原始 candidate。系统不得把 \(x_a\) 回写为机器 proposal，也不得在保存 \(x_a\) 时擦除 \(x_c\)。

## 6. Observation model

### 6.1 Information classes

令完整 distinction basis 为：

\[
\mathcal D=\{D_C,D_V,D_F,D_B,D_S\},
\]

其中：

- \(D_C\)：candidate identity and context；
- \(D_V\)：dual-value attribution；
- \(D_F\)：freshness discriminator；
- \(D_B\)：batch/successor completeness；
- \(D_S\)：total source attribution。

这些是 information classes，而不是强制字段名。例如 \(D_F\) 可由 version number、logical clock、immutable state hash、transaction epoch 或 revision token 实现。

### 6.2 Observation projection

对 \(I\subseteq\mathcal D\)，定义：

\[
\pi_I(h)
\]

为只保留信息类别 \(I\) 时 mechanism 可观察到的 authority-relevant history 投影。

候选标识也不要求一定存在名为 `candidate_id` 的字段；要求是 candidate identity equivalence class 不得退化为 value equality。

### 6.3 Outcome

定义：

\[
O(h)=\langle status,successor,trace\rangle,
\]

其中：

- `status`：accept、reject 或 failed/stuttering attempt；
- `successor`：authoritative successor projection，或无 successor；
- `trace`：complete、incomplete、ambiguous 或 unavailable。

Outcome 不能只定义为 binary accept/reject，否则无法表达 source-complete 与 source-ambiguous successors 的差异。

### 6.4 Distinguishability failure

若存在 safe history \(h_s\) 与 unsafe history \(h_u\)，满足：

\[
O(h_s)\neq O(h_u),
\]

但：

\[
\pi_I(h_s)=\pi_I(h_u),
\]

则任何决策只依赖 \(\pi_I\) 的 mechanism 都无法正确区分二者。因此，\(I\) 对对应 failure family 不充分。

## 7. Five failure-distinguishability requirements

在数学定义与 proof obligations 完整前，论文使用 `requirement`、`distinguishability lemma` 或 `characterization claim`，不预先称为 theorem。

### R1. Candidate-context distinguishability

两个 candidates 可以具有相同 value，但属于不同 record、field、evidence、producer 或 persisted candidate identity。

要求：系统必须保留 candidate identity equivalence class 及足以约束授权作用域的 context；value equality 不能替代 candidate identity。

对应失败：equal-value candidate substitution。

### R2. Dual-value attribution distinguishability

只观察 final value 无法同时表达机器 proposal 与人类 authorized value，也无法区分合法 Correction 与 candidate erasure/rewrite。

要求：系统必须分别保留 \(x_c\)、\(x_a\) 及其 machine/human semantic roles。

对应失败：Correction erasure 或 false machine attribution。

### R3. Freshness distinguishability

同一个 candidate 和 authorization 在当前 state 与 superseded state 中可以保持字节相同，但应产生不同 admission outcome。

要求：系统必须保存并在 commit-time 检查足以区分 current 与 superseded context 的 freshness discriminator。

对应失败：stale replay。

### R4. Successor-completeness distinguishability

一个完整 batch commit 与只产生部分 field effects 的 successor 可能共享若干最终字段值，但其 authority outcome 不等价。

要求：系统必须保留 declared batch domain、changed-field framing 与 atomic successor boundary。

对应失败：partial successor。

形式上应明确：

\[
\operatorname{Complete}(S_{v+1})
\]

关注 successor 是否完整产生。

### R5. Source-attribution distinguishability

两个 successors 可以具有完全相同的 field values，但一个拥有完整、唯一、可重建的 field-source history，另一个存在 missing、replaced、duplicate 或 ambiguous source。

要求：系统必须保存 total per-field source relation，并对 unchanged field 执行 exact source copy-forward。

对应失败：source ambiguity。

形式上应明确：

\[
\operatorname{Attributed}(S_{v+1})
\]

关注 successor 产生后是否能解释每个 authoritative field 的来源。

## 8. Characterization boundary

### 8.1 Necessity-like / irredundancy result

对每项 \(d_i\in\mathcal D\)，构造 paired histories：

\[
h_s^{(i)},h_u^{(i)},
\]

满足：

\[
\pi_{\mathcal D-\{d_i\}}
\left(h_s^{(i)}\right)
=
\pi_{\mathcal D-\{d_i\}}
\left(h_u^{(i)}\right),
\]

同时：

\[
O\left(h_s^{(i)}\right)
\neq
O\left(h_u^{(i)}\right).
\]

该结果支持：每个 information class 对其 paired failure family 是 individually irredundant。

它不支持：

- 当前关系 schema 是唯一实现；
- 具体字段名 universal necessary；
- 对所有可能 failure family 的全局最小性。

### 8.2 Sufficiency-like bounded result

完整 \(\mathcal D\) 下，Full contract 应在声明的 failure catalogue 和 bounded Alloy scopes 中：

- 接受声明的合法 histories；
- 拒绝每个 paired unsafe history，或保持 authoritative-state stutter；
- 对成功 admission 构造 complete successor；
- 使每个 authoritative field 具有 complete and unambiguous trace。

允许的主张是：

> The full distinction basis is sufficient to separate the declared failure families in the encoded model and bounded scopes, while each information class is individually irredundant with respect to its paired witness family.

禁止升级为：

- universal sufficiency；
- unbounded proof；
- globally minimal information basis；
- representation-independent unique solution。

## 9. Formal and concrete evidence mapping

论文应新增一张 requirement-to-evidence mapping table：

| Information requirement | Safe/unsafe witness | Alloy support | Concrete support |
|---|---|---|---|
| Candidate context | exact candidate / equal-valued cross-context substitute | field, evidence-identity, evidence-owner, record, authorization-certificate and preexistence ablations | record/field/evidence/certificate substitution catalogue |
| Dual value | preserved Correction / candidate rewrite or wrong committed value | authorization-value ablation plus legal Correction witness | singleton/all-field/mixed Correction lifecycle and immutable candidate checks |
| Freshness | current authorization / superseded authorization | certificate-version and freshness ablations | stale replay, competing confirmation and CAS rejection |
| Successor completeness | complete batch / partial batch effect | transition-bijection ablation and whole-batch framing assertions | failpoints, transaction rollback, exact changed-field and concurrent tests |
| Source attribution | total source map / missing, replaced or duplicate source | P6 source-anchor attack witnesses | source corruption catalogue and reverse-trace validation |

### 9.1 Alloy's role

Alloy 不负责证明 universal information minimality。其角色是：

1. 将五类高层 distinctions 映射到具体 relational encoding；
2. 为删除一个 encoded distinction 后的 observation collapse 提供 bounded witnesses；
3. 在 Full contract 与两个声明 scope 中搜索合法、失败和 invariant-violation instances；
4. 支持 bounded sufficiency-like claim。

推荐解释：

> Each ablation is a bounded witness that removing one encoded distinction makes two operationally different histories admissible under the same reduced observation.

若现有 assertions 不能逐项直接支撑五类 separation，应增加明确命名的 checks；不为了数字或表面规模扩大 scope。

### 9.2 Concrete realization's role

SQLite realization 是该 information basis 的一个 reference realization，而不是唯一实现。它通过：

- canonical candidate certificate；
- separate immutable authorization binding；
- explicit authorized value；
- commit-time principal recheck；
- expected-version CAS；
- exact changed-field validation；
- one atomic batch transaction；
- total value/source snapshot；
- unchanged-field source copy-forward；
- reverse-trace validation；

实现上述五类 distinctions。

## 10. Behavioral Variation, Authority Invariance

### 10.1 Design principle

Agent behavior 可以随 model、provider、prompt 和 repetition 改变，但 authority outcome 应由 host-side admission contract 决定：

\[
BehaviorTrace_{m,p,s,r}
\text{ may vary},
\]

while：

\[
AuthorityOutcome_{m,p,s,r}
=
ContractOutcome_s.
\]

该原则是 empirical validation contribution，不替代 C1/C2。

### 10.2 Behavioral-diversity measurements

benchmark 至少应记录：

- tool-call sequence；
- proposal/verification order；
- retry count；
- unavailable-capability attempt；
- stale/cross-context handling；
- Correction handling；
- scenario completion；
- response/tool-trace diversity across model and prompt cells。

只有观察到实际 behavior-trace differences，才能使用 `behavioral variation`。如果行为没有可测差异，只报告 `cross-model repeated execution`。

### 10.3 Authority-invariance measurements

每个 run 应验证：

- model-facing surface 不暴露 fact-write 或 confirmation capability；
- successful admission 只能由 trusted host path 完成；
- stale、cross-context、mutated-evidence 和 unavailable-capability attempts fail closed；
- rejection 前后 authoritative-state digest 完全相同；
- Correction 保留 candidate value，同时只 commit explicit authorized value；
- source and release hashes 在声明边界中保持稳定。

零 violation 只支持已执行 cells 下的 empirical invariance，不支持对所有模型、prompts 或 adversaries 的 universal guarantee。

## 11. Final contribution hierarchy

### C1 — Correction-aware authoritative-state admission

定义从 untrusted persisted candidate 和 candidate-bound human authorization 到 complete authoritative successor 的软件边界。核心语义是 candidate retention、dual-value attribution 与 authority/origin separation。

### C2 — Conditional failure-distinguishability characterization

刻画五类 failure family 所需的 information distinctions，给出 paired-history irredundancy argument，并界定 full distinction basis 的 bounded sufficiency。

### C3 — Relational and transactional realization

用 Alloy ablations 和 Full checks 支撑 encoded distinction loss/full separation，再由 transactional SQLite realization、formal–concrete projection 和 executable catalogue 实现与检查这些 distinctions。

### C4 — Behavioral validation under authority invariance

在跨模型、跨 prompt、重复 agent executions 中同时测量 behavioral diversity 与 contract-governed authority outcome，验证有限实验范围内的 behavioral variation/authority invariance principle。

C1--C4 不是工作内容并列列表，而是一条依赖链：C1 定义对象，C2 给出结构性知识，C3 实现并验证该知识，C4 检验其在 agent behavior 变化下的系统意义。

## 12. Recommended core wording

### 12.1 Primary novelty statement

> We identify correction-aware authoritative-state admission as the software relation that maps an untrusted persisted candidate and a candidate-bound human authorization to a complete authoritative successor while retaining the candidate as non-authoritative historical evidence. We characterize the observable information distinctions required to separate candidate substitution, correction erasure, stale replay, partial-successor, and source-ambiguous histories.

### 12.2 Characterization statement

> Under the declared observation and failure model, the full distinction basis is sufficient to separate the five encoded failure families in the bounded formal scopes, while each information class is individually irredundant with respect to its paired witness family.

### 12.3 Mutation contrast

> Unlike authorized mutation of an already authoritative object, correction-aware admission preserves the machine candidate as non-authoritative evidence and may commit a distinct human-authorized value.

### 12.4 Alloy statement

> Each ablation provides a bounded witness that removing one encoded distinction makes operationally different histories indistinguishable to the reduced admission relation; the Full checks establish only bounded separation within the declared scopes.

### 12.5 Behavioral statement

> Agent behavior may vary across models, prompts, and repetitions, while authoritative-state change remains determined by the host-side contract within the executed scenarios.

## 13. Claim whitelist and blacklist

### 13.1 Allowed claims

- identify and characterize a correction-aware authoritative-state admission boundary；
- dual-value attribution separates machine proposal from human-authorized value；
- five information classes are individually irredundant with respect to declared paired failures；
- the full basis is sufficient only over the declared catalogue, encoded model and bounded scopes；
- Auto-Decte is one transactional realization, not the unique schema；
- Alloy provides bounded witnesses and bounded separation evidence；
- repeated agent runs provide empirical, scenario-bounded authority-invariance evidence；
- closest public works address neighboring mutation, source-validation, governance, recovery or supersession dimensions。

### 13.2 Forbidden or unsupported claims

- first admission mechanism；
- first AI update transaction boundary；
- first authorized mutation or provenance-preserving history；
- universal necessity of `candidate_id`、`expectedVersion` or any exact column；
- globally minimal or unique schema；
- unbounded formal proof；
- universal authority invariance across agents；
- production security, authenticated human identity or semantic truth；
- treating arXiv/CoRR status as a formal CCF A/B venue acceptance。

## 14. Manuscript restructuring plan

### Abstract

按以下顺序压缩：

1. proposal-to-authority problem；
2. correction-aware admission abstraction；
3. five-family conditional characterization；
4. relational/transactional realization；
5. strongest bounded formal and concrete evidence；
6. behavioral validation result，仅在 final benchmark 完成后写入。

### Introduction

- 不以 seven-mechanism conjunction 开篇；
- 先区分 candidate origin、authorization authority 和 committed value；
- 引出 \(x_c\neq x_a\)；
- 把旧 four-failure story 拆成 five failure families；
- 用 C1→C4 贡献链替换当前 evidence-layer list。

### Related Work

- 分别加入并比较 MutMem、MemTxn、SuperLocalMemory 4.0、Stale Constraints 和现有 MemTX；
- 使用 relation-level comparison，而非空白格推断 competitor 缺陷；
- 对未展示关系统一写 `not shown in the reviewed public artifact`；
- 不以对方是否正式录用决定 novelty relevance；public disclosure 即构成 collision risk。

### Problem and Contract

- 正式定义 history、information class、\(\pi_I\) 和 \(O(h)\)；
- 正式定义 admission relation；
- 增加 dual-value attribution semantics；
- 将 partial successor 与 source ambiguity 拆开；
- 给出五个 requirements/lemmas；
- 明确 information necessity 与 schema necessity 的差别。

### Relational Analysis

- 按五项 requirements 重新组织 11 个 ablations、P6 attacks 和 Full assertions；
- 增加 requirement-to-Alloy mapping；
- 明确 necessity-like witness 与 bounded sufficiency-like checks；
- 保留有限 scope 和非唯一编码边界。

### Evaluation and Results

- RQ1：Full distinction basis 的 bounded legal/failure separation；
- RQ2：per-information-class irredundancy witnesses；
- RQ3：formal–concrete projection；
- RQ4：concrete fail-closed catalogue；
- RQ5：dual-value Correction lifecycle；
- RQ6：cost；
- RQ7：restricted harness boundary；
- RQ8：behavioral diversity and authority invariance，仅在 repeated benchmark 完成并冻结后启用。

### Discussion

- 解释 information basis 可由多种 representation 实现；
- 区分 authorization integrity 与 truth；
- 区分 behavioral invariance、agent robustness 和 production security；
- 明确 characterization 只覆盖声明的 failure model。

### Conclusion

按 C1→C4 顺序收束，不以“组合了多种机制”结尾。

## 15. Acceptance criteria for the novelty reconstruction

只有满足以下条件，才可以声称 novelty 已从系统组合提升为 abstraction + characterization：

- [ ] 定义 authority-relevant history \(h\)；
- [ ] 定义 observation projection \(\pi_I\)；
- [ ] 定义三元 outcome \(O(h)\)；
- [ ] 定义 information classes \(\mathcal D\)；
- [ ] 定义 correction-aware admission relation；
- [ ] 定义 dual-value attribution semantics；
- [ ] 将 failure taxonomy 拆成五类；
- [ ] 为五类 failure 提供 safe/unsafe paired construction；
- [ ] 建立 information requirement ↔ Alloy relation/check mapping；
- [ ] 明确 bounded sufficiency 的检查边界；
- [ ] 修改 title、abstract、RQ、contributions、Related Work 和 conclusion；
- [ ] 修复 MemTX 与 MemTxn 的文献区分；
- [ ] repeated benchmark 完成后测量真实 behavioral diversity；
- [ ] authority-invariance result 与 frozen raw evidence 对齐；
- [ ] 所有新增 claim 通过 citation、artifact 和 code-paper consistency audit。

如果只替换术语而未完成以上定义与映射，论文仍然只是机制组合型系统稿，不能使用 characterization-level novelty claim。

## 16. Self-review

本设计没有把 admission 名称本身作为 novelty，没有声称唯一 schema、universal necessity、unbounded proof 或 universal model invariance。它区分了信息类别与具体字段，区分了 candidate origin 与 committed-value authority，区分了 successor completeness 与 source attribution，并为 necessity-like irredundancy 和 bounded sufficiency-like evidence分别规定了主张边界。

文档不改变任何现有实验结果、denominator、hash、citation key 或 manuscript evidence identity。Repeated cross-provider benchmark 在完成和冻结前只作为 evaluation design，不得提前写成论文结果。
