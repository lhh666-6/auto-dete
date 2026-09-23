# Transactional realization

原字数：876；压缩后：709；压缩比例：19.06%。

口径：正文叙述及 contribution 文本；不计标题、引文/交叉引用标记、公式、表格、图注和参考文献。

**是否影响 scientific claim：No。** 这是逐段编辑核对结论；静态保护检查见总报告，不替代重新验证科研结果。

## P01 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
\system{} is implemented in Python with SQLAlchemy and SQLite. The application exposes three separate authority interfaces: \code{CandidateWritePort} appends an evidence/candidate unit, \code{AuthorityReadPort} loads persisted objects for review and trace, and \code{FactAdmissionPort} admits a complete transition bundle. Recognition receives the candidate facade but not the fact-admission facade; review receives the latter. The external generator, including the hosted-AI session used for the AI-origin fixture, is outside this trusted application boundary: its output is treated as an untrusted candidate until the persisted certificate and human admission checks succeed. This boundary provides application-level capability separation within one process.
```

## P02 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
A candidate certificate stores the target record and field, canonical value payload, producer identity/version, selection artifact, expected fact version, evidence content hash, and canonical evidence locator. Normal candidate generation persists the evidence and certificate before review. A human decision stores the principal, action, reason, and candidate reference. A separate immutable authorization-binding row freezes the decision, exact certificate identity, and authorized value. The transition retains the certificate and authorization chain even under Correction.
```

## P03 — COMPRESS

理由：压缩策略实现描述，保留角色、重查时机与宿主假设。

原段落：

```latex
The principal policy is a thread-safe, revocable in-memory mapping from identifiers to the \code{fact-admitter} role. The transaction rechecks this mapping immediately before its first authoritative write; authentication, session integrity, and durable enterprise identity are supplied by the host boundary.
```

修改后的英文：

```latex
A thread-safe, revocable in-memory policy maps identifiers to the \code{fact-admitter} role. Admission rechecks it immediately before the first authoritative write; the host supplies authentication, session integrity, and durable enterprise identity.
```

重复位置与主叙述位置：Contract is the primary trust-boundary account.

## P04 — COMPRESS

理由：精简重复的证据校验语句，保留所有绑定分量和独立重建。

原段落：

```latex
Certificate construction, admission, and trace rebuild the persisted locator with one canonical JSON function. It applies NFC and path/URI normalization, rejects unsafe path segments, and binds the form, related field, URI, locator version, and optional crop. Admission reloads the evidence row and compares owner, content hash, and independently reconstructed locator against the certificate. A copied locator string therefore cannot conceal disagreement with persisted evidence. The artifact retains the exact normalization rules.
```

修改后的英文：

```latex
Certificate construction, admission, and trace share a canonical JSON locator function: NFC and path/URI normalization, unsafe-segment rejection, and binding of form, field, URI, locator version, and optional crop. Admission reloads evidence and checks its owner, content hash, and independently reconstructed locator against the certificate. Copying a locator string cannot mask persisted disagreement. The artifact retains the normalization rules.
```

## P05 — COMPRESS

理由：压缩事务前检查的叙述，明确事务内重验。

原段落：

```latex
The application first loads the current form and validates obvious certificate mappings for useful rejection messages. The database adapter nevertheless repeats the authoritative checks inside the transaction. Its sequence is:
```

修改后的英文：

```latex
The application prechecks certificate mappings against the current form for useful rejection messages. The adapter repeats authoritative checks inside the transaction:
```

## P06 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
\begin{enumerate}[leftmargin=*]
  \item reload the declared field set, current record version, previous complete values/source map, certificates, evidence, and principal policy;
  \item derive the initial full domain or later changed-field set under canonical JSON equality and reject empty later changes, deletions, hidden changes, extra transitions, duplicate fields, or an incomplete prior snapshot;
  \item validate unused identities and the complete decision--binding--certificate--evidence--transition relation, including
  $x_{\mathrm{authorized}}\eqc x_{\mathrm{transition}}\eqc x_{\mathrm{successor}}$;
  \item issue a conditional update whose predicate is the expected current version;
  \item construct one source transition for every admitted field, copy the exact old source for every unchanged field, and require value/source domains to be identical;
  \item insert the decision, authorization binding, transitions, complete record-version row, field projections, and audit event before one commit.
\end{enumerate}
```

## P07 — COMPRESS

理由：压缩失败路径和约束描述，保留完整回滚条件。

原段落：

```latex
The compare-and-swap update is the first authoritative write. If validation fails, the CAS affects no row, a competing contender loses, or an injected exception occurs before commit, the transaction rolls back. Schema constraints provide additional defense in depth: among other relations, fact transitions and authorization bindings have unique decision and certificate indexes, and transition identity is unique per record/version/field.
```

修改后的英文：

```latex
CAS is the first authoritative write. Validation failure, a zero-row CAS, a losing contender, or a pre-commit exception rolls back the transaction. Schema constraints additionally enforce unique decision/certificate indexes for transitions and authorization bindings, and unique transition identity per record/version/field.
```

## P08 — MOVE-SUPP

理由：将连接参数和 isolation 设置原样移到补充，保留事务机制及移植边界。

原段落：

```latex
The application uses SQLite through SQLAlchemy without an explicit isolation-level setting; the concurrency harness records SQLite's default deferred transaction at serializable isolation. Every connection enables \code{foreign\_keys=ON} and \code{busy\_timeout=5000}. Only the performance and concurrency harnesses enable WAL and \code{synchronous=NORMAL}. Transactions provide atomic commit/rollback, CAS rejects stale or competing updates, and unique/foreign-key constraints enforce relational integrity. Other DBMSs or isolation regimes require new transaction, locking, conflict, and anomaly checks.
```

正文保留版本：

```latex
SQLite transactions, version CAS, and unique/foreign-key constraints provide atomicity, conflict rejection, and relational integrity. Supplement S4 records the engine settings; other DBMSs or isolation regimes require new transaction, locking, conflict, and anomaly checks.
```

迁移范围：原段落全文，逐字保留于 Supplement S4 / SQLite engine configuration and portability。

## P09 — COMPRESS

理由：去掉与 Contract 重复的数值等价反例，保留一致性要求与证据入口。

原段落：

```latex
Changed-field decisions use canonical JSON equality consistently across admission, trace, and the independently expressed test oracles. This distinguishes $2$ from $2.0$ and $1$ from \code{true}; the public-API regression checks are summarized in \cref{sec:conformance}.
```

修改后的英文：

```latex
Admission, trace, and independently expressed oracles use the canonical equality of \cref{sec:contract}; \cref{sec:conformance} reports the public-API regressions.
```

重复位置与主叙述位置：Contract canonical value equality is the primary definition and numeric/Boolean example.

## P10 — KEEP

理由：保留定义、证据、限定或已足够紧凑的叙述；不为压缩比例改动。

```latex
Manual entry can create a derived certificate at confirmation time for product compatibility. It is excluded from the AI-derived candidate conformance claim and does not stand in for Correction, which always preserves a preexisting machine certificate.
```

## P11 — COMPRESS

理由：压缩适配器实现清单，保留版本、能力隔离、桥接边界与受信宿主路径。

原段落：

```latex
The harness adapter is an out-of-tree TypeScript plugin for DeepSeek Harness \code{dsh-v0.1.1-rc.2} at commit \code{b150a551b}. It registers exactly two model-callable operations: \code{auto_decte_propose}, which invokes the candidate-only service, and \code{auto_decte_verify}, which reloads and hash-checks a certificate/evidence binding. A versioned one-shot JSON bridge runs the Python authority core with bounded time and output. The plugin exposes no confirmation operation, accepts no reviewer identity, and receives no \code{FactAdmissionPort}. A trusted deterministic driver invokes the existing \code{ReviewForms.confirm} service separately for Accept or Correction.
```

修改后的英文：

```latex
An out-of-tree TypeScript plugin targets DeepSeek Harness \code{dsh-v0.1.1-rc.2}, commit \code{b150a551b}. Its only model-callable operations are \code{auto_decte_propose} (candidate-only service) and \code{auto_decte_verify} (reload and hash-check certificate/evidence binding). A versioned one-shot JSON bridge invokes Python with bounded time/output. The plugin exposes neither confirmation, reviewer identity, nor \code{FactAdmissionPort}. A trusted deterministic driver separately calls \code{ReviewForms.confirm} for Accept or Correction.
```

## P12 — COMPRESS

理由：缩短持久化流程，保留绑定、原子追加、失败清理和字节校验。

原段落：

```latex
The proposal path stores canonical JSON as \code{AI_OUTPUT} evidence, creates a certificate whose source is \code{AI_SUGGESTION}, and binds it to one persisted parent certificate, DSH session/execution identifiers, and the current expected fact version. A database append stores evidence, certificate, and audit event atomically; a failed append discards the just-created file. Before host confirmation, the bridge independently hashes the stored evidence bytes.
```

修改后的英文：

```latex
The proposal path stores canonical JSON as \code{AI_OUTPUT} evidence and creates an \code{AI_SUGGESTION} certificate bound to a persisted parent certificate, DSH session/execution identifiers, and expected fact version. Evidence, certificate, and audit append atomically; failure discards the new file. The bridge independently hashes stored evidence bytes before host confirmation.
```

## P13 — COMPRESS

理由：压缩追溯流程，保留每一校验关系及完整前缀要求。

原段落：

```latex
For a selected certificate-era record version, the query path examines every declared field in every prefix version. At the initial version it requires one source transition created in that version per field. At a later version, a changed field must acquire the unique transition created at that version, while an unchanged field must retain the exact previous source identifier. It then checks the source record, field, creation and record-version identifiers, committed value, decision, authorization binding, certificate, producer, persisted evidence content and locator, and expected version relations.
```

修改后的英文：

```latex
For a selected certificate-era version, tracing examines every declared field in every prefix version. Initially, each field requires one source transition from that version. Later changes require the unique transition from their version; unchanged fields retain the exact prior source. Checks cover source record/field, creation and record-version identifiers, committed value, decision, authorization, certificate, producer, persisted evidence content/locator, and expected version relations.
```

## P14 — COMPRESS

理由：精简返回语义，保留失败不修复和历史状态边界。

原段落：

```latex
The trace returns \code{complete} only if all fields and prefix relations pass. Missing or inconsistent rows produce \code{incomplete} with reasons; the query never repairs or silently substitutes an alternative source. Pre-certificate legacy states are reported separately and are not upgraded to complete evidence.

```

修改后的英文：

```latex
The trace returns \code{complete} only when every field and prefix relation passes; otherwise it reports \code{incomplete} with reasons. It never repairs or substitutes sources. Pre-certificate legacy states remain separately reported rather than upgraded to complete evidence.
```

公式、表格、图及其图注统一为 **KEEP**：保持数学关系、结果和解释不变。
