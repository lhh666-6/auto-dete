# 保守压缩与图解叙事记录 — 2026-09-27

基准：`cd5bded02f76869223e7d3e6f1dcfac8363fd1f9`（44 页正文、12 页补充材料）。本次正文 30 页、补充材料 21 页。正文 PDF 提取词数由 12,292 降为 8002（约 34.9%），包括表格、图注、声明和参考文献。页数变化没有使用缩小字号或边距。

下表按英文源码计数，去除引用键、路径和数学表达式，保留段落及表格中的英文词；图中的英文不计入源码词数，因而与 PDF 总词数不同。

| 节 | 原词数 | 新词数 | 压缩比例 | scientific claim changed |
|---|---:|---:|---:|---|
| Abstract | 211 | 201 | 4.7% | No |
| 01-introduction | 867 | 557 | 35.8% | No |
| 02-related-work | 1320 | 543 | 58.9% | No |
| 03-problem-contract | 2141 | 1576 | 26.4% | No |
| 04-relational-analysis | 723 | 285 | 60.6% | No |
| 05-transactional-realization | 692 | 384 | 44.5% | No |
| 06-formal-concrete-conformance | 604 | 282 | 53.3% | No |
| 07-evaluation-protocol | 1556 | 748 | 51.9% | No |
| 08-results | 1013 | 603 | 40.5% | No |
| 09-discussion-threats | 1202 | 424 | 64.7% | No |
| 10-conclusion | 163 | 115 | 29.4% | No |

## 科研叙事的唯一主位置

- Introduction：问题、equal-valued candidate separator、C1–C3、关系的整体意义；图 1 承担完整机制总览。
- Contract：形式对象、五类观察、限定 Proposition 1、完整批次关系和 P0–P6；完整观察函数/域移入 S2。
- Realization / Conformance：事务执行与独立映射检查；S2 放完整映射表、命令和作用域。
- Protocol：单位、政策、oracle 与计时边界；图 2 串联证据，S1/S6 放操作参数和详细规则。
- Results：实例政策与 context 政策的行为差异、持久化一致性、浏览器边界、主要成本；S4 保留全矩阵。
- Discussion：政策含义、信任和有效性边界；S7 扩展细节，S5 为历史结果唯一完整叙述位置。

## 段落标签和压缩后的英文

原文段落依空行编号；LaTeX 方程、表格、列表及其结构不算 prose 段落。结构化内容单列。重组是多对多合并，因此 COMPRESS 段落对应本节下方的完整新英文源码；MOVE-SUPP 给出正文锚句和移动范围。KEEP 表示原句逐字保留；DELETE 仅指已经在正文或补充材料保留的冗余表述。

### Abstract

COMPRESS — 概念结论先于 benchmark 数字，保留 exact/context 政策差异、review boundary 与 conditional scope。精确 latency 数值仍在 Results 与 S4。

AI-assisted data acquisition separates a machine proposal from the value a human authorizes for a database. Identical final values can conceal different reviewed candidates, corrected values, and field sources. We specify a correction-aware admission relation that binds an exact persisted candidate to an explicit authorized value, checks predecessor freshness, and atomically constructs a complete successor with total field-level provenance. Five paired histories establish class-wise irredundancy under declared observations. A Python/SQLite realization connects the relation to bounded analysis, persisted-state projections, and a 35-case fault catalogue. A constructed comparison evaluates a context-preserving event journal, its exact-binding extension, and the reference implementation. The two exact-binding mechanisms agree on all 165 corresponding cases. The context journal admits 15 equal-valued candidate substitutions that satisfy its value/context policy but violate instance accountability; the stricter mechanisms reject those substitutions. In 60 scripted browser cases, a server-held review-session gate blocks nine request substitutions accepted by the original path. Both paths accept three display-only substitutions, locating the trusted presentation boundary. Current-version workloads characterize admission, provenance reconstruction, and storage costs; bulk and point trace access return identical complete objects. The results connect the admission relation to enforceable integrity obligations across two storage designs, within the declared model, trust boundary, and measured workloads.

### 01-introduction

| 原 prose 段 | 标签 | 一句理由 |
|---|---|---|
| P1: 98 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P2: 90 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P3: 79 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P4: 57 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P5: 39 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P6: 87 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P7: 14 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P8: 79 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P9: 104 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P10: 24 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |

压缩后的完整英文（保留 LaTeX 以便逐句定位；KEEP 段也包含在内）：

```latex
\section{Introduction}
\label{sec:introduction}

An AI-assisted acquisition system may extract a value, propose an update, and ask a person to approve it. Once admitted, the value can drive queries and decisions. Its authority depends on a history that the final value alone cannot identify: which persisted proposal was reviewed, what value was authorized, and which predecessor and field sources the resulting record retained.

Consider quantity 90. A recognizer proposes 100, but a reviewer authorizes 101; an unchanged batch-code field should keep its earlier source. Overwriting the proposal with 101 erases the machine--human distinction. Recording only 101 and a reviewer leaves the reviewed proposal ambiguous. Copying values without sources produces a numerically correct snapshot with incomplete provenance. Correction-aware admission must retain the proposal $x_c$ separately from the authorized value $x_a$, including
\begin{equation}
x_c\neq x_a.
\label{eq:intro-correction}
\end{equation}

Candidate identity gives a sharper separator. Two persisted extraction attempts may propose the same value for the same field and evidence. A value/context policy can treat them as interchangeable. An instance-accountability policy must distinguish the candidate selected by the reviewer from an equal-valued substitute. We specify that stricter relation and evaluate both policies explicitly.

Transactions, optimistic validation, and provenance provide established foundations \citep{gray1981transaction,kung1981occ,moreau2013provdm}. The contribution is a correction-aware admission relation over their semantic objects:
\begin{equation}
\begin{aligned}
\textit{exact candidate}
&\rightarrow\textit{candidate-bound authorization}\\
&\rightarrow\textit{explicit authorized value}\\
&\rightarrow\textit{complete successor and total field sources}.
\end{aligned}
\label{eq:admission-chain}
\end{equation}
The candidate remains historical evidence; authorization supplies permission for the committed value. One transaction creates the successor, assigning new transitions to changed fields and preserving exact sources for unchanged fields. Relational tables and event journals can both represent these obligations.

Five information classes characterize the histories the relation distinguishes: candidate identity and context, value roles, freshness, successor completeness, and field-source attribution. For each class, a paired construction has different authority outcomes but equal remaining observations when that class is omitted. The result establishes class-wise irredundancy within the declared history and observation model.

We realize the relation in \system{}, a Python/SQLite service, and make three contributions:
\begin{enumerate}[label=\textbf{C\arabic*:},leftmargin=*]
\item \textbf{A correction-aware admission contract and conditional characterization.} Separate proposal and authorized values, candidate-bound review, and complete field sources support five failure-distinguishing information classes.
\item \textbf{Relational and transactional enforcement.} An Alloy model, in-transaction validation, version compare-and-swap, selected formal--concrete projections, and persisted-state checks connect the relation to executable behavior.
\item \textbf{Comparative, review-boundary, and cost evidence.} Event-journal controls isolate exact candidate binding; browser controls locate the transfer of review intent; current-version workloads measure admission, tracing, and storage.
\end{enumerate}

The central comparison has 165 corresponding constructed cases per mechanism. The exact-binding event journal and reference agree on every decision and provenance-query answer. The context journal accepts 15 equal-valued substitutions that satisfy its value/context policy but violate instance accountability. These are also 15 additional rejections by the stricter mechanisms under the looser policy. The separator therefore identifies the authorization relation rather than a uniquely capable storage architecture.

Review intent must reach that relation faithfully. A server-held review session rejects nine request substitutions accepted by the original path, while both paths accept three display-only substitutions. The contract enforces the authorization supplied to it; authenticated identity and faithful review presentation remain trust assumptions. \Cref{fig:admission-workflow} summarizes this boundary.

\begin{figure*}[t]
\centering
\includegraphics[width=\textwidth]{figures/refined/figure-1-admission-workflow.pdf}
\caption{Correction-aware admission: (a) equal-valued candidates remain distinct under instance authorization; (b) Correction retains the original proposal; (c) failed admission leaves authoritative state unchanged; (d) changed and unchanged fields retain their respective sources. Values illustrate a constructed example. OpenAI Codex (GPT-6) and OpenAI's image-generation tool assisted visual design on 27 September 2026; the latter exposed no model/version identifier. The checked vector diagram was rendered with Matplotlib 3.10.8.}
\label{fig:admission-workflow}
\end{figure*}
```

### 02-related-work

| 原 prose 段 | 标签 | 一句理由 |
|---|---|---|
| P1: 56 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P2: 62 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P3: 110 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P4: 83 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P5: 81 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P6: 98 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P7: 101 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P8: 64 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P9: 100 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P10: 94 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P11: 94 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P12: 96 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P13: 95 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P14: 65 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P15: 88 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |

压缩后的完整英文（保留 LaTeX 以便逐句定位；KEEP 段也包含在内）：

```latex
\section{Background and related work}
\label{sec:related}

\subsection{Transactions, provenance, and event histories}

Transactions provide atomic, durable state transformations; optimistic concurrency control validates conflicting work before installing effects \citep{gray1981transaction,kung1981occ}. Our compare-and-swap is an application freshness check inside that transaction. The admission relation specifies which candidate, authorization, value, and source relationships the transaction must enforce. Existence of a candidate or a current predecessor alone does not determine whether an approval targets that candidate or its separately authorized correction.

Why-, how-, and where-provenance describe the reasons, derivations, and origins of query results \citep{buneman2001whywhere,cheney2009provenance}. PROV-DM represents entities, activities, agents, derivation, and responsibility, with application extension points \citep{moreau2013provdm}. Our field-source map identifies durable transitions responsible for a committed record's fields. A proposal can be a PROV entity and review an activity; the admission relation adds the operational obligation to check their bindings before creating a complete snapshot.

Transaction reenactment reconstructs multi-version provenance from update histories, audit logs, and prior database versions \citep{arab2018reenactment}. Such histories can include proposal and review data when the application records them. Our focus is the correction-aware association to enforce: the immutable proposal, the explicit human-authorized value, and the source of each changed or copied-forward field.

Event sourcing records a sequence of changes from which state can be reconstructed \citep{fowler2005eventsourcing}. Its schema and validation rules determine the granularity of approval. This motivates our two rich-context journals: both retain versions, sources, and transactional behavior, while one additionally binds the exact reviewed instance. The exact journal's agreement with the reference supports enforcement in both representations. Equal-valued substitution exposes the policy distinction between approved content and approved candidate instances.

\subsection{Adjacent activation and governed-memory contracts}

Recent preprints address neighboring authority boundaries. Continuity Kernel binds proposal identity, exact predecessor, pre-state authority, evidence, lineage, and a complete accepted unit, with relational, object-manifest, and replicated-log realizations \citep{he2026continuity}. General proposal/authority separation and complete-successor activation are therefore established in that account. Our contribution concerns a reviewed field candidate whose proposed value can differ from the authorized correction, exact field-source propagation, and the conditional observation analysis and executable evidence for that relation.

MemTxn separates source-support admission, temporal visibility, and application-state recovery \citep{cui2026memtxn}; its source-support predicate complements the candidate-to-human-authorization predicate studied here. MutMem binds signed retrieval-weight changes to provenance, signer epochs, old/new weights, and predecessor continuity \citep{saidi2026mutmem}. Its mutation and cryptographic assurance differ from reviewed field correction. LatticeMind retains claim status, conflict, supersession, and provenance \citep{zhou2026latticemind}. Stored Is Not Supported begins with an authenticated accepted head and governs subsequent assertion release \citep{he2026stored}. We compare these preprints' stated scopes; their representations may encode the relation evaluated here.

\subsection{Review binding and executable analysis}

OAuth DPoP specifies proof-of-possession and request method/URI bindings \citep{fett2023dpop}. Our review experiment similarly distinguishes what a request binds from what a reviewer was shown. Host authentication and channel integrity remain premises. AgentDojo evaluates tool agents over untrusted data with separate task and security outcomes \citep{debenedetti2024agentdojo}. Our new studies instead examine deterministic admission and review boundaries using archived values and constructed histories; historical model integration is reported separately.

Alloy and Kodkod provide SAT-based bounded relational analysis \citep{jackson2002alloy,torlak2007kodkod}; TestEra connects relational specifications and executable programs through abstraction and concretization \citep{marinov2001testera}. We apply these methods to legal histories, conjunct removals, and selected persisted-state projections. The paired-history argument characterizes observations, Alloy checks its encoding within finite scopes, and concrete tests examine persisted behavior. These evidence layers support distinct parts of the admission relation.
```

### 03-problem-contract

| 原 prose 段 | 标签 | 一句理由 |
|---|---|---|
| P1: 15 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P2: 16 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P3: 37 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P4: 37 words | KEEP | 保留原句及其科学限定。 |
| P5: 25 words | KEEP | 保留原句及其科学限定。 |
| P6: 10 words | MOVE-SUPP | 完整细节保存在 S2/S6/S7，正文保留关系或计量边界。 |
| P7: 82 words | MOVE-SUPP | 完整细节保存在 S2/S6/S7，正文保留关系或计量边界。 |
| P8: 20 words | KEEP | 保留原句及其科学限定。 |
| P9: 28 words | KEEP | 保留原句及其科学限定。 |
| P10: 97 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P11: 34 words | KEEP | 保留原句及其科学限定。 |
| P12: 61 words | KEEP | 保留原句及其科学限定。 |
| P13: 13 words | KEEP | 保留原句及其科学限定。 |
| P14: 73 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P15: 56 words | KEEP | 保留原句及其科学限定。 |
| P16: 20 words | KEEP | 保留原句及其科学限定。 |
| P17: 13 words | KEEP | 保留原句及其科学限定。 |
| P18: 14 words | MOVE-SUPP | 完整细节保存在 S2/S6/S7，正文保留关系或计量边界。 |
| P19: 94 words | MOVE-SUPP | 完整细节保存在 S2/S6/S7，正文保留关系或计量边界。 |
| P20: 89 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P21: 10 words | KEEP | 保留原句及其科学限定。 |
| P22: 45 words | KEEP | 保留原句及其科学限定。 |
| P23: 108 words | KEEP | 保留原句及其科学限定。 |
| P24: 27 words | KEEP | 保留原句及其科学限定。 |
| P25: 47 words | KEEP | 保留原句及其科学限定。 |
| P26: 68 words | KEEP | 保留原句及其科学限定。 |
| P27: 60 words | KEEP | 保留原句及其科学限定。 |
| P28: 24 words | KEEP | 保留原句及其科学限定。 |
| P29: 26 words | KEEP | 保留原句及其科学限定。 |
| P30: 51 words | KEEP | 保留原句及其科学限定。 |
| P31: 85 words | KEEP | 保留原句及其科学限定。 |
| P32: 82 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P33: 104 words | MOVE-SUPP | 完整细节保存在 S2/S6/S7，正文保留关系或计量边界。 |
| P34: 37 words | MOVE-SUPP | 完整细节保存在 S2/S6/S7，正文保留关系或计量边界。 |

压缩后的完整英文（保留 LaTeX 以便逐句定位；KEEP 段也包含在内）：

```latex
\section{Authoritative-state admission contract}
\label{sec:contract}

\subsection{Candidate, authorization, and authoritative state}


Correction-aware admission links an untrusted persisted candidate $c$, attributable authorization $a$, and authoritative pre-state $\Sigma_v$:
\begin{equation}
\operatorname{Admit}(c,a,\Sigma_v)=\Sigma_{v+1}.
\label{eq:admit}
\end{equation}
The candidate stays non-authoritative historical evidence. Proposal origin, value authority, and committed value remain distinct roles.

Let $r$ be a record with a nonempty authoritative field set $F_r$. Its committed state $\Sigma_v$ contains a total value map $V_v:F_r\rightarrow X$ and a total source map $S_v:F_r\rightarrow T$, where $T$ is the set of durable fact transitions. A machine candidate for field $f$ is
\begin{equation}
c=\langle r,f,e,v_{\mathrm{exp}},x_c,p,c_{\mathrm{id}}\rangle,
\label{eq:candidate}
\end{equation}
where $e$ is persisted evidence, $v_{\mathrm{exp}}$ is the expected current version, $x_c$ is the machine proposal, $p$ identifies its producer, and $c_{\mathrm{id}}$ is an identity over the modeled candidate content.


Evidence identity combines a content digest and canonical record/field locator:
\begin{equation}
EID(e)=\langle H(\mathrm{bytes}(e)),L(r,f,u,\kappa)\rangle.
\label{eq:evidence}
\end{equation}
Here $H$ is SHA-256, and $L$ contains the owner record, field, normalized storage-relative URI $u$, locator version, and optional crop $\kappa$. Alloy abstracts content and locators as primitive domains. Identity uniqueness in its scopes relies on collision resistance and canonicalization/store integrity in the implementation (Supplement S2).

An attributable authorization is
\begin{equation}
a=\langle c_{\mathrm{id}},x_a,q\rangle,
\label{eq:authorization}
\end{equation}
where $q$ is an authorized human principal and $x_a$ is the value explicitly permitted to enter the record. The dual-value semantics are
\begin{align}
\operatorname{proposal}(c)&=x_c, &
\operatorname{authorize}(a)&=x_a,\nonumber\\
\operatorname{commit}(\Sigma_{v+1},f)&=x_a, &
\operatorname{origin}(\Sigma_{v+1},f)&=c.
\label{eq:dual-value}
\end{align}
Accept has $x_c\eqc x_a$. Correction has $x_c\neqc x_a$; the candidate remains unchanged and the committed value derives its authority from $a$. Here $\operatorname{origin}$ identifies the retained proposal, not the authority for a corrected value.


\paragraph{Canonical value equality}
Write $x\eqc y$ when sorted-key, whitespace-minimal JSON serializations agree. This distinguishes $2$ from $2.0$ and $1$ from \code{true}, although Python equality does not. Change detection, value checks, tracing, the independent oracle, and projection use this relation. \Cref{sec:conformance} reports the cross-layer repair.

\subsection{History, observations, and outcomes}

An authority-relevant history is
\begin{equation}
h=\Sigma_0\xrightarrow{e_1}\Sigma_1\xrightarrow{e_2}\cdots\xrightarrow{e_n}\Sigma_n,
\end{equation}
where events may persist evidence or candidates, record review and authorization, attempt admission, commit or stutter, and reconstruct a reverse trace. The abstraction describes semantic information rather than requiring particular table or column names.

We group the observable distinctions into
\begin{equation}
\mathcal D=\{D_C,D_V,D_F,D_B,D_S\},
\label{eq:distinction-basis}
\end{equation}
where $D_C$ is candidate identity and context, $D_V$ is dual-value attribution, $D_F$ is freshness, $D_B$ is batch/successor completeness, and $D_S$ is total source attribution. For $I\subseteq\mathcal D$, $\pi_I(h)$ retains only the information classes in $I$. Candidate identity may be implemented by a certificate, stable handle, or another equivalence class, provided it does not collapse to value equality. Freshness may likewise use a version, state hash, epoch, or comparable discriminator.

To make ``retains'' precise, let $\operatorname{obs}_d(h)$ be the observation function for class $d$ and define
\begin{equation}
\pi_I(h)=\langle\operatorname{obs}_d(h)\rangle_{d\in I}.
\label{eq:observation-projection}
\end{equation}
The functions are logical projections, not claims that a database must store five physically separate objects. A certificate can co-locate several classes. In a projection, however, a content address is treated as an opaque equality-preserving handle: its preimage is not available as a side channel. This prevents a nominally omitted value or version from being recovered merely because the concrete certificate hash covers it. The complete observation functions are given in Supplement S2.

The full-history authority-outcome label is
\begin{equation}
O(h)=\langle status,successor,trace\rangle,
\label{eq:outcome}
\end{equation}
where $status$ is admissible, inadmissible, or failed/stuttering; $successor$ classifies the authoritative post-state or its absence; and $trace$ is complete, incomplete, ambiguous, or unavailable. This is the normative label assigned from the full history, not an additional input available to a mechanism restricted to $\pi_I$. A binary accept/reject label is insufficient because value-identical successors may differ in source completeness.

An observation set $I$ fails to distinguish a failure family when there exist a safe history $h_s$ and unsafe history $h_u$ such that
\begin{equation}
O(h_s)\neq O(h_u)
\quad\land\quad
\pi_I(h_s)=\pi_I(h_u).
\label{eq:indistinguishable}
\end{equation}
Any admission decision based only on that reduced observation cannot separate the pair.


The executable histories contain candidate and authorization registries, declared items, expected and observed versions, a connected commit sequence, endpoint maps, and transition sources. Projections and outcomes are derived from these relations. Schema fields determine total map domains; declared items determine required effects. Missing or conflicting sources remain failures in the domain. Supplement S2 gives the complete functions, finite tuple, and checker rules.

\subsection{Conditional failure-distinguishability characterization}

Table~\ref{tab:distinctions} summarizes the paired histories for this fixed observation basis.

\begin{table}[t]
\centering
\footnotesize
\caption{Failure-distinguishing information classes in the declared observation model.}
\label{tab:distinctions}
\begin{tabularx}{\textwidth}{@{}l>{\raggedright\arraybackslash}p{0.23\textwidth}>{\raggedright\arraybackslash}p{0.27\textwidth}>{\raggedright\arraybackslash}X@{}}
\toprule
Class & Safe/unsafe pair & Required distinction & Failure if omitted \\
\midrule
$D_C$ & exact candidate / equal-valued cross-context substitute & persisted candidate identity plus record, field, evidence, and producer context & candidate substitution \\
$D_V$ & preserved Correction / erased or false role attribution with the candidate unchanged & separate machine proposal $x_c$, human-authorized value $x_a$, committed value, and role relation & correction erasure or false machine attribution \\
$D_F$ & current authorization / same authorization after supersession & commit-time freshness discriminator tied to the observed pre-state & stale replay \\
$D_B$ & one atomic commit / two connected commits with the same final values & actual per-step effects and one atomic successor & fragmented successor \\
$D_S$ & total trace / equal-valued successor with missing or conflicting source & total per-field source relation and exact unchanged-source copy-forward & source ambiguity \\
\bottomrule
\end{tabularx}
\end{table}

\paragraph{Proposition 1 (conditional failure distinguishability)}
For each information class $d_i\in\mathcal D$, the declared failure model contains a safe history and a corresponding unsafe history whose authority outcomes differ but whose projections become equal when $d_i$ is omitted. Consequently, an admission mechanism that observes only $\mathcal D\setminus\{d_i\}$ cannot distinguish the paired failure family under this model.

\paragraph{Proof sketch (by construction)}
For $D_C$, hold the value-role, temporal, batch, and source observations constant while changing non-temporal candidate context. For $D_V$, retain the same candidate, proposal value 100, and committed value 101, but falsely attribute the corrected value to the machine proposal. For $D_F$, change only the admission-entry freshness comparison. For $D_B$, compare one two-field commit with two connected single-field commits that reach the same final values and sources; the latter exposes an intermediate partial state. Effect domains and successor counts follow from these sequences. For $D_S$, remove one source anchor while retaining candidates, values, freshness, and the commit sequence. Each construction changes its selected observation coordinate and the derived outcome, while leaving the other four coordinates equal.

Thus, for every $d_i\in\mathcal D$, the constructed histories satisfy
\begin{equation}
\pi_{\mathcal D\setminus\{d_i\}}(h_s^{(i)})
=
\pi_{\mathcal D\setminus\{d_i\}}(h_u^{(i)})
\quad\text{and}\quad
O(h_s^{(i)})\neq O(h_u^{(i)}).
\label{eq:irredundancy}
\end{equation}
Any decision function of the reduced projection receives the same input for both histories and cannot assign both distinct required outcomes. This establishes the claimed conditional irredundancy.

The executable checker validates each complete $\widehat h$ and derives observations and outcomes from its relations; witnesses store neither. It checks domain validity, unequal outcomes, equal four-class projections, and unequal full projections. Schema fields define the total value/source domains, whereas declared item fields define the required effect domain.

The original $D_C$ pair changes record context while retaining the candidate handle, establishing irredundancy of the combined class. An additional pair fixes the two-candidate registry and every context/value component, then selects either the authorized candidate or the equal-valued alternative. It isolates candidate binding within this observation model. A single-field copy-forward control checks the distinction between schema and effect domains. Supplement S2 identifies the executable constructions and raw histories.

\paragraph{Scope of the result}
Proposition 1 establishes class-wise irredundancy for the declared failure, history, observation, and outcome model, not universal minimality, schema uniqueness, or completeness over all admission failures. The checker validates the five class pairs, identity pair, and copy-forward control; it is not a general admission oracle. These constructions establish Eq.~\eqref{eq:irredundancy}; the separate Alloy checks test encoded assertions and conjunct-removal sensitivity in finite scopes.

\subsection{Batch admission relation}

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

For every $i\in B$, admission requires
\begin{align}
i.r &= r, & i.f&\in F_r,\nonumber\\
EID(i.e) &= EID(i.c.e), & i.v_{\mathrm{exp}}&=v,\nonumber\\
i.a.c_{\mathrm{id}}&=i.c.c_{\mathrm{id}}, & i.a.q&=q,\nonumber\\
i.x &\eqc i.a.x_a, & t_i.x&\eqc V_{v+1}(i.f)\eqc i.x.
\label{eq:item-bindings}
\end{align}
Together these instantiate the admission preconditions
\begin{equation}
\begin{aligned}
&\operatorname{Bind}(a,c)\land\operatorname{Fresh}(c,\Sigma_v)\land\operatorname{Authorized}(a)\\
&\qquad\land\operatorname{Complete}(\Sigma_{v+1})\land\operatorname{Attributed}(\Sigma_{v+1}).
\end{aligned}
\end{equation}

The successor is atomic: all admission-time decision, authorization, transition, version, source-map, and audit effects commit together, or authoritative state stutters. This does not require rollback of evidence, candidates, or review intent persisted before the admission attempt. For a changed field, $S_{v+1}(f)=t_i$. For an unchanged field, value and exact source are copied forward:
\begin{equation}
f\notin\Delta(V_v,V_{v+1})\Rightarrow
V_{v+1}(f)\eqc V_v(f)\land S_{v+1}(f)=S_v(f).
\label{eq:copy-forward}
\end{equation}
Alloy permits same-value admission for correspondence with the historical singleton model; concrete post-initial admissions require a value change. For submitted items $U$, the admitted batch is $B=\{i\in U\mid i.x\neqc V_v(i.f)\}$, with $B\neq\varnothing$. A mixed submission admits exactly $B$ and copies unchanged items' exact prior sources into the complete successor, creating no transition or authorization binding for $U\setminus B$. Thus Eq.~\eqref{eq:changed-fields} concerns admitted effects, not all submitted reviews. Recording renewed review or re-attribution without a value change requires a separate review-event path outside this contract; persisted candidate identity allows that path to distinguish equal-valued proposals.

\subsection{Operational properties and trust boundary}

\begin{table}[t]
\centering
\caption{Admission properties and their operational interpretation.}
\label{tab:properties}
\begin{tabularx}{\textwidth}{@{}l>{\raggedright\arraybackslash}p{0.29\textwidth}>{\raggedright\arraybackslash}X@{}}
\toprule
Property & Requirement & Operational interpretation \\
\midrule
P0 & Direct-write exclusion & Machine/candidate capability cannot change authoritative values, versions, sources, transitions, or authorizations. \\
P1 & Candidate non-substitutability & Authority refers to the same canonical persisted certificate, not merely an equal value or analogous candidate. \\
P2 & Context-bound admission & Record, field, persisted evidence content and locator, and expected version agree across the item and certificate. \\
P3 & Authorization integrity & The principal is allowed at the in-transaction policy check before the compare-and-swap, and the authorization names the exact certificate and explicit committed value; in-flight revocation semantics are stated in \cref{sec:authorization-timing}. \\
P4 & Freshness & The expected version equals the transactionally observed current version; stale or competing decisions fail closed. \\
P5 & Successor integrity & One atomic successor has an item--transition bijection, exact changed-field effects, and complete changed/unchanged framing. \\
P6 & Trace soundness & Each committed field resolves through its exact source transition to consistent authorization, certificate, evidence, producer, and version relations. \\
\bottomrule
\end{tabularx}
\end{table}


Model output and candidate-only callers are untrusted. The trusted base comprises the admission service, adapter, exercised transaction semantics, canonicalization and hashing, and principal policy. Host authentication, session integrity, and faithful review presentation are external assumptions. The confirmation API constructs its binding from caller-supplied candidate and value; the contract preserves that binding, not factual truth or protection from a compromised host.

\paragraph{Authorization timing and revocation}
\label{sec:authorization-timing}
The in-transaction principal check precedes compare-and-swap and authority writes. Revocation visible before the check causes zero-write rejection; a later overlapping revocation does not cancel an in-flight commit. This is commit-entry revalidation. Supplement S2 states the policy-lock and stronger-revocation boundaries.
```

### 04-relational-analysis

| 原 prose 段 | 标签 | 一句理由 |
|---|---|---|
| P1: 56 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P2: 55 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P3: 66 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P4: 25 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P5: 55 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P6: 42 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P7: 72 words | MOVE-SUPP | 完整细节保存在 S2/S6/S7，正文保留关系或计量边界。 |
| P8: 89 words | MOVE-SUPP | 完整细节保存在 S2/S6/S7，正文保留关系或计量边界。 |
| P9: 77 words | MOVE-SUPP | 完整细节保存在 S2/S6/S7，正文保留关系或计量边界。 |
| P10: 41 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |

压缩后的完整英文（保留 LaTeX 以便逐句定位；KEEP 段也包含在内）：

```latex
\section{Bounded relational characterization}
\label{sec:alloy}

The Alloy model represents records, fields, ordered versions, evidence, candidates, certificates, principals, authorizations, transitions, and states. Once a record is authoritative, its value and source maps cover exactly its field domain. \code{MachineEvent} can extend candidate/evidence sets while framing authority (P0). \code{BatchAdmissionEvent} has a nonempty item set in one envelope. \code{TamperEvent} freezes values and source pointers while modifying transitions.

The base effect advances one version and applies item values and sources. Full adds unique fields, complete snapshot shape, preexisting certificate/evidence, contextual and authorization bindings, freshness, and an exact item--transition bijection. Separating these conjuncts permits controlled removal. Each ablation uses at least two items: one violates only the selected conjunct and another remains Full-valid. The reduced relation admits that set; Full rejects it with authoritative-state stutter.

Six legal commands exercise Accept, Correction, mixed batches, same-value admission, initial coverage, and singleton admission. Eleven ablations test encoded bindings. Three source attacks remove, replace, or duplicate an anchor after a legal prefix. Fourteen assertions per profile check framing, preservation, singleton correspondence, and trace conditions. The class-to-conjunct map and complete command descriptions are in Supplement S2.

The positive trace assertion requires a trace-complete predecessor and no stray successor transition. It checks admitted fields for one encoded step. Reachable initial and carry-forward witnesses establish a nonempty premise; removing post-state certificate binding changes UNSAT to SAT. Concrete tracing additionally validates predecessor prefixes. This distinguishes bounded preservation from the observation-level proposition.

Two scope profiles increase representative bounds from two records, three fields, six versions, and four states/events to three records, four fields, eight versions, and five states/events. Individual domain bounds remain fixed by deposited commands. SAT denotes a found witness; UNSAT denotes no counterexample within that command's finite scope \citep{jackson2002alloy,torlak2007kodkod}.

\input{tables/generated/formal_evidence}
```

### 05-transactional-realization

| 原 prose 段 | 标签 | 一句理由 |
|---|---|---|
| P1: 72 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P2: 73 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P3: 64 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P4: 16 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P5: 69 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P6: 54 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P7: 47 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P8: 61 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P9: 59 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |

压缩后的完整英文（保留 LaTeX 以便逐句定位；KEEP 段也包含在内）：

```latex
\section{Transactional realization}
\label{sec:realization}

\subsection{Persistent objects and admission}

\system{} implements the relation in Python, SQLAlchemy, and SQLite. \code{CandidateWritePort} appends candidates/evidence, \code{AuthorityReadPort} loads persisted objects, and \code{FactAdmissionPort} admits a complete bundle. Recognition receives the candidate facade; trusted review receives admission. This separates capabilities within the process while retaining the host trust boundary.

A certificate retains target, canonical proposal, producer/version, selection artifact, expected fact version, evidence hash, and canonical locator. A decision names reviewer and candidate; its immutable binding fixes the exact certificate and authorized value. Transitions preserve this chain for Accept and Correction. The revocable principal-role mapping is checked inside the transaction.

Admission reloads evidence and reconstructs its canonical locator, checking ownership, content hash, and record/field location against the certificate. The adapter repeats authoritative preflight checks transactionally:
\begin{enumerate}[leftmargin=*]
\item reload the field domain, current version, complete predecessor, candidates, evidence, and principal policy;
\item derive initial coverage or later changed fields using canonical JSON equality, rejecting duplicate, hidden, empty, or incomplete effects;
\item validate unused identities and the decision--binding--certificate--evidence--transition relation, including agreement of authorized, transition, and successor values;
\item compare-and-swap the expected current version;
\item create one transition per admitted field, copy exact unchanged sources, and commit decision, binding, complete version, projections, and audit together.
\end{enumerate}
CAS is the first authority write. Failure before commit rolls back admission. Unique indexes and foreign keys reinforce bindings and transition uniqueness. The zero-write baseline is immediately before admission, after any candidate or review preparation. Connection parameters and locator rules are in Supplement S1 and the artifact.

The confirmation API receives candidate, value, and principal from its caller and constructs the binding at confirmation. E2 evaluates an earlier server-held review binding. Manual-source compatibility derives a certificate at confirmation and is outside the preexisting-machine-candidate claim. The historical restricted agent interface permits proposal and verification, with confirmation retained by the host (Supplement S5).

\subsection{Reverse trace and source evolution}

Tracing checks each field in every prefix version. Initial and changed fields need their unique transition; unchanged fields retain the exact prior source. The verifier checks source record/field/version, committed value, decision, authorization, certificate, producer, evidence hash/locator, and expected-version relations.

A trace is \code{complete} when these relations agree, otherwise \code{incomplete} with reasons. It does not repair or substitute sources; legacy pre-certificate states are identified separately. Completeness concerns consistency of persisted authorization lineage under the trust boundary in \cref{sec:contract}.
```

### 06-formal-concrete-conformance

| 原 prose 段 | 标签 | 一句理由 |
|---|---|---|
| P1: 11 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P2: 52 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P3: 42 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P4: 43 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P5: 51 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P6: 61 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P7: 63 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P8: 39 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P9: 96 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |

压缩后的完整英文（保留 LaTeX 以便逐句定位；KEEP 段也包含在内）：

```latex
\section{Formal--concrete projection and executable conformance}
\label{sec:conformance}

A test-side abstraction connects selected persisted events to the model:
\begin{equation}
\alpha:\mathrm{PersistedPrePost}\rightarrow\mathrm{BatchAlloyInstance}.
\end{equation}
It independently reads targets, field domains, evidence/locators, certificates, decision/binding rows, version values/sources, transition sets, and pre/post identity sets. Canonical JSON classes become Value atoms, certificates become primitive identities, and a decision/binding becomes Authorization. The complete mapping is in Supplement S2.

A committed wrapper fixes the instance and checks \code{legalAdmission[event, Full]}. A rejected wrapper requires equal full-database digests, state stutter, and failure of Full. Twenty single-dimension mapping mutants exercise context, freshness, authorization, preexistence, transition, and coverage sensitivity. The adapter shares neither the production planner nor the trace builder.

A second oracle reads all SQLite application tables and checks domains, source evolution, transitions, version anchors, lineage, and values. Five relation mutants exercise its sensitivity. The 35-case catalogue includes five legal cases and thirty rejection, corruption, schema-prevention, stateful-evolution, or oracle-mutant cases. Rejections require the expected public error and unchanged deterministic database digest; post-persistence corruption instead requires a changed digest and trace/oracle diagnosis.

Thirteen regressions test canonical equality, including unchanged controls, numeric/Boolean and nested changes, and no-op rejection. Seven fail before the equality repair and all pass afterward. A separate witness-domain repair retains the five class pairs and adds identity and copy-forward controls (Supplement S2).

Nine intended projections cover singleton and multi-field Accept and Correction, mixed batches, initial coverage, copy-forward, staleness, and whole-batch rejection. They provide selected bounded correspondence. Three scope differences remain explicit: concrete post-initial no-ops are rejected; SQLite uniqueness prevents one modeled duplicate-source state; and concrete prefix tracing checks corruptions and predecessor relations beyond the formal single-level anchor predicate. Thus the positive Alloy assertion concerns one encoded admission step under its well-formed-pre-state condition.
```

### 07-evaluation-protocol

| 原 prose 段 | 标签 | 一句理由 |
|---|---|---|
| P1: 15 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P2: 87 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P3: 97 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P4: 76 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P5: 63 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P6: 98 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P7: 45 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P8: 125 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P9: 55 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P10: 80 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P11: 61 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P12: 79 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P13: 54 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P14: 84 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P15: 85 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P16: 82 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P17: 57 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P18: 63 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P19: 61 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P20: 82 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |

压缩后的完整英文（保留 LaTeX 以便逐句定位；KEEP 段也包含在内）：

```latex
\section{Evaluation protocol}
\label{sec:evaluation}

\subsection{Questions and evidence layers}

\begin{description}[leftmargin=2.6em,labelwidth=2.1em]
\item[RQ1] Do the formal and concrete checks support the admission contract, and what changes when a rich event journal records the exact reviewed candidate?
\item[RQ2] Which inconsistencies between recorded review intent and confirmation can server-held session binding reject, and which remain outside its guarantee?
\item[RQ3] What admission, reverse-trace, and storage costs occur on the repaired implementation under the declared workloads?
\end{description}

The retained Alloy, projection, and 35-case catalogue evidence is distinguished from E1--E3, which use the equality-repaired reference at commit \code{c6d512843c905cab6d8521dd8c914f7fb26d85ae}. Before the new studies, 85 selected implementation regressions and ten harness checks were rerun. The prospective local protocol, pilot amendments, environment, raw receipts, and execution status are documented in Supplements S1 and S6. E1--E3 make no hosted-model calls; historical agent runs remain separate in S5.

\Cref{fig:evidence-route} connects these evidence layers to the questions they answer. Constructed execution, provenance-answer, browser-case, and timing denominators remain separate.

\begin{figure}[htbp]
\centering
\includegraphics[width=\textwidth]{figures/refined/figure-2-evidence-route.pdf}
\caption{Evidence route from the conditional characterization to persistence checks and E1--E3. E1 compares instance and value/context policies; E2 compares the original and session-bound confirmation paths; E3 measures call and access costs. E1/E2 counts and E3 timing totals are read from the archived tables and CSV summaries. OpenAI Codex (GPT-6, 27 September 2026) assisted diagram scripting; Matplotlib 3.10.8 rendered the deterministic vectors.}
\label{fig:evidence-route}
\end{figure}

\subsection{RQ1: rich-context and exact-binding comparison}

A separately written \code{sqlite3} journal retains immutable candidates/events, review context, versions, transactions, and complete field sources. Its \emph{context} configuration checks field, version, evidence, and retained context while omitting candidate/certificate identifiers and instance-creation time. Its \emph{exact} configuration adds the reviewed-candidate link. The third arm invokes the reference's actual transaction. We score both instance authorization and the looser value/context policy.

Fifteen inputs cross eleven case families and three mechanisms, giving $15\times11\times3=495$ executions. Twelve deterministically selected archived proposal cells contain four distinct values; three synthetic type controls bring the total to seven. They enter newly constructed histories, rather than complete historical-task replays. Cases exercise Accept, Correction, multi-field admission, equal-valued candidate and different-evidence substitutions, staleness, replay, unauthorized value, and three interrupted transaction locations. Supplement S6 lists the inputs and cases.

After acceptance, an independent reader checks six provenance questions on three fields: proposal, authorized value, reviewer, reviewed candidate, current value, and source version. Each accepted history contributes eighteen answers, classified as correct, wrong, ambiguous, or unavailable. Rejection requires the expected reason and unchanged logical fact-database digest, measured after authorization preparation. Prior review records may persist. Original strengthened-baseline continuity checks have a separate denominator.

\subsection{RQ2: review-to-confirmation boundary}

Local Chrome/Playwright runs an instrumented review fixture backed by \code{ReviewForms.confirm}. An independent driver records the displayed candidate, proposal, and authorized value before confirmation. Three JSON inputs cross ten interactions and two paths, giving sixty cases; six confirmations separately prepare replay setups. Positive controls cover acceptance, correction, and reselection. Candidate/value/principal request substitutions, stale/replayed requests, interrupted commits, and display-only substitution probe distinct boundaries.

The original path is compared with a server-held session binding candidate, version, reviewer, and value. Acceptance, agreement with recorded review intent, and writes on rejection are recorded. Fixed principal labels and a separate session database make this a scripted boundary study; authentication, human attention, and cross-database crash atomicity remain outside its evidence.

\subsection{RQ3: current-version costs}

Two ten-cell admission comparisons contribute 4,000 observations each; a 36-cell trace comparison contributes 14,400. Each cell has five warmups and 200 timed calls per arm in seeded randomized order, for 22,400 timed observations excluding warmups. These measurements come from one machine with uncontrolled background activity; environment versions and full grids are in Supplements S1, S4, and S6.

The mechanism comparison times complete confirmation on shared recognition-source workloads. Construction and database cloning are excluded: the journal opens its connection before timing, whereas the reference may connect lazily inside confirmation. Schema, ORM, validation, and application functionality also differ. These are costs at the declared call boundary, rather than isolated binding overhead.

A separate manual-source materialization ablation times persistence of a prevalidated delta while retaining authority rows, complete sources, transactionality, and CAS. Its result must match the precomputed relational fingerprint. Validation and planning occur outside that timer; its full-path column belongs to a different workload from the mechanism comparison.

The trace comparison holds the verifier fixed and changes three bulk repository reads to identifier enumeration and point lookups. Every returned complete object must agree. The grid varies record width, history length, and total records. Storage fixtures populate full/reduced schemas at three transition scales; their footprint excludes external evidence/model outputs, and the reduced schema has fewer audit obligations.
```

### 08-results

| 原 prose 段 | 标签 | 一句理由 |
|---|---|---|
| P1: 65 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P2: 97 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P3: 48 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P4: 62 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P5: 54 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P6: 62 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P7: 53 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P8: 44 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P9: 67 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P10: 32 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P11: 64 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P12: 59 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P13: 42 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P14: 77 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P15: 53 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P16: 11 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P17: 77 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |

压缩后的完整英文（保留 LaTeX 以便逐句定位；KEEP 段也包含在内）：

```latex
\section{Results}
\label{sec:results}

\subsection{RQ1: exact binding and persisted conformance}

\paragraph{E1: equal-valued candidate separation}
\label{sec:executable-relation-result}
All 495 executions completed without harness errors. The exact journal and reference agreed on all 165 paired decisions and query-answer sets. Each accepted 45 legal cases and rejected 120 without fact-database writes after authorization preparation, including all three rollback locations.

\input{tables/dke/comparator}

The context journal accepted 15 equal-valued substitutions. They satisfy its value/context policy but violate instance authorization; the exact mechanisms therefore make 15 additional rejections under the looser policy. All mechanisms reject substitutions with different retained evidence. Equal-valued candidate substitution isolates what richer context alone still leaves unresolved.

Accepted context-journal histories produced 1,020 correct answers and sixty ambiguous reviewed-candidate answers. Each exact mechanism produced 810 correct answers and none wrong, ambiguous, or unavailable. Totals differ because each accepted history contributes eighteen answers. These observations concern the constructed histories, not independent query workloads.

The original strengthened-baseline continuity run reproduced seven-of-eight single-history agreement, with equal-valued substitution as the separator; its paired-history distinction is a separate ninth check. The richer exact journal closes that gap in E1 by preserving the authorization link. The evaluated relation is therefore enforceable in both storage designs.

\paragraph{Formal and persisted support}
All 72 Alloy outcomes matched the manifests: each profile had six legal, eleven ablation, three source-attack, and two nonempty-precondition witnesses, plus fourteen assertions without counterexamples within scope. The projection produced nine satisfiable intended instances and twenty unsatisfiable mapping mutants. All 35 catalogue cases, two stateful profiles, and 33 rollback/concurrency tests passed in the retained execution.

The illustrative lifecycle retained proposal 100, separately authorized correction 101, exact sources for the other two fields, and a complete trace/export. Six archived AI-origin lifecycles and ten pinned-interface controls also matched their outcomes. The new execution passed 85 selected regressions and ten harness checks. These are separate evidence layers; the retained tests were not all rerun for E1--E3.

\subsection{RQ2: request binding and display controls}

Each path completed thirty browser cases and accepted all nine legitimate controls. The original path accepted nine request substitutions inconsistent with recorded review intent; the server-held gate rejected all nine. Both rejected stale submissions, replays, and precommit interruptions without fact writes.

\input{tables/dke/review}

Both nevertheless accepted three display-only substitutions: the page showed B while server and request continued with A. The original transaction preserves the caller-supplied binding; the gate adds consistency with an earlier server-held review record. Faithful presentation remains a premise for both.

\subsection{RQ3: admission, trace, and storage costs}

\paragraph{Admission}
Both admission comparisons completed ten cells. Shared mechanism queries agreed; materialized states matched their precomputed fingerprints. \Cref{tab:dke-admission-selected} shows representative cells; Supplement S4 retains every cell.

\input{tables/dke/admission-selected}

With 128 fields all changed, median reference confirmation was 712.00~ms and exact-journal confirmation 22.09~ms. Both enforce exact binding; the difference describes the implementation and connection boundaries in \cref{sec:evaluation}. In the separate manual-source ablation, full confirmation was 427.59~ms and prevalidated materialization 23.50~ms. The latter excludes validation and planning from timing and is not a complete admission path.

\paragraph{Reverse trace}
All 36 paired cells completed 14,400 calls with identical full returned objects. At 128 fields, 100 versions, and 1,000 records, bulk p50/p95 was 170.24/216.75~ms versus 509.09/595.85~ms for point access, a median ratio of 2.99.

\input{tables/dke/trace}

Bulk tracing used twelve SQL statements in every measured cell; the largest point-access cell used 693. Both arms run the same current verifier, so the difference concerns repository access. Processing, prefix traversal, and memory can still grow with history and fields despite constant round trips.

\paragraph{Schema footprint}
Full-schema sizes were 1.52, 13.16, and 134.53~MiB at the tested transition scales, with roughly 1.1~kB incremental main-database storage per transition relative to the reduced fixture.

\input{tables/dke/storage}

These synthetic fixtures exclude external evidence and model-output files. The reduced schema has fewer audit obligations; the measurements characterize their footprints.

\subsection{Separate historical integration}
\label{sec:historical-integration}

The archived matrix retains 1,260 planned runs. Strict benign yield was 320/360 (88.89\%) and post-hoc endpoint yield 331/360 (91.94\%), with 25 unscorable runs; all 93 runtime failures remain recorded. Fixed host checks recorded no unauthorized mutation in 720 invalid-tuple calls or 179 capability-unavailable branches, the latter making no admission call. Supplement S5 preserves conditional denominators, configuration-specific failures, and annotation. These support restricted-interface integration separately from E1/E2.
```

### 09-discussion-threats

| 原 prose 段 | 标签 | 一句理由 |
|---|---|---|
| P1: 101 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P2: 89 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P3: 91 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P4: 73 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P5: 88 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P6: 99 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P7: 90 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P8: 86 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P9: 75 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P10: 80 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P11: 72 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P12: 77 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P13: 60 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P14: 87 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |

压缩后的完整英文（保留 LaTeX 以便逐句定位；KEEP 段也包含在内）：

```latex
\section{Discussion and limitations}
\label{sec:discussion}

\subsection{Correction-aware authority as a data relation}

The result links three roles that a final value cannot recover: proposal origin, human value authority, and committed field source. Admission binds these roles to one candidate and fresh predecessor while constructing a complete successor. The paired histories explain the corresponding observation distinctions; the formal, projection, and transaction checks test their enforcement.

The journal comparison locates the contribution in this relation. Exact binding gives the journal and reference the same 165 decisions and query-answer sets. Instance accountability requires rejecting the 15 context-equivalent substitutions; value/context accountability permits them. Applications should choose the granularity that their audit questions require. Renewed approval without a value change belongs to a separate review-event path, because concrete post-initial admission creates transitions only for changed values.

\subsection{Trust and validity boundaries}

The server-held gate demonstrates request-to-review consistency for the tested substitutions. Display-only controls retain a separate presentation boundary. Host authentication, review-channel integrity, principal policy, hashing/canonicalization, and database execution remain trusted. Recorded lineage identifies authorization and sources, not factual truth. Evidence checks compare stored hashes and locators rather than re-reading external bytes; unnoticed external replacement requires immutable storage or additional integrity checks. Commit-entry policy revalidation does not cancel later-revoked in-flight operations (Supplement S2).

Proposition 1 concerns the declared projections, opaque handles, and failure model. Alloy checks finite scopes; selected projections establish bounded correspondence. The formal no-op, schema-uniqueness, and trace-prefix differences are stated in \cref{sec:conformance}. Distributed revocation, other database engines, deletion/redaction, and retention expiry require additional design and evidence.

E1 reuses seven distinct proposal values in constructed cases; the journals are same-study implementations. E2 uses a local scripted fixture, fixed principals, and separate session/fact databases. Its evidence does not extend to human attention, hostile hosts, or cross-database crash atomicity. Historical hosted-agent outcomes and author-involved annotation have separate scoring, missingness, and failure records in Supplement S5.

E3 characterizes one machine with uncontrolled background activity. The admission implementations differ in schema, ORM, validation, features, and connection lifecycle; the materialization timer omits validation/planning. The paired trace study holds the verifier fixed, identifying an access-pattern difference rather than total cost independent of history. Complete workload and validity details are in Supplements S4, S6, and S7.

\subsection{Applying the relation}

Adoption begins with the approval policy and one correction traced through persisted records. Identify the reviewed candidate, authorized value, predecessor check, and changed/unchanged source links. Retain a legal control and a failure probe for each boundary. Supplement S3 provides the worked example and inspection checklist. An independently implemented deployment with operational reviewers would provide the next test of transferability.
```

### 10-conclusion

| 原 prose 段 | 标签 | 一句理由 |
|---|---|---|
| P1: 65 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |
| P2: 97 words | COMPRESS | 合并本节重复解释，保留对象、作用、证据和限定；新英文见下方。 |

压缩后的完整英文（保留 LaTeX 以便逐句定位；KEEP 段也包含在内）：

```latex
\section{Conclusion}
\label{sec:conclusion}

Correction-aware admission links an exact persisted candidate, explicit human-authorized value, fresh predecessor, and complete successor with total field sources. Five paired histories establish class-wise irredundancy within the declared observation model. Bounded relational analysis, selected persisted-state projections, and transaction tests connect the relation to an executable realization.

The exact-binding event journal and reference agree on all 165 corresponding constructed cases; equal-valued substitution separates their decisions from context-only approval. A review-session gate rejects the tested request substitutions while display integrity remains assumed. Current-version workloads characterize admission and source reconstruction, including bulk/point tracing with the same verifier. Together, these results make the correction-to-authority relation enforceable at commit and queryable afterward under the stated trust and workload boundaries.
```

## 结构化内容标签与迁移锚句

| 内容 | 标签 | 正文保留 | 移动范围 / 理由 |
|---|---|---|---|
| Formal definitions / Proposition 1 / protected equations | KEEP | 完整定义、命题和方程 | 核心关系和限定不变；自动逐字核对 11 个带标签方程。 |
| Complete observation functions and finite history tuple | MOVE-SUPP | “The complete observation functions are given in Supplement S2.” “Supplement S2 gives the complete functions, finite tuple, and checker rules.” | 原观察函数表、完整 tuple、域和 opaque-handle 规则；S2。 |
| Operational P0–P6 table and five-witness proof | KEEP | 完整保留于正文 Contract | 删除补充材料里的相同副本，不删除定义或证明。 |
| Mapping/class-to-evidence tables and detailed Alloy commands | MOVE-SUPP | “The complete mapping is in Supplement S2.” | 完整映射表、class evidence 表、14 assertions 的分类和两组 bounds；S2。 |
| Complete admission grid | MOVE-SUPP | “Supplement S4 retains every cell.” | 全 10 cells 和 ablation grid 保留在 S4；正文显示 1/1、32/32、128/128 三个代表格点，数值原样复制。 |
| Environment, setup, hooks, source receipts and scoring | MOVE-SUPP | “The prospective local protocol, pilot amendments, environment, raw receipts, and execution status are documented in Supplements S1 and S6.” | 小版本、journaling、warmup、seed、query 状态、timer 和 replay 规则；S1/S6。 |
| Detailed validity boundaries | MOVE-SUPP | “Complete workload and validity details are in Supplements S4, S6, and S7.” | JSON serialization、trace traversal、cross-database/session 边界、measurement limits；S7。 |
| Repeated contribution/architecture/background descriptions | DELETE | C1–C3 与 Contract 是主叙述位置 | 删除重复说法；论文贡献为 relation + conditional characterization，不归因于新数据库 primitive。 |
| Historical integration detail | MOVE-SUPP | 正文仍报告 1,260、320/360、331/360、25、93、720 与 179 | 配置、conditional denominator 和 annotation 的完整表在 S5。 |

## 图解设计与准确性

图 1 是构造例，而非数据结果。参考风格为深蓝标题、浅蓝分区、蓝/橙对照和方向箭头；只保留能解释 admission relation 的对象。图 2 是证据路线：formal classes、persisted conformance、E1 政策差异、E2 review boundary 和 E3 costs。

OpenAI 生图仅提供设计原型。原型混淆了 field source 的 transition 身份，因此未进入正文。最终图为确定性 PDF/SVG 矢量版；脚本读取 E1/E2 tables 和 E3 CSV，断言计数并记录数据源哈希。图注与 AI declaration 均披露工具、可获得的版本、日期及用途。

检查记录见 compression-verification.json；本次没有重跑原科研实验，编辑检查不作为新实验结果。
