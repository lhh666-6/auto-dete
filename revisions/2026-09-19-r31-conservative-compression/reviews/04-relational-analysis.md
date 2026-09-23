# Bounded relational characterization

原字数：643；压缩后：517；压缩比例：19.6%。

口径：正文叙述及 contribution 文本；不计标题、引文/交叉引用标记、公式、表格、图注和参考文献。

**是否影响 scientific claim：No。** 这是逐段编辑核对结论；静态保护检查见总报告，不替代重新验证科研结果。

## P01 — COMPRESS

理由：压缩枚举式背景，不改变状态和全域映射定义。

原段落：

```latex
The Alloy model represents records, authoritative fields, linearly ordered versions, evidence content and locators, candidates, certificates and primitive identities, principals, authorizations, transitions, and states. A state maps each committed record/field pair to at most one value and one source transition. Once a record has an authoritative snapshot, both maps cover exactly its declared field domain.
```

修改后的英文：

```latex
The Alloy model represents records, authoritative fields, ordered versions, evidence content/locators, candidates, certificates/identities, principals, authorizations, transitions, and states. Each state maps a committed record/field pair to at most one value and source transition. Once an authoritative snapshot exists, both maps cover exactly the record's declared field domain.
```

## P02 — COMPRESS

理由：缩短事件类型介绍，保留所有框架条件。

原段落：

```latex
Three event families define the bounded histories. A \code{MachineEvent} may extend candidate, certificate, and evidence sets but frames authoritative values, sources, versions, transitions, and authorizations, encoding P0. A \code{BatchAdmissionEvent} contains a nonempty item set sharing an event envelope. A \code{TamperEvent} freezes values and source pointers while changing only the transition set, giving P6 a deliberately narrow corruption boundary.
```

修改后的英文：

```latex
Three event families define bounded histories. \code{MachineEvent} may extend candidates, certificates, and evidence but frames authoritative values, sources, versions, transitions, and authorizations (P0). \code{BatchAdmissionEvent} contains a nonempty item set sharing an envelope. \code{TamperEvent} changes only the transition set while freezing values and source pointers, defining P6's narrow corruption boundary.
```

## P03 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
The base effect advances one record version and applies item values and sources while intentionally leaving transition structure underconstrained. Full supplies unique item fields; initial or later complete-snapshot shape; preexisting certificate and evidence; record, field, evidence-identity, evidence-owner, certificate-version, freshness, authorization-certificate, principal, and authorization-value bindings; and an exact item--transition bijection. Keeping these conjuncts separate permits one encoded distinction to be removed without silently changing the others.
```

## P04 — COMPRESS

理由：简化高层类与低层约束的映射说明。

原段落：

```latex
Table~\ref{tab:distinction-evidence} connects the representation-independent classes of \cref{eq:distinction-basis} to the concrete relational operators and executable evidence. Several low-level conjuncts may encode one high-level class; the eleven ablations are therefore not eleven separate novelty claims.
```

修改后的英文：

```latex
Table~\ref{tab:distinction-evidence} maps the representation-independent classes in \cref{eq:distinction-basis} to relational operators and executable evidence. Several conjuncts can encode one class; eleven ablations therefore do not imply eleven novelty claims.
```

## P05 — COMPRESS

理由：集中区分敏感性测试与观察层论证，保留双项构造。

原段落：

```latex
Each ablation pair contains at least two items: one violates only the selected conjunct and another remains Full-valid. The same attempted item set is admitted by the reduced relation and rejected with authoritative-state stutter by Full. This tests the sensitivity of the selected relational conjunct. The observation-level irredundancy argument is the separate paired-history construction in \cref{sec:contract}.
```

修改后的英文：

```latex
Each ablation pair contains at least two items: one violates only the selected conjunct and another is Full-valid. The reduced relation admits the item set; Full rejects it with authoritative-state stutter. This tests conjunct sensitivity, separately from the observation-level irredundancy construction in \cref{sec:contract}.
```

## P06 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
Six legal-witness commands cover multi-field Accept, Correction, mixed Accept/Correction, same-value admission, initial snapshot, and singleton admission. Eleven paired ablations remove the conjuncts mapped in \cref{tab:distinction-evidence}. Principal membership remains fixed; the unused \code{ABL\_7} marker is excluded because host identity trust is an external assumption.
```

## P07 — COMPRESS

理由：删除与下一段重复的 assertion 列表，保留三种攻击和总数。

原段落：

```latex
Three source-attack commands start from a legal Full prefix and then remove a source anchor, replace it with another transition atom, or add a duplicate source-version transition; each requires the trace to become incomplete. Fourteen assertions per scope cover invariant preservation, P0/P1/P3/P4/P5 regressions, whole-batch effect and rejection framing, bidirectional singleton correspondence, Full rejection of an ablated attempt, P6 incompleteness, and positive trace completeness under an explicit well-formed-pre-state condition.
```

修改后的英文：

```latex
Three source-attack commands follow a legal Full prefix by removing a source anchor, replacing it with another transition atom, or adding a duplicate source-version transition. Each requires an incomplete trace. Fourteen assertions per scope cover the checks grouped below.
```

重复位置与主叙述位置：Following paragraph is the single detailed nine-plus-five assertion inventory.

## P08 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
Nine assertions guard definitions and immediate consequences: P0, P1, P3, P4, P5, whole-batch effects, rejection framing, and the two P6 checks. Five others check state-invariant preservation, two singleton correspondences, Full rejection of an ablated attempt, and positive trace completeness under a well-formed pre-state.
```

## P09 — COMPRESS

理由：压缩正向断言的元解释，完整保留前提、反例敏感性、见证及单步限制。

原段落：

```latex
The positive assertion requires a trace-complete predecessor and no stray transition to the successor version; otherwise the permissive base effect allows a legal Full admission whose post-state fails \code{traceComplete}. Concrete enforcement uses predecessor-prefix validation, per-record transition uniqueness, and CAS with in-transaction revalidation. Removing the post-state certificate binding changes UNSAT to SAT (\code{evidence/r27-trace-mutation/}). The assertion covers admitted fields in one step, not arbitrary histories or every carried-forward field. Both profiles witness its precondition through \code{SAT_TRACE_wellformed_pre_initial} and \code{SAT_TRACE_wellformed_pre_carryforward}; the latter has a non-vacuously complete predecessor trace. Precondition reachability, bounded absence of counterexamples, and sensitivity to a removed conjunct are distinct results. Fourteen UNSAT commands therefore do not constitute fourteen independent proofs.
```

修改后的英文：

```latex
The positive assertion requires a trace-complete predecessor and no stray transition to the successor version; otherwise Full admission may fail \code{traceComplete}. Concrete enforcement combines predecessor-prefix validation, per-record transition uniqueness, and CAS with in-transaction revalidation. Removing post-state certificate binding changes UNSAT to SAT (\code{evidence/r27-trace-mutation/}). The assertion covers admitted fields in one step, not arbitrary histories or every carried-forward field. Both profiles witness its precondition through \code{SAT_TRACE_wellformed_pre_initial} and \code{SAT_TRACE_wellformed_pre_carryforward}; the latter has a non-vacuously complete predecessor trace. Reachability, bounded counterexample absence, and mutation sensitivity are distinct: fourteen UNSAT commands are not fourteen independent proofs.
```

## P10 — MOVE-SUPP

理由：将逐域上界移至补充，正文保留有限范围及第二范围增大的解释。

原段落：

```latex
The S1 profile bounds principal structural domains at two records, three fields, six versions, up to six admission items/transitions for most commands, and four states/events. S2 increases representative bounds to three records, four fields, eight versions, up to eight admission items/transitions, and five states/events. Individual commands adjust Value, Evidence, or Transition bounds when a witness needs an extra atom. The artifact contains the executable scopes; this summary is not a replacement for them.
```

正文保留版本：

```latex
S1 and S2 use finite, command-specific bounds, with S2 increasing representative structural domains. Supplement S4 retains both scope vectors and their exceptions; the artifact supplies the executable scopes.
```

迁移范围：原段落全文，逐字保留于 Supplement S4 / Alloy scope profiles。

重复位置与主叙述位置：Artifact executable scopes remain authoritative.

## P11 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
An UNSAT assertion means that the Analyzer found no counterexample within the encoded command scope. A SAT run means that it found the requested witness \citep{jackson2002alloy,torlak2007kodkod}. Singleton contract/effect checks additionally guard the batch lift against silently changing the historical one-item semantics.
```

公式、表格、图及其图注统一为 **KEEP**：保持数学关系、结果和解释不变。
