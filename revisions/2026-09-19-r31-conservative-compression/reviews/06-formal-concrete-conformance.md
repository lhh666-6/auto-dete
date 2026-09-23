# Formal--concrete projection and executable conformance

原字数：525；压缩后：414；压缩比例：21.14%。

口径：正文叙述及 contribution 文本；不计标题、引文/交叉引用标记、公式、表格、图注和参考文献。

**是否影响 scientific claim：No。** 这是逐段编辑核对结论；静态保护检查见总报告，不替代重新验证科研结果。

## P01 — COMPRESS

理由：缩短引导句，保持映射公式原样。

原段落：

```latex
To connect the model suite and Python suite to the same admission event, we define an explicit abstraction
\begin{equation}
\alpha:\mathrm{PersistedPrePost}\rightarrow\mathrm{BatchAlloyInstance}.
\end{equation}
```

修改后的英文：

```latex
An explicit abstraction connects model and Python checks of the same admission event:
\begin{equation}
\alpha:\mathrm{PersistedPrePost}\rightarrow\mathrm{BatchAlloyInstance}.
\end{equation}
```

## P02 — COMPRESS

理由：精简投影对象枚举，保留映射输入、相等类和哈希假设。

原段落：

```latex
For one selected event, $\alpha$ reads SQLite through query methods and serializes the form, declared field domain, evidence rows, candidate certificates, decisions and authorization bindings, fact transitions, record-version values and source maps, version chain, and relevant pre/post identity sets. Concrete JSON value-equivalence classes become Alloy Value atoms; certificate hashes become primitive \code{CertId} atoms without assuming hash injectivity. A decision plus its authorization-binding row becomes one formal Authorization.
```

修改后的英文：

```latex
For a selected event, $\alpha$ queries SQLite and serializes the form, field domain, evidence, certificates, decisions/bindings, transitions, version values/source maps, version chain, and relevant pre/post identities. Concrete JSON value-equivalence classes become Alloy Value atoms; certificate hashes become primitive \code{CertId} atoms without assuming injectivity. Each decision and binding row becomes one formal Authorization.
```

## P03 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
\Cref{tab:abstraction} states the relation-by-relation mapping used by the executable projection.
```

## P04 — COMPRESS

理由：压缩 accepted/rejected 的执行过程，保留三项拒绝检查。

原段落：

```latex
For a committed case, the generator writes an exact Alloy wrapper and asks whether the fixed instance satisfies \code{legalAdmission[event, Full]}. For a rejected case, it first compares canonical database digests before and after the attempted call. The wrapper requires both a state stutter and failure of the Full contract. A changed digest causes projection failure before Alloy is invoked.
```

修改后的英文：

```latex
A committed case generates a fixed Alloy instance checked against \code{legalAdmission[event, Full]}. A rejected case first requires equal canonical database digests before/after the call; its wrapper requires state stutter and Full-contract failure. A changed digest fails projection before Alloy runs.
```

## P05 — COMPRESS

理由：精简独立性声明，保留二十个 mutant 及所有改变维度。

原段落：

```latex
The projection is a test-side adapter, independent of the production admission planner, certificate validator, and reverse-trace builder. Twenty single-dimension mutants alter field, evidence, version, freshness, authorization, transition, preexistence, committed effects, or initial coverage in the serialized mapping and provide selected sensitivity checks for $\alpha$.
```

修改后的英文：

```latex
The test-side projection is independent of the production planner, certificate validator, and trace builder. Twenty single-dimension mapping mutants probe field, evidence, version, freshness, authorization, transition, preexistence, committed effects, or initial coverage, providing selected sensitivity checks for $\alpha$.
```

## P06 — COMPRESS

理由：压缩 oracle 校验清单，保留独立预期来源和五类 mutant。

原段落：

```latex
A second oracle reads every SQLite application table directly. It checks the exact declared value/source domains, adjacent source evolution, transition sets, record-version anchors, decision/principal/certificate/authorization/evidence relations, and authorized/transition/committed values. It does not use the production planner or trace builder as its expected-value source. Five in-memory relation mutants test the oracle's sensitivity to source, authorization, locator, principal, and value changes.
```

修改后的英文：

```latex
A second oracle directly reads every SQLite application table, checking value/source domains, adjacent source evolution, transitions, version anchors, decision/principal/certificate/authorization/evidence relations, and authorized/transition/committed values. Expected values do not come from the production planner or trace builder. Five in-memory mutants probe source, authorization, locator, principal, and value sensitivity.
```

## P07 — COMPRESS

理由：压缩 catalogue 判据的说明，保留分类、样本量、摘要覆盖范围及 completeness 边界。

原段落：

```latex
The declared 35-case catalogue contains five legal cases and thirty rejection, post-persistence corruption, schema-prevention, stateful-evolution, or oracle-mutant cases. Rejection cases require the public error classification and equality of a deterministic digest covering schema version, identity sequences, and every application table. Corruption cases instead require a changed digest and an incomplete trace/oracle diagnosis. The machine-readable declaration fixes the catalogue's completeness scope.
```

修改后的英文：

```latex
The declared 35-case catalogue comprises five legal cases and thirty rejection, corruption, schema-prevention, stateful-evolution, or oracle-mutant cases. Rejections require the public error classification and an unchanged deterministic digest of schema version, identity sequences, and every application table. Corruptions require a changed digest and incomplete trace/oracle diagnosis. The machine-readable declaration bounds catalogue completeness.
```

## P08 — COMPRESS

理由：压缩修复历史，保留所有计数、回归类型和见证域边界。

原段落：

```latex
The repaired implementation uses canonical JSON equality for changed-field decisions. Thirteen regressions include unchanged controls, numeric/Boolean and nested changes, and a rejected no-op; seven fail before the repair and all pass afterward. The witness checker separately represents schema and declared-item domains, preserving the five original pairs, adding the candidate-identity pair, and admitting a copy-forward control. It is a construction checker, not a general admission oracle. Supplement S2 records the defects and checks.
```

修改后的英文：

```latex
Canonical JSON equality repairs changed-field decisions. Thirteen regressions cover unchanged controls, numeric/Boolean and nested changes, and a rejected no-op: seven fail before repair and all pass afterward. Separating schema from declared-item domains preserves the five witness pairs and adds candidate-identity and copy-forward controls. This construction checker is not a general admission oracle; Supplement S2 retains defects and checks.
```

## P09 — COMPRESS

理由：缩短九类 intended projection 的列表，保留每类与有界性。

原段落：

```latex
The nine intended projections include singleton Accept and Correction; multi-field all-Accept, all-Correction, and mixed batches; an initial batch; unchanged-source copy-forward; stale rejection; and whole-batch rejection caused by one invalid item. Together they constitute selected bounded refinement evidence; Section~\ref{sec:discussion} states the generalization boundary.
```

修改后的英文：

```latex
Nine intended projections cover singleton Accept/Correction; multi-field all-Accept, all-Correction, and mixed batches; initial admission; unchanged-source copy-forward; stale rejection; and whole-batch rejection for one invalid item. These are selected bounded refinement evidence (\cref{sec:discussion}).
```

## P10 — COMPRESS

理由：压缩形式与实现差异，完整保留两个偏差、额外测试和前缀限制。

原段落：

```latex
Two intentional scope differences remain. First, the concrete post-initial no-op rule narrows the formal same-value behavior. Second, SQLite uniqueness makes one modeled duplicate-source state unreachable through the trusted schema. Conversely, concrete trace tests cover persisted pointer and binding corruptions that the formal P6 tamper event does not encode. The formal \code{traceComplete} predicate is a single-level anchor and uniqueness condition over the persisted relations, whereas the concrete trace builder additionally traverses each predecessor prefix and retains exact previous sources. The bounded positive assertion therefore establishes the encoded admission step under its stated well-formed-pre-state condition, not prefix-wide trace completeness.

```

修改后的英文：

```latex
Two intentional differences remain: concrete post-initial admission rejects formal same-value no-ops, and SQLite uniqueness prevents one modeled duplicate-source state through the trusted schema. Concrete trace tests additionally cover pointer and binding corruptions absent from the formal P6 tamper event. Formal \code{traceComplete} checks single-level anchors and uniqueness; concrete tracing traverses every predecessor prefix and retains exact prior sources. The bounded positive assertion covers only the encoded admission step under its well-formed-pre-state condition, not prefix-wide trace completeness.
```

公式、表格、图及其图注统一为 **KEEP**：保持数学关系、结果和解释不变。
