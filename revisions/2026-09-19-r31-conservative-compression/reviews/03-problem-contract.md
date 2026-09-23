# Authoritative-state admission contract

原字数：1789；压缩后：1591；压缩比例：11.07%。

口径：正文叙述及 contribution 文本；不计标题、引文/交叉引用标记、公式、表格、图注和参考文献。

**是否影响 scientific claim：No。** 这是逐段编辑核对结论；静态保护检查见总报告，不替代重新验证科研结果。

## P01 — COMPRESS

理由：以正向语句保留候选、授权和提交值的三个角色，删除同义重复。

原段落：

```latex
Admission does not make the candidate itself authoritative. It transforms a candidate-bound authorization into an authoritative successor while retaining the candidate as non-authoritative historical evidence. Proposal origin, value authority, and committed value are therefore distinct semantic roles.
```

修改后的英文：

```latex
Admission converts candidate-bound authorization into an authoritative successor while retaining the candidate as non-authoritative historical evidence. Proposal origin, value authority, and committed value remain distinct semantic roles.
```

## P02 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
Let $r$ be a record with a nonempty authoritative field set $F_r$. A committed version $v$ contains a total value map $V_v:F_r\rightarrow X$ and a total source map $S_v:F_r\rightarrow T$, where $T$ is the set of durable fact transitions. A machine candidate for field $f$ is
\begin{equation}
c=\langle r,f,e,v_{\mathrm{exp}},x_c,p,c_{\mathrm{id}}\rangle,
\label{eq:candidate}
\end{equation}
where $e$ is persisted evidence, $v_{\mathrm{exp}}$ is the expected current version, $x_c$ is the machine proposal, $p$ identifies its producer, and $c_{\mathrm{id}}$ is an identity over the modeled candidate content.
```

## P03 — COMPRESS

理由：压缩抽象到实现的说明，完整保留身份组成和碰撞假设。

原段落：

```latex
where $H$ is SHA-256 and $L$ is a versioned canonical locator containing the owner record, related field, normalized storage-relative URI $u$, and optional crop identity $\kappa$. The Alloy model abstracts content and locator as primitive domains. Its \code{certIdentityFacts} assumes unique certificate identities over the modeled certificate objects, excluding identity collisions from the checked scopes. Relating this abstraction to the implementation requires collision resistance of the deployed digest and integrity of the canonicalization and evidence store; it is not a proof or claim that SHA-256 is mathematically injective.
```

修改后的英文：

```latex
where $H$ is SHA-256 and $L$ is a versioned canonical locator containing owner record, related field, normalized storage-relative URI $u$, and optional crop identity $\kappa$. Alloy abstracts content and locator as primitive domains. Its \code{certIdentityFacts} assumes unique identities over modeled certificate objects, excluding collisions within checked scopes. The implementation correspondence requires digest collision resistance and canonicalization/evidence-store integrity; it does not assume mathematical injectivity of SHA-256.
```

## P04 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
An attributable authorization is
\begin{equation}
a=\langle c_{\mathrm{id}},x_a,q\rangle,
\label{eq:authorization}
\end{equation}
where $q$ is an authorized human principal and $x_a$ is the value explicitly permitted to enter the record. The dual-value semantics are
\begin{align}
\operatorname{proposal}(c)&=x_c, &
\operatorname{authorize}(a)&=x_a,\nonumber\\
\operatorname{commit}(S_{v+1},f)&=x_a, &
\operatorname{origin}(S_{v+1},f)&=c.
\label{eq:dual-value}
\end{align}
Accept has $x_c=x_a$. Correction has $x_c\neq x_a$; the candidate remains unchanged and the committed value derives its authority from $a$.
```

## P05 — COMPRESS

理由：压缩规范相等关系的动机，保留定义、反例、全部适用层和修复指引。

原段落：

```latex
Two values are identical throughout the contract only when their canonical JSON serializations agree. Write $x\eqc y$ when the sorted-key, whitespace-minimal JSON forms of $x$ and $y$ are equal, and $x\neqc y$ otherwise. Python equality would identify $2$ with $2.0$ and $1$ with \code{true}; the contract does not, because a successor whose serialized value changes must obtain a new transition and source even when the two values compare equal in the host language. The changed-field domain, the admission planner, transition-value checks, reverse-trace validation, the independent database oracle, and the formal projection use this single relation; \cref{sec:conformance} reports the regression that closed a cross-layer disagreement in an earlier build.
```

修改后的英文：

```latex
The contract equates values only when their canonical JSON serializations agree: $x\eqc y$ denotes equal sorted-key, whitespace-minimal forms, and $x\neqc y$ denotes unequal forms. Unlike Python equality, this distinguishes $2$ from $2.0$ and $1$ from \code{true}: a changed serialization requires a new transition and source. The changed-field domain, planner, transition-value checks, reverse trace, independent database oracle, and formal projection share this relation. \Cref{sec:conformance} reports the regression repairing their earlier disagreement.
```

## P06 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
An authority-relevant history is
\begin{equation}
h=S_0\xrightarrow{e_1}S_1\xrightarrow{e_2}\cdots\xrightarrow{e_n}S_n,
\end{equation}
where events may persist evidence or candidates, record review and authorization, attempt admission, commit or stutter, and reconstruct a reverse trace. The abstraction describes semantic information rather than requiring particular table or column names.
```

## P07 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
We group the observable distinctions into
\begin{equation}
\mathcal D=\{D_C,D_V,D_F,D_B,D_S\},
\label{eq:distinction-basis}
\end{equation}
where $D_C$ is candidate identity and context, $D_V$ is dual-value attribution, $D_F$ is freshness, $D_B$ is batch/successor completeness, and $D_S$ is total source attribution. For $I\subseteq\mathcal D$, $\pi_I(h)$ retains only the information classes in $I$. Candidate identity may be implemented by a certificate, stable handle, or another equivalence class, provided it does not collapse to value equality. Freshness may likewise use a version, state hash, epoch, or comparable discriminator.
```

## P08 — COMPRESS

理由：精简物理表示解释，保留观察投影的关键不泄露条件。

原段落：

```latex
The functions are logical projections, not claims that a database must store five physically separate objects. A certificate can co-locate several classes. In a projection, however, a content address is treated as an opaque equality-preserving handle: its preimage is not available as a side channel. This prevents a nominally omitted value or version from being recovered merely because the concrete certificate hash covers it. Table~\ref{tab:observation-functions} defines what each function exposes and deliberately hides.
```

修改后的英文：

```latex
These logical projections permit several classes in one physical certificate. They treat content addresses as opaque equality-preserving handles, with no preimage side channel. Thus a concrete hash cannot expose an omitted value or version through its covered content. Table~\ref{tab:observation-functions} specifies each function's exposed and hidden information.
```

## P09 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
The full-history authority-outcome label is
\begin{equation}
O(h)=\langle status,successor,trace\rangle,
\label{eq:outcome}
\end{equation}
where $status$ is admissible, inadmissible, or failed/stuttering; $successor$ classifies the authoritative post-state or its absence; and $trace$ is complete, incomplete, ambiguous, or unavailable. This is the normative label assigned from the full history, not an additional input available to a mechanism restricted to $\pi_I$. A binary accept/reject label is insufficient because value-identical successors may differ in source completeness.
```

## P10 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
An observation set $I$ fails to distinguish a failure family when there exist a safe history $h_s$ and unsafe history $h_u$ such that
\begin{equation}
O(h_s)\neq O(h_u)
\quad\land\quad
\pi_I(h_s)=\pi_I(h_u).
\label{eq:indistinguishable}
\end{equation}
Any admission decision based only on that reduced observation cannot separate the pair.
```

## P11 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
For the executable construction below, each finite history is represented by the complete tuple
\begin{equation}
\widehat h=\langle r,C,A,B,v_{\mathrm{exp}},v_{\mathrm{obs}},
F_{\mathrm{decl}},K,V_v,V_{v'},S_v,S_{v'},T\rangle,
\label{eq:witness-history}
\end{equation}
containing the target, candidate and authorization registries, batch references, expected and observed pre-versions, declared fields, a commit sequence $K$, endpoint value and source maps, and a registry $T$ of source-transition identifiers, fields, and values. Each commit step records a distinct successor identity and complete before/after value maps. The domain predicate checks unique candidate and authorization keys, resolvable batch references, schema-valid fields, total value maps, and a connected commit sequence from $V_v$ to $V_{v'}$. Its committed effect domain is the union of the steps' actual value-change domains; its successor count is $|K|$. Neither is an independently assigned witness attribute.
```

## P12 — COMPRESS

理由：压缩来源观察的说明，保留所有暴露项、排除项和与 P6 的边界。

原段落：

```latex
Source observations expose each field's anchor count, reverse-resolution count in $T$, agreement of the resolved field/value with the successor, and exact prior-source retention for an unchanged field. Missing, duplicate, or inconsistent sources remain semantic failures rather than being excluded by the domain predicate. These are local source checks: the complete authorization--candidate--evidence chain belongs to the operational P6 checks below. Source observations hide intermediate commit grouping; freshness observes the admission-entry pre-state comparison. These explicit observation boundaries make it possible to compare atomic and fragmented histories with identical endpoints.
```

修改后的英文：

```latex
Source observations expose anchor counts, reverse-resolution counts in $T$, resolved field/value agreement, and exact prior-source retention for unchanged fields. Missing, duplicate, and inconsistent sources are semantic failures, not domain exclusions. These local checks exclude the complete authorization--candidate--evidence chain checked by operational P6. They also hide intermediate commit grouping; freshness observes the admission-entry pre-state comparison. These boundaries permit atomic and fragmented histories with identical endpoints.
```

## P13 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
Table~\ref{tab:distinctions} states the five information classes of the declared basis. Each concerns an information class, not a mandatory physical representation.
```

## P14 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
The observation basis is defined from the declared admission obligations and failure model and then held fixed for the omission analysis.
```

## P15 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
\paragraph{Proposition 1 (conditional failure distinguishability)}
For each information class $d_i\in\mathcal D$, the declared failure model contains a safe history and a corresponding unsafe history whose authority outcomes differ but whose projections become equal when $d_i$ is omitted. Consequently, an admission mechanism that observes only $\mathcal D\setminus\{d_i\}$ cannot distinguish the paired failure family under this model.
```

## P16 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
\paragraph{Proof sketch (by construction)}
For each declared failure family associated with $d_i\in\mathcal D$, Table~\ref{tab:distinctions} provides a paired construction consisting of a safe history $h_s^{(i)}$ and an unsafe history $h_u^{(i)}$ such that
$O(h_s^{(i)})\neq O(h_u^{(i)})$ while
$\pi_{\mathcal D\setminus\{d_i\}}(h_s^{(i)})=\pi_{\mathcal D\setminus\{d_i\}}(h_u^{(i)})$.
The five constructions are as follows. For $D_C$, hold the proposal, authorization, temporal, batch, and source observations constant but substitute an equal-valued candidate carrying another non-temporal context. For $D_V$, retain the same candidate---including its identity and proposal value 100---and the same committed value 101, but falsely relabel the human authorization as machine attribution. For $D_F$, compare the same candidate and authorization before and after pre-state supersession, leaving the four non-temporal projections unchanged. For $D_B$, the safe history changes two fields in one commit; the unsafe history changes the first field in one commit and the second in a subsequent commit. The latter exposes a partial intermediate state, although both histories reach the same final values and source map. Their effect domains and successor counts are derived from these connected state sequences; only the batch/grouping observation differs. For $D_S$, remove one successor source anchor while retaining the candidates, values, freshness, and commit sequence. Thus each pair differs in exactly one declared observation coordinate and in its derived outcome label.
```

## P17 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
Formally, for each $d_i\in\mathcal D$, the construction seeks histories $h_s^{(i)}$ and $h_u^{(i)}$ such that
\begin{equation}
\pi_{\mathcal D\setminus\{d_i\}}(h_s^{(i)})
=
\pi_{\mathcal D\setminus\{d_i\}}(h_u^{(i)})
\quad\text{and}\quad
O(h_s^{(i)})\neq O(h_u^{(i)}).
\label{eq:irredundancy}
\end{equation}
Therefore, removing the corresponding information class eliminates the ability to distinguish at least one declared failure family.
```

## P18 — COMPRESS

理由：精简检查器叙述，保留派生性、四项检查和 schema/item 区分。

原段落：

```latex
The checker \code{code/formal-fixed/observation_witnesses.py} validates each complete $\widehat h$ and derives its observations and outcome from the underlying relations; witnesses store neither. It verifies domain validity, unequal outcomes, equal four-class projections, and unequal full projections for each pair. Schema fields define the total value/source domains; declared item fields define the required effect domain. A single-field update with another field copied forward is therefore complete.
```

修改后的英文：

```latex
The checker \code{code/formal-fixed/observation_witnesses.py} derives observations and outcomes from each complete $\widehat h$; witnesses store neither. For each pair it checks domain validity, unequal outcomes, equal four-class projections, and unequal full projections. Schema fields define total value/source domains; declared item fields define required effects. A single-field update with another field copied forward is therefore complete.
```

## P19 — COMPRESS

理由：轻度压缩身份隔离补充说明，保留模型边界、固定变量和额外控制。

原段落：

```latex
The original $D_C$ pair changes record context while retaining the candidate handle, establishing irredundancy of the combined class rather than each component. An additional identity pair fixes the two-candidate registry, record, field, evidence, producer, proposal, and authorization. The safe batch selects the authorized candidate; the unsafe batch selects the equal-valued alternative. Only $D_C$ and the derived outcome differ, isolating candidate binding within the same observation model without establishing universal practical necessity. A separate control checks single-field copy-forward. Raw histories, both field domains, and derived values appear in \code{evidence/r27-witness/observation-witness-report-v5.json}.
```

修改后的英文：

```latex
The original $D_C$ pair changes record context but retains the candidate handle, establishing irredundancy of the combined class rather than each component. An additional identity pair fixes the two-candidate registry, record, field, evidence, producer, proposal, and authorization. The safe batch selects the authorized candidate; the unsafe batch selects its equal-valued alternative. Only $D_C$ and the derived outcome differ, isolating candidate binding within this model rather than universal practical necessity. A separate control checks single-field copy-forward. Raw histories, field domains, and derived values are in \code{evidence/r27-witness/observation-witness-report-v5.json}.
```

## P20 — COMPRESS

理由：先陈述正向结果，再集中保留所有限制；不改动 Proposition 或证明。

原段落：

```latex
Proposition 1 establishes class-wise irredundancy for the declared failure, history, observation, and outcome model, not universal minimality, schema uniqueness, or completeness over all admission failures. The checker validates the five class pairs, identity pair, and copy-forward control; it is not a general admission oracle. These constructions establish Eq.~\eqref{eq:irredundancy}; the separate Alloy checks test encoded assertions and conjunct-removal sensitivity in finite scopes.
```

修改后的英文：

```latex
Proposition 1 establishes class-wise irredundancy within the declared failure, history, observation, and outcome model. It establishes neither universal minimality, schema uniqueness, nor completeness over all admission failures. The checker covers the five class pairs, identity pair, and copy-forward control, not general admission. These constructions establish Eq.~\eqref{eq:irredundancy}; Alloy separately checks encoded assertions and conjunct-removal sensitivity in finite scopes.
```

重复位置与主叙述位置：Discussion formal validity points here for the full characterization boundary.

## P21 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
A batch $B$ is a nonempty set of items sharing one target record, principal, expected pre-version, and successor. Under Full, item fields are unique. Let
\begin{equation}
\Delta(V_v,V_{v+1})=\{f\in F_r\mid V_v(f)\neqc V_{v+1}(f)\}.
\end{equation}
For a post-initial concrete admission,
\begin{equation}
\Delta(V_v,V_{v+1})=\{i.f\mid i\in B\}=\{t.f\mid t\in T_{v+1}\},
\label{eq:changed-fields}
\end{equation}
with one transition per item. At the first certificate-era version, the batch covers all of $F_r$, establishing total value and source domains. Deletion is outside the model.
```

## P22 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
For every $i\in B$, admission requires
\begin{align}
i.r &= r, & i.f&\in F_r,\nonumber\\
EID(i.e) &= EID(i.c.e), & i.v_{\mathrm{exp}}&=v,\nonumber\\
i.a.c_{\mathrm{id}}&=i.c.c_{\mathrm{id}}, & i.a.q&=q,\nonumber\\
i.x\eqc i.a.x_a, & t_i.x&\eqc V_{v+1}(i.f)\eqc i.x.
\label{eq:item-bindings}
\end{align}
Together these instantiate the admission preconditions
\begin{equation}
\operatorname{Bind}(a,c)\land\operatorname{Fresh}(c,S_v)\land
\operatorname{Authorized}(a)\land\operatorname{Complete}(S_{v+1})\land
\operatorname{Attributed}(S_{v+1}).
\end{equation}
```

## P23 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
The successor is atomic: either all decision, authorization, transition, version, source-map, and audit effects commit, or authoritative state stutters. For a changed field, $S_{v+1}(f)=t_i$. For an unchanged field, both value and exact source are copied forward:
\begin{equation}
f\notin\Delta(V_v,V_{v+1})\Rightarrow
V_{v+1}(f)\eqc V_v(f)\land S_{v+1}(f)=S_v(f).
\label{eq:copy-forward}
\end{equation}
Alloy permits same-value admission for correspondence with the historical singleton model; concrete post-initial admissions require a value change. For submitted items $U$, the admitted batch is $B=\{i\in U\mid i.x\neqc V_v(i.f)\}$, with $B\neq\varnothing$. A mixed submission admits exactly $B$ and copies unchanged items' exact prior sources into the complete successor, creating no transition or authorization binding for $U\setminus B$. Thus Eq.~\eqref{eq:changed-fields} concerns admitted effects, not all submitted reviews. Recording renewed review or re-attribution without a value change requires a separate review-event path outside this contract; persisted candidate identity allows that path to distinguish equal-valued proposals.
```

## P24 — COMPRESS

理由：压缩信任边界段落，保留全部受信组件、外部假设和不覆盖对象。

原段落：

```latex
Model output and candidate-only callers are untrusted. The trusted computing base comprises the admission service, narrow adapter, exercised SQLite transaction semantics, canonical serialization and hashing, and principal-policy source. The prototype checks a supplied principal's active status and role; host authentication, session integrity, and faithful review presentation are external assumptions. It does not protect a compromised process, host, or database administrator. The contract enforces an existing authorization through persisted binding, CAS admission, and source lineage; faithfully forming that authorization from the review remains a host obligation.
```

修改后的英文：

```latex
Model output and candidate-only callers are untrusted. The trusted base comprises the admission service, narrow adapter, exercised SQLite semantics, canonical serialization/hashing, and principal-policy source. The prototype checks principal status and role; host authentication, session integrity, and faithful review presentation remain external. Persisted binding, CAS, and lineage enforce the recorded authorization; the host must form it faithfully. Compromised processes, hosts, and database administrators remain outside this protection.
```

## P25 — COMPRESS

理由：精简撤销时序解释，保留锁范围、线性化边界和部署条件。

原段落：

```latex
The prototype evaluates the in-memory principal-role allow-list inside the database transaction, before the version compare-and-swap and any authority write. A revocation that completes before this check causes zero-write rejection. The allow-list lock protects only the policy lookup/update; it is not held for the remainder of the database transaction. Consequently, a revocation that overlaps an admission after its successful policy check does not cancel that in-flight commit. The implementation therefore provides commit-entry revalidation, not linearizable revocation against already admitted operations, distributed identity-provider semantics, or session invalidation. Deployments requiring those properties must place a transactional policy epoch or equivalent revocation discriminator inside the admission compare-and-swap.
```

修改后的英文：

```latex
The prototype checks the in-memory principal-role allow-list inside the transaction before CAS or any authority write. Prior revocation causes zero-write rejection. The allow-list lock covers lookup/update only, so revocation after a successful check cannot cancel an in-flight commit. This provides commit-entry revalidation, not linearizable revocation, distributed identity-provider semantics, or session invalidation. Those properties require a transactional policy epoch or equivalent revocation discriminator inside the admission CAS.
```

## P26 — COMPRESS

理由：先正向定义契约保证，再保留真实性限制。

原段落：

```latex
Human authorization is not a truth oracle. The contract establishes who authorized which persisted candidate and value in which context, and whether the successor was constructed atomically. It cannot establish that the authorized value is factually correct.
```

修改后的英文：

```latex
The contract establishes who authorized which persisted candidate and value in which context, and whether the successor was atomic. It does not establish the authorized value's factual correctness.
```

公式、表格、图及其图注统一为 **KEEP**：保持数学关系、结果和解释不变。
