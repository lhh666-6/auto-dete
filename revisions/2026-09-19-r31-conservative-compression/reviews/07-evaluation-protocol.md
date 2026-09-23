# Evaluation protocol

原字数：1698；压缩后：1361；压缩比例：19.85%。

口径：正文叙述及 contribution 文本；不计标题、引文/交叉引用标记、公式、表格、图注和参考文献。

**是否影响 scientific claim：No。** 这是逐段编辑核对结论；静态保护检查见总报告，不替代重新验证科研结果。

## P01 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
The protocol tests relational encodings (RQ1--RQ2), persisted realization and controls (RQ3--RQ5), and engineering cost and integration (RQ6--RQ8). Proposition 1 provides the observation-level argument; live-agent repetition measures integration.
\begin{description}[leftmargin=2.6em,labelwidth=2.1em]
\item[RQ1] Does Full separate the declared legal, rejected, and trace-corrupt histories in both Alloy profiles?
\item[RQ2] Does each selected conjunct removal admit a paired malformed history that Full rejects?
\item[RQ3] Do the selected persisted executions map to the Full batch relation?
\item[RQ4] Does the service handle all catalogue cases without partial admission?
\item[RQ5] Does the lifecycle preserve Correction, copied sources, complete trace, and matching export?
\item[RQ6] What admission, trace, and storage costs occur on the frozen grid?
\item[RQ7] Does the pinned harness expose proposal/verification while reserving admission for the host, with checkable lifecycle and failure behavior?
\item[RQ8] How do task outcomes vary across qualified configurations, and do separate host checks preserve authoritative state?
\end{description}
```

## P02 — MOVE-SUPP

理由：将系统和依赖版本、连接参数原样移至补充，正文保留冻结协议和可复现入口。

原段落：

```latex
Immutable manifests bind each baseline and extension to source, dependencies, configuration, raw receipts, and normalized inputs (Supplement S1). The repeated Final additionally binds model/matrix settings and the tool surface. Concrete runs used Windows 10 build 26200, CPython 3.11.9, SQLAlchemy 2.0.51 where reported, and SQLite 3.45.1. Foreign keys and a 5,000-ms busy timeout were enabled on every connection; the performance runs additionally used WAL and \code{NORMAL} synchronization, with no implicit lock retry.
```

正文保留版本：

```latex
Immutable manifests bind source, dependencies, configuration, raw receipts, and normalized inputs; Final also fixes model/matrix settings and the tool surface. Supplements S1 and S4 retain the manifests and exact execution environment.
```

迁移范围：原段落全文，逐字保留于 Supplement S4 / Frozen execution environment。

## P03 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
RQ1--RQ2 use the complete manifest of 36 commands in each Alloy profile. RQ3 uses nine intended projections and twenty mapping mutants. RQ4 uses the versioned 35-case catalogue. Rejected calls compare the full canonical database digest, while post-persistence corruption has a separate expected outcome.
```

## P04 — MOVE-SUPP

理由：将具体并发重复网格移入补充，保留状态对照、覆盖要求及安全/活性判据。

原段落：

```latex
Stateful evidence uses a Hypothesis rule-based model whose own value/source state is compared with persisted snapshots and query traces. Its companion coverage test requires every declared rule to execute. Transactional tests include all pre-commit failpoints and real contending calls. The declared concurrency grid contains 50 two-thread repetitions, 20 four-thread repetitions, 20 eight-thread repetitions, and 20 two-process controls. Safety requires at most one complete winner and no loser authority-row identifiers; liveness requires at least one complete winner in the exercised configuration. The test denominator counts declared tests and profiles, not their internal iterations.
```

正文保留版本：

```latex
Stateful tests compare an independent value/source model with persisted snapshots and query traces, with mandatory rule coverage. Failpoint and concurrent-call tests require at most one complete winner, no loser authority-row identifiers, and at least one winner for liveness; Supplement S4 retains the concurrency grid and test/profile counting rule.
```

迁移范围：原段落全文，逐字保留于 Supplement S4 / Stateful and concurrent test grid。

## P05 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
RQ5 uses a synthetic/public three-field form. Version 1 establishes quantity, batch, and operator. Version 2 corrects a machine quantity candidate of 100 to an authorized value of 101 while copying forward batch and operator. The exported values and reverse trace are checked against the final record.
```

## P06 — COMPRESS

理由：压缩集成控制的功能描述，保留六例、十例及与 live runs 的区分。

原段落：

```latex
Six archived AI-origin lifecycle cases check that a persisted model output can enter the Accept/Correction and rejection paths. Ten keyless pinned-plugin cases check tool exposure, host admission, unloading, and receipt integrity. These controls establish input and interface compatibility; RQ8 separately observes live tool use. Detailed setups are retained in Supplement S2.4.
```

修改后的英文：

```latex
Six archived AI-origin cases exercise Accept/Correction and rejection using persisted model output. Ten keyless pinned-plugin cases test tool exposure, host admission, unloading, and receipt integrity. These establish input/interface compatibility; RQ8 observes live tool use. Supplement S2.4 retains the setups.
```

## P07 — COMPRESS

理由：压缩重复比较叙述，保留 B1/E1/B2 的不同控制目的及证据路径。

原段落：

```latex
The nine-case SQLite demonstrator holds immutable candidates, value-bound approvals, complete audits, and atomic CAS common across policies. Strengthened control B1 extends transaction, audit-integrity, evidence, versioning, and reconstruction safeguards without adding explicit authorization-to-candidate binding. Identity-isolation control E1 fixes baseline-visible observations while varying agreement with the test-side review oracle. B2 records richer review context to test the resulting boundary. Supplement S3 specifies their construction, projections, and persisted-state criteria. These constructed controls accompany RQ5, with evidence in \code{evidence/r27-standard-practice-baseline/} and \code{evidence/strong-baseline/}.
```

修改后的英文：

```latex
The nine-case SQLite demonstrator shares immutable candidates, value-bound approvals, complete audits, and atomic CAS across policies. B1 strengthens transaction, audit-integrity, evidence, versioning, and reconstruction safeguards without explicit authorization-to-candidate binding. E1 fixes baseline-visible observations while varying agreement with a test-side review oracle; B2 adds review context. Supplement S3 specifies constructions, projections, and persisted-state criteria. RQ5 evidence is in \code{evidence/r27-standard-practice-baseline/} and \code{evidence/strong-baseline/}.
```

## P08 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
\paragraph{Live-agent task execution and separate host checks}
The locked Final matrix crosses three qualified configurations (G1: OpenAI \code{gpt-5.6-luna}, low reasoning; G2: OpenAI \code{gpt-5.6-terra}, low reasoning; D1: DeepSeek \code{deepseek-v4-flash}), three prompt variants, fourteen scenarios, and ten repetitions, yielding $3\times3\times14\times10=1{,}260$ planned executions. Every run uses an independent database and a frozen two-tool surface exposing \code{auto_decte_propose} and \code{auto_decte_verify}; no model-facing confirmation or fact-write capability exists.
```

## P09 — COMPRESS

理由：压缩资格规则说明，保持全部比例和 Final 后不剔除规则。

原段落：

```latex
A frozen 28-cell pilot excluded configurations with runtime-failure rates above 5\%: D2 (5/28, 17.86\%) and D2b (2/28, 7.14\%) failed; G1 (0/28), G2 (1/28), and D1 (0/28) qualified. Once Final started, all 1,260 planned runs were retained without replacement or post-hoc exclusion. D1's subsequent failures describe execution reliability, not a further selection rule.
```

修改后的英文：

```latex
A frozen 28-cell pilot excluded runtime-failure rates above 5\%: D2 (5/28, 17.86\%) and D2b (2/28, 7.14\%) failed; G1 (0/28), G2 (1/28), and D1 (0/28) qualified. Final retained all 1,260 planned runs without replacement or post-hoc exclusion. Later D1 failures measure reliability, not reselection.
```

## P10 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
B1--B4 cover propose--verify, Correction, multi-field proposal, and stale-state recovery. The ten challenge scenarios cover confirmation instructions, contextual/value/evidence/stale substitutions, replay, partial admission, and unavailable confirmation. Task behavior, runtime reliability, and host authority are measured separately.
```

## P11 — COMPRESS

理由：简化分母及提示变体说明，保留缺失处理和研究设计限定。

原段落：

```latex
Execution yield uses all 360 planned benign runs; unscored runs contribute no demonstrated success and receive no imputed verdict. Conditional rates use the 335 scorable runs. This is a reporting choice, not retrospective preregistration or a randomized trial. Prompt variants preserve the semantic payload: V1 uses direct instructions, V2 an operations-reviewer role, and V3 adds informational background.
```

修改后的英文：

```latex
Execution yield includes all 360 planned benign runs; unscored runs supply neither demonstrated success nor imputed verdicts. Conditional rates use 335 scorable runs. These reporting choices imply neither retrospective preregistration nor a randomized trial. Prompt variants preserve the payload: V1 is direct, V2 uses an operations-reviewer role, and V3 adds informational background.
```

## P12 — COMPRESS

理由：压缩 lexical/semantic 区分，保留历史标签不替换。

原段落：

```latex
The B4 strict verdict includes the literal word \code{stale}; it therefore measures compliance with that frozen output rule as well as the call sequence, not semantic recognition. The endpoint sensitivity removes this lexical requirement without overwriting the historical verdict.
```

修改后的英文：

```latex
B4's strict verdict requires the literal word \code{stale}, measuring compliance with a frozen lexical and call-sequence rule rather than semantic recognition. Endpoint sensitivity removes that lexical requirement while preserving the historical verdict.
```

## P13 — COMPRESS

理由：缩短 secondary endpoint 的规则复述，保留顺序和所有限制。

原段落：

```latex
For the sensitivity rule, each declared field must have at least one exact proposal followed by successful verification of its returned certificate. B4 additionally requires the designated stale certificate to have been verified before that replacement proposal. Additional calls are allowed; this post-hoc task criterion does not establish absence of incorrect intermediate proposals or general recovery competence.
```

修改后的英文：

```latex
Endpoint sensitivity requires an exact proposal for each field followed by successful verification of its certificate. B4 also requires verification of the designated stale certificate before replacement. Extra calls are allowed; this post-hoc criterion establishes neither absence of incorrect intermediate proposals nor general recovery competence.
```

重复位置与主叙述位置：Table of benign criteria owns the full side-by-side endpoint definitions.

## P14 — COMPRESS

理由：精简输入审计与规则修复叙述，保留全部计数及非独立语义验证限定。

原段落：

```latex
A retrospective scenario audit checks all 1,260 frozen prepared inputs and their embedded prompt contexts and maps each scenario to the endpoint it can support (Supplement S2.6). This is an input/measurement-scope audit, not independent validation of semantic labels. A post-hoc script coded 174 context and 151 stale outputs under an author-specified rubric. Repair v2.1 corrects denial scope and equivalent field-identifier contrasts, changes 11 of 325 historical labels, and retains the other labels (Supplement S2).
```

修改后的英文：

```latex
A retrospective audit maps all 1,260 frozen inputs and embedded contexts to supported endpoints (Supplement S2.6), checking measurement scope rather than independently validating semantic labels. An author-specified post-hoc rubric coded 174 context and 151 stale outputs. Repair v2.1 corrects denial scope and equivalent field-identifier contrasts, changing 11 of 325 historical labels while retaining the rest (Supplement S2).
```

## P15 — COMPRESS

理由：压缩标注流程，保留所有可见/隐藏字段、盲法限制、连接规则与无仲裁口径。

原段落：

```latex
After rule labels were frozen, second author X.W. coded the same 325 shuffled outputs under the frozen affirmative-acknowledgment rubric (1/0), providing a rationale for every row. Only endpoint family and full assistant text were visible; old labels, configurations, run/scenario identifiers, prompt variants, and repetitions were hidden, although textual clues remained. X.W. knew the study purpose, so this is author-involved blinded coding rather than third-party validation. Exact text matching after line-ending normalization linked all rows. We report human--rule agreement against v2.1 without adjudication or label replacement (Supplement S2).
```

修改后的英文：

```latex
After rule-label freezing, second author X.W. coded 325 shuffled outputs under the affirmative-acknowledgment rubric (1/0), giving a rationale for each. Only endpoint family and full text were visible; labels, configurations, run/scenario identifiers, variants, and repetitions were hidden. Textual clues and knowledge of study purpose limit this author-involved blinding. Line-ending-normalized exact text matched every row. We report human--rule v2.1 agreement without adjudication or label replacement (Supplement S2).
```

## P16 — COMPRESS

理由：简化重复表述，保留参与者、量表、辅助翻译、盲法差异和两种复核角色。

原段落：

```latex
Separately, X.W. and one non-author volunteer independently coded all 360 benign runs using the same frozen terminal-completion rubric (1 = completed, 0 = not completed, 9 = unable to determine), manual, and original English text. Optional LLM-assisted Chinese translations were logged and treated as non-authoritative aids. Both coders were blind to rule labels and configuration identifiers; the volunteer was additionally blind to prompt variants, repetitions, and hypotheses, whereas X.W. knew the hypotheses. First author L.H. adjudicated their sole disagreement and separately reviewed eleven human--rule disagreements under the strict-trajectory criterion, preserving the original completion labels. The 25 unscorable runs remain outside the 335-run primary comparison. \Cref{sec:results} reports agreement and adjudication for these author-involved measurements.
```

修改后的英文：

```latex
X.W. and a non-author volunteer independently coded all 360 benign runs using the frozen terminal-completion rubric (1 = completed, 0 = not completed, 9 = unable to determine), manual, and original English. Optional LLM-assisted Chinese translations were logged as non-authoritative aids. Both were blind to rule labels and configurations; the volunteer was also blind to variants, repetitions, and hypotheses, which X.W. knew. L.H. adjudicated their sole disagreement and separately reviewed eleven human--rule disagreements against the strict criterion, preserving completion labels. The 25 unscorable runs remain outside the 335-run comparison (\cref{sec:results}).
```

## P17 — COMPRESS

理由：压缩 A3 歧义解释，保留全部任务条件和不得合并的统计口径。

原段落：

```latex
A2 supplies an explicit target record. A3 supplies no unique target field in any of its 90 prepared inputs; its challenge certificate belongs to the second listed field, while the host separately targets quantity. Responses matching that listed field are defensible. Accordingly, A2 and A3 are separate and A3 is exploratory, with no merged context-recognition rate. Stale indicators use B4/A6 and unavailable-capability attempts use A10.
```

修改后的英文：

```latex
A2 specifies a target record; none of A3's 90 inputs specifies a unique target field. A3's certificate belongs to the second listed field while the host targets quantity, making listed-field responses defensible. We therefore report A2 separately and A3 as exploratory, without a merged context-recognition rate. Stale indicators use B4/A6; unavailable-capability attempts use A10.
```

## P18 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
The 899 authority-evaluable challenges comprise two different host operations:
\begin{table}[tb]
\centering
\footnotesize
\caption{Composition and model-output dependence of the authority endpoint.}
\label{tab:authority-dataflow}
\begin{tabularx}{\columnwidth}{@{}lrr>{\raggedright\arraybackslash}X@{}}
\toprule
Cells & $N$ & Admission call & Challenge input \\
\midrule
A2--A9 & 720 & yes & fixed host-constructed invalid tuple; not generated from model output \\
A1, A10 & 179 & no & host records \code{CAPABILITY\_UNAVAILABLE}; model behavior is scored separately \\
\bottomrule
\end{tabularx}
\end{table}
The 0/720 and 0/179 components are the interpreted results; their 0/899 sum is retained only for complete accounting. No challenge parameter was synthesized from the model's answer; the model trace can vary, but the host executes the predeclared branch.
```

## P19 — COMPRESS

理由：集中保留依赖性、非总体推断和零事件边界，压缩冗余修饰。

原段落：

```latex
Existing run-level exact binomial intervals are retained as conditional descriptive calculations. They ignore dependence within the 36 benign configuration--prompt--scenario cells (three configurations, three prompts, four scenarios, ten repetitions each); they are not cluster-adjusted intervals and do not establish population-level model differences. Authority outcomes remain counts of executed host operations, with no zero-event population bound. Raw and normalized evidence is indexed in Supplement S1.
```

修改后的英文：

```latex
Run-level exact binomial intervals are conditional descriptive calculations. They ignore dependence within 36 benign configuration--prompt--scenario cells (three configurations, three prompts, four scenarios, ten repetitions), so they are neither cluster-adjusted nor evidence of population-level model differences. Authority results count host operations without a zero-event population bound. Supplement S1 indexes raw and normalized evidence.
```

## P20 — MOVE-SUPP

理由：将基础 seed、warmup 与试验次数原样移入补充。

原段落：

```latex
The performance protocol uses seed 20260823, five warmups, and 200 measured trials per cell.
```

正文保留版本：

```latex
Supplement S4 records the fixed seeds, warmups, and trial counts for the cost protocols.
```

迁移范围：原段落全文，逐字保留于 Supplement S4 / Base performance protocol。

## P21 — MOVE-SUPP

理由：将完整网格、种子和逐对象时序移至补充，正文保留等价性要求和成本差的解释边界。

原段落：

```latex
The feature-equivalent persistence ablation uses ten unique field/change cells from 1, 8, 32, and 128 total fields with 1, 4, or all fields changed, five warmups, and 200 measured pairs under seed 20260828. Before timing, one full admission generates a relational delta. The materialization arm applies that exact post-state---complete snapshot and source map, candidate certificates, decisions, authorization bindings, transitions, audit, one transaction, and form-version compare-and-swap---while moving certificate/lineage validation, admission-plan derivation, and authority-object construction outside the timed region. Every cell must match the full reference state's canonical fingerprint. The generic delta materializer differs from the production persistence path, so the measured gap descriptively combines excluded validation/planning work with implementation-path differences.
```

正文保留版本：

```latex
The admission ablation compares the full path with materialization of the same complete authority state under one transaction and version CAS; every cell must match the reference fingerprint. Validation/planning and authority-object construction occur outside materialization timing, and its generic persistence path differs, so the gap combines excluded work with implementation-path differences (Supplement S4).
```

迁移范围：原段落全文，逐字保留于 Supplement S4 / Persistence-equivalent admission protocol。

## P22 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
The historical comparator omits authority relations and provides only a lower-bound reference; its randomized paired protocol and complete cell tables are retained in Supplement S1--S2.
```

## P23 — MOVE-SUPP

理由：将完整三维网格移至补充，保留观测数和 trace-complete 指标定义。

原段落：

```latex
The trace grid crosses 1, 8, 32, and 128 fields; 1, 10, and 100 versions; and 1, 100, and 1,000 records. Each of the 36 cells uses one persistent connection and 200 measured trials after five warmups, giving 7,200 observations. The metric is latency of a trace required to return complete.
```

正文保留版本：

```latex
Trace costs use 36 field/version/record cells, five warmups, and 200 trials per cell (7,200 observations), requiring every trace to return complete. Supplement S4 retains the full grid and connection protocol.
```

迁移范围：原段落全文，逐字保留于 Supplement S4 / Trace workload grid。

## P24 — COMPRESS

理由：精简优化结构和复测步骤，保留硬上界、全网格对照和复杂度。

原段落：

```latex
The optimized implementation replaces per-version and per-field database reads with a twelve-statement database snapshot assembled for the form and in-memory indexes over transitions, certificates, bindings, and evidence. The same 36-cell/7,200-observation protocol is rerun and compared cell for cell with the recorded baseline execution. A hard check rejects any optimized observation exceeding twelve SQL statements. The algorithm performs constant database round trips with respect to $V$ versions and $F$ fields and $O(VF+T+C+E)$ in-memory work for $T$ transitions, $C$ certificates, and $E$ evidence rows.
```

修改后的英文：

```latex
The optimized trace replaces per-version/field reads with a form-scoped twelve-statement snapshot and in-memory transition, certificate, binding, and evidence indexes. It reruns all 36 cells/7,200 observations against the recorded baseline; a hard check rejects observations above twelve SQL statements. Database round trips are constant in $V$ versions and $F$ fields; in-memory work is $O(VF+T+C+E)$ for $T$ transitions, $C$ certificates, and $E$ evidence rows.
```

## P25 — COMPRESS

理由：缩短存储协议叙述，保留规模、测量对象和一致性要求。

原段落：

```latex
Separate lower and full SQLite databases are populated at 1,000, 10,000, and 100,000 transitions. After checkpointing, the primary database size is measured and the full-minus-lower difference reported. Foreign-key checks must be empty and residual WAL/SHM sizes zero. The grid characterizes the recorded SQLite schema and configuration.
```

修改后的英文：

```latex
Separate lower/full databases contain 1,000, 10,000, and 100,000 transitions. After checkpointing, we report the primary-file full-minus-lower size, requiring empty foreign-key failure lists and zero residual WAL/SHM bytes. This characterizes the recorded SQLite schema/configuration.
```

## P26 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
\paragraph{Figure generation}
Figures~3 and~4 use deterministic Matplotlib scripts to plot the frozen JSON inputs; no plotted element is model-generated. OpenAI Codex (\code{gpt-6-astra}, OpenAI) assisted with the scripts. Inputs, scripts, and regeneration commands are deposited in Supplement~S1.
```

公式、表格、图及其图注统一为 **KEEP**：保持数学关系、结果和解释不变。
