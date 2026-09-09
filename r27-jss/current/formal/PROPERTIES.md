# PROPERTIES.md — Auto-Decte Historical Singleton Property Draft v0.6

> **2026-08-23 implementation addendum:** P0–P6 have been lifted to the approved batch model in `formal/alloy/batch/`. The active development freeze contains multi-item legal witnesses, effective paired ablations, non-circular preservation checks, singleton mapping checks, and corrected legal-prefix P6 witnesses at S1/S2. This file remains the historical singleton property record; use the batch README/results for current executable evidence.

> **Status:** DeepSeek Property Draft v0.6 — revised after the GPT-5.6 Sol Semantic Gate v0.5 verdict **REWORK** (`DEEPSEEK_SEMANTIC_REWORK_PROMPT_v05.md`).
> **Canonical constraint:** `formal/RESEARCH_LOCK_SNAPSHOT.md` §7 (Property Hierarchy), §14 (Avoid Tautology), §15 (Alloy Validation Plan), §16 (Mechanism Ablation Plan), §17 (Concurrency Claim Boundary), §19 (Executable Conformance Plan), §22 (Final RQs).
> **Companion files:** `FORMAL_MODEL.md` (model, trace semantics, contract, dependency table), `THREAT_MODEL.md` (attacks and invalid-state entry).
> **v0.6 changes:** `orderedTrace` now enforces `stateInvariant` on every state of every reachable trace (P0); the dependency re-check keeps all of ABL_1..ABL_10 satisfiable with that invariant enforced, including ABL_3 / `C-record` (P0 dep); P6 wording now says the formal trace predicate mirrors the detailed binding checks but the Alloy P6 corruption/minimality claim is restricted to source-anchor loss/replacement and source-version duplicates, with individual binding-corruption necessity evaluated through executable conformance tests and not claimed as a separate Alloy minimality result (P1-1); `State.candidates` is explicitly auxiliary and no P0–P6 claim depends on it (P1-2).

---

## 1. Property hierarchy (P0–P6)

All quantifications below are over `ReachableFullState` / `ReachableFullEvent`, i.e. states and events occurring in some `EnforcingTrace` as defined in FORMAL_MODEL.md §5. They are **not** over arbitrary disconnected event atoms. Each trace edge has exactly one event (`Trace.events[i]`). **v0.6 P0:** every such state satisfies `stateInvariant`, because `orderedTrace` itself contains `all s: tr.states.elems | stateInvariant[s]`; no property below is stated over a state outside that structural validity class.

### Structural reachability invariant (v0.6 P0)

For every ordered trace `tr` and every `s in tr.states.elems`:

```
stateInvariant[s]:
  all r: Record | s.currentVersion[r].record = r
  all r: Record, f: Field |
    (some s.committedValue[r][f]) iff (some s.committedSource[r][f])
  all r: Record, f: Field, t: Transition |
    t = s.committedSource[r][f] => t.targetRecord = r and t.targetField = f
```

This is **structural state validity only**. It deliberately does **not** require `committedSource[r][f] in s.transitions` (a post-tamper P6 state may keep an anchor whose transition was deleted), and it deliberately does **not** require `committedSource[r][f].value = committedValue[r][f]` (that is the P5/P6 binding property, not structural validity).

### P0 — Architectural invariant: Direct-Write Exclusion

**Role:** architecture invariant, not central novelty.

```
for every reachable MachineEvent e or TamperEvent e:
  e.post.committedValue  = e.pre.committedValue
  and e.post.committedSource = e.pre.committedSource
  and e.post.currentVersion = e.pre.currentVersion

for every reachable MachineEvent e:
  e.post.authorizations = e.pre.authorizations
```

In trace form (lock wording):

```
MachineOnlyTrace => CommittedStateUnchanged
```

Concretely: machine perception, retrieval, LLM, and rule services can create candidates/certificates/evidence but cannot create authorizations and cannot directly write committed values or whole-record versions. `ReviewForms.confirm()` is the only fact-writing path, and human authorization is modeled atomically inside that `AdmissionEvent` (P0-3).

### P1 — Central property: Certificate-Bound Non-Substitutability

**Role:** the most important falsifiable property in the paper.

Let:

```
Context(c) = (record, field, evidenceIdentity, expectedVersion)
evidenceIdentity(x) = (x.content, x.locator)
attemptContext(e) = (targetRecord, targetField,
                     evidenceIdentity(targetEvidence), expectedVersion)
```

For every effective admission event occurring in an enforcing trace:

```
attemptContext(e) != Context(e.certificate.candidate)
  =>  admissionEffect(e) = False
  and sameState(e.pre, e.post)
```

Authorization form (canonical identity, v0.2 P1-3):

```
Authorization(a, Cert(ci), v) and canonicalCertId(ci) != canonicalCertId(cj)
  =>  Authorize(a, Cert(cj), v) = False
```

Even when values are identical:

```
Value(ci) = Value(cj) and canonicalCertId(ci) != canonicalCertId(cj)
  !=>  SameAuthority(ci, cj)
```

Short form: **SameValue ⇏ SameAuthority.**

Canonical certificate identity is primitive `CertId` equality (v0.4 P1-2). The model asserts only that a difference in a modeled binding component implies a different canonical id; it asserts no converse, so unmodeled `_content()` inputs (policy/template/config identity) may distinguish two certificate ids. S5 and all authorization checks use exact `certId` equality.

The dimensions covered are exactly S1 (field), S2a/S2b (evidence identity / evidence owner), S3 (record), S4a (certificate↔attempt version), S4b (current-record freshness), S5 (certificate/authorization). P1 owns S1, S2a, S2b, S3, S4a, S5; P4 owns S4b. Evidence identity is canonical `(content, locator)` — not raw atom inequality (P1-2).

### P2 — Context-Bound Admission

**Role:** the problem framework. A successful admission requires all of:

```
CandidateContextMatch
and DurableMachineArtifacts          -- certificate and evidence pre-exist
and ValidAuthorization               -- certificate-bound, principal-bound, value-bound
and FreshVersion
and ValidTransition
```

P2 must **not** be modeled as a tautology. It is the conjunction P1 ∧ P3 ∧ P4 ∧ P5 plus the artifact-preexistence conjuncts, each independently checkable and independently ablatable. Invalid transitions remain reachable in the abstract state space so the contract and ablations are meaningful.

**Candidate persistence (v0.6 P1-2).** The scientific persistence object is the **persisted `Certificate` with embedded `Candidate`** (`Certificate.candidate : one Candidate`; concrete `CandidateCertificate` row carries all candidate fields). Therefore `C-cert-preexists` is sufficient and there is **no** separate candidate-preexistence conjunct. `State.candidates` is retained only as an **auxiliary machine-artifact/reachability set** that records materialized machine candidate payloads; **no P0–P6 claim depends on `State.candidates`** (the contract and properties always read the candidate through `Certificate.candidate`).

### P3 — Authorization Necessity and Reference Integrity (admission-time, P0-2)

**Role:** any effective committed change requires an authorization that canonically references the same certificate as the appended transition, is attributable to an authorized principal, and carries the exact committed value.

```
for every EnforcingTrace tr, every edge i, every AdmissionEvent
e = tr.events[i] with admissionEffect(e), and the unique transition
t in (e.post.transitions - e.pre.transitions):

  e.authorization in e.post.authorizations
  and t = e.post.committedSource[e.targetRecord][e.targetField]
  and t.authorization = e.authorization
  and t.certificate   = e.certificate
  and sameCanonicalCertificate(e.authorization.certificate, e.certificate)
  and e.authorization.principal in PrincipalRegistry.authorized
  and e.value = e.authorization.authorizedValue
  and t.value = e.authorization.authorizedValue
```

P3 is **admission-time**: it quantifies over the transition appended by the effective event, not over every transition in arbitrary reachable post-tamper states. After a `TamperEvent`, P6 is the property that observes corruption; P3 does not promise that every existing transition in every later state remains correctly bound (P0-2).

Core attack: a decision for certificate A reused for certificate B (S5); a value the authorization never carried (S8, P0-1).

Concretely: `HumanDecision.decision_id/reviewer_id/reason` must be non-empty and attributable; the planned `AuthorizationBindingRow` makes `decision -> certificate_id -> authorized_value` an immutable decision-time relation; `transition.decision_id = decision.decision_id`; `transition.certificate_id = binding.certificate_id`; committed `values[field_key]` equals the bound authorized value (P0-1/P0-2).

### P4 — Version Freshness / Stale Non-Interference

**Role:** supporting property implemented with OCC/CAS. No new concurrency-control claim.

```
for every effective admission e in an enforcing trace:
  e.expectedVersion = e.pre.currentVersion[e.targetRecord]
```

Equivalently:

```
ExpectedVersion(c) != CurrentVersion(record)
  => Commit = Reject
  and sameState(State_before, State_after)
```

This is S4b only. S4a (attempt version vs certificate embedded version) is P1.

Concretely: application-level precheck plus SQL `UPDATE FormRow ... WHERE current_record_version = expected_version` as the first write of one transaction; stale conflict returns `False` and rolls back.

**Sequential competing confirmation (P1-4).** In one linear trace A and B do not share a pre-state after one commits. A generated for `v0` commits `v0 -> v1` at edge `i`; B generated for `v0` is a later edge whose pre-state already has `currentVersion = v1`, so `B.expectedVersion = v0 != pre.currentVersion` and B is rejected with `sameState`. This is the only interleaving claim the formal model makes.

### P5 — Transition Integrity (strengthened per v0.4 P0-1/P0-2)

**Role:** every effective admission produces **exactly one appended transition total**, equal to the fact's `committedSource`, structurally complete, unique, attributable, with all bindings and **both value anchors** — the authorized value and the actual post-state committed value.

For every effective admission event `e`:

```
exists! t in (e.post.transitions - e.pre.transitions):
  e.post.transitions = e.pre.transitions + t
  and t = e.post.committedSource[e.targetRecord][e.targetField]   -- P0-2
  and t.targetRecord  = e.targetRecord
  and t.targetField   = e.targetField
  and t.evidence      = e.targetEvidence
  and t.fromVersion   = e.pre.currentVersion[e.targetRecord]
  and t.toVersion     = e.post.currentVersion[e.targetRecord]
  and t.toVersion     = successor[t.fromVersion]
  and t.value         = e.authorization.authorizedValue
  and t.value         = e.post.committedValue[e.targetRecord][e.targetField]  -- v0.4 P0-1
  and t.producer      = e.certificate.candidate.producer
  and t.certificate   = e.certificate
  and t.authorization = e.authorization
```

The two value obligations make the transition describe the actual committed update (v0.4 P0-1). The value obligation is **not** `t.value = e.certificate.candidate.value`, because Correction is allowed. P5 is an admission-time property of the unique appended transition (P0-2).

Forbidden outcomes: missing transition; duplicate transitions for one committed update; appended transition different from `committedSource[r,f]`; blank target; mismatched target version; transition detached from its authorization/certificate; transition detached from record/field/evidence/value/producer/from/to versions; transition value different from the authorized value; transition value different from the value actually written into `post.committedValue`.

**ABL_8 intended failure (v0.4 P0-1).** When only `C-auth-value` is removed, the witness `e.authorization.authorizedValue = X`, `e.value = Y`, `X != Y` commits `Y` while the retained `C-transition` records `t.value = X` and `t = committedSource`. All other conjuncts hold, and P5 fails on `t.value != e.post.committedValue[r,f]`.

**P1-7 update rule.** The committed-value write is pair-specific and preserves every non-target field; the committed-source write is likewise pair-specific and preserves every non-target field's older source (P0-2):

```
setFieldValue[s, r, f, v] =
  s.committedValue - (r -> f -> Value) + (r -> f -> v)

setCommittedSource[s, r, f, t] =
  s.committedSource - (r -> f -> Transition) + (r -> f -> t)
```
### P6 — Trace Soundness (source-anchor; v0.6 carries v0.5 P0-1/P0-2/P1)

**Role:** supporting property, and the **only post-tamper verification property**. It starts from a committed `(record, field)` fact and formally claims **source-anchor loss/replacement detection** and **source-version duplicate detection** — nothing stronger.

```
CommittedFact(s, r, f) -> committedSource[s][r][f] -> Transition
    -> Authorization -> Certificate -> Evidence
```

```
traceComplete[s, r, f] =
  some s.committedValue[r][f]
  and let src = s.committedSource[r][f] |
    some t = src |
      t in s.transitions
      and t.targetRecord = r
      and t.targetField  = f
      and t.value = s.committedValue[r][f]

      -- v0.5 P0-1 source-version uniqueness:
      -- exactly one transition at (r, f, src.toVersion)
      and (one u: s.transitions |
           u.targetRecord = r
           and u.targetField = f
           and u.toVersion = src.toVersion)

    -- concrete verifier contract: the formal predicate mirrors these binding
    -- checks, but Alloy P6 claims only source-anchor loss/replacement and
    -- source-version duplicates (not individual binding-check minimality):
    and every transition -> authorization -> certificate -> evidence
        hop exists and is binding-consistent:
        (authorization/certificate/evidence membership,
         exact certificate certId equality,
         sameEvidenceIdentity(certificate.candidate.evidence, t.evidence),
         evidence owner = r,
         record/field/producer/version bindings,
         t.value = authorization.authorizedValue)
```

**Formal vs executable split (v0.6 P1-1).** Alloy atoms are immutable, so a rebound transition is modeled as removal of the source atom plus insertion of another atom. Since `committedSource` is preserved, the **Alloy P6 claim** is exactly: (1) `committedSource[r,f] = t` but `t not in s.transitions` ⇒ Incomplete; (2) more than one transition shares `(r, f, t.toVersion)` ⇒ Incomplete. **The formal trace predicate mirrors the producer/evidence/value/version/certificate/authorization binding checks, but the Alloy P6 corruption/minimality claim is restricted to source-anchor loss/replacement and source-version duplicates. Individual binding-corruption necessity is evaluated through executable conformance tests and is not claimed as a separate Alloy minimality result.** Those detailed checks are listed in THREAT_MODEL.md §12.

**P0-2 deletion and unchanged-field semantics.** If `committedSource[r,f] = t` and a `TamperEvent` deletes `t` from `s.transitions`, then `traceComplete[s,r,f]` is false. If `(r,f)` was not updated by a later admission while `(r,f2)` was, `committedSource[r,f]` still points at the older transition and `traceComplete[s,r,f]` still succeeds even though `currentVersion[r]` advanced. The planned concrete anchor is immutable `RecordVersionRow.fact_sources`; the withdrawn `MAX(created_version) among remaining transitions` would have silently promoted an older transition after deletion and is no longer used.

**P1-1 formal reachability.** Only `State.transitions` is tamperable in v0.6. Missing authorization/certificate/evidence artifacts are not formal P6 classes; `tamperStep` preserves those sets. Concrete certificate/decision/evidence-row deletion tests are implementation-level robustness evidence outside the Alloy P6 submodel.

**Explicit non-claims.** A row-identity change that preserves every validated binding is not claimed detectable. Individual post-hoc binding checks are **not claimed as separate Alloy minimality results**; their necessity is evaluated through executable conformance tests. A coherent rewrite of all dependent artifacts can pass `traceComplete` in the abstract model unless an immutable external anchor is introduced; such a rewrite is outside the locked threat model (arbitrary privileged DBA). The paper will state this boundary wherever P6 is discussed.

---

## 2. Central Non-Transferability Assertion (CNTA)

This is the renamed “Central theorem” (v0.2 P1-5). The word **theorem** is not used for a bounded Alloy claim.

```
Central Non-Transferability Assertion (CNTA, bounded).

For every EnforcingTrace tau, every edge i, and every AdmissionEvent
e = tau.events[i] occurring at that edge with admissionEffect(e):

  e.certificate in e.pre.certificates
  and e.targetEvidence in e.pre.evidence

  and attemptContext(e) = certificateContext(e.certificate)

  and sameCanonicalCertificate(e.authorization.certificate, e.certificate)

  and e.authorization.principal in PrincipalRegistry.authorized

  and e.expectedVersion = e.pre.currentVersion[e.targetRecord]

  and e.value = e.authorization.authorizedValue

  and transitionIntegrity(e)
```

Consequently:

```
Authorize(a, Cert(ci), v) and canonicalCertId(ci) != canonicalCertId(cj)
  => no effective admission event e in any EnforcingTrace with
       e.authorization = a and e.certificate = Cert(cj).
```

This holds even when:

```
Value(Cert(ci)) = Value(Cert(cj)).
```

An Accept (`authorizedValue = candidate.value`) and a Correction (`authorizedValue != candidate.value`) are both admitted instances of `e.value = e.authorization.authorizedValue`; neither weakens CNTA, because CNTA is about context/authorization transfer, not about forcing the machine proposal through unchanged. `transitionIntegrity(e)` here is the strengthened v0.4 form: the unique appended transition equals `committedSource`, and its value equals both the authorized value and the post-state committed value.

The paper reports: *“No counterexample was found within the explored scope”* (lock §15), never a universal proof unless a separate genuine proof exists.
---

## 3. Formal assertion catalog (all reachable-trace, one event per edge)

| Assertion | Formula (abbreviated) | Expected result in full model |
|---|---|---|
| `P0_stateInvariant_reachable` | for every `orderedTrace[tr]` and every `s in tr.states.elems`, `stateInvariant[s]` | no counterexample (definitional regression: the clause lives inside `orderedTrace`, v0.6 P0) |
| `SAT_invariant_admission_tamper` | some ordered trace exists with an effective admission followed by a source-transition-deleting `TamperEvent` | satisfiable (the post-tamper state still satisfies the structural invariant because the invariant has no `committedSource in transitions` clause) |
| `P0_no_machine_write` | every reachable machine/tamper event leaves `committedValue`, `committedSource`, and `currentVersion` unchanged; every machine event leaves `authorizations` unchanged | no counterexample |
| `P1_no_cross_context` | no effective AdmissionEvent in any EnforcingTrace has `attemptContext != certificateContext` (evidence identity = content+locator) | no counterexample |
| `P1_auth_nontransfer` | no effective AdmissionEvent in any EnforcingTrace has `canonicalCertId[e.authorization.certificate] != canonicalCertId[e.certificate]` | no counterexample |
| `P3_auth_reference` | for every effective AdmissionEvent, the unique appended transition has an authorized, canonically certificate-bound, value-carrying authorization (admission-time) | no counterexample |
| `P4_stale_reject` | no effective admission in any EnforcingTrace is stale vs `pre.currentVersion`; the later of two v0-generated confirmations rejects | no counterexample |
| `P5_unique_transition` | exactly one complete transition per effective admission, equal to `committedSource[r,f]`, with `t.value = e.authorization.authorizedValue` **and** `t.value = e.post.committedValue[r,f]` | no counterexample |
| `P6_trace_soundness` | for every reachable full state and committed `(r,f)`, source-anchor loss/replacement or a duplicate `(r,f,src.toVersion)` transition is never `traceComplete[s,r,f]`; detailed binding mismatches are executable checks | no counterexample |
| `SAT_1_accept` | a legal Accept exists in an ordered enforcing trace | satisfiable |
| `SAT_1_correction` | a legal Correction exists in an ordered enforcing trace (`authorizedValue != candidate.value`) | satisfiable |
| `SAT_2_invalid_states` | each of S1, S2a, S2b, S3, S4a, S4b, S5, S8 (committed Y / transition X mismatch), S9, S10, unauthorized principal, transition-only tamper/deletion/rebinding, source-version duplicate insertion, sequentialized interleaving is reachable with contract off | satisfiable |
| `ABL_1`, `ABL_2a`, `ABL_2b`, `ABL_3`, `ABL_4a`, `ABL_4b`, `ABL_5`, `ABL_6`, `ABL_7`, `ABL_8`, `ABL_9`, `ABL_10` | weakened model admits the named attack | **counterexample found (required)** |

---

## 4. Non-tautology protocol (lock §14)

Forbidden pattern: define `Admit <=> ContextMatch`, then assert `Admit => ContextMatch`.

Required protocol, to be executed by the future `.als` model:

1. **Define before constrain.** `admissionEffect[e]` is defined as a state delta over independently supplied event fields (`targetRecord`, `targetField`, `targetEvidence`, `expectedVersion`, `value`). `Contract[e]` is added only at the enforcing boundary.
2. **Keep invalid successes reachable.** `baseAdmissionStep[e] = rejectedAdmission[e] or admissionEffect[e]` allows mismatched effective admissions in the abstract ordered universe, including unrecorded values and conjured artifacts.
3. **Check satisfiability of both worlds.**
   - `SAT_1_accept`: legal Accept with full contract — must be satisfiable, otherwise P1 is vacuously true.
   - `SAT_1_correction`: legal Correction with full contract — must be satisfiable, otherwise the model incorrectly forces `t.value = candidate.value` (P0-1).
   - `SAT_2`: each of S1, S2a, S2b, S3, S4a, S4b, S5, S8, S9, S10 and each tamper/sequential-interleaving state with contract off — must be satisfiable in an ordered trace, otherwise the attack was excluded by construction.
4. **Prove in the full model.** Run the full-model checks over `EnforcingTrace` / `ReachableFullState`.
5. **Break in the ablations.** Run `ABL_1`, `ABL_2a`, `ABL_2b`, `ABL_3`, `ABL_4a`, `ABL_4b`, `ABL_5`, `ABL_6`, `ABL_7`, `ABL_8`, `ABL_9`, `ABL_10` and require each to produce its named counterexample. A missing counterexample means the ablated conjunct was redundant or the state space was too small. **v0.6 P0 dep:** every ablation run uses `orderedTrace`, hence every witness state must satisfy the enforced `stateInvariant`; FORMAL_MODEL.md §7.3 records the ablation-by-ablation structural check, and ABL_3 remains independent because the invariant ties `currentVersion[targetRecord]` to `targetRecord` but never to `candidate.targetRecord`.
6. **Use the dependency table.** FORMAL_MODEL.md §7.3 shows for every ablated conjunct that the remaining conjuncts do not imply it, and gives the satisfiable witness structure.
7. **Report scope honestly.** Every negative check result is reported as no-counterexample-within-scope.

Gate rule: **any ablation check that passes is a gate failure.**

The same protocol covers P5 and P6: `traceComplete[s,r,f]` is defined from a committed fact over independently mutable transition references, not over an already-validated chain. `ABL_6` must find missing/duplicate/source-detached transitions; `ABL_7` must find a deleted or rebound source transition, or a source-version duplicate, that the weakened verifier would label `Complete`; `ABL_8` must find the committed-Y / transition-X mismatch that breaks the strengthened P5 (v0.4 P0-1).

---

## 5. Full model versus ablation models (v0.2 P1-4 split retained; v0.3 P1-3 split applied)

| Model | Definition | Expected check outcome |
|---|---|---|
| `M_full` | base effects + all `Contract` conjuncts + reachable-trace semantics + trace validation | P0–P6 all hold in scope; SAT-1 Accept and Correction satisfiable |
| `ABL_1` | `M_full` without `C-field` | `P1_no_cross_context` fails with S1 |
| `ABL_2a` | `M_full` without `C-evidence-id` only | `P1_no_cross_context` fails with S2a |
| `ABL_2b` | `M_full` without `C-evidence-record` only | `P1_no_cross_context` fails with S2b |
| `ABL_3` | `M_full` without `C-record` | `P1_no_cross_context` fails with S3 |
| `ABL_4a` | `M_full` without `C-version` only | `P1_no_cross_context` fails with S4a (certificate↔attempt version substitution) |
| `ABL_4b` | `M_full` without `C-fresh` only | `P4_stale_reject` fails with S4b (stale replay vs current record version) |
| `ABL_5` | `M_full` without `C-auth-cert` | `P1_auth_nontransfer` and `P3_auth_reference` fail with S5 |
| `ABL_6` | `M_full` without `C-transition` | `P5_unique_transition` fails (missing source transition, duplicate, or `t != committedSource`) |
| `ABL_7` | `M_full` without trace-validation conjuncts (source-anchor membership, source-version uniqueness, and binding checks) | `P6_trace_soundness` fails: deleted/replaced source anchor or duplicate `(r,f,src.toVersion)` is reported Complete |
| `ABL_8` | `M_full` without `C-auth-value` | `P3_auth_reference`/`P5_unique_transition` fail with S8; P5 fails because committed value Y differs from source-transition value X (`X != Y`) — the intended v0.4 P0-1 reason |
| `ABL_9` | `M_full` without `C-cert-preexists` | admission succeeds with a conjured certificate (S9) |
| `ABL_10` | `M_full` without `C-evidence-preexists` | admission succeeds with a conjured evidence row (S10) |

`ABL_5` directly supports the non-transferable-authorization claim and uses exact primitive `certId` equality (v0.4 P1-2). `ABL_4a` and `ABL_4b` are separate commands because v0.2 P1-4 requires the two version phenomena to be tested separately. `ABL_2a` and `ABL_2b` are separate commands because v0.3 P1-3 requires the two evidence phenomena to be tested separately.
---

## 6. Concurrency claim boundary (lock §17)

Alloy may model:

- stale authorization;
- certificate↔attempt version mismatch (S4a);
- stale attempt against the current whole-record version (S4b);
- **sequentialized** competing confirmations: A and B both generated for `v0`; A commits `v0 -> v1`; B is processed afterward with `pre.currentVersion = v1` and rejects stale.

The paper may say:

> bounded analysis of stale and sequentially interleaved admission states

It may **not** say:

> formal verification of concurrent database correctness.

The formal model never claims two events share one pre-state inside the same ordered trace (P1-4). Concrete atomicity evidence comes from DB transactions, CAS, concurrency tests, and no-partial-write assertions — not from Alloy.

---

## 7. Executable conformance plan (lock §19)

Use **Hypothesis RuleBasedStateMachine** (or a semantically equivalent stateful property framework) with at minimum these actions:

```
create_evidence
generate_candidate
authorize_candidate            -- Accept: authorizedValue = candidate.value
correct_candidate              -- Correction: authorizedValue != candidate.value
substitute_field
substitute_evidence            -- S2a identity or S2b owner
substitute_record
substitute_certificate_version      -- S4a: attempt version != certificate version
replay_stale_candidate              -- S4b: stale vs current record version
substitute_authorization_certificate
substitute_authorized_value         -- S8: commit a value the authorization never carried
conjure_certificate_at_admission    -- S9 (should be rejected)
conjure_evidence_at_admission       -- S10 (should be rejected)
concurrent_confirm                  -- sequentialized: A commits, B stale-rejects
tamper_transition                -- transition-only formal tamper (P1-1)
delete_transition
rebind_version
insert_duplicate_transition      -- same (form_id, created_version, field_key)
verify_trace                     -- starts from a committed (record,field) fact
-- concrete-only, labeled outside the Alloy P6 submodel (P1-1):
tamper_certificate_row
tamper_decision_row
tamper_evidence_row
```

Test-oracle rule: the oracle must not simply reuse the production validator. It must re-check the abstract bindings independently (e.g., recompute certificate content address from raw DB rows, re-join decision/certificate/transition by id, and re-derive trace hops from persisted rows starting at the committed `(form_id, field_key)` fact). After the planned `AuthorizationBindingRow` and `RecordVersionRow.fact_sources` are implemented, the oracle must also join `decision -> authorization_bindings -> certificate_id`, check `authorized_value_payload/hash` against the committed `RecordVersion.values`, resolve `fact_sources[field_key]` to the source transition id, and reject a missing/unresolved source id, a duplicate source-version row, or a transition whose value or certificate does not match that binding. Certificate/decision/evidence-row corruption actions remain concrete-only conformance evidence and are not part of the Alloy P6 submodel. Until `fact_sources` exists, P6 executable conformance is explicitly conditional (v0.5 P0-2).

### 7.1 Concrete fault mapping

| Hypothesis action | Concrete fault / test family | Abstract property |
|---|---|---|
| `substitute_field` | cross-field certificate tests | P1 |
| `substitute_evidence` | cross-form/tampered evidence tests | P1 (S2a/S2b) |
| `substitute_record` | cross-form certificate/evidence tests | P1 |
| `substitute_certificate_version` | `certificate.expected_fact_version != expected_version` tests | P1 (A4a) |
| `replay_stale_candidate` | stale confirm / CAS conflict tests | P4 (A4b) |
| `substitute_authorization_certificate` | decision-candidate mismatch + planned binding tests | P1/P3 |
| `substitute_authorized_value` | transition/committed value vs planned binding payload tests | P3/P5 (A8) |
| `conjure_certificate_at_admission` | derived-certificate-at-confirm path reworked to a pre-existing machine certificate + binding value | P3/P5 (A9) |
| `conjure_evidence_at_admission` | evidence row must exist before the fact write | P3/P5 (A10) |
| `concurrent_confirm` | CAS first-write + retry tests (sequentialized) | P4 |
| `tamper_transition` | `_tamper("fact_transitions", ...)` tests | P6 (formal) |
| `delete_transition` | `DELETE FROM fact_transitions` test (planned `fact_sources` left unresolved) | P6 (formal) |
| `insert_duplicate_transition` | duplicate `(form_id, created_version, field_key)` fault | P6 (formal, source-version uniqueness) |
| `rebind_version` | FK-valid next-version row rebinding test | P6 (formal anchor loss; executable version check) |
| `tamper_certificate_row` / `tamper_decision_row` / `tamper_evidence_row` | SQL mutation tests, if present | concrete-only robustness evidence outside Alloy P6 (v0.4 P1-1) |
| `verify_trace` | `build_provenance_trace` / pipeline trace statuses, fact-query reconstruction from `(form_id, field_key)` | P6 |

Existing assets: fault corpus, randomized trials, 239 automated tests, Ruff/mypy, deterministic reproducibility, byte-identical outputs, manifest (lock §20).

---
## 8. Research question mapping (lock §22)

| RQ | Formal check / evidence |
|---|---|
| RQ1 Admission Safety | `P1_no_cross_context` + `P0_no_machine_write` + `P1_auth_nontransfer` + `P3_auth_reference` full-model checks over reachable traces |
| RQ2 Mechanism Role | `ABL_1`, `ABL_2a`, `ABL_2b`, `ABL_3`, `ABL_4a`, `ABL_4b`, `ABL_5`, `ABL_6`, `ABL_7`, `ABL_8`, `ABL_9`, `ABL_10` required counterexamples |
| RQ3 Executable Conformance | Hypothesis stateful actions + fault injection + existing 239-test corpus |
| RQ4 Instantiation | industrial form workflow as Executable Instantiation / Industrial Document Case Study |

---

## 9. Wording guardrails for the eventual paper

Allowed:

- "No counterexample was found within the explored scope."
- "The full contract excludes the substitution families within the bounded model."
- "Each single-mechanism ablation produces the expected counterexample."
- "The concrete implementation preserves the abstract properties under valid, corrected, substituted, stale, sequentially interleaved, and corrupted workflows."
- "Trace verification starts from a committed (record, field) fact and detects source-anchor loss/replacement and source-version duplicate transitions."
- "Detailed producer/evidence/value/version/certificate/authorization binding-corruption checks are executable conformance evidence."
- "The transition value equals both the human-authorized value and the actual post-state committed value; the committed value may accept or correct the machine proposal."
- "Formal P6 tamper classes are transition-only: source deletion, source replacement, and source-version duplicate insertion; certificate/decision/evidence-row faults are implementation-level robustness evidence outside the Alloy P6 submodel."

Not allowed:

- "We formally verify concurrent database correctness."
- "We prove universal security."
- "The Python implementation is formally verified."
- "This is the first candidate–fact separation."
- "This is a new CAS / concurrency-control algorithm."
- "Human authorization guarantees correct facts."
- "Alloy proves each individual post-hoc trace-binding check is minimal" (the formal trace predicate mirrors those checks, but the Alloy P6 claim is restricted to source-anchor loss/replacement and source-version duplicates; individual binding-corruption necessity is evaluated through executable conformance tests, v0.6 P1).

---

## 10. Gate exit criteria (Round 6)

The six files (`FORMAL_MODEL.md`, `THREAT_MODEL.md`, `PROPERTIES.md`, `RED_TEAM_NOTES.md`, `SEMANTIC_REWORK_CHANGELOG.md`, `HANDOFF.md`) pass to the next stage only if the gate confirms all of:

1. Primary direction and RQ are exactly the locked ones (lock §1–§2, §32).
2. `orderedTrace` itself enforces `all s: tr.states.elems | stateInvariant[s]`; every reachable ordered-trace state therefore satisfies the four structural clauses (`currentVersion[r].record = r`; committed-value/committed-source domain equivalence; source target record/field). The invariant has no `committedSource in transitions` clause and no source-value/committed-value equality clause.
3. The v0.6 dependency re-check keeps all named ablations structurally satisfiable with the invariant enforced: ABL_1, ABL_2a, ABL_2b, ABL_3, ABL_4a, ABL_4b, ABL_5, ABL_6, ABL_7, ABL_8, ABL_9, ABL_10. ABL_3 / `C-record` remains independent.
4. Prior v0.5 fixes remain intact: `traceComplete` source-version uniqueness (duplicate insertion Incomplete); planned immutable `RecordVersionRow.fact_sources` anchor with `MAX(created_version) among remaining transitions` withdrawn and no older-transition promotion.
5. The formal trace predicate mirrors the producer/evidence/value/version/certificate/authorization binding checks, but the Alloy P6 corruption/minimality claim is restricted to source-anchor loss/replacement and source-version duplicates; individual binding-corruption necessity is evaluated through executable conformance tests and is not claimed as a separate Alloy minimality result. Those checks are not labeled as exclusive to the executable layer.
6. Candidate is embedded in the persisted Certificate; `State.candidates` is only an auxiliary machine-artifact/reachability set that no P0–P6 claim depends on; no separate candidate-preexistence conjunct exists; `AdmissionEvent.targetField` remains independently supplied; principal failure is called unauthorized/unregistered principal and real impersonation remains out of scope.
7. Prior mechanisms remain intact: P5 dual value anchors + ABL_8 intended failure; P3/P5 admission-time; MachineEvent cannot create Authorization; pre-existing certificate/evidence; transition-only TamperEvent; primitive CertId one-way identity; one event per edge; `sameState` rejection; pair-specific updates.
8. Current repository gaps are stated honestly: `AuthorizationBindingRow` and `RecordVersionRow.fact_sources` are planned post-PASS conformance prerequisites; no document claims current code already satisfies them.
9. No `.als` file or Alloy run has been created yet.
10. Wording rules of lock §15, §17, §23, §25 are respected.

Only after a recorded PASS may the full Alloy implementation begin.

## 11. Relationship to supporting properties (lock §24)

These are supporting, never separate novelty claims:

- direct-write exclusion;
- version freshness (P4, S4b only);
- CAS;
- correction-preserving lineage;
- reverse-trace soundness;
- append-only history;
- human attribution;
- reproducibility;
- content addressing.

Version **binding** (S4a, certificate's embedded expectedVersion) is part of P1; version **freshness** (S4b, current record version) is P4. Evidence **identity binding** (S2a) and evidence **owner binding** (S2b) are both part of P1 and are now separate ablations.

---

## 12. Locked status

- Research status: **RESEARCH LOCKED**.
- Default venue: **JSS first**; SCP / SoSyM conditional pivots per lock §27.
- Central property: **Certificate-Bound Non-Substitutability**; central assertion: **Central Non-Transferability Assertion (CNTA)**.
- Do not begin full Alloy implementation until the Semantic Gate approves this Rework.
