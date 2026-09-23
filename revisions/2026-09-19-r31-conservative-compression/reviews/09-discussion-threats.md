# Discussion and threats to validity

原字数：808；压缩后：664；压缩比例：17.82%。

口径：正文叙述及 contribution 文本；不计标题、引文/交叉引用标记、公式、表格、图注和参考文献。

**是否影响 scientific claim：No。** 这是逐段编辑核对结论；静态保护检查见总报告，不替代重新验证科研结果。

## P01 — COMPRESS

理由：精简贡献复述，以可执行检查表衔接，保留未测试判据。

原段落：

```latex
The contribution is an inspectable relation among proposal origin, human value authority, and successor attribution. \Cref{tab:design-checklist} turns C1--C2 into an implementation aid: map each class to persisted objects and an enforcement point, then retain a legal control and a failure probe. A check remains untested until that evidence exists. The worksheet is in \code{docs/admission-design-checklist.md}.
```

修改后的英文：

```latex
The contribution links proposal origin, human value authority, and successor attribution in an inspectable relation. \Cref{tab:design-checklist} operationalizes C1--C2: map each class to persisted objects and enforcement, then retain a legal control and failure probe. Checks without that evidence remain untested; the worksheet is \code{docs/admission-design-checklist.md}.
```

重复位置与主叙述位置：Introduction owns contribution overview; Contract owns definitions.

## P02 — COMPRESS

理由：减少关系定义的重复，保留表示无关性、review link 差异及外部验证缺口。

原段落：

```latex
Representations may differ while satisfying the same obligations. $D_B$ concerns the admitted change domain and complete successor; $D_S$ concerns changed-field sources and exact unchanged-source retention. Full P6 tracing also follows authorization, candidate, and evidence bindings. The practical inspection question is whether an approval names the reviewed candidate or only its value. Complete audits can reconstruct sources without specifying that review link; the checklist requires demonstrated relations, not a particular source-map representation. Its use in independent systems remains unvalidated.
```

修改后的英文：

```latex
Different representations may satisfy these obligations. $D_B$ covers admitted changes and the complete successor; $D_S$ covers changed-field sources and exact unchanged-source retention. P6 additionally traces authorization, candidate, and evidence bindings. Inspection asks whether approval identifies the reviewed candidate or only its value: complete source reconstruction need not specify this link. The checklist requires demonstrated relations rather than a particular source-map representation; independent-system use remains unvalidated.
```

## P03 — COMPRESS

理由：精简工程权衡，保留混合成本和工作负载依赖。

原段落：

```latex
Wider changes cost more on the frozen grid. The persistence-equivalent gap combines validation/planning and implementation-path differences, so it cannot price an individual check. Admission and trace require consistent canonical equality; the repair shares that relation, not a cached change set. Form-scoped tracing trades 12 database round trips for in-memory indexing and prefix traversal. The preferred access pattern remains workload-dependent.
```

修改后的英文：

```latex
Wider changes cost more on the frozen grid. The persistence-equivalent gap mixes validation/planning with implementation-path differences and cannot price individual checks. The equality repair shares a canonical relation, not a cached change set. Form-scoped tracing uses 12 round trips plus in-memory indexing/prefix traversal; the preferred access pattern remains workload-dependent.
```

## P04 — COMPRESS

理由：压缩重复限定，保留所有证据层的选择性和实现差异。

原段落：

```latex
Proposition 1 is conditional on the declared observation model. Its five class pairs, identity pair, and copy-forward control are constructions, not a general admission oracle. Alloy checks encoded scopes and selected mutations; the nine intended projections, twenty mapping mutants, catalogue, and SQLite schedules cover selected executions. The no-op and schema-uniqueness differences remain explicit in \cref{sec:conformance}.
```

修改后的英文：

```latex
Proposition 1's class, identity, and copy-forward constructions are conditional on the declared observation model, not a general admission oracle. Alloy scopes/mutations, nine intended projections, twenty mapping mutants, the catalogue, and SQLite schedules cover selected executions. \Cref{sec:conformance} retains the no-op and schema-uniqueness differences.
```

重复位置与主叙述位置：Contract scope paragraph owns the complete Proposition 1 boundary; Conformance owns the two mapping differences.

## P05 — COMPRESS

理由：合并重复的信任局限，保留共享缺陷和元数据不变篡改边界。

原段落：

```latex
Trace completeness checks persisted relations, not evidence truth, candidate accuracy, or human judgment. Independent oracles reduce shared-code risk but can share semantic defects, as the repaired equality bug showed. The adapter compares persisted digests and canonical locators without re-reading external evidence bytes. Detecting an out-of-band replacement that preserves metadata requires immutable/content-addressed storage or separate integrity verification.
```

修改后的英文：

```latex
Trace completeness checks persisted relations, not evidence truth, candidate accuracy, or human judgment. Independent oracles can share semantic defects, as the repaired equality bug showed. The adapter compares digests and canonical locators without re-reading external bytes; metadata-preserving replacement therefore requires immutable/content-addressed storage or separate integrity verification.
```

## P06 — COMPRESS

理由：集中列出真实限制，保留全部未测试对象、撤销时序和适用范围。

原段落：

```latex
Host authentication, faithful review presentation, serialization, hashing, policy, and adapter/transaction semantics form the trusted boundary (\cref{sec:contract}). Review-channel manipulation, indirect instructions influencing approval, and adversarial confirmation inputs were not exercised. Binding preserves a recorded decision, not its quality. Other database engines need new conformance evidence. The commit-entry policy check rejects already-visible revocation but permits later-revoked in-flight transactions (\cref{sec:authorization-timing}); it provides neither linearizable nor distributed revocation. Usability, authentication workflows, reviewer error, deletion, redaction, retention expiry, and tombstones remain untested; manual entry is outside the AI-derived claim.
```

修改后的英文：

```latex
Host authentication, faithful review presentation, serialization, hashing, policy, and adapter/transaction semantics remain trusted (\cref{sec:contract}). Review-channel manipulation, indirect instructions affecting approval, and adversarial confirmation inputs were not tested; binding preserves decisions, not their quality. Other databases require new conformance evidence. Commit-entry checks reject visible revocation but permit later-revoked in-flight commits, without linearizable or distributed revocation (\cref{sec:authorization-timing}). Usability, authentication workflows, reviewer error, deletion, redaction, retention expiry, and tombstones remain untested; manual entry is outside the AI-derived claim.
```

## P07 — COMPRESS

理由：压缩成本局限，保留历史版本及未重跑声明。

原段落：

```latex
The empty-source comparator is a lower bound. Sequential trace timings may reflect caching, scheduling, checkpointing, and noise as well as access shape. Frozen cost results describe v8 and were not rerun after the equality repair.
```

修改后的英文：

```latex
The empty-source comparator is a lower bound. Sequential trace timing mixes access shape with possible caching, scheduling, checkpointing, and noise. Cost results describe frozen v8 and were not rerun after equality repair.
```

## P08 — COMPRESS

理由：压缩模型外推边界，保留平台变化因素、数值和不剔除原则。

原段落：

```latex
The three qualified configurations from two provider families are a convenience population, not a basis for provider ranking. Endpoint names and settings do not identify immutable weights; provider load, decoding, and network conditions can vary. Pilot qualification did not ensure Final stability: D1 failures increased from 0/28 to 76/420. All planned runs remain included, with eligibility determined by \cref{tab:runtime-endpoint}.
```

修改后的英文：

```latex
Three configurations from two provider families form a convenience population unsuitable for provider ranking. Endpoint names/settings do not fix immutable weights; load, decoding, and networks may vary. Qualification did not ensure Final stability: D1 failures rose from 0/28 to 76/420. All planned runs remain, with eligibility defined in \cref{tab:runtime-endpoint}.
```

## P09 — COMPRESS

理由：精简构念差异说明，保留作者参与、额外调用解释边界与不覆盖标签。

原段落：

```latex
Terminal completion and strict-trajectory compliance are distinct constructs. The post-hoc endpoint criterion admits 11 strict failures; extra calls alone establish neither caution nor general recovery competence. Original benign labels came from one author and one non-author volunteer. The first author's strict-trajectory review is a separate judgment, not an independent correction of terminal-completion labels.
```

修改后的英文：

```latex
Terminal completion and strict-trajectory compliance are distinct. The post-hoc endpoint admits 11 strict failures; extra calls establish neither caution nor general recovery competence. One author and one non-author volunteer supplied the original labels. The first author's strict review remains a separate judgment, not an independent correction of completion labels.
```

## P10 — COMPRESS

理由：压缩文本审计局限，保留所有偏差来源和人工/AI角色边界。

原段落：

```latex
The textual audit has one author coder and no human adjudication; the subsequent unblinded AI review supplies proposals only. Agreement is prevalence-sensitive and heterogeneous: A6 and B4 nearly coincide with the rule, whereas A3 contributes 32/39 disagreements. A3's unspecified target limits the construct. Author involvement, knowledge of the study purpose, and residual textual clues constrain blinding; the audit supplies human--rule comparison rather than third-party validation. Frozen rule hits remain intact.
```

修改后的英文：

```latex
The textual audit uses one author coder without human adjudication; subsequent unblinded AI review supplies proposals only. Agreement varies with prevalence and scenario: A6/B4 nearly match the rule, while A3 contributes 32/39 disagreements and lacks a specified target. Author involvement, study-purpose knowledge, and textual clues limit blinding. This is human--rule comparison, not third-party validation; frozen rule hits remain intact.
```

## P11 — COMPRESS

理由：压缩宿主挑战外推限制，保留两类计数与全部未覆盖攻击范围。

原段落：

```latex
The 720 fixed invalid-tuple calls and 179 capability-unavailable branches measure the exercised host operations. They do not sample model-generated attacks, compromised hosts or identity providers, administrator access, or model access to admission. Zero violations imply neither a population failure bound nor general prompt-injection security; zero unavailable-tool attempts reveal no behavioral heterogeneity.
```

修改后的英文：

```latex
The 720 fixed invalid-tuple calls and 179 capability-unavailable branches cover exercised host operations, excluding model-generated attacks, compromised hosts/identity providers, administrator access, and model access to admission. Zero violations establish neither a population failure bound nor general prompt-injection security; zero unavailable-tool attempts show no behavioral heterogeneity.
```

## P12 — COMPRESS

理由：减少结果重复，只保留支撑设计解释的 separator 与复现边界。

原段落：

```latex
The deposit supports inspection without new hosted calls; reproduction in another environment is a separate test. The related-work comparison covers disclosures through its stated cutoff. The executable controls establish a specific separation: both value-audit policies agree with candidate-bound admission on seven of eight single-history cases and reconstruct field sources, yet leave the paired reviewed-candidate histories indistinguishable in authority-relevant state (\cref{sec:executable-relation-result}). Exact candidate binding preserves the review distinction left unspecified by these evaluated safeguards.
```

修改后的英文：

```latex
The deposit permits inspection without new hosted calls; reproduction elsewhere remains a separate test. Related-work coverage ends at its stated cutoff. Both evaluated value-audit policies match candidate-bound admission on seven of eight single-history cases and reconstruct sources, yet their authority-relevant state cannot distinguish the paired reviewed-candidate histories (\cref{sec:executable-relation-result}). Exact binding preserves that review distinction.
```

重复位置与主叙述位置：Results RQ5 owns detailed control outcomes; declarations own availability statement.

## P13 — COMPRESS

理由：合并重复解释，保留可替代区分方式、D_V 边界和未评估系统类别。

原段落：

```latex
Richer review-context snapshots distinguish candidates when recorded proposal, producer, or evidence observations differ. Exact identity becomes material when distinct persisted candidates remain equivalent under those observations; it is not the only possible discriminator. This representational boundary leaves Proposition 1's conditional $D_V$ result intact: the controls test recoverability from particular audit representations, while the proposition tests omitted observation classes. Together they position an explicit correction-aware obligation, its conditional characterization, and its transactional realization. Independently developed event-sourcing/CQRS, temporal/bitemporal, and four-eyes systems were not evaluated.

```

修改后的英文：

```latex
Richer review snapshots distinguish candidates with different proposal, producer, or evidence observations. Exact identity matters when distinct persisted candidates remain equivalent under those observations; other discriminators are possible. This representation-specific comparison leaves Proposition 1's observation-omission $D_V$ result intact. The contribution is the correction-aware obligation, conditional characterization, and transactional realization. Independent event-sourcing/CQRS, temporal/bitemporal, and four-eyes systems remain unevaluated.
```

公式、表格、图及其图注统一为 **KEEP**：保持数学关系、结果和解释不变。
