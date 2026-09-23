# Background and related work

原字数：940；压缩后：794；压缩比例：15.53%。

口径：正文叙述及 contribution 文本；不计标题、引文/交叉引用标记、公式、表格、图注和参考文献。

**是否影响 scientific claim：No。** 这是逐段编辑核对结论；静态保护检查见总报告，不替代重新验证科研结果。

## P01 — COMPRESS

理由：删除交叉领域的泛化开场，保留比较框架、截止日期与发表状态边界。

原段落：

```latex
Authoritative-state admission sits at the intersection of agent-state governance, authorization, transactional provenance, and formal--concrete checking. We organize prior work by the software boundary it governs: memory activation and update, authorization and effects, provenance, or executable validation. The comparison includes public preprints available through 3 September 2026, with publication status recorded separately.
```

修改后的英文：

```latex
We compare prior work by its governed boundary: memory activation and update, authorization and effects, provenance, or executable validation. The comparison includes public preprints through 3 September 2026, with publication status recorded separately.
```

## P02 — COMPRESS

理由：压缩邻近工作介绍，保留全部比较维度和最近邻定位。

原段落：

```latex
Continuity Kernel is the closest general activation-boundary neighbor. It separates off-commit candidate evaluation from a short transaction that revalidates ownership, predecessor authority, freshness, and effect uniqueness before atomically installing a complete accepted unit \citep{he2026continuity}.
```

修改后的英文：

```latex
Continuity Kernel separates off-commit candidate evaluation from a short transaction that revalidates ownership, predecessor authority, freshness, and effect uniqueness before installing a complete accepted unit atomically \citep{he2026continuity}. It is the closest general activation-boundary neighbor.
```

## P03 — COMPRESS

理由：压缩重复的冲突处理说明，保留状态类型与实际比较范围。

原段落：

```latex
LatticeMind moves claim conflict handling into write-time structured memory. It represents proposed, confirmed, contested, and superseded items; reconciles slot-scoped claims using symbolic checks and selective model assistance; and retains losing claims with provenance \citep{zhou2026latticemind}. Its reviewed artifact focuses on conflict-aware claim selection and supersession.
```

修改后的英文：

```latex
LatticeMind represents proposed, confirmed, contested, and superseded claims in write-time structured memory. It combines symbolic checks with selective model assistance for slot-scoped reconciliation and retains losing claims with provenance \citep{zhou2026latticemind}. Its reviewed artifact concerns claim selection and supersession.
```

## P04 — COMPRESS

理由：精简两项工作的共同结论，保留各自机制与引文。

原段落：

```latex
When Memory Becomes Authority identifies \emph{authority collapse}: consolidation may preserve claim content while erasing source constraints governing later reuse \citep{zhan2026authoritycollapse}. Correct Is Not Governed similarly separates correct outcomes from governed execution through versioned authority/fact sets and dependency provenance \citep{salas2026governed}. These works establish that retaining content or reaching the right answer does not by itself preserve authority.
```

修改后的英文：

```latex
When Memory Becomes Authority identifies \emph{authority collapse}: consolidation preserves content but may erase constraints on source reuse \citep{zhan2026authoritycollapse}. Correct Is Not Governed distinguishes correct outcomes from governed execution using versioned authority/fact sets and dependency provenance \citep{salas2026governed}. Both separate retained content or correct answers from retained authority.
```

## P05 — COMPRESS

理由：删去总结中的同义重复，维持各系统名称及能力归属。

原段落：

```latex
MutMem cryptographically authorizes mutation of an already persistent memory property, binding old/new retrieval weights, signer epoch, provenance, and a no-fork predecessor \citep{saidi2026mutmem}. MemTX stages and validates belief writes, while the distinct MemTxn system places source-supported updates, conflict-conditioned visibility, and complete-state recovery behind an answer-model-external transaction boundary \citep{li2026memtx,cui2026memtxn}. SuperLocalMemory 4.0 adds governed admission, generation fencing, transaction verification, compensation, erasure ownership, and completion manifests \citep{bhardwaj2026superlocalmemory}. Together, these systems establish authorized mutation, update transactions, governed admission, source validation, and recovery as adjacent foundations.
```

修改后的英文：

```latex
MutMem authorizes persistent-property mutation by binding old/new retrieval weights, signer epoch, provenance, and a no-fork predecessor cryptographically \citep{saidi2026mutmem}. MemTX stages and validates belief writes; the distinct MemTxn system places source-supported updates, conflict-conditioned visibility, and complete-state recovery behind an answer-model-external transaction boundary \citep{li2026memtx,cui2026memtxn}. SuperLocalMemory 4.0 adds governed admission, generation fencing, transaction verification, compensation, erasure ownership, and completion manifests \citep{bhardwaj2026superlocalmemory}. These provide adjacent mutation, transaction, source-validation, and recovery foundations.
```

## P06 — COMPRESS

理由：压缩互补边界说明，保留该工作的输入假设与下游问题。

原段落：

```latex
Stored Is Not Supported separates persisted availability from warranted assertion through typed provenance, authorized projections, and a mediated release gate \citep{he2026stored}. It takes an authenticated accepted-state head as input and treats lower-level atomic storage as an assumption. The boundaries are complementary: valid admission alone does not establish that a later statement is supported or authorized for disclosure.
```

修改后的英文：

```latex
Stored Is Not Supported distinguishes stored availability from warranted assertion through typed provenance, authorized projections, and a mediated release gate \citep{he2026stored}. It assumes authenticated accepted state and atomic storage. This complementary boundary concerns whether admitted information supports a later statement and its disclosure.
```

## P07 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
\Cref{tab:nearest-neighbors} compares reported admission relations. Atomicity and freshness alone do not bind a human-authorized value to its machine proposal or preserve unchanged-field sources. An unreported relation is not a demonstrated defect or an inability to extend the compared system.
```

## P08 — COMPRESS

理由：缩短经验动机，保留验证预算和研究边界。

原段落：

```latex
When Stale Constraints Go Unchecked shows empirically that immutable provenance can remain reachable while an agent fails to revisit a superseded constraint under a verification budget \citep{nakayashiki2026staleconstraints}. It motivates the freshness distinction used in our declared admission model, but does not itself define a candidate-bound authoritative commit relation.
```

修改后的英文：

```latex
When Stale Constraints Go Unchecked finds that agents under a verification budget may overlook superseded constraints despite reachable immutable provenance \citep{nakayashiki2026staleconstraints}. It motivates our freshness distinction rather than defining a candidate-bound commit relation.
```

## P09 — COMPRESS

理由：压缩背景定义，保留每项技术的绑定对象和草案状态。

原段落：

```latex
Proof-carrying authentication places a machine-checkable proof on the requester and checks it at the server with a minimal trusted computing base \citep{appel1999pca}. DPoP sender-constrains OAuth tokens to a proof-of-possession key and the presenting HTTP request \citep{fett2023dpop}. The active OAuth Transaction Tokens draft propagates signed authorization and request context through one call chain, whereas the active individual SPT-Txn draft binds a short-lived token to a declared action and resource \citep{tulshibagwale2026txtokens,coetzee2026spttxn}. Both Internet-Drafts are works in progress. CapLease additionally treats authorization consumption as durable state for replay-resistant agent actions \citep{xu2026caplease}.
```

修改后的英文：

```latex
Proof-carrying authentication checks requester-supplied proofs at a server with a minimal trusted computing base \citep{appel1999pca}. DPoP binds OAuth tokens to a proof-of-possession key and presenting request \citep{fett2023dpop}. The OAuth Transaction Tokens draft propagates signed authorization and request context through a call chain; the individual SPT-Txn draft binds a short-lived token to an action and resource \citep{tulshibagwale2026txtokens,coetzee2026spttxn}. Both drafts remain works in progress. CapLease makes authorization consumption durable for replay-resistant agent actions \citep{xu2026caplease}.
```

## P10 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
PCE separates proposed traces, certification, and execution; DTF derives execution authority from a structured intent, justification proof, and approval record; EBTE checks typed action claims against server-held intent, policy, payload, tool, risk, provenance, and freshness facts; and CAP+PCL composes provenance-bound context attestation with deterministic policy authorization \citep{liu2026pce,he2026dtf,zhu2026ebte,chitan2026cappcl}. CAGE shows that categorical source-binding uncertainty and numerical uncertainty in typed returns cannot safely be certified in isolation before authorizing a downstream action \citep{delattre2026cage}.
```

## P11 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
ToolGate checks preconditions and postconditions before symbolic-state updates; CapChain governs field/value updates through scoped capabilities and the current provenance predecessor root \citep{liu2026toolgate,choong2026capchain}.
```

## P12 — COMPRESS

理由：压缩衔接句，保留比较来源和实现接口。

原段落：

```latex
Agent harnesses provide the extension boundary through which a model can reach such services. A source-level comparison of deepagents, pi, and DeepSeek Harness reports explicit extension seams as a convergent feature \citep{dai2026harnesses}; the pinned DeepSeek Harness architecture specifically registers model-facing capabilities on \code{ctx.tools} and routes execution through a guarded runtime pipeline \citep{deepseek2026architecture}.
```

修改后的英文：

```latex
Agent harnesses expose service-extension boundaries. A comparison of deepagents, pi, and DeepSeek Harness identifies explicit extension seams as a convergent feature \citep{dai2026harnesses}. The pinned DeepSeek Harness registers model-facing capabilities on \code{ctx.tools} and uses a guarded execution pipeline \citep{deepseek2026architecture}.
```

## P13 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
Indirect prompt injection can cause integrated models to interpret untrusted content as instructions \citep{greshake2023indirect}. AgentDojo separates task utility from security over a dynamic tool-agent environment \citep{debenedetti2024agentdojo}.
```

## P14 — COMPRESS

理由：减少溯源领域的教科书背景，保留文献覆盖和关系种类。

原段落：

```latex
Why- and where-provenance distinguish why an output exists from where its values originated, and later surveys systematize why-, how-, and where-provenance \citep{buneman2001whywhere,cheney2009provenance}. The Open Provenance Model and W3C PROV provide technology-independent vocabularies for causal histories, entities, activities, agents, derivations, and responsibility \citep{moreau2011opm,moreau2013provdm}. Transaction reenactment and multi-version provenance reconstruct how database states arise from update histories \citep{arab2016rcsi,arab2018reenactment,arab2019thesis}.
```

修改后的英文：

```latex
Why-, how-, and where-provenance describe output justification, derivation, and value origins \citep{buneman2001whywhere,cheney2009provenance}. The Open Provenance Model and W3C PROV represent causal histories, entities, activities, agents, derivations, and responsibility \citep{moreau2011opm,moreau2013provdm}. Transaction reenactment and multi-version provenance reconstruct database update histories \citep{arab2016rcsi,arab2018reenactment,arab2019thesis}.
```

## P15 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
These provenance vocabularies can represent the relevant relationships; adopting a vocabulary alone does not specify when admission must enforce candidate binding, authorized-value equality, or exact source copy-forward.
```

## P16 — COMPRESS

理由：压缩方法背景，保留有界性与投影相关先例。

原段落：

```latex
Alloy searches finite relational scopes through SAT-based model finding \citep{jackson2002alloy,torlak2007kodkod}. TestEra maps Alloy-generated inputs to Java executions and abstracts their outputs back to Alloy; bounded program checkers similarly translate annotated programs into finite relational or propositional searches \citep{marinov2001testera,dennis2006sat,galeotti2013taco}.
```

修改后的英文：

```latex
Alloy checks finite relational scopes by SAT-based model finding \citep{jackson2002alloy,torlak2007kodkod}. TestEra connects Alloy-generated inputs, Java execution, and abstraction back to Alloy; bounded program checkers translate annotated programs into finite relational or propositional searches \citep{marinov2001testera,dennis2006sat,galeotti2013taco}.
```

## P17 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
Mutation analysis asks whether checks distinguish deliberately altered constraints \citep{sullivan2017alloymutation,jia2011mutation,just2014mutants}.
```

## P18 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
Property-based state machines and controlled schedule exploration reveal history-dependent and concurrent failures that examples may miss \citep{claessen2000quickcheck,claessen2009pulse,musuvathi2008chess}. Elle illustrates the value of an independent checker over observed histories \citep{kingsbury2020elle}.
```

## P19 — COMPRESS

理由：合并复现背景的通用要求，保留所有原有引文及主要归属。

原段落：

```latex
Collberg and Proebsting distinguish disclosed source from code that actually builds and executes \citep{collberg2016repeatability}. Artifact-evaluation and experimental-method work likewise emphasize documented, consistent, complete, and executable packages, and show that configuration and repetition can alter empirical conclusions \citep{hermann2020artifacts,klees2018fuzz,kessel2024openscience,liu2024artifacts}. JSS studies connecting formal models, implementations, and empirical assessment motivate the article's theory--implementation--evidence structure \citep{stachtiari2018correctness,alam2021dbverify,song2023continuous,coppa2024concolic}.
```

修改后的英文：

```latex
Reproducibility requires more than source disclosure: artifacts must build, execute, and retain consistent evidence \citep{collberg2016repeatability,hermann2020artifacts,kessel2024openscience,liu2024artifacts}. Configuration and repetition can change empirical conclusions \citep{klees2018fuzz}. JSS studies connecting formal models, implementations, and empirical assessment motivate our theory--implementation--evidence structure \citep{stachtiari2018correctness,alam2021dbverify,song2023continuous,coppa2024concolic}.
```

## P20 — COMPRESS

理由：保留关系层贡献与公平比较限定，删除重复过渡句。

原段落：

```latex
These foundations supply adjacent mechanisms. \system{} examines their joint correction-aware obligation: bind an exact candidate to a separately attributable human-authorized value, construct a complete successor, and retain every field's source. The question is whether evaluated controls entail this relation, not whether they can be extended to represent it. Bounded checks, persisted-state projections, and host-separated integration examine different parts of that obligation.
```

修改后的英文：

```latex
We examine the joint correction-aware obligation: bind an exact candidate to a separately attributable human-authorized value, construct a complete successor, and retain every field's source. Evaluated controls are tested for whether they entail this relation, not whether they could be extended to represent it. Bounded checks, persisted-state projections, and host-separated integration address distinct parts of that obligation.
```

重复位置与主叙述位置：Introduction C1–C3; Contract owns definitions, this paragraph owns literature positioning.

公式、表格、图及其图注统一为 **KEEP**：保持数学关系、结果和解释不变。
