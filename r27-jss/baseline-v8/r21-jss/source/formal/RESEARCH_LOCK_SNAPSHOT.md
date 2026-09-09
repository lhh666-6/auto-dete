# Auto-Decte Formalization — RESEARCH_LOCK.md

> **Status:** RESEARCH LOCKED  
> **Date:** 2026-08-22  
> **Primary venue orientation:** JSS-first, with SCP / SoSyM as conditional pivots  
> **Rule:** All later DeepSeek / Codex / implementation work must treat this file as the highest-level research constraint. If implementation conflicts with this file, report the conflict; do not silently redefine the research problem.

---

# 1. Final Primary Direction

## Primary Direction

**Certificate-Bound Non-Substitutable Admission of AI-Derived Candidate Updates into Versioned Authoritative Records**

Narrative framing:

**Context-Bound Admission of AI-Derived Candidate Updates into Versioned Authoritative Records**

- `Context-Bound Admission` = problem framework.
- `Certificate-Bound Non-Substitutability / Non-Transferability` = central formal property.
- version freshness, lineage, reverse trace, and direct-write exclusion = supporting mechanisms/properties.

## Not the primary novelty

Do not sell the following as the core novelty:

- Candidate != Fact by itself;
- machine output cannot directly become fact by itself;
- human-final authority by itself;
- write != commit by itself;
- provenance-aware commit by itself;
- version/CAS by itself;
- append-only correction history by itself;
- reverse trace by itself;
- OCR / HOG-SVM accuracy.

The research center is:

> **An authorization over one AI-derived candidate must not be transferable to a different record, field, evidence, version, or candidate-certificate context, even when the proposed value is identical.**

---

# 2. Final Research Question

## Main RQ

> **How can an AI-assisted information system admit machine-derived candidate updates into versioned authoritative records while ensuring that candidate validity and authorization are non-transferable across record, field, evidence, version, and certificate contexts?**

中文：

> **AI 辅助信息系统如何将机器生成的候选更新准入到版本化权威记录，同时确保候选有效性与授权不能跨记录、字段、证据、版本或候选证书上下文转移？**

## Secondary RQ

> **Can this admission contract be formally analyzed and shown to have executable counterparts in a concrete document-intelligence system under substitution, stale-replay, transition-corruption, and trace-corruption faults?**

---

# 3. Central Thesis

The core thesis is not prediction accuracy or human finality.

It is:

> **Authority attaches to a context-bound candidate identity, not merely to its value.**

Therefore, even when:

\[
Value(c_1)=Value(c_2)
\]

if:

\[
Context(c_1)\neq Context(c_2)
\]

then:

\[
Authorize(c_1)\not\Rightarrow Authorize(c_2)
\]

In short:

\[
SameValue \not\Rightarrow SameAuthority
\]

---

# 4. Terminology Lock

## Candidate Update

> A machine-derived proposal to change a field of a versioned record, together with the context and evidence under which the proposal was produced.

## Versioned Authoritative Record

> A versioned operational record whose current committed state is allowed by the application to drive consequential downstream operations.

Examples of authoritative downstream sinks:

- export;
- payroll;
- reports;
- accounting/statistics;
- downstream workflow;
- official API / integration.

## Committed Fact

Formal sections should prefer **Committed Fact**.

> A field value contained in the current committed version of a versioned authoritative record.

`Authoritative fact` may be used as a narrative alias only if we explicitly state:

\[
Authoritative \Rightarrow OperationallyAccepted
\]

but not:

\[
Authoritative \Rightarrow ObjectivelyCorrect
\]

Authority is operational, not epistemic.

## Authorization

The formal model uses a general `Authorization` relation. It must:

- be produced by an authorized principal;
- explicitly reference one candidate certificate;
- not be usable independently of that certificate/context.

Current Auto-Decte implementation:

\[
Authorization = HumanReviewDecision
\]

The paper does not claim to implement automated authorization, dual authorization, policy-only authorization, or cryptographic delegation.

## Candidate Certificate

> A persistent, content-addressed binding artifact that identifies one candidate update together with the context in which it is eligible for admission.

Its contribution is **binding semantics**, not a new hash or cryptographic protocol.

---

# 5. Context Lock

Core context:

\[
Context(c)=(record,field,evidence,expectedVersion)
\]

Recommended concrete certificate also includes:

\[
(value,producer,policy/template)
\]

Concrete certificate identity may be represented as:

\[
Cert(c)=H(record\Vert field\Vert value\Vert evidence\Vert expectedVersion\Vert producer\Vert policy)
\]

The formal model need not promote every engineering field into a core relation.

---

# 6. The Boundary We Study

We study:

\[
CandidateUpdate \xrightarrow{Admission} CommittedFact
\]

Not:

- AI -> Action;
- Observation -> AgentBelief;
- User -> Permission.

The precise question is:

> **Which exact machine-derived update may alter which exact committed record state under which exact evidence, version, and authorization binding?**

---

# 7. Property Hierarchy

## P0 — Architectural Invariant: Direct-Write Exclusion

\[
MachineOnlyTrace \Rightarrow CommittedStateUnchanged
\]

Machine perception, retrieval, LLM, and rule services can create candidates but cannot directly write committed facts.

**Role:** architecture invariant, not central novelty.

## P1 — Central Property: Certificate-Bound Non-Substitutability

If candidate certificate and target admission context differ:

\[
Context(c_i)\neq Context_j
\]

then:

\[
Admit(c_i,Context_j)=False
\]

and:

\[
CommittedState_{after}=CommittedState_{before}
\]

Authorization form:

\[
Authorization(a,Cert(c_i))
\]

cannot authorize a different certificate:

\[
Cert(c_i)\neq Cert(c_j)
\Rightarrow
Authorize(Cert(c_i))\not\Rightarrow Authorize(Cert(c_j))
\]

This is the most important falsifiable property in the paper.

## P2 — Context-Bound Admission

A successful admission requires:

\[
CandidateContextMatch
\land ValidAuthorization
\land FreshVersion
\land ValidTransition
\]

before a new committed state is produced.

This must not be modeled as a tautology. Invalid transitions must remain reachable in the abstract state space so that the full contract and ablations can be meaningfully checked.

## P3 — Authorization Necessity and Reference Integrity

Any committed fact change requires an attributable authorization that references the same candidate certificate as the transition:

\[
CommittedChange
\Rightarrow
\exists a,c: Authorization(a,Cert(c))
\]

Core attack:

> a decision for certificate A reused for certificate B.

## P4 — Version Freshness / Stale Non-Interference

If:

\[
ExpectedVersion(c)\neq CurrentVersion(record)
\]

then:

\[
Commit=Reject
\]

and:

\[
CommittedState_{after}=CommittedState_{before}
\]

**Role:** supporting property implemented with OCC/CAS. No claim of a new concurrency-control algorithm.

## P5 — Transition Integrity

A successful admission must produce a structurally complete, unique, attributable transition:

- no missing transition;
- no duplicate transition for one committed field update;
- no blank target;
- no mismatched target version;
- no transition detached from its authorization/certificate.

Uniqueness may be expressed using:

\[
\exists! t
\]

## P6 — Trace Soundness

Reverse trace:

\[
CommittedFact
\rightarrow Transition
\rightarrow Authorization
\rightarrow Certificate
\rightarrow Evidence
\]

`VerifyTrace(f)=Complete` is allowed only if all required nodes and bindings are valid.

Tampering, missing nodes, wrong evidence, wrong versions, wrong certificate references, deleted transitions, or producer rebinding must not be falsely accepted as `Complete`.

Claim **trace soundness**, not universal trace availability or permanent completeness.

---

# 8. Five Core Substitution / Transfer Attacks

## S1 — Field Substitution

\[
field_A \rightarrow field_B
\]

## S2 — Evidence Substitution

\[
e_A \rightarrow e_B
\]

## S3 — Record Substitution

\[
record_A \rightarrow record_B
\]

## S4 — Version Substitution / Stale Replay

\[
v_t \rightarrow v_{t+k}
\]

## S5 — Authorization / Certificate Substitution

A legal:

\[
Authorize(Cert_A)
\]

is attempted against:

\[
Cert_B
\]

even when:

\[
Value(Cert_A)=Value(Cert_B)
\]

This must fail. S5 is a particularly important experiment because it directly demonstrates authorization non-transferability.

---

# 9. Threat Model

## In Scope

- wrong machine prediction;
- wrong LLM suggestion;
- irrelevant retrieval;
- direct machine fact-write attempt;
- field substitution;
- evidence substitution;
- record substitution;
- stale/version replay;
- authorization/certificate substitution;
- concurrent/interleaved confirmation;
- duplicate evidence;
- transition producer tampering;
- transition deletion;
- transition rebinding;
- record-version rebinding;
- incomplete reverse trace;
- mismatched certificate/decision/transition references.

## Out of Scope

- OS/root compromise;
- arbitrary privileged DBA rewriting all data coherently;
- cryptographic hash collision;
- compromised trusted runtime;
- compromised DB engine;
- compromised dependency supply chain;
- forged real-world human identity;
- correctness of the human reviewer;
- confidentiality guarantees;
- availability guarantees;
- arbitrary physical destruction;
- general network security;
- universal Byzantine behavior.

## Critical Boundary

> **Human authorization != human correctness.**

If a reviewer approves a wrong value, the system may produce a wrong but still committed value. The paper guarantees attribution, binding, freshness, state-transition integrity, and traceability—not semantic truth.

---

# 10. Prior-Art Boundary Lock

## MemTX

**MemTX: Transactional Belief Commit for Stateful Agent Memory (2026, preprint)** is the closest current prior art.

It already covers write-vs-commit separation, evidence, permissions, provenance, validity, snapshot-isolated staging, validate-and-commit, stale-before-authority, property-based testing, and bounded state checking.

Therefore we cannot claim:

- first write/commit separation;
- first governed AI persistence;
- first provenance-aware AI commit;
- first version-aware AI admission.

Our defensible boundary is narrower:

> **non-transferable admission authority over persistent candidate identities tied to a versioned authoritative record update.**

Do not dismiss MemTX with only “memory vs records.”

## SAGE-Mem

**Before It Persists: Write-Time Defense for Multimodal Agent Memory (ICML 2026 SCALE Workshop)** explicitly separates transient evidence from durable belief and implements write-time admission, belief promotion, and provenance-aware retrieval.

Therefore Candidate–Fact type separation is not a first-of-kind contribution.

Our boundary is:

- persistent candidate certificate;
- exact record/field/evidence/version context;
- authorization reference integrity;
- non-transferable admission;
- committed operational record state.

## EBTE

**Explanation-Bound Tool Execution for AI Agents (2026, preprint)** already checks typed action claims against intent, policy, payload, tool, risk, provenance, and freshness.

Therefore context binding / provenance / freshness by themselves are not unique.

Difference:

- EBTE target = governed tool execution;
- our target = versioned committed record transition;
- our center = authorization over candidate certificate is non-transferable.

## CapLease

**Beyond Single-Use Tokens: Durable Authorization State for Replay-Resistant LLM Agent Actions (2026, preprint)** already studies durable authorization state, semantic replay, user confirmation binding, and transactional authorization consumption.

Therefore replay resistance / durable authorization state are not standalone novelty.

Difference:

> candidate-update identity + committed-record target + certificate-bound non-transferability.

## OpenPort

OpenPort already covers draft/human review, preflight impact binding, delayed approval TOCTOU, and fail-closed state revalidation.

Therefore human review, approval binding, and freshness cannot be claimed as first-of-kind.

## Provenance-Bound Context Attestation / Policy Authorization

This work studies provenance-bound contextual verification and deterministic policy authorization for agentic executable actions.

It is an important context-binding neighbor, not a direct authoritative-record admission study.

## Candidate-to-Authoritative Practice

The candidate-record / authoritative-record distinction predates this paper in records and master-data practice.

Do not write:

> “We introduce the first candidate/authoritative distinction.”

Instead:

> **We build on the established distinction between provisional/source-specific information and authoritative operational records, and study a narrower question: when authorization over an AI-derived candidate remains valid for one exact record-state transition and must fail under contextual substitution.**

---

# 11. Novelty Statement Lock

Allowed:

> **The contribution is not candidate/fact separation alone, but a formally analyzable admission contract in which candidate identity and authorization are context-bound and non-transferable across record, field, evidence, version, and certificate references, together with executable conformance evidence.**

Not allowed:

- first candidate-fact separation;
- first human-authorized AI database;
- first provenance-aware AI system;
- new CAS protocol;
- formal proof of all system security;
- formally verified Python system.

---

# 12. Relationship to Classical Areas

## RBAC / ABAC / Capability

Classical question:

\[
Who\ may\ perform\ which\ operation?
\]

Our question:

\[
Which\ exact\ candidate\ may\ become\ which\ exact\ committed\ fact\ under\ which\ binding?
\]

Access control can implement part of the system but does not replace the admission abstraction.

## Provenance

Provenance answers where information came from. Here provenance/evidence identity participates in whether admission remains valid. This is not by itself unique, but it is part of the contract.

## OCC / CAS

OCC/CAS is reused as one conjunct of admission validity. No new concurrency-control claim.

## HITL / Workflow

Human review is modeled as one attributable authorization event over one candidate certificate. Human-finality is not the contribution.

## Event Sourcing / Temporal DB

Used to support immutable history and lineage, not claimed as novelty.

---

# 13. Formal Model Skeleton

Suggested entities:

\[
\mathcal{M}=(E,R,K,C,Cert,A,V,T,P)
\]

- E: Evidence
- R: Record
- K: Field / Key
- C: Candidate Update
- Cert: Candidate Certificate
- A: Authorization
- V: Record Version
- T: Fact Transition
- P: Producer

Core relations:

- `candidate.targetsRecord`
- `candidate.targetsField`
- `candidate.evidence`
- `candidate.expectedVersion`
- `candidate.producer`
- `certificate.bindsCandidate`
- `authorization.referencesCertificate`
- `transition.referencesAuthorization`
- `transition.fromVersion`
- `transition.toVersion`
- `record.currentVersion`

---

# 14. Formalization Rule: Avoid Tautology

Forbidden approach:

1. define `Admit iff ContextMatch`;
2. assert `Admit => ContextMatch`.

That only proves the definition.

Required approach:

- define states, transitions, references, and certificate construction;
- allow malformed bindings / replay / substitution states to exist in the search space;
- constrain successful committed transitions through the full contract;
- remove one mechanism at a time;
- require counterexamples to emerge in ablations.

---

# 15. Alloy Validation Plan

Full contract checks:

- P1 non-substitutability;
- P3 authorization-reference integrity;
- P4 stale non-interference;
- P5 transition integrity;
- P6 trace soundness.

Result wording:

> **No counterexample was found within the explored scope.**

Never write universal mathematical proof unless there is a separate genuine proof.

---

# 16. Mechanism Ablation Plan

| Ablation | Removed mechanism | Expected counterexample |
|---|---|---|
| A1 | field binding | cross-field admission |
| A2 | evidence binding | cross-evidence admission |
| A3 | record binding | cross-record admission |
| A4 | expectedVersion binding | stale replay |
| A5 | authorization→certificate binding | authorization transfer |
| A6 | transition uniqueness/integrity | missing/duplicate/misbound transition |
| A7 | trace validation | corrupted trace falsely accepted |

**A5 is especially important** because it most directly supports the non-transferable-authorization claim.

---

# 17. Concurrency Claim Boundary

Alloy may model:

- stale authorization;
- version mismatch;
- competing/interleaved abstract admission states.

The paper may say:

> **bounded analysis of stale and interleaved admission states**

It may not say:

> formal verification of concurrent database correctness.

Concrete atomicity evidence comes from DB transactions, CAS, concurrency tests, and no-partial-write assertions.

---

# 18. Formal-to-Concrete Mapping Goal

Later define:

\[
\alpha:S_{concrete}\rightarrow S_{formal}
\]

Suggested mapping:

| Formal | Concrete |
|---|---|
| Evidence | Evidence row + SHA-256 |
| Candidate | candidate payload / CandidateCertificate data |
| Certificate | persisted content-addressed certificate |
| Authorization | ReviewDecision |
| RecordVersion | RecordVersion |
| Transition | FactTransition |
| Freshness | expected-version CAS |
| Admission | review-service transaction |
| Trace | reverse-trace reconstruction |

---

# 19. Executable Conformance Plan

Use **Hypothesis RuleBasedStateMachine**.

At minimum generate:

- create_evidence;
- generate_candidate;
- authorize_candidate;
- correct_candidate;
- substitute_field;
- substitute_evidence;
- substitute_record;
- replay_stale_candidate;
- substitute_authorization_certificate;
- concurrent_confirm;
- tamper_transition;
- delete_transition;
- rebind_version;
- verify_trace.

The test oracle must not simply reuse the production validator.

---

# 20. Existing Experimental Assets

Reinterpret current assets as **implementation-level conformance evidence**:

- existing fault corpus;
- cross-field / cross-form faults;
- stale replay;
- producer tampering;
- deleted transition;
- version rebinding;
- randomized trials;
- 239 automated tests;
- Ruff / mypy;
- deterministic reproducibility;
- byte-identical outputs;
- manifest.

The 239 tests demonstrate software artifact quality, not a scientific sample size.

---

# 21. Industrial Document Case Study Role

The industrial form workflow remains as:

> **Executable Instantiation / Industrial Document Case Study**

It shows that the admission contract can be embedded around a real AI-assisted perception workflow.

It does not prove:

- production OCR superiority;
- industrial deployment effectiveness;
- handwriting generalization;
- human-review productivity.

Synthetic recognition results may remain, but they do not carry the core novelty.

---

# 22. Final Paper Research Questions

## RQ1 — Admission Safety

> Does the full admission contract prevent context-mismatched candidate updates from producing committed record transitions within the explored formal state space?

## RQ2 — Mechanism Role

> Which certificate and authorization bindings are required to prevent field, evidence, record, version, and authorization-transfer counterexamples?

## RQ3 — Executable Conformance

> Does the concrete implementation preserve the abstract admission properties under valid, substituted, stale, interleaved, and corrupted workflows?

## RQ4 — Instantiation

> Can the contract be instantiated in an AI-assisted industrial document workflow while keeping machine-produced candidate updates non-authoritative until a valid admission transition?

---

# 23. Contribution Lock

Keep at most four contributions.

## C1 — Admission Model

A formal Candidate-Update-to-Committed-Fact admission model for versioned authoritative records.

## C2 — Non-Substitutability Property

A certificate-bound non-substitutability / non-transferability property covering record, field, evidence, version, and authorization-reference contexts.

## C3 — Formal Mechanism Analysis

Bounded model checking plus single-mechanism ablations that expose counterexamples when context or authorization bindings are removed.

## C4 — Executable Conformance

A concrete implementation mapping, property-based stateful testing, fault injection, and an industrial document instantiation.

---

# 24. Supporting Properties, Not Separate Novelty Claims

- Direct-write exclusion;
- version freshness;
- CAS;
- correction-preserving lineage;
- reverse-trace soundness;
- append-only history;
- human attribution;
- reproducibility;
- content addressing.

---

# 25. Non-Claims

Do not claim:

- universal security;
- mathematical proof of all system behavior;
- formally verified Python implementation;
- new cryptographic protocol;
- new access-control model;
- new concurrency-control algorithm;
- new provenance model;
- new event-sourcing model;
- human decision correctness;
- production deployment effectiveness;
- robustness against root/DBA compromise;
- agent-memory superiority;
- OCR algorithm novelty;
- real-world industrial generalization.

---

# 26. Proposed Paper Structure

1. Introduction
2. Related Work and Problem Boundary
3. Versioned Authoritative Record Admission Model
4. Certificate-Bound Non-Substitutability
5. Formal Analysis and Mechanism Ablations
6. Executable Conformance
7. Industrial Document Instantiation
8. Discussion
9. Limitations
10. Conclusion

Related Work should preferably compare prior work along:

1. What is being admitted?
2. What binds the admitted object?
3. Who/what provides authority?
4. What persistent state changes?
5. How is validity checked?

This supports direct comparison with MemTX, SAGE-Mem, EBTE, CapLease, OpenPort, provenance, and workflow authorization.

---

# 27. Journal Orientation

## Primary — JSS

Best fit for:

- software architecture;
- formal contract;
- executable implementation;
- conformance;
- fault injection;
- reproducible artifact.

Default:

\[
JSS\ first
\]

## Conditional Pivot — SCP

Pivot if:

- Alloy/property contribution becomes the strongest part;
- ablation counterexamples are particularly strong;
- semantics dominate the industrial case study;
- concrete mapping remains rigorous.

## Conditional Pivot — SoSyM

Consider if modeling semantics, state models, and abstraction relation become the clearest contribution.

---

# 28. Working Title Options

## Preferred

**Context-Bound Admission of AI-Derived Updates into Versioned Authoritative Records**

Subtitle / abstract focus:

> Certificate-Bound Non-Substitutability and Executable Conformance

## More Technical

**Non-Substitutable Admission Contracts for AI-Assisted Versioned Records**

## Retaining Project Name

**Auto-Decte: Certificate-Bound Admission of AI-Derived Updates into Versioned Authoritative Records**

Do not currently place `Candidate–Fact Separation` as the first title phrase because the broader abstraction is heavily crowded by memory-admission and records-management prior art.

---

# 29. Reopen Triggers

Reopen this Research Lock only if:

1. prior work is found that directly formalizes candidate + record + field + evidence + version + certificate-bound authorization -> authoritative committed record;
2. MemTX adds the same certificate-bound authorization non-transferability;
3. SAGE-Mem or follow-up work formalizes record/field/version/certificate transfer resistance;
4. peer-reviewed work already unifies the five substitution families under the same admission property;
5. Alloy shows P1 cannot be made non-tautological under a reasonable threat model;
6. the concrete implementation cannot map to the formal semantics without hiding essential state.

If triggered: stop adding experiments and reopen Research Review first.

---

# 30. Monitoring Rule

The existing literature-monitoring task should prioritize:

- AI memory admission;
- belief commit;
- candidate write gates;
- provenance-bound authorization;
- agent action authorization;
- durable authorization state;
- context binding;
- non-transferable approval;
- versioned record admission;
- formal authorization;
- authoritative-record AI updates.

Any new High/Critical work should trigger review of Sections 10, 11, and 29.

---

# 31. Immediate Next Step for DeepSeek

After this lock, DeepSeek still should **not** immediately build the full Alloy model.

First produce:

```text
formal/FORMAL_MODEL.md
formal/THREAT_MODEL.md
formal/PROPERTIES.md
```

Requirements:

1. follow this RESEARCH_LOCK;
2. do not add a new primary research problem;
3. do not widen novelty claims;
4. explain how P1 is non-tautological;
5. model all five substitution attacks;
6. include Authorization→Certificate binding explicitly;
7. explain how invalid states enter the Alloy state space;
8. distinguish full model from ablation models;
9. map key abstract states to concrete Python concepts;
10. update HANDOFF.md.

Then run:

> Independent DeepSeek Red Team → GPT Semantic Gate

Only after PASS should full Alloy implementation begin.

---

# 32. Final Locked Summary

## What we study

\[
AI\ CandidateUpdate \rightarrow CommittedFact
\]

under an explicit admission contract.

## What is central

\[
\boxed{Certificate\text{-}Bound\ Non\text{-}Substitutability}
\]

## What it means

Authorization or candidate validity created for one exact:

\[
(record,field,evidence,version,certificate)
\]

context cannot be transferred to another.

## What is supporting

- stale-safe commit;
- transition integrity;
- trace soundness;
- correction lineage;
- direct-write exclusion.

## What we do not sell as novelty

- Candidate != Fact;
- HITL;
- provenance;
- CAS;
- hashes;
- audit logs;
- event sourcing;
- OCR.

## Default venue

\[
\boxed{JSS}
\]

## Research status

\[
\boxed{RESEARCH\ LOCKED}
\]

Do not begin full Alloy implementation until the Semantic Gate approves the DeepSeek Formal Draft.
