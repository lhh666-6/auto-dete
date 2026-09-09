# THREAT_MODEL.md — Auto-Decte Threat Model v0.6 (Semantic Gate Rework Round 5)

> **Status:** DeepSeek Threat-Model Draft v0.6 — revised after the GPT-5.6 Sol Semantic Gate v0.5 verdict **REWORK** (`DEEPSEEK_SEMANTIC_REWORK_PROMPT_v05.md`). Not yet an Alloy implementation.
> **Canonical constraint:** `formal/RESEARCH_LOCK_SNAPSHOT.md` §9 (Threat Model), §8 (S1–S5), §16 (Mechanism Ablation Plan), §17 (Concurrency Claim Boundary).
> **Rule:** this document only formalizes the locked threat model. It does not add threats, widen novelty claims, or begin Alloy implementation.
> **v0.6 changes:** `orderedTrace` now enforces `stateInvariant` on every state in every reachable trace (P0), and the ABL_1..ABL_10 dependency re-check shows every ablation witness still satisfies that invariant (P0 dep); the formal trace predicate mirrors the detailed producer/evidence/value/version/certificate/authorization checks, but the Alloy P6 corruption/minimality claim is restricted to source-anchor loss/replacement and source-version duplicates, with individual binding-corruption necessity evaluated through executable conformance tests and not claimed as a separate Alloy minimality result (P1-1); `State.candidates` is explicitly auxiliary and no P0–P6 claim depends on it, while the scientific persistence object remains the Certificate with embedded Candidate (P1-2).

---

## 1. Purpose

This file defines, for the formal model in `FORMAL_MODEL.md` v0.6:

1. who can perform which primitive action;
2. which substituted / replayed / corrupted / unrecorded-value / conjured-artifact attempts are representable;
3. how each in-scope threat maps to a reachable `Event`, a violated contract conjunct, a property, and a concrete Auto-Decte fault;
4. exactly how invalid states enter the Alloy search space;
5. which boundaries are deliberately out of scope.

---

## 2. System boundary and trusted components

**System under study:** the admission path from machine-derived candidate to committed record fact in Auto-Decte.

Trusted (attacks against them are out of scope, lock §9):

- trusted Python/SQLite runtime;
- trusted DB engine;
- OS process boundary;
- SHA-256 as a collision-resistant hash;
- cryptographic supply chain;
- physical infrastructure.

Untrusted / fault-prone (attacks are in scope):

- OCR / HOG-SVM perception outputs;
- LLM suggestion adapter;
- local retrieval adapter;
- human reviewer as an authorization actor who may be stale, concurrent, or substituted at the application layer;
- machine modules that attempt direct fact writes;
- a local tamperer who, in the **formal v0.6 model** (v0.4 P1-1 carried), can issue transition-row-only corruption/deletion/rebinding. The concrete fault benchmark additionally exercises certificate/decision/evidence-row SQL mutations, but those are implementation-level robustness evidence **outside** the Alloy P6 submodel, not formal `TamperEvent` capabilities.

**P0-3 trust note.** Machine services may persist certificates (each certificate embeds its `Candidate` payload) and evidence, but the formal machine semantics does **not** permit them to persist an `Authorization` (v0.5 P2-2). Authorization is created only atomically inside an `AdmissionEvent` (review + commit) or by trusted initialization. Until the planned `AuthorizationBindingRow` exists, the formal `Authorization.certificate` / `authorizedValue` relations have no exact persisted counterpart; the current transition-level `(decision_id, certificate_id)` pair is **conformance evidence only**, not the formal decision-time binding.

---

## 3. Attacker capabilities

| Capability | In scope? | Formal representation | Concrete representation |
|---|---|---|---|
| Produce wrong recognition candidate | Yes | `MachineEvent` creates candidate with wrong `value` | wrong OCR/HOG-SVM output |
| Produce wrong LLM suggestion | Yes | `MachineEvent` creates candidate with wrong `value` | AI adapter fault corpus |
| Retrieve irrelevant evidence | Yes | `MachineEvent` creates candidate whose `evidence` identity is irrelevant to target | retrieval fault corpus |
| Attempt a direct fact write | Yes | non-`AdmissionEvent` event attempting a fact delta | `attempted_direct_fact_write` benchmark (12 attempted paths, 12 blocked) |
| Machine fabricates an Authorization | Yes (must be impossible) | `MachineEvent` with `post.authorizations != pre.authorizations` | no production path; asserted by P0 (P0-3) |
| Substitute field (S1) | Yes | `AdmissionEvent.targetField != certificate.candidate.targetField` | cross-field certificate selection in `confirm()` |
| Substitute evidence identity (S2a) | Yes | `sameEvidenceIdentity(targetEvidence, certificate.candidate.evidence) = False` | wrong `evidence_hash` or wrong `evidence_locator` |
| Substitute evidence owner (S2b) | Yes | `targetEvidence.record != targetRecord` while identity matches | `EVIDENCE_FORM_MISMATCH` |
| Substitute record (S3) | Yes | `AdmissionEvent.targetRecord != certificate.candidate.targetRecord` | certificate for form A used on form B |
| Version substitution: certificate↔attempt (S4a) | Yes | `e.expectedVersion != certificate.candidate.expectedVersion` while attempt is fresh | missing check that `certificate.expected_fact_version == expected_version` in `confirm()` |
| Stale replay against current record version (S4b) | Yes | `e.expectedVersion != pre.currentVersion[targetRecord]` | `STALE_FACT_VERSION` / CAS update returning 0 rows |
| Substitute authorization/certificate (S5) | Yes | `canonicalCertId[e.authorization.certificate] != canonicalCertId[e.certificate]` | `DECISION_CANDIDATE_MISMATCH`; planned `AuthorizationBindingRow` enforcement |
| Commit an unrecorded final value (S8, P0-1) | Yes | `e.value != e.authorization.authorizedValue`; ABL_8 witness has committed value Y and source-transition value X (`X != Y`), so strengthened P5 fails on `t.value != post.committedValue` | missing authorized-value column; planned binding payload check |
| Conjure certificate at admission (S9, P1-1) | Yes | `e.certificate not in e.pre.certificates`; the scientific persistence object is the persisted Certificate with embedded Candidate, so no separate candidate-preexistence conjunct is needed; `State.candidates` is only an auxiliary machine-artifact set and no P0–P6 claim depends on it (v0.6 P1-2) | derived-certificate-at-confirm path reworked as planned conformance change |
| Conjure evidence at admission (S10, P1-1) | Yes | `e.targetEvidence not in e.pre.evidence` | evidence row created in the same fact-writing transaction |
| Sequential competing confirmation | Yes | A generated for v0 commits v0→v1; B generated for v0 is a later edge with pre.currentVersion=v1 and rejects | CAS first-write and retry in `append_fact_transition` |
| Duplicate evidence | Yes | two distinct `Evidence` atoms with equal `(content, locator)`; not distinct certificate contexts | SHA-256 duplicate detection / duplicate-evidence fault |
| Tamper transition fields | Yes | `TamperEvent` may replace/rebind any transition field by swapping the transition atom in `State.transitions` (transition-only) | SQL `UPDATE fact_transitions ...` in fault benchmark |
| Delete transition | Yes | `TamperEvent` removing a transition from `State.transitions` | SQL `DELETE FROM fact_transitions` |
| Rebind transition / version | Yes | `TamperEvent` changing transition references (target record/field, evidence, from/to version, value, producer, certificate, authorization) | SQL rebind to another certificate/decision/record-version row |
| Delete or mutate certificate / decision / evidence rows | Concrete-only (not formal) | **not** a v0.4 `TamperEvent` capability; `tamperStep` preserves `certificates`, `authorizations`, and `evidence` | SQL mutation tests exist in the fault benchmark and are labeled implementation-level robustness evidence outside the Alloy P6 submodel (P1-1) |
| Approve a wrong value as an **authenticated** reviewer | Boundary | correct bindings, wrong `authorizedValue` | wrong-but-attributable commit; reviewer correctness is out of epistemic scope |
| Unauthorized / unregistered principal (v0.5 P2-1) | Blocked | `e.authorization.principal not in PrincipalRegistry.authorized` | `UNATTRIBUTED_DECISION` / missing registered reviewer |
| Real-world impersonation of a valid reviewer | Out of scope (distinct from unauthorized principal) | not modeled as defeatable | lock §9 forged real-world human identity |

---

## 4. Formal threat model (reachable traces, one event per edge)

`FORMAL_MODEL.md` has three primitive event families inside an ordered state trace whose edge `i` has **exactly one** event `trace.events[i]` (P1-5):

```
MachineEvent     — may create candidates/certificates/evidence; never
                   authorizations; never committedValue/committedSource/
                   currentVersion.
AdmissionEvent   — the only event allowed to change committedValue/
                   committedSource/currentVersion, and only through
                   admissionEffect under the full contract. It may atomically
                   persist the human Authorization (P0-3).
TamperEvent      — transition-only corruption/deletion/rebinding (v0.4 P1-1);
                   may change State.transitions; never committedValue,
                   committedSource, currentVersion, or other artifacts.
```

The formal threat model is the **set of all events occurring in some ordered trace** whose pre/post states satisfy the base `eventStep` predicates but violate at least one conjunct of `Contract` or of the trace predicate. Those events are reachable in the pre-contract state space; the assertions P0–P6 exclude their effective occurrence in full (`EnforcingTrace`) histories.

**v0.6 P0 — structural invariant is enforced on reachable states.** `orderedTrace` itself asserts `all s: tr.states.elems | stateInvariant[s]` (FORMAL_MODEL.md §5.1). Therefore every state used by any threat witness or assertion must satisfy: `currentVersion[r].record = r`; `(some committedValue[r,f]) iff (some committedSource[r,f])`; and `committedSource[r,f].targetRecord = r` / `.targetField = f`. The invariant intentionally has **no** `committedSource in s.transitions` clause (post-tamper P6 states may keep a deleted source anchor) and **no** `committedSource.value = committedValue` clause (that is the P5/P6 binding property). No threat in this file relies on violating those structural clauses; all in-scope attacks violate contract or trace-validation conjuncts on top of structurally valid states.

**P0-2:** P3 and P5 are admission-time properties of the unique transition appended by an effective `AdmissionEvent`. They do **not** claim that every transition in every later reachable state is always correctly bound; that post-tamper question belongs to P6, which starts from a committed `(record, field)` fact, follows `committedSource`, and reports `Incomplete` when the source anchor is missing/replaced or when the source-version slot has a duplicate (v0.5 P0-1/P1).

**P0-3:** threat conditions and assertions are stated over `Init`, `eventStep`, `Occurs`, `wellFormedTrace`, `orderedTrace` (including its v0.6 `stateInvariant` clause), `ReachableState`, `ReachableEvent` (FORMAL_MODEL.md §5). A threat is only considered representable if a SAT-2 witness exists in an ordered trace.

---

## 5. The substitution attacks (S2 and S4 split per P1-3/P1-4)

### S1 — Field substitution

```
field_A -> field_B
```

A certificate for `field_A` is carried by an admission attempt targeting `field_B`. The proposed value may be identical.

- Violated conjunct: `C-field`.
- Blocking property: P1 / P2.
- Concrete guard: `confirm()` rejects `FIELD_KEY_BINDING_MISMATCH` when `loaded.field_key != field_key`; `TransitionPolicy.authorize()` and `verify_transition_authorization()` also check decision-field binding.
- Concrete tests: `test_confirm_rejects_cross_field_selected_certificate`, `test_confirm_rejects_cross_field_abstained_certificate`.
- A1 witness: `e.targetField = f_B`, `certificate.candidate.targetField = f_A`; every other conjunct is satisfiable because no remaining conjunct mentions `candidate.targetField`.

### S2 — Evidence substitution (split per P1-3)

```
e_A -> e_B
```

Two independent sub-cases, each its own ablation:

- **S2a evidence-identity substitution:** `sameEvidenceIdentity[e.targetEvidence, certificate.candidate.evidence] = False` — different `content` or different `locator`. Violates `C-evidence-id`. Removed by `ABL_2a`.
- **S2b evidence-record substitution:** `sameEvidenceIdentity[e.targetEvidence, certificate.candidate.evidence]` but `e.targetEvidence.record != e.targetRecord`. Violates `C-evidence-record`. Removed by `ABL_2b`.

Evidence identity is `(content, locator)`, the same pair frozen in `CandidateCertificate._content()` as `evidence_hash` + `evidence_locator` (P1-2). Raw evidence-atom inequality is **not** the binding: two duplicate rows with equal `(content, locator)` are the same certificate context.

- Blocking property: P1 / P2.
- Concrete guard: independent evidence-row loading; `EVIDENCE_HASH_MISMATCH`; `EVIDENCE_FORM_MISMATCH`; `EVIDENCE_BINDING_MISSING`.
- Concrete tests: `test_confirm_rejects_tampered_evidence_row_hash`, `test_confirm_rejects_cross_form_manual_evidence`.

**P0-1 note (v0.2, retained):** because there is no global axiom `candidate.evidence.record = candidate.targetRecord`, S2a and S2b remain independent from S3. Retaining `C-evidence-id` + `C-evidence-record` while removing `C-record` derives only `candidate.evidence.record = e.targetRecord` (for the candidate's evidence atom) and says nothing about `candidate.targetRecord`, so A3 remains satisfiable.

### S3 — Record substitution

```
record_A -> record_B
```

A certificate for `record_A` is used in an attempt whose target is `record_B`.

- Violated conjunct: `C-record`.
- Blocking property: P1 / P2.
- Concrete guard: `RECORD_BINDING_MISMATCH` in `verify_transition_authorization`; certificate `target_record_id` is frozen into the certificate content address.
- Concrete tests: cross-form certificate/evidence tests in `test_authority_integration.py`.
- A3 witness: `candidate.targetRecord = r_A`, `e.targetRecord = r_B`, `candidate.evidence` with an evidence identity owned by `r_B`, `candidate.expectedVersion` a Version of `r_B`; `C-evidence-id`, `C-evidence-record`, `C-version`, `C-fresh` all hold for the `r_B` attempt, and no remaining conjunct mentions `r_A`. This is possible only because the v0.1 candidate-coherence axiom was removed (v0.2 P0-1).

### S4a — Certificate↔attempt version substitution (P1 scope)

```
certificate.expectedVersion = v_i,  attempt.expectedVersion = v_j,  v_i != v_j
```

The certificate embeds version `v_i`, but the admission attempt declares the record's current version `v_j` and is otherwise fresh. Without `C-version` the attempt writes at `v_j` even though the certificate was not bound to `v_j`.

- Violated conjunct: `C-version`.
- Blocking property: P1 (version is part of certificate context).
- Concrete guard: `TransitionPolicy.authorize()` / `confirm()` must check `certificate.expected_fact_version == expected_version`; the certificate content address freezes `expected_fact_version`.
- Concrete tests: expected-version mismatch tests for certificate vs attempt.

### S4b — Stale replay against current record version (P4 scope)

```
certificate.expectedVersion = v_i,  pre.currentVersion[targetRecord] = v_j,  v_i != v_j
```

A certificate/decision produced at version `v_i` is replayed after the record has advanced to `v_j`. The attempt correctly mirrors the certificate (`e.expectedVersion = certificate.expectedVersion`), but it is stale against the whole-record counter.

- Violated conjunct: `C-fresh`.
- Blocking property: P4 (supporting property; OCC/CAS reused).
- Concrete guard: application precheck `expected_version == form.current_record_version`; database CAS `UPDATE ... WHERE current_record_version = expected_version` is the first write of one transaction.
- Concrete tests: `test_confirm_stale_version_rejected`, `test_review_rejects_a_stale_expected_version`, CAS conflict tests.

**P1 vs P4 scope:** S4a is a certificate-context (version binding) violation and belongs to P1. S4b is a current-state freshness violation and belongs to P4. They are checked separately as `ABL_4a` and `ABL_4b`.

### S5 — Authorization / certificate substitution

A legal `Authorize(Cert_A, v)` is attempted against `Cert_B`, even when `Value(Cert_A) = Value(Cert_B)`.

```
canonicalCertId(Cert_A) != canonicalCertId(Cert_B)
and Value(Cert_A) = Value(Cert_B)
and Authorize(Cert_A, v)
  !=>  successful admission with Cert_B
```

- Violated conjunct: `C-auth-cert` (exact primitive `certId` equality, v0.4 P1-2).
- Blocking properties: P1 (non-transferability) and P3 (authorization reference integrity).
- Concrete guard: `HumanDecision.candidate_id` must equal `CandidateCertificate.candidate_id` (`DECISION_CANDIDATE_MISMATCH`); transition must reference the same `certificate_id` as the decision; `verify_transition_authorization` re-verifies the whole attempt. The planned `AuthorizationBindingRow` will make `decision -> certificate_id` an immutable decision-time relation.
- Concrete tests: `test_authorize_requires_decision_candidate_binding`, transition-vs-certificate mismatch tests, `test_model_substitutability_preserves_contract`.

**S5 is the decisive experiment.** The model must contain two distinct certificates with the same value payload but different modeled context; the one-way fact `certIdFaithfulToModeledBindings` gives them **different canonical ids**, and the full model must reject the transfer while `ABL_5` admits it. With `C-auth-value` retained, the witness uses `e.value = e.authorization.authorizedValue = valueX` so only the certificate transfer is being tested. The model asserts **no** converse: two certificates with an identical modeled tuple may carry different primitive `certId`s because unmodeled `_content()` inputs (policy/template/config identity) can distinguish them; S5 still operates on exact `certId` equality, so no collapse is possible.

### S8 — Unrecorded final value (P0-1)

```
candidate.value = X,  authorization.authorizedValue = X (or any Z),
e.value = Y,  Y != authorization.authorizedValue
```

Every context and authorization/certificate binding holds, but the effective write commits `Y`. Without `C-auth-value` the payload is not bound to the authorization.

- Violated conjunct: `C-auth-value`.
- Blocking properties: P3/P5 (authorization must carry the exact committed value; the transition must describe the actual committed update).
- Concrete guard: planned `AuthorizationBindingRow.authorized_value_payload/hash` checked against the committed `RecordVersion.values[field_key]`; currently the value path is guarded only indirectly through certificate derivation.
- Ablation: `ABL_8` removes `C-auth-value`. The witness has `e.authorization.authorizedValue = X`, `e.value = Y`, `X != Y`; the effective write commits `Y` in `committedValue`, and the retained `C-transition` binds the unique source transition to `t.value = X`. All remaining conjuncts hold. The strengthened `transitionIntegrity(e)` then fails on `t.value != e.post.committedValue[targetRecord][targetField]` — the v0.4 P0-1 intended reason.

**Accept vs Correction are both legal.** Accept sets `authorizedValue = candidate.value`; Correction sets `authorizedValue != candidate.value`. S8 tests only the third case: a value the authorization never carried.

### S9 / S10 — Conjured durable artifacts (P1-1)

```
S9: e.certificate not in e.pre.certificates
S10: e.targetEvidence not in e.pre.evidence
```

Base `admissionEffect` adds both artifacts to the post-state, so without `C-cert-preexists` / `C-evidence-preexists` an effective admission could materialize its own certificate or evidence at commit time.

- Violated conjuncts: `C-cert-preexists` / `C-evidence-preexists`.
- Blocking properties: P3/P5 (admission-time artifact durability).
- Concrete guard: machine `append_candidate_unit` persists evidence+certificate before any human confirm; the planned correction conformance keeps the machine certificate as the reviewed certificate (see FORMAL_MODEL.md §14.2).
- Ablations: `ABL_9` and `ABL_10`.

---

## 6. Other in-scope threats

| Threat | Property | Expected full-model outcome | Concrete fault/tests |
|---|---|---|---|
| Wrong machine prediction | P0, P2 | Candidate created; committed state unchanged | `wrong_recognition` fault, `fact_unchanged = True` |
| Wrong LLM suggestion | P0, P2 | Candidate created; committed state unchanged | `wrong_llm_suggestion` fault |
| Irrelevant retrieval | P0, P2 | Candidate created; committed state unchanged | `irrelevant_retrieval` fault |
| Direct machine fact write | P0 | No committed-value/version delta without AdmissionEvent | `attempted_direct_fact_write`: 12/12 paths blocked |
| Machine creates Authorization | P0 (P0-3) | `authorizations` unchanged across every MachineEvent | no production path; asserted |
| Sequential competing confirmation | P4 | A commits v0→v1; later B with expectedVersion v0 rejects with `sameState` | CAS tests; `ConcurrentReviewError` tests |
| Duplicate evidence (equal content+locator) | P0/P2 | Not distinct certificate contexts; no extra fact from duplicate identity alone | `duplicate_evidence` fault |
| Transition producer tampering | P6 (formal: source-anchor loss; executable conformance: producer check) | Alloy sees the old source atom removed/replaced, so `traceComplete` is Incomplete via source-anchor loss; the specific producer mismatch is checked by the executable verifier | `_tamper("fact_transitions","producer_id","tampered-producer")` |
| Transition deletion | P6 (formal) | `committedSource[r,f] = t` and `t not in s.transitions` ⇒ Incomplete | `DELETE FROM fact_transitions` |
| Transition rebinding (record/field/evidence/certificate/authorization) | P6 (formal: source-anchor loss; executable conformance: each specific binding) | Alloy sees the source atom replaced, so the anchor is missing; the detailed rebinding equality checks are exercised by executable conformance tests and are not claimed as separate Alloy minimality results (v0.6 P1) | rebind transition row to wrong certificate/decision/record-version row |
| Transition value rebinding | P6 (formal: source-anchor loss; executable conformance: value anchors) | Alloy sees the source atom replaced, so the anchor is missing; the `t.value == committedValue` / `== authorizedValue` checks are exercised by executable conformance tests and are not separate Alloy minimality claims | planned binding payload check |
| Record-version rebinding (transition version fields) | P6 (formal: source-anchor loss; executable conformance: from/toVersion checks) | Alloy sees the source atom replaced; executable verifier checks `fromVersion`/`toVersion` | FK-valid rebind to next version's row test |
| Duplicate transition insertion | P6 (formal) | second transition with the same `(r, f, src.toVersion)` violates the source-version uniqueness conjunct in `traceComplete` (v0.5 P0-1) | unique `(form_id, created_version, field_key)` + duplicate-fault test |
| Incomplete reverse trace (deleted/broken source) | P6 | Not `Complete` for the committed `(r,f)` query | trace-status assertions in pipeline benchmark |
| Mismatched certificate/decision/transition references | P1/P3/P5/P6 | At admission: rejected; post-tamper: source-anchor loss/replacement makes formal P6 Incomplete; detailed reference mismatches are exercised by executable conformance tests and are not separate Alloy minimality claims | `verify_transition_authorization` and `build_provenance_trace` tests |
| Missing/deleted authorization, certificate, or evidence rows | Concrete-only (not formal P6) | not reachable under v0.4 `TamperEvent`; labeled implementation-level robustness evidence outside the Alloy P6 submodel (P1-1) | concrete SQL deletion tests if present |

---

## 7. Out of scope (lock §9, verbatim boundary)

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

**Consequence for Alloy:** the model must not assert security against an arbitrary coherent writer. `TamperEvent` is limited to transition-only corruption/deletion/rebinding (v0.4 P1-1 carried); it cannot rewrite facts, versions, certificates, decisions, or evidence, and it cannot rewrite all references simultaneously into a new coherent history. `P6` inherits this boundary and is worded only as source-anchor loss/replacement + source-version duplicate detection (v0.6 P1).

---

## 8. Critical boundary: wrong authenticated decision vs unauthorized principal vs unrecorded value

> **Human authorization != human correctness.**

| Failure class | Formal state | Is it blocked? | Guarantee |
|---|---|---|---|
| An authenticated reviewer approves a wrong `value` for the correctly bound certificate/context | `e.authorization.principal in authorized`, `authorizedValue` is the wrong value, all `C-*` conjuncts hold | Not blocked by the admission contract | Wrong but attributable, bound, fresh, traceable commit; reviewer correctness is out of scope |
| A value the authorization **never carried** | `e.value != e.authorization.authorizedValue` | Blocked by `C-auth-value` | The committed value is the authorization's exact authorized value (P0-1) |
| A decision claims an unregistered / empty / unauthorized principal | `e.authorization.principal not in PrincipalRegistry.authorized`, or principal identity empty | Blocked by `C-principal` | The attempted authorization references a registered authorized principal (v0.5 P2-1); real impersonation of a valid reviewer is out of scope |
| An authorization created for `Cert_A` is carried against `Cert_B` | `canonicalCertId[e.authorization.certificate] != canonicalCertId[e.certificate]` | Blocked by `C-auth-cert` | Authorization is certificate-bound and non-transferable |

The paper guarantees attribution, binding, freshness, authorized-value binding, transition integrity, and traceability. It does **not** guarantee semantic truth of the committed value.

---

## 9. Property coverage map

| Threat family | P0 | P1 | P2 | P3 | P4 | P5 | P6 |
|---|---|---|---|---|---|---|---|
| Direct machine write | X | | | | | | |
| Machine-created Authorization (P0-3) | X | | | | | | |
| S1 field substitution | | X | X | | | | |
| S2a evidence identity substitution | | X | X | | | | |
| S2b evidence owner substitution | | X | X | | | | |
| S3 record substitution | | X | X | | | | |
| S4a cert↔attempt version substitution | | X | X | | | | |
| S4b stale replay vs current record version | | | X | | X | | |
| S5 auth/cert substitution | | X | X | X | | | |
| S8 unrecorded final value | | | X | X | | X | X |
| S9/S10 conjured certificate/evidence | | | X | X | | X | |
| Unauthorized / unregistered principal | | | X | X | | | |
| Sequential competing confirmation | | | X | | X | | |
| Transition tamper/delete/rebind (transition-only, v0.4 P1-1) | | | | | | X | X |
| Source-version duplicate insertion (v0.5 P0-1) | | | | | | | X |
| Trace corruption (missing/replaced source anchor, duplicate source version) | | | | | | | X |
| Certificate/decision/evidence-row corruption or deletion | concrete-only evidence outside Alloy P6 | | | | | | |

---

## 10. How invalid states enter the Alloy state space

This section answers requirement 7 of the lock's immediate next step explicitly, in reachable-trace form.

### 10.1 Invalid attempts are ordinary atoms in ordered traces

An `AdmissionEvent` is a signature with free relations. In some `Init`/`eventStep` trace, Alloy may instantiate:

- `e.certificate = Cert_A` and `e.targetField = field_B` (S1);
- `e.targetEvidence` with a different `(content, locator)` than `candidate.evidence` (S2a), or same identity but a different `.record` (S2b);
- `e.targetRecord` pointing at another record (S3);
- `e.expectedVersion` differing from the certificate's version while fresh (S4a);
- `e.expectedVersion` equal to the certificate's version but stale against `pre.currentVersion` (S4b);
- `e.authorization.certificate = Cert_A` while `e.certificate = Cert_B` with distinct canonical ids (S5);
- `e.value` differing from `e.authorization.authorizedValue` (S8); in ABL_8 the base effect commits `Y` while the retained `C-transition` makes the source transition record `X`, so the strengthened P5 fails on the committed-state anchor;
- `e.certificate` or `e.targetEvidence` absent from the pre-state (S9/S10).

No `fact` forces these relations to agree. They exist in the pre-contract universe by construction.

### 10.2 Base semantics does not filter them

`baseAdmissionStep` is `rejectedAdmission[e] or admissionEffect[e]`. For a substituted event, Alloy may choose the `admissionEffect` branch and produce a state where the wrong field/record/evidence/version/value was committed at the record's next whole-record version. That state is the counterexample target of the ablation checks. **v0.6 P0:** every such ordered-trace state still satisfies the structural `stateInvariant` — the attacks are binding/contract violations, not violations of the four structural clauses (FORMAL_MODEL.md §7.3).

### 10.3 The contract is applied only at the enforcing boundary

`EnforcingTrace` constrains only **effective** admission events occurring in the trace (`admissionEffect[e] => Contract[e]`). Rejected attempts remain in the trace with `sameState(pre, post)`, possibly moving to a distinct snapshot atom with identical contents (P1-6). Full-model assertions then ask: can an effective substituted event occur in an `EnforcingTrace`? The expected bounded answer is no.

### 10.4 Tamper and sequential interleaving states

`TamperEvent` may produce any transition set while preserving `committedValue`, `committedSource`, `currentVersion`, and all other artifacts (transition-only, v0.4 P1-1). Deleting or replacing the fact's source transition leaves `committedSource[r,f]` pointing at the old atom, so `traceComplete[s,r,f]` observes `Incomplete`. Because the invariant has no transition-membership clause, that post-tamper state still satisfies `stateInvariant` (v0.6 P0). Competing confirmations are **sequentialized** (P1-4): A generated for `v0` commits at edge `i`; B generated for `v0` is a later edge whose pre-state already has `currentVersion = v1`, so B is stale and rejected. Both configurations are reachable and must be exhibited by SAT-2 runs.

### 10.5 Non-degeneracy requirements (SAT-2 witnesses)

The later Alloy implementation must provide ordered-trace `run` witnesses for:

1. one valid Accept (SAT-1) and one valid Correction (SAT-1-correction);
2. one field-substituted effective admission with contract off (S1);
3. one evidence-identity-substituted effective admission with contract off (S2a);
4. one evidence-record-substituted effective admission with contract off (S2b);
5. one record-substituted effective admission with contract off (S3);
6. one certificate↔attempt version-substituted effective admission with contract off (S4a);
7. one stale effective admission with contract off (S4b);
8. one authorization-transfer effective admission with `Value(Cert_A) = Value(Cert_B)`, distinct canonical ids, contract off (S5);
9. one unrecorded-value effective admission with contract off (S8), exhibiting committed value Y and source-transition value X with `X != Y`;
10. one conjured-certificate and one conjured-evidence effective admission with contract off (S9/S10);
11. one transition-only tampered/deleted/rebound state (source transition removed or replaced), one source-version duplicate state, plus explicit note that certificate/decision/evidence-row faults are concrete-only;
12. one sequentialized competing confirmation pair: A commits v0→v1, later B stale-rejects.

If any witness is unsatisfiable, the model accidentally excluded the attack by construction and must be fixed before the Semantic Gate.

---

## 11. Ablation threat realization

| Ablation | Removed conjunct | Attack becomes possible | Property check that must then FAIL |
|---|---|---|---|
| A1 | `C-field` | S1 cross-field admission | P1 |
| A2a | `C-evidence-id` only | S2a cross-evidence-identity admission | P1 |
| A2b | `C-evidence-record` only | S2b wrong evidence owner admission | P1 |
| A3 | `C-record` | S3 cross-record admission | P1 |
| A4a | `C-version` only | S4a certificate↔attempt version substitution | P1 |
| A4b | `C-fresh` only | S4b stale replay against current record version | P4 |
| A5 | `C-auth-cert` | S5 authorization transfer | P1/P3 |
| A6 | `C-transition` | missing source transition, duplicate transitions, or appended transition != `committedSource[r,f]` with misbound fields | P5 |
| A7 | trace validation | corrupted trace reported `Complete`: deleted/replaced source anchor or duplicate `(r, f, src.toVersion)` transition | P6 |
| A8 | `C-auth-value` | S8 committed value Y while source transition records authorized value X (`X != Y`); strengthened P5 fails on `t.value != post.committedValue` | P3/P5 |
| A9 | `C-cert-preexists` | S9 certificate conjured at admission | P3/P5 |
| A10 | `C-evidence-preexists` | S10 evidence conjured at admission | P3/P5 |

Each ablation removes exactly one mechanism and keeps all other conjuncts (including the structural `stateInvariant`, `certIdFaithfulToModeledBindings`, and `certIdRowUnique`). **v0.6 P0 dependency re-check:** because `stateInvariant` is now enforced inside `orderedTrace`, every ablation witness must land in a state satisfying all four invariant clauses. FORMAL_MODEL.md §7.3 records this ablation by ablation: ABL_1, ABL_2a, ABL_2b, ABL_3, ABL_4a, ABL_4b, ABL_5, ABL_6, ABL_7, ABL_8, ABL_9, ABL_10 each remain structurally satisfiable. In particular ABL_3 / `C-record` remains independent: `stateInvariant => currentVersion[targetRecord].record = targetRecord` is available, but it never mentions `candidate.targetRecord`, so the S3 cross-record witness still lands in an invariant state. The expected counterexample must be checked by a dedicated `check Ablation_i_has_counterexample` command, and that check must **fail** (find a counterexample). FORMAL_MODEL.md §7.3 proves by construction that no removed conjunct is implied by the rest. `ABL_2a` and `ABL_2b` are separate commands (P1-3).

---

## 12. Trace-corruption submodel (v0.6 carries v0.5 P0-1/P0-2/P1)

In-scope trace corruption is modeled as a `TamperEvent` that changes **only** `State.transitions` (v0.4 P1-1). Alloy atoms are immutable, so a SQL `UPDATE` of a transition field is modeled by removing the old transition atom from `State.transitions` and inserting a different atom. Because `tamperStep` preserves `committedSource`, the formal P6 detection route for a rebound transition is **source-anchor loss/replacement** (the preserved `committedSource[r,f]` points at the old atom, which is no longer in `s.transitions`), not the individual field-equality check that the concrete verifier runs.

**Formal P6 claim (v0.6 P1).** Alloy P6 claims exactly two outcomes for every reachable state and committed fact `(r,f)`:

1. **source-anchor loss/replacement** — `committedSource[r,f] = t` and `t not in s.transitions` (deletion or any transition-field rebinding represented by atom replacement) ⇒ `traceComplete[s,r,f] = Incomplete`;
2. **source-version duplicate** — two transitions in `s.transitions` share `(targetRecord = r, targetField = f, toVersion = committedSource[r,f].toVersion)` ⇒ `traceComplete[s,r,f] = Incomplete` (v0.5 P0-1 carried).

The formal trace predicate mirrors the producer/evidence/value/version/certificate/authorization binding checks, but the Alloy P6 corruption/minimality claim is restricted to those two source-anchor outcomes. Individual binding-corruption necessity is evaluated through executable conformance tests and is not claimed as a separate Alloy minimality result.

| Corruption | Formal effect under `TamperEvent` | Formal P6 claim | Executable conformance check (not an individual Alloy claim) |
|---|---|---|---|
| Transition deletion | source anchor removed | Incomplete: source missing | deleted transition id cannot be resolved |
| Producer rebinding | old source atom removed; new atom inserted | Incomplete: source anchor replaced | `t.producer == certificate.producer` |
| Field rebinding | old source atom removed; new atom inserted | Incomplete: source anchor replaced | `t.field_key == certificate.field_key` |
| Record rebinding | old source atom removed; new atom inserted | Incomplete: source anchor replaced | `t.record_id == certificate.target_record_id` |
| Evidence identity rebinding | old source atom removed; new atom inserted | Incomplete: source anchor replaced | `evidence_hash/locator == certificate.evidence_hash/locator` |
| Evidence owner rebinding | old source atom removed; new atom inserted | Incomplete: source anchor replaced | evidence row belongs to the same form |
| Value rebinding | old source atom removed; new atom inserted | Incomplete: source anchor replaced | `t.value == committedValue` and `t.value == authorizedValue` |
| Version rebinding | old source atom removed; new atom inserted | Incomplete: source anchor replaced | `fromVersion/toVersion/record_version_id` checks |
| Certificate rebinding | old source atom removed; new atom inserted | Incomplete: source anchor replaced | exact `certificate_id` match |
| Authorization rebinding | old source atom removed; new atom inserted | Incomplete: source anchor replaced | decision/binding id and authorized-value match |
| Duplicate transition insertion | extra atom inserted with the same `(r, f, src.toVersion)` | Incomplete: source-version uniqueness fails | unique `(form_id, created_version, field_key)` + duplicate fault |

**P0-2 source anchor (v0.5 carried).** The formal `committedSource` is mapped to the planned immutable `RecordVersionRow.fact_sources[field_key]` (§14.3 of FORMAL_MODEL.md), copied forward per snapshot and updated per admission. The derivation `MAX(created_version) among remaining FactTransition rows` is **withdrawn**: it would let deleting the latest transition promote an older row to source, which contradicts the preserved formal source identity. After the planned schema change, deleting a transition leaves the stored `source_transition_id` unresolved and P6 returns `Incomplete`; no older row is silently promoted. Current repository conformance is explicitly **conditional** on that planned change.

**Duplicate evidence note.** A swap between two evidence rows with equal `(content, locator)` is **not** a detected corruption class: the concrete certificate and transition both identify evidence by `evidence_hash` + `evidence_locator`, not by `file_id`. The formal model states the same boundary via `sameEvidenceIdentity`.

**P1-2 certificate identity note.** Certificate hops use exact primitive `certId` equality. Two concrete certificates with identical modeled components but different unmodeled `_content()` inputs (policy/template/config identity) may have different `certId`s; the formal model asserts no converse, so S5 and P6 never collapse them.

**Narrowed claim (v0.6).** The paper claims **trace soundness for source-anchor loss/replacement and source-version duplicate detection**, and nothing stronger. It does **not** claim that any row-identity change is detectable, that each individual binding check is a minimal Alloy theorem, or that a coherent rewrite of all dependent artifacts is detected. If an attacker can consistently rewrite the transition, decision, certificate, evidence, and version rows so every cross-reference agrees again, `traceComplete` can pass; such a rewrite is outside the locked threat model (arbitrary privileged DBA) and would require an immutable external anchor to detect. This boundary is stated in every paper section that mentions P6.

---

## 13. Concrete evidence already owned by the project

These existing assets are reinterpreted as implementation-level conformance evidence (lock §20), not as new experiments:

- existing fault corpus: wrong recognition, wrong LLM suggestion, irrelevant retrieval, stale human replay, duplicate evidence, attempted direct fact write;
- cross-field / cross-form faults;
- stale replay;
- producer tampering;
- deleted transition;
- record-version rebinding;
- certificate-row / decision-row / evidence-row SQL faults (if present in the benchmark), explicitly labeled **implementation-level robustness evidence outside the Alloy P6 submodel** (v0.4 P1-1);
- planned post-PASS evidence for the v0.6 P6 claim: immutable `RecordVersionRow.fact_sources` anchor plus transition-deletion and duplicate-transition faults that leave the stored source id unresolved;
- randomized trials;
- 239 automated tests;
- Ruff / mypy;
- deterministic reproducibility and byte-identical outputs;
- manifest.

The 239 tests demonstrate software artifact quality, **not** a scientific sample size.

**Planned conformance gaps (two, both post-PASS):** (1) until `AuthorizationBindingRow` (with `certificate_id` and `authorized_value_payload/hash`) is implemented (§14.2 of FORMAL_MODEL.md), S5 and S8 conformance is evidenced by `decision.candidate_id = certificate.candidate_id` plus transition reference checks, but is not yet the literal `Authorization.certificate` / `Authorization.authorizedValue` relation. (2) Until `RecordVersionRow.fact_sources` is implemented (§14.3 of FORMAL_MODEL.md), the v0.6 P6 source-anchor claim has no exact current concrete anchor; current repository evidence does **not** yet literally support the remaining formal P6 claim, and no document claims otherwise. The current derived-certificate correction path is also not yet the v0.6 formal reading (machine-derived-only embedded `Candidate`; correction carried solely by `Authorization.authorizedValue`). These gaps are documented, not hidden.
