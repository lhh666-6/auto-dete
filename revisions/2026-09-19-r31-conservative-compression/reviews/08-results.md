# Results

原字数：1615；压缩后：1294；压缩比例：19.88%。

口径：正文叙述及 contribution 文本；不计标题、引文/交叉引用标记、公式、表格、图注和参考文献。

**是否影响 scientific claim：No。** 这是逐段编辑核对结论；静态保护检查见总报告，不替代重新验证科研结果。

## P01 — DELETE

理由：删除无科学内容的章节导航句；小节标题已给出顺序。

原段落：

```latex
Results follow the protocol from bounded relational checks to persisted behavior, evaluated-control separation, and engineering cost and integration.
```

无替换文字；仅删除导航性重复。

重复位置与主叙述位置：Evaluation protocol and Introduction roadmap already give this order.

## P02 — COMPRESS

理由：缩短结果枚举，保持 72/22/14 与各类见证计数及覆盖范围。

原段落：

```latex
All 72 Alloy outcomes matched the current command manifest. In each profile, the Analyzer found six legal witnesses, eleven ablation witnesses, three trace-attack witnesses, and two nonempty witnesses to the positive trace assertion's precondition (22 SAT outcomes); fourteen assertion commands returned UNSAT. The added precondition witnesses cover initial admission and admission with a trace-complete predecessor and unchanged-field copy-forward. S2 reproduced the S1 outcome classes (\cref{tab:alloy-outcomes}).
```

修改后的英文：

```latex
All 72 Alloy outcomes matched the current manifest. Each profile returned 22 SAT outcomes: six legal, eleven ablation, three trace-attack, and two positive-trace-precondition witnesses; fourteen assertions returned UNSAT. The added witnesses cover initial admission and admission with a trace-complete predecessor and unchanged-field copy-forward. S2 reproduced S1's outcome classes (\cref{tab:alloy-outcomes}).
```

## P03 — COMPRESS

理由：精简解释，保留有界性和 stutter 结论。

原段落：

```latex
Both profiles therefore witness legal and source-corrupt histories. Full's rejection wrappers stutter on the declared malformed attempts, and preservation checks find no counterexample within the encoded scopes.
```

修改后的英文：

```latex
Both profiles witness legal and source-corrupt histories. Full's rejection wrappers stutter on declared malformed attempts; preservation checks find no counterexample within the encoded scopes.
```

## P04 — COMPRESS

理由：压缩对照重复描述，保留同一 item set 与两个结果。

原段落：

```latex
All eleven conjunct-removal operators produced a paired witness with one malformed item and at least one Full-valid item. The reduced contract admitted a non-stuttering effect, while Full rejected the same item set with a stuttering post-state. \Cref{tab:distinction-evidence} maps the covered failure classes to their encodings.
```

修改后的英文：

```latex
All eleven conjunct removals produced a paired witness containing one malformed and at least one Full-valid item. The reduced contract admitted a non-stuttering effect; Full rejected the same item set with stutter. \Cref{tab:distinction-evidence} maps classes to encodings.
```

## P05 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
The ablations exercise $D_C$, $D_V$, $D_F$, and $D_B$ encodings; three source attacks exercise $D_S$. This finite sensitivity evidence is separate from Proposition~1's observation-omission construction. Principal membership remains fixed.
```

## P06 — COMPRESS

理由：精简投影统计描述，保留全部数量与包装条件。

原段落：

```latex
The independent adapter produced 29 fixed formal instances. All nine intended projections were SAT under their committed or stuttering wrappers, and all twenty mapping mutants were UNSAT. The covered cases and two intentional formal--concrete differences are defined in \cref{sec:conformance}.
```

修改后的英文：

```latex
The independent adapter produced 29 fixed instances: all nine intended projections were SAT under their committed/stuttering wrappers, and all twenty mapping mutants were UNSAT. \Cref{sec:conformance} defines cases and the two intentional formal--concrete differences.
```

## P07 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
The production-facing catalogue passed all 35 declared cases with zero failures, using the rejection, corruption, and oracle criteria in \cref{sec:conformance}.
```

## P08 — MOVE-SUPP

理由：将开发版本计数和历史静态检查原样移至补充，正文保留主要回归结果与 catalogue 分母区别。

原段落：

```latex
The two stateful profiles and 33 rollback/concurrency tests passed. The evaluated snapshot records 354 passing tests; revisions added 13 equality regressions and further checks, with 377 tests passing in development and all 389 in the r26 isolated export. The latter includes ten optional-Git checks and two revocation schedules; its implementation/test sources are unchanged here (Supplement S2.5). Earlier Ruff and mypy checks passed, covering 55 typed source files. These regression checks are separate from the 35-case conformance denominator.
```

正文保留版本：

```latex
The two stateful profiles, 33 rollback/concurrency tests, and all 389 tests in the r26 isolated export passed; Supplement S4 records versioned test counts and static checks. These regression checks remain separate from the 35-case conformance denominator.
```

迁移范围：原段落全文，逐字保留于 Supplement S4 / Versioned regression and static-check results。

## P09 — COMPRESS

理由：精简 lifecycle 结果，保留双值、来源和导出一致性。

原段落：

```latex
The lifecycle completed two record versions. Version 2 preserved a machine quantity candidate of 100, stored an independently authorized value of 101, and anchored the resulting quantity transition to the original certificate. The unchanged \code{batch} and \code{operator} fields retained their prior source transitions. The final reverse trace was complete, and the exported values equaled the final record values.
```

修改后的英文：

```latex
The lifecycle completed two versions. Version 2 retained the machine quantity proposal of 100, committed the independently authorized 101, and linked its transition to the original certificate. Unchanged \code{batch} and \code{operator} fields retained their prior sources. The final trace was complete and export matched the final record.
```

## P10 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
The six archived AI-origin cases also matched their declared lifecycle outcomes, supporting compatibility with persisted model output (Supplement S2.4).
```

## P11 — COMPRESS

理由：以观察结果呈现 separator，保留完整强化清单和比较对象。

原段落：

```latex
Both policies in the nine-case SQLite control retain immutable candidates, complete value audits, value-bound approvals, and CAS. They agree on seven of eight single-history outcomes. Equal-valued candidate substitution separates them: value-audit admission accepts a different candidate with the same record, field, and value; candidate-bound admission rejects it. Adding the transaction, audit-integrity, evidence, versioning, replay, grouping, and source-accounting safeguards in Supplement S3 leaves all outcomes unchanged.
```

修改后的英文：

```latex
Both policies in the nine-case SQLite control retain immutable candidates, complete value audits, value-bound approvals, and CAS. They agree on seven of eight single-history outcomes. Under equal-valued substitution, value-audit admission accepts a different candidate with the same record, field, and value; candidate-bound admission rejects it. Strengthening transaction, audit-integrity, evidence, versioning, replay, grouping, and source-accounting safeguards leaves every outcome unchanged (Supplement S3).
```

## P12 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
The paired histories review 100 or 101 from the same candidate pool and both approve and commit 101. Their logical application-table states coincide under both value-bound controls, which omit review-context snapshots; candidate-bound histories retain different reviewed-candidate identities. Both policies reconstruct unchanged-field sources; their observed difference concerns review linkage rather than source reconstruction.
```

## P13 — COMPRESS

理由：压缩 identity control 叙述，保留投影条件、richer-context 边界和 D_V 区分。

原段落：

```latex
The identity-isolation control fixes baseline-visible review observations and varies which equal-valued candidate admission selects. Strengthened value-audit histories remain equal under the declared authority-relevant projection, with several candidates compatible with the recorded authorization. Candidate-bound admission retains the exact review link. Richer review-context snapshots narrow this separation by distinguishing proposals or evidence that differ (\cref{sec:discussion}). These representation-specific results leave Proposition 1's observation-class $D_V$ result intact.
```

修改后的英文：

```latex
Identity isolation fixes baseline-visible review observations while varying the admitted equal-valued candidate. Strengthened value-audit histories remain equal under the authority-relevant projection, leaving several candidates compatible with authorization; candidate-bound admission retains the exact review link. Richer review-context snapshots distinguish differing proposals/evidence and narrow this separation (\cref{sec:discussion}). These representation-specific results preserve Proposition 1's observation-class $D_V$ result.
```

## P14 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
In these constructed comparisons, the demonstrator persists approval before admission. The reference service constructs a decision and binding from the certificate selected by \code{ReviewForms.confirm}, then checks that binding. Both rely on the host for confirmation-channel authentication and fidelity to the earlier review (\cref{sec:contract}). Supplement S3 retains the complete cases and projections.
```

## P15 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
\Cref{fig:evidence-chain} maps the contract and conditional characterization to the implementation checks and experimental observations, with separate inference limits.
```

## P16 — COMPRESS

理由：紧凑报告所有延迟和端点，保留等价性检查及成本差的混合解释。

原段落：

```latex
The persistence-equivalent ablation completed all ten cells and 2,000 measured pairs with zero command failures. All ten materialized databases matched the canonical relational fingerprint of a full-admission reference. Full-path p50 ranged from 17.820 to 194.862 ms, whereas equivalent materialization p50 ranged from 10.469 to 16.479 ms. The paired mean full-minus-materialization difference ranged from 7.455 ms (8 fields, 1 changed) to 182.021 ms (128 fields, all changed). Both arms retain the complete source map and every authority row. The descriptive gap combines excluded validation/planning work with implementation-path differences (\cref{tab:feature-baseline}).
```

修改后的英文：

```latex
The persistence-equivalent ablation completed ten cells and 2,000 pairs without command failure; all ten materialized databases matched the full-reference fingerprint. Full-path p50 was 17.820--194.862 ms, versus 10.469--16.479 ms for equivalent materialization. Paired mean differences ranged from 7.455 ms (8 fields, 1 changed) to 182.021 ms (128 fields, all changed). Both arms retain complete sources and authority rows; the gap combines excluded validation/planning with persistence-path differences (\cref{tab:feature-baseline}).
```

## P17 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
The historical lower-bound admission comparison, including its two negative paired differences, is retained in Supplement S1.1.
```

## P18 — COMPRESS

理由：压缩性能结果句法，保留全部数值、单元条件和顺序执行限定。

原段落：

```latex
The optimized form-scoped snapshot implementation completed all 36 cells and 7,200 observations with zero command failures. Every observation used exactly 12 SQL statements, compared with 16--13,422 in the recorded baseline. Optimized p50 ranged from 4.338 to 53.049 ms and the maximum p95 was 64.360 ms at 128 fields, 100 versions, and one record. Descriptive cellwise p50 ratios ranged from $1.224\times$ to $152.462\times$; at the prior maximum-p50 cell (128 fields, 100 versions, 1,000 records), p50 fell from 7,857.313 to 51.536 ms and p95 from 8,046.960 to 62.025 ms (\cref{tab:trace-optimization}). The ratios compare two sequential executions in the fixed environment.
```

修改后的英文：

```latex
Optimized form-scoped tracing completed 36 cells and 7,200 observations without command failure, using exactly 12 SQL statements each versus 16--13,422 at baseline. Optimized p50 was 4.338--53.049 ms; maximum p95 was 64.360 ms at 128 fields, 100 versions, and one record. Cellwise p50 ratios were $1.224\times$--$152.462\times$. At the prior maximum-p50 cell (128 fields, 100 versions, 1,000 records), p50 fell from 7,857.313 to 51.536 ms and p95 from 8,046.960 to 62.025 ms (\cref{tab:trace-optimization}). These descriptive ratios compare sequential executions in the fixed environment.
```

## P19 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
Historical trace cell values are retained in Supplement S1.1.
```

## P20 — COMPRESS

理由：缩短存储报告，保持所有字节数和基准/一致性条件。

原段落：

```latex
The incremental main-database sizes of the full authority schema relative to the lower population were 1,085,440, 10,772,480, and 111,230,976 bytes at 1,000, 10,000, and 100,000 transitions (\cref{tab:storage-cost}). Foreign-key failure lists were empty, and WAL/SHM bytes were zero after the measurement protocol. RQ6 characterizes the recorded runtime grid; its scaling and portability boundaries are consolidated in \cref{sec:discussion}.
```

修改后的英文：

```latex
The full authority schema added 1,085,440, 10,772,480, and 111,230,976 primary-database bytes over the lower population at 1,000, 10,000, and 100,000 transitions (\cref{tab:storage-cost}). Foreign-key failures were absent and post-measurement WAL/SHM bytes zero. These recorded-grid results retain the scaling and portability limits in \cref{sec:discussion}.
```

## P21 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
\Cref{fig:cost} foregrounds persistence-equivalent admission and optimized reverse trace. Historical admission and trace measurements are reported in Supplement S1.1; storage is reported in \cref{tab:storage-cost}.
```

## P22 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
\FloatBarrier
```

## P23 — COMPRESS

理由：压缩接口结果，保持接口与行为证据的分离。

原段落：

```latex
All ten pinned-plugin cases passed: the interface exposed proposal and verification while retaining host admission, and its rejection and receipt-integrity controls matched the declared outcomes. Supplement S2.4 retains the lifecycle, unloading, and tamper details. This is interface-conformance evidence; the following live runs examine task execution on that interface.
```

修改后的英文：

```latex
All ten pinned-plugin cases passed, exposing proposal/verification while reserving host admission and meeting rejection/receipt-integrity expectations. Supplement S2.4 retains lifecycle, unloading, and tamper details. These establish interface conformance; live runs assess task execution.
```

## P24 — COMPRESS

理由：压缩重复端点解释与表格导航，保留所有分母、比例、区间、11 例构成及独立宿主结果。

原段落：

```latex
The Final matrix contains all 1,260 planned executions. Among 360 planned benign runs, execution yield was 320/360 (88.89\%) under the frozen strict rule and 331/360 (91.94\%) under the post-hoc endpoint rule. Twenty-five runs had no scorable behavior verdict. Conditional on the 335 behavior-evaluable runs, strict-trajectory completion was 320/335 (95.52\%; 95\% exact interval 92.72--97.47\%). Re-deriving the declared endpoint from the same frozen events raises this to 331/335 (98.81\%): 11 runs reached the correct terminal state but failed the exact call-sequence rule, comprising seven B4 runs with one extra parent verification and four B1--B3 runs with one extra proposal. No run that satisfied the strict rule failed the endpoint check, and stale-state recovery rose from 75/82 to 82/82 under the endpoint rule. The increase measures the effect of relaxing the task criterion; independent corroboration would require separate evidence. Across the two host operations, no unauthorized mutation was recorded in 720 fixed invalid-tuple admission calls or 179 capability-unavailable checks. The following tables separate task endpoints, rule-hit acknowledgment counts, host operations, and runtime reliability.
```

修改后的英文：

```latex
Final retained all 1,260 planned executions. Among 360 benign runs, strict-rule yield was 320/360 (88.89\%), versus 331/360 (91.94\%) under the post-hoc endpoint rule; 25 lacked scorable verdicts. Among 335 behavior-evaluable runs, strict completion was 320/335 (95.52\%; 95\% exact interval 92.72--97.47\%). Endpoint completion was 331/335 (98.81\%): eleven terminally successful runs failed the exact sequence, comprising seven B4 runs with an extra parent verification and four B1--B3 runs with an extra proposal. Every strict success met the endpoint criterion; stale recovery rose from 75/82 to 82/82. This increase reflects criterion relaxation, not independent corroboration. Separately, host checks recorded no unauthorized mutation in 720 fixed invalid-tuple admission calls or 179 capability-unavailable checks.
```

## P25 — COMPRESS

理由：精简重复标注方法，保留全部统计、不同标准、作者复核与非独立性说明。

原段落：

```latex
One author (X.W.) and one non-author volunteer coded all 360 benign runs under the terminal-completion rubric. Original labels agreed on 359/360 runs (99.72\%; three-category $\kappa=0.974$, case-bootstrap 95\% CI $[0.911,1.000]$). Conditional on the 335 behavior-evaluable runs, both judged 331 terminally complete and each agreed with the strict rule on 324/335 (96.72\%). The eleven human-positive/strict-negative cases reflect different criteria: extra calls do not violate the issued completion rubric. L.H. agreed with the strict-negative classification of the eleven discrepant cases; the frozen strict total remains 320/335, and the original completion labels are unchanged. T153, outside that comparison, was adjudicated separately. Supplement~S2.8 retains binary sensitivity, confusion matrices, unscored cases, procedure deviations, and clustering sensitivity; these are author-involved measurements.
```

修改后的英文：

```latex
X.W. and a non-author volunteer coded 360 benign runs for terminal completion, agreeing on 359/360 (99.72\%; three-category $\kappa=0.974$, case-bootstrap 95\% CI $[0.911,1.000]$). Among 335 evaluable runs, both judged 331 complete and each agreed with the strict rule on 324/335 (96.72\%). Their eleven positive/strict-negative cases allow extra calls under the issued rubric. L.H.'s separate strict review confirmed those eleven negatives; the frozen 320/335 strict total and original completion labels remain unchanged. T153 was adjudicated outside this comparison. Supplement S2.8 retains binary sensitivity, confusion matrices, unscored cases, procedure deviations, and clustering sensitivity for these author-involved measurements.
```

## P26 — COMPRESS

理由：精简 runtime 统计，保留每个配置分母和跨端点可评估性。

原段落：

```latex
Runtime failures totaled 93: 76/420 for D1, 4/420 for G1, and 13/420 for G2 (\cref{tab:runtime-endpoint}). No \code{SETUP\_FAILURE} or \code{TOOL\_RUNTIME\_FAILURE} occurred. Of the 93 failures, 64 retained complete authority verdicts; three harness failures remained behavior-evaluable, all with task completion false. Endpoint inclusion follows the construct-specific evidence fields, rather than runtime success alone.
```

修改后的英文：

```latex
Runtime failures totaled 93: D1 76/420, G1 4/420, and G2 13/420 (\cref{tab:runtime-endpoint}), with no \code{SETUP\_FAILURE} or \code{TOOL\_RUNTIME\_FAILURE}. Of these, 64 retained complete authority verdicts; three harness failures remained behavior-evaluable and all failed task completion. Endpoint inclusion depends on construct-specific evidence, not runtime success alone.
```

## P27 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
\Cref{tab:agent-behavior-final} retains configuration-specific evaluable denominators. Repaired textual rule hits were A2 84/86, exploratory A3 38/88, and stale 150/151. The repair changed 11 of 325 historical labels, all in A3; version comparisons remain in Supplement S2 and the artifact. No unavailable-capability attempt was observed in evaluable cells.
```

## P28 — COMPRESS

理由：合并重复的 Supplement 指引，保留全部统计和不仲裁/不覆盖边界。

原段落：

```latex
X.W.'s labels agreed with rule v2.1 on 286/325 outputs (88.00\%; $\kappa=0.644$, case-bootstrap 95\% CI $[0.543,0.741]$). A3 accounts for 32/39 disagreements and has no uniquely specified target field, supporting the construct-ambiguity limitation. All 39 disagreements remain without human adjudication; separate AI-assisted review proposals do not replace the frozen labels (Supplement S2). Supplement S2 gives per-scenario agreement, confusion matrices, additional coefficients, and resampling sensitivity.
```

修改后的英文：

```latex
X.W. agreed with rule v2.1 on 286/325 outputs (88.00\%; $\kappa=0.644$, case-bootstrap 95\% CI $[0.543,0.741]$). A3 contributes 32/39 disagreements and lacks a unique target field, supporting the construct-ambiguity limitation. All 39 remain without human adjudication; AI-assisted proposals leave frozen labels unchanged. Supplement S2 retains per-scenario agreement, confusion matrices, additional coefficients, and resampling sensitivity.
```

## P29 — COMPRESS

理由：缩短缺失敏感性解释，保留所有边界和统计解释限制。

原段落：

```latex
All 25 unscored benign runs belong to recorded runtime-failure classes (\cref{tab:benign-unscored}); the remaining 68 of the 93 runtime failures occur outside this unscored benign subset. If the 25 unknown behavior outcomes were assigned all failures or all successes, the strict proportion would lie between 320/360 and 345/360 (88.89--95.83\%); the endpoint range would be 331/360 to 356/360 (91.94--98.89\%). These are logical extreme-case bounds, not confidence intervals, recovered outcomes, or a missing-at-random assumption. Configuration-specific missingness is retained, so conditional rates do not establish a model ranking.
```

修改后的英文：

```latex
All 25 unscored benign runs are runtime failures (\cref{tab:benign-unscored}); 68 of the 93 failures lie outside this subset. Assigning all 25 unknowns failure or success gives strict extremes of 320/360--345/360 (88.89--95.83\%) and endpoint extremes of 331/360--356/360 (91.94--98.89\%). These logical bounds are neither confidence intervals nor recovered outcomes and make no missing-at-random assumption. Retained configuration-specific missingness precludes model ranking from conditional rates.
```

## P30 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
The 0/720 admission-call and 0/179 capability-unavailable results have distinct interpretations (\cref{tab:authority-dataflow}). Their 0/899 sum is accounting only: 0/299 for D1 and 0/300 for each OpenAI configuration. \Cref{tab:admission-mechanism-final} gives the zero-violation counts by invoked mechanism family.
```

## P31 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
Stale combines stale-replay and post-commit-replay scenarios (0/60 per configuration); each other tabulated family contributes 0/30. Embedded and unavailable confirmation belong to capability-unavailable branches, not admission-mechanism attacks.
```

## P32 — COMPRESS

理由：删除与 preceding results 重复的任务/宿主分离说明，保留固定挑战限定。

原段落：

```latex
Task outcomes varied across the qualified configurations, while the predeclared host checks preserved authoritative state. Together they characterize task execution and host-enforced admission on the restricted interface. The fixed, model-independent challenge parameters delimit these observations to integration conformance (\cref{sec:discussion}).

```

修改后的英文：

```latex
Task outcomes varied across qualified configurations; predeclared host checks preserved authoritative state. Their fixed, model-independent challenges support integration conformance on the restricted interface (\cref{sec:discussion}).
```

公式、表格、图及其图注统一为 **KEEP**：保持数学关系、结果和解释不变。
