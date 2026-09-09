# FORMAL_MODEL.md — Auto-Decte Historical Singleton Formal Draft v0.6

> **2026-08-23 implementation addendum:** Option A is approved and the conservative batch extension now lives in `formal/alloy/batch/`. Its active development freeze runs a complete 66-command S1/S2 catalog. This document remains the historical singleton design record; where it says no `.als` implementation exists, that statement describes the original gate stage, not the current repository state. See `formal/alloy/batch/README.md` and `formal/alloy/batch/RESULTS.md` for the current model and bounded results.

> **Status:** DeepSeek Formal Draft v0.6 — revised after the GPT-5.6 Sol Semantic Gate v0.5 verdict **REWORK** (`DEEPSEEK_SEMANTIC_REWORK_PROMPT_v05.md`). Not yet an Alloy implementation.
> **Canonical constraint:** the repository-local, verbatim research-lock snapshot in `formal/RESEARCH_LOCK_SNAPSHOT.md` (RESEARCH LOCKED, 2026-08-22).
> **Rule:** this document must not widen the research problem, must not create a new primary direction, and must not start full Alloy implementation before the Semantic Gate PASS.
> **Direction (unchanged):** Certificate-Bound Non-Substitutable Admission of AI-Derived Candidate Updates into Versioned Authoritative Records; narrative framing = Context-Bound Admission.
> **Version note:** v0.6 applies every item of the GPT Semantic Gate v0.5 verdict (P0 enforce `stateInvariant` on every reachable trace state, mandatory dependency re-check for ABL_1..ABL_10, P1 formal-vs-executable wording cleanup, P1 Candidate-auxiliary-state cleanup) on top of v0.5. The change-by-change ledger is `SEMANTIC_REWORK_CHANGELOG.md`; Red-Team Pass 6 is in `RED_TEAM_NOTES.md`.

---

## 1. Rework compliance map (GPT gate v0.5 items)

| Gate item | Required change | Where resolved |
|---|---|---|
| P0 | `orderedTrace` must enforce `stateInvariant[s]` for every `s: tr.states.elems`; the invariant guarantees at minimum `currentVersion[r].record = r`, `(some committedValue[r,f]) iff (some committedSource[r,f])`, and `committedSource[r,f].targetRecord = r` / `.targetField = f`. It must **not** include `committedSource in s.transitions` or `committedSource.value = committedValue` | §4.8, §5.1, §5.2; PROPERTIES.md §1; CHANGELOG.md §2.1 |
| P0 dep | Re-evaluate the dependency table with the invariant actually enforced on every reachable state; each of ABL_1, ABL_2a, ABL_2b, ABL_3, ABL_4a, ABL_4b, ABL_5, ABL_6, ABL_7, ABL_8, ABL_9, ABL_10 must remain structurally satisfiable; ABL_3 / `C-record` must remain independent | §7.3; THREAT_MODEL.md §11; PROPERTIES.md §4 |
| P1-1 | Use the gate-required wording instead of labeling the producer/evidence/value/version/certificate/authorization checks as exclusive to the executable layer. Required wording: the formal trace predicate mirrors those binding checks, but the Alloy P6 corruption/minimality claim is restricted to source-anchor loss/replacement and source-version duplicates; individual binding-corruption necessity is evaluated through executable conformance tests and is not claimed as a separate Alloy minimality result | §12.3, §13, §15, §16; THREAT_MODEL.md §12; PROPERTIES.md §1 P6 |
| P1-2 | The scientific persistence object is the `Certificate` with embedded `Candidate`. `State.candidates` is **kept as an auxiliary machine-artifact/reachability set that no P0–P6 claim depends on**; no `C-candidate-preexists` is introduced; the durable admission prerequisite remains `e.certificate in e.pre.certificates` | §4.4, §4.8, §7; THREAT_MODEL.md §3; PROPERTIES.md §1 P2 |

---
## 2. What this file is and is not

**Is**

- A formalization-level specification of the locked research problem.
- An Alloy-oriented model skeleton (signatures, relations, predicates, assertion names) that a later step may turn into a compiling `.als` model.
- The source of truth for what “admission”, “candidate certificate”, “authorization”, “version”, and “non-substitutability” mean in the paper.

**Is not**

- A runnable Alloy model. No `.als` file is created at this stage.
- A mathematical security proof. All bounded results will be reported as *“no counterexample was found within the explored scope”* (lock §15).
- A new formalization of databases, concurrency control, provenance, RBAC, or event sourcing.

---

## 3. Locked research problem (restated, not changed)

### 3.1 Main RQ

> How can an AI-assisted information system admit machine-derived candidate updates into versioned authoritative records while ensuring that candidate validity and authorization are non-transferable across record, field, evidence, version, and certificate contexts?

### 3.2 Central thesis

> **Authority attaches to a context-bound candidate identity, not merely to its value.**

```
Value(c1) = Value(c2) ∧ Context(c1) ≠ Context(c2)
  ⇒  Authorize(c1) ⇏ Authorize(c2)
```

In one line: **SameValue ⇏ SameAuthority.**

### 3.3 The boundary studied

```
CandidateUpdate --Admission--> CommittedFact
```

The model studies **one bounded transition**, not AI→Action, not Observation→AgentBelief, not User→Permission.

### 3.4 Operational, not epistemic authority

```
Authoritative ⇒ OperationallyAccepted
Authoritative ⇏ ObjectivelyCorrect
```

`Committed Fact` is the preferred formal term; `authoritative fact` is only a narrative alias under the operational reading above.

---

## 4. Formal vocabulary and domains

### 4.1 Universe

```
E           Evidence
EC          EvidenceContent   (hash-equivalence class; concrete SHA-256 bytes)
EL          EvidenceLocator   (concrete evidence_locator string)
R           Record
K           Field / Key
P           Producer
PR          Principal (authorized reviewer)
VALUE       Value
C           Candidate Update
Cert        Candidate Certificate
CertId      Canonical certificate identity
A           Authorization
V           Record Version
T           Fact Transition
S           State
Ev          Event
```

`PRINCIPAL` is a small carrier for the “authorized principal” requirement of lock §4. It is not a new research object.

### 4.2 Core context

```
Context(c) = (record, field, evidence, expectedVersion)
```

The concrete certificate additionally carries `(value, producer, policy/template, evidence hash and locator)`. The formal model promotes only the four context components to core binding conjuncts; value, producer, and template participate in certificate canonical identity but not in context equality. Evidence, inside `Context(c)`, is the **canonical evidence identity** defined in §4.3, which matches the concrete certificate content address (P1-2).

### 4.3 Primitive domains

```
sig Value {}
sig Record {}
sig Field {}
sig Producer {}
sig Principal {}
one sig PrincipalRegistry { authorized : set Principal }

sig EvidenceContent {}          -- canonical evidence bytes (SHA-256 abstraction)
sig EvidenceLocator {}          -- concrete evidence_locator string

sig Evidence {
  record  : one Record,          -- which record owns this evidence row
  content : one EvidenceContent, -- which bytes this row contains
  locator : one EvidenceLocator  -- the locator string frozen in the certificate
}

-- Canonical evidence identity used by certificate content identity (P1-2).
-- Two Evidence atoms are the SAME evidence context iff they have the same
-- (content, locator) pair, matching CandidateCertificate._content(), which
-- binds evidence_hash + evidence_locator and NOT evidence_file_id.
pred sameEvidenceIdentity[e1, e2: Evidence] {
  e1.content = e2.content and e1.locator = e2.locator
}

sig CertId {}                    -- primitive canonical certificate-identity namespace (v0.4 P1-2)

sig Version {
  record : one Record,
  number : one Int               -- final .als may replace Int with ordered Version atoms
}
```

**P1-2 decision recorded.** `CandidateCertificate._content()` contains `"evidence_hash"` and `"evidence_locator"`; it does **not** contain `evidence_file_id` (the `CandidateCertificateRow.evidence_file_id` column is a persistence FK, but it is not part of the content address). Concrete certificate identity therefore identifies evidence by `(hash, locator)`, not by row id. The formal model adopts exactly that identity: `sameEvidenceIdentity` compares `(content, locator)`, and certificate canonical identity in §4.5 includes both. Consequently two duplicate `Evidence` atoms with equal content **and** equal locator are distinct persisted rows but are **not** distinct certificate contexts; two atoms with equal content but different locators **are** distinct certificate contexts. This removes the v0.2 asymmetry in which formal context identity (raw evidence atom) was stronger than certificate content identity.

**P0-1 design decision.** `Evidence` has an independent `record` relation, but **there is no global fact** tying a candidate's evidence record to the candidate's target record. That missing axiom is exactly what makes `C-evidence` and `C-record` independent conjuncts: the full contract derives `candidate.evidence.record = candidate.targetRecord` only when all three relevant conjuncts are simultaneously present (see §7.3).

Version rules:

```
fact versionUniqueness {
  all r: Record, n: Int | lone v: Version | v.record = r and v.number = n
}

fact everyRecordHasInitialVersion {
  all r: Record | one v: Version | v.record = r and v.number = 0
}

fun initialVersion[r: Record] : one Version {
  { v: Version | v.record = r and v.number = 0 }
}

fun successor[v: Version] : set Version {
  { v': Version | v'.record = v.record and v'.number = v.number.plus[1] }
}
```

### 4.4 Candidate update

```
sig Candidate {
  targetRecord    : one Record,
  targetField     : one Field,
  evidence        : one Evidence,      -- candidate evidence context (identity = content+locator)
  expectedVersion : one Version,
  value           : one Value,
  producer        : one Producer
}
```

A candidate is **machine-derived only** (recognition, retrieval, LLM suggestion, or a machine rule service). Declaring a candidate does not change any committed state. The human correction path is **not** a second producer of core `Candidate` atoms: a human correction is represented solely by `Authorization.authorizedValue` (§4.6), which may differ from the machine `Candidate.value` while the machine certificate continues to reference the original machine candidate. Any concrete manual-entry product path (for example a `MANUAL_ENTRY` certificate) is kept outside the core formal `Candidate` definition and appears only as a concrete conformance note (§14.2).

**P2-2 candidate persistence (v0.5 carried).** `Candidate` is **embedded inside the persisted `Certificate`**: `Certificate.candidate : one Candidate` and the concrete `CandidateCertificate`/`CandidateCertificateRow` store all candidate fields (`candidate_id`, field, value payload, evidence, template, producer, selection metadata, expected version) in the same immutable content-addressed row. The scientific persistence object is therefore the **Certificate with its embedded Candidate**, not an independently persisted Candidate object.

**P1-2 auxiliary Candidate state (v0.6).** `State.candidates` is retained only as an **auxiliary machine-artifact/reachability set**: it records which machine candidate payloads have been materialized in a state, mirroring the fact that machine steps may create candidate payloads before any certificate exists. **No P0–P6 claim depends on `State.candidates`** — the contract and all properties read the candidate through `Certificate.candidate` — so its presence neither adds nor removes any property obligation. The durable admission prerequisite remains exactly `e.certificate in e.pre.certificates` (`C-cert-preexists`); no `C-candidate-preexists` conjunct is introduced, because the embedded candidate exists iff its Certificate exists.

**Deliberate freedom.** `Candidate` carries `targetRecord`, `evidence`, and `expectedVersion` as **independent relations**. No signature fact or global fact says `candidate.evidence.record = candidate.targetRecord` or `candidate.expectedVersion.record = candidate.targetRecord`. A malformed candidate (evidence owned by another record, expectedVersion of another record) is therefore representable in the base universe. It is excluded from **effective** admission only by the conjunction of `C-record`, `C-evidence-id`, `C-evidence-record`, `C-version`, `C-fresh`, and the state invariant. This is the v0.2 P0-1 independence fix, retained in v0.6.

**P0-1 value separation.** `Candidate.value` is the **original machine proposal**. It is frozen in the certificate and never overwritten. The human-authorized final value lives in `Authorization.authorizedValue` (§4.6). An **Accept** sets `authorizedValue = candidate.value`; a **Correction** sets `authorizedValue != candidate.value` while the certificate keeps the machine value. Nothing in the contract ever requires `AdmissionEvent.value = candidate.value`.

### 4.5 Candidate certificate and canonical identity (v0.6 carries P1-2)

```
sig Certificate {
  candidate : one Candidate,
  certId    : one CertId
}
```

Canonical identity is **primitive**, not a formal re-derivation of the modeled content tuple:

```
fun canonicalCertId[c: Certificate] : one CertId { c.certId }

pred sameCanonicalCertificate[c1, c2: Certificate] {
  c1.certId = c2.certId
}
```

The modeled content tuple is retained for the one implication the paper actually needs:

```
pred certModeledContentEqual[c1, c2: Certificate] {
  c1.candidate.targetRecord      = c2.candidate.targetRecord
  c1.candidate.targetField       = c2.candidate.targetField
  c1.candidate.value             = c2.candidate.value
  c1.candidate.evidence.content  = c2.candidate.evidence.content
  c1.candidate.evidence.locator  = c2.candidate.evidence.locator
  c1.candidate.expectedVersion   = c2.candidate.expectedVersion
  c1.candidate.producer          = c2.candidate.producer
}

fact certIdFaithfulToModeledBindings {
  -- ONLY the direction required for S5 and P1: a difference in any modeled
  -- binding component implies a different canonical certificate identity.
  all c1, c2: Certificate |
    not certModeledContentEqual[c1, c2] => c1.certId != c2.certId
}

fact certIdRowUnique {
  -- canonical certificate id is a row key: no two certificate atoms share it
  all c1, c2: Certificate | c1.certId = c2.certId => c1 = c2
}
```

**P1-2 boundary (v0.4).** The formal tuple models only `(record, field, value, evidence content, evidence locator, expectedVersion, producer)`. The concrete `CandidateCertificate._content()` additionally binds `policy/template`, `template_version`, `source_kind`, `producer_version`, selection metadata, lineage ids, and other inputs. The v0.4 model therefore asserts **no** implication of the form

```
same modeled tuple  =>  same canonical certificate id
```

because such an implication would collapse concrete certificates that differ only in unmodeled hash inputs. It asserts only the one-way direction required by S5: **a difference in a modeled binding component guarantees different canonical ids**. Two concrete certificates whose modeled tuple is identical but whose policy/template/config inputs differ may have different `CertId`s in the formal universe; nothing in the formal model equates them. This is the exact abstraction required by the gate: S5 is decided by exact canonical identity, never by modeled-tuple equality.

`certModeledContentEqual` is therefore **not** an identity predicate. It is only used (a) to express the S5 premise that two certificates carry the same value but different modeled context, and (b) in the dependency analysis. `C-auth-cert`, `traceComplete`, CNTA, and every authorization/transition↔certificate check use `sameCanonicalCertificate` (`c.certId` equality).

**Concrete address verification stays implementation-level.** `verify_content_address()` (recompute `certificate_id = sha256(canonical_json(_content()))`) remains a concrete guard in the mapping table. It is not a formal contract conjunct in v0.4, because the formal model no longer re-derives certificate identity from an incomplete modeled content tuple.

Two certificates with **identical value but different context** differ in a modeled binding component, so the one-way fact gives them **different canonical ids** — exactly the construct S5 requires. Two certificates whose modeled tuples are identical may be distinct atoms with distinct or equal `CertId`s; the formal model takes no position on that case, and no paper claim depends on it.
### 4.6 Authorization — explicit Authorization→Certificate binding and human-authorized value (v0.4 P0-1)

```
sig Authorization {
  certificate    : one Certificate,   -- the machine certificate that was reviewed
  authorizedValue : one Value,        -- the human-authorized FINAL value (P0-1)
  principal      : one Principal
}
```

```
Authorize(a, Cert(ci), v) and sameCanonicalCertificate(ci, cj) = False
   =>  Authorize(a, Cert(cj), v) = False
```

The authorization is produced by an authorized principal and explicitly references exactly one candidate certificate **and exactly one authorized final value**. It is **not** a capability, a role, or a policy that can be re-targeted.

**P0-1 Accept vs Correction.**

```
Accept:     a.authorizedValue = a.certificate.candidate.value
Correction: a.authorizedValue != a.certificate.candidate.value
```

The certificate preserves the original machine proposal; the authorization preserves the human-authorized final value. The committed value is bound to the authorization, never silently taken from an unbound event field or always forced to the candidate value. An authenticated reviewer may approve a wrong value, but the *recorded* value is still the value the authorization carries (wrong-but-attributable); a value that the authorization did not carry at all is blocked by `C-auth-value`.

**AuthorizationBinding resolution (v0.3 gate P0-2, carried forward).** The abstract relation is intentionally stronger than the current concrete `HumanDecision` dataclass (`decision_id, reviewer_id, candidate_id, field_key, reason, decided_at`; no `certificate_id`, no authorized value column). v0.4 does **not** claim that the current transition-level `(decision_id, certificate_id)` pair or the current derived-certificate correction path is identical to decision-time Authorization→Certificate plus authorized value. Instead §14.2 specifies the required concrete change: a dedicated, immutable **`AuthorizationBinding`** artifact persisted at authorization time with `decision_id`, `certificate_id`, `authorized_value_payload` (or `authorized_value_hash`), and `bound_at`. The formal property is kept; the concrete schema change is documented but **not implemented** in this phase.

### 4.7 Record version and transition (v0.4 P0-1/P0-2)

```
sig Transition {
  targetRecord  : one Record,
  targetField   : one Field,
  evidence      : one Evidence,
  fromVersion   : one Version,      -- version the transition was based on
  toVersion     : one Version,      -- version the transition produced
  value         : one Value,
  producer      : one Producer,
  certificate   : one Certificate,  -- T->Cert binding
  authorization : one Authorization -- T->A binding
}
```

`Transition.value` is the **human-authorized final value**. Under the full contract it is bound to `authorization.authorizedValue` (`C-transition`), not necessarily to `certificate.candidate.value`. `Transition` is the whole-record snapshot append entry produced by one authorized admission. It carries both version endpoints; there are no per-fact version relations anywhere in v0.4.

### 4.8 State (whole-record semantics; v0.6 P0-2 fact-to-source)

```
sig State {
  committedValue  : Record -> Field -> lone Value,      -- one value per (record, field)
  committedSource : Record -> Field -> lone Transition, -- last transition that established it
  currentVersion  : Record -> one Version,              -- whole-record snapshot version
  transitions     : set Transition,                     -- append-only transition history
  candidates      : set Candidate,                      -- auxiliary set of candidate payloads; admission persistence is via Certificate.candidate
  certificates    : set Certificate,                    -- persisted certificate artifacts
  authorizations  : set Authorization,                  -- persisted authorization artifacts
  evidence        : set Evidence
}

pred stateInvariant[s: State] {
  all r: Record | s.currentVersion[r].record = r
  -- committedSource has exactly the committed (record,field) domain and
  -- always points at a transition of that record/field pair:
  all r: Record, f: Field |
    (some s.committedValue[r][f]) iff (some s.committedSource[r][f])
  all r: Record, f: Field, t: Transition |
    t = s.committedSource[r][f] => t.targetRecord = r and t.targetField = f
}
```

`committedValue` directly mirrors the concrete latest `RecordVersion.values` mapping for the record, and `currentVersion[r]` mirrors the concrete `FormRow.current_record_version` whole-record counter. `committedSource[r,f]` is the **fact-to-source** relation introduced by the v0.3 gate (P0-2): for each committed `(record,field)` fact it points to the transition that last established that value.

**v0.6 P0 — structural validity is enforced on every reachable state.** `stateInvariant` is not a prose side condition: `orderedTrace` itself asserts `all s: tr.states.elems | stateInvariant[s]` (§5.1), so every `ReachableState` satisfies it. The invariant is deliberately **structural only** and does **not** include (a) `committedSource[r,f] in s.transitions` — a post-tamper state may keep a source anchor whose transition row was deleted, which is exactly the P6 case; or (b) `committedSource[r,f].value = committedValue[r,f]` — that equality is a contract-derived binding property (P5/P6), not structural state validity, and its absence after corruption is exactly what P6 observes via `traceComplete[s,r,f]` (§13).

The v0.1 `Fact` signature with its per-fact `version` relation remains **removed**. There are no per-fact version relations anywhere in v0.6; the whole-record version advances for every admission while a non-target field keeps both its committed value and its older source transition.
### 4.9 Events

```
abstract sig Event { pre : one State, post : one State }

sig MachineEvent extends Event {}
  -- recognition / retrieval / LLM / rule services: may create candidates,
  -- certificates, and evidence; MUST NOT create authorizations; NEVER changes
  -- committedValue, committedSource, or currentVersion (P0-3).

sig AdmissionEvent extends Event {
  certificate     : one Certificate,
  authorization   : one Authorization,
  targetRecord    : one Record,      -- attempted target, supplied independently
  targetField     : one Field,       -- independently supplied attempted field;
                                     -- NEVER inferred from the certificate (P2-1)
  targetEvidence  : one Evidence,    -- independently supplied attempted evidence
  expectedVersion : one Version,     -- version claimed by the attempt (not by cert)
  value           : one Value        -- attempted final value; bound to the
}                                    -- authorization only by C-auth-value

sig TamperEvent extends Event {}
  -- v0.4 P1-1: transition-only corruption/deletion/rebinding.
  -- May change State.transitions only; never committedValue,
  -- committedSource, currentVersion, or any other artifact.
```

`AdmissionEvent` deliberately carries the attempted context independently of `certificate.candidate`. These free relations are the formal slots in which S1–S5 substitutions enter the model. `expectedVersion` is **the attempt's declared version**, and is never inferred from the certificate. `value` is the attempted final value; only `C-auth-value` ties it to the human-authorized value.

**P0-3 authorization creation boundary.** `Authorization` atoms are created only as part of an `AdmissionEvent` (atomic review+commit abstraction, option A of the gate instruction) or by the trusted initialization of the model. `MachineEvent` never fabricates an `Authorization`. A missing or unregistered `Principal` reference on an attempted authorization is a rejectable admission (`C-principal`); real-world impersonation of a valid reviewer identity is out of scope (lock §9, forged real-world human identity).

---

## 5. Reachable trace semantics (v0.3 P1-4/P1-5/P1-6 carried forward)

v0.4 retains the explicit state trace **with one event per edge** before any assertion. The assertion catalog in §12 quantifies only over states and events that occur in such traces.

### 5.1 Semantic definitions

```
Trace.states : seq State
Trace.events : seq Event

wellFormedTrace(tr)  :=
    states is a non-empty finite sequence s_0, ..., s_n
    and events is a finite sequence e_0, ..., e_(n-1)
    and for every i in 0..n-1:
        events[i].pre  = states[i]
        and events[i].post = states[i+1]

-- EXACTLY ONE EVENT PER TRACE EDGE (P1-5).
-- The one-to-one indexed pairing above gives every adjacent state pair
-- (states[i], states[i+1]) exactly one event slot events[i]. There is no
-- existential Step(states[i], states[i+1]) that several Event atoms could
-- simultaneously satisfy: the event of edge i IS events[i].
```

**P1-4 sequential interleaving.** A trace is one ordered sequence of states. If two confirmations A and B were both generated against version `v0`, only one of them can occupy the edge that advances `v0 -> v1`. The other is a **later** event in the same trace, processed after `pre.currentVersion = v1`; because its `expectedVersion = v0`, `C-fresh` fails and it is rejected via `sameState`. The model never claims A and B share one pre-state inside the same linear trace; the abstract universe may contain a *counterfactual* state pair for each attempt, but a concrete ordered trace interleaves them sequentially.

```
Occurs(e, pre, post)  :=  e.pre = pre and e.post = post

ReachableState(s)  :=  exists ordered trace tau and index i with tau.states[i] = s
ReachableEvent(e)  :=  exists ordered trace tau and index i with tau.events[i] = e

sameState(x, y)  :=                       -- observational equality (P1-6)
    x.committedValue  = y.committedValue
    and x.committedSource = y.committedSource
    and x.currentVersion = y.currentVersion
    and x.transitions    = y.transitions
    and x.candidates     = y.candidates
    and x.certificates   = y.certificates
    and x.authorizations = y.authorizations
    and x.evidence       = y.evidence
```

**P1-6 note.** `sameState` compares **all modeled state relations**, not snapshot atoms. A rejected step is allowed to move from state atom `s` to a **different** state atom `s'` whenever `sameState(s, s')`; it is never defined as `post = pre`. For this reason v0.6 does **not** use `util/ordering[State]` as the trace encoding; the authoritative encoding is the bounded `seq State` / `seq Event` shape above.

Alloy-oriented skeleton:

```
sig Trace { states : seq State, events : seq Event }

pred Occurs[e: Event, pre: State, post: State] {
  e.pre = pre and e.post = post
}

pred wellFormedTrace[tr: Trace] {
  some tr.states
  -- event slots are exactly the indices of the first n-1 state indices
  tr.events.inds =
    { i: Int | i in tr.states.inds and i < lastIndex[tr.states] }
}

pred orderedTrace[tr: Trace] {
  wellFormedTrace[tr]

  all s: tr.states.elems |
    stateInvariant[s]

  init[tr.states[0]]

  all i: tr.events.inds |
    Occurs[tr.events[i], tr.states[i], tr.states[i.plus[1]]]
    and eventStep[tr.events[i]]
}
```

**v0.6 P0 — `stateInvariant` is part of reachable-state semantics.** The invariant clause `all s: tr.states.elems | stateInvariant[s]` is inside `orderedTrace`, not a prose addition. `ReachableState(s)` is defined as existence in some ordered trace (§5.1), so **every reachable state of every ordered trace satisfies `stateInvariant`**. The first state is covered by this clause together with `init[tr.states[0]]`; every post-state of every event edge is likewise covered by the same universal quantification. An event step whose post-state violates one of the four structural clauses simply does not produce an ordered trace. This is the exact gate-required formulation; no separate `plus stateInvariant` prose dependency is used anywhere.

`eventStep` is defined in §5.2. Because every edge is tied to its indexed event slot, no edge has zero or several events.

### 5.2 Init and event steps in Alloy-oriented form

```
pred init[s: State] {
  no s.committedValue
  no s.committedSource
  all r: Record | s.currentVersion[r] = initialVersion[r]
  no s.transitions
  -- s.candidates / s.certificates / s.authorizations / s.evidence are
  -- unconstrained: trusted initialization and machine artifacts may
  -- pre-exist the first admission. Any pre-existing authorization is
  -- trusted initialization, NOT the product of a MachineEvent.
}

pred eventStep[e: Event] {
  (e in MachineEvent   and machineStep[e])
  or
  (e in AdmissionEvent and baseAdmissionStep[e])
  or
  (e in TamperEvent    and tamperStep[e])
}
```

There is no standalone existential `step[pre, post]` used to build traces (P1-5). `machineStep`, `baseAdmissionStep`, and `tamperStep` constrain the single event stored in each trace edge.

**v0.6 P0 note on `init` and `eventStep`.** `init[s]` is already consistent with `stateInvariant`: `no committedValue` and `no committedSource` make the domain-equivalence clause vacuously true, and `initialVersion[r]` is defined with `v.record = r` (§4.3), so `currentVersion[r].record = r` holds in the initial state. `eventStep` predicates are deliberately not duplicated inside `orderedTrace`'s invariant clause: the universal `all s: tr.states.elems | stateInvariant[s]` filters every pre-state **and** post-state of every event edge. In particular, the base `admissionEffect` must land in a structurally valid post-state (`successor` keeps the same record; the same target `(r,f)` is written in both `committedValue` and `committedSource`; the installed source transition carries `targetRecord = r` and `targetField = f`), and `tamperStep` preserves `committedValue`, `committedSource`, and `currentVersion`, so deleting or replacing transitions cannot violate the structural invariant.

### 5.3 Enforcing trace (full model boundary)

```
pred EnforcingTrace[tr: Trace] {
  orderedTrace[tr]
  all i: tr.events.inds | let e = tr.events[i] |
    (e in AdmissionEvent and admissionEffect[e]) => Contract[e]
}
```

A **full reachable state/event** is one occurring in some `EnforcingTrace`:

```
ReachableFullState(s)  :=  exists enforcing trace tau, index i: tau.states[i] = s
ReachableFullEvent(e)  :=  exists enforcing trace tau, index i: tau.events[i] = e
```

Rejections need not satisfy `Contract`; they simply satisfy `sameState(pre, post)`. This is the formal reading of fail-closed admission: illegal attempts are representable and can be rejected, but they are never effective in a full trace. `EnforcingTrace` replaces the v0.1 `EnforcingRun` that quantified over disconnected event atoms (open risk G2).

---
## 6. Transition semantics: base semantics first, contract second

### 6.1 Primitive effects (non-tautological base)

The base semantics defines **what an event can do to the state**, without deciding whether it is legal.

**P1-7 pair-specific field update.** `committedValue` is ternary. The field-level write does not use a blanket `++`; it removes exactly the pair `(record -> field)` slot and adds the one new value, preserving every other field of the record:

```
fun setFieldValue[s: State, r: Record, f: Field, v: Value]
    : Record -> Field -> lone Value {
  s.committedValue - (r -> f -> Value) + (r -> f -> v)
}
```

**P0-2 pair-specific source update.** `committedSource` is updated with the same pair-specific discipline: only the target `(record, field)` slot changes; every other field keeps its older source transition even though the record's whole-record version advances.

```
fun setCommittedSource[s: State, r: Record, f: Field, t: Transition]
    : Record -> Field -> lone Transition {
  s.committedSource - (r -> f -> Transition) + (r -> f -> t)
}

fun setCurrentVersion[s: State, r: Record, v: Version]
    : Record -> one Version {
  s.currentVersion - (r -> Version) + (r -> v)
}

pred sameState[a, b: State] {
  a.committedValue  = b.committedValue
  a.committedSource = b.committedSource
  a.currentVersion  = b.currentVersion
  a.transitions     = b.transitions
  a.candidates      = b.candidates
  a.certificates    = b.certificates
  a.authorizations  = b.authorizations
  a.evidence        = b.evidence
}

pred rejectedAdmission[e: AdmissionEvent] {
  sameState[e.pre, e.post]    -- fail-closed; snapshot atoms may differ (P1-6)
}

pred admissionEffect[e: AdmissionEvent] {
  -- the attempted target becomes the current value for that (record, field);
  -- the record advances from its PRE-STATE current version, independently
  -- of e.expectedVersion. This independence is what makes C-fresh (A4b)
  -- a real, ablatable mechanism.
  some newVersion: successor[e.pre.currentVersion[e.targetRecord]] {
    e.post.committedValue =
        setFieldValue[e.pre, e.targetRecord, e.targetField, e.value]
    e.post.currentVersion =
        setCurrentVersion[e.pre, e.targetRecord, newVersion]
    e.post.candidates     = e.pre.candidates
    e.post.certificates   = e.pre.certificates + e.certificate
    e.post.authorizations = e.pre.authorizations + e.authorization
    e.post.evidence       = e.pre.evidence + e.targetEvidence
  }
  -- P0-2: an effective admission also installs a source transition for the
  -- updated fact. The source transition's other bindings (versions, evidence,
  -- producer, certificate, authorization, value) are deliberately left free
  -- in the base semantics; C-transition fixes them in the full contract.
  some sourceTransition: Transition {
    e.post.committedSource =
        setCommittedSource[e.pre, e.targetRecord, e.targetField, sourceTransition]
    sourceTransition.targetRecord = e.targetRecord
    sourceTransition.targetField  = e.targetField
  }
  -- NOTE: e.post.transitions is deliberately UNCONSTRAINED in the base
  -- semantics. An illegal attempt may append no transition, duplicate
  -- transitions, a transition different from committedSource, or a misbound
  -- transition. C-transition in Contract is the only thing that excludes
  -- those outcomes; this is what makes ablation A6 meaningful. Likewise
  -- e.value is unconstrained against the authorization in the base effect;
  -- C-auth-value is the only mechanism binding it to the authorization, and
  -- P5 (transitionIntegrity) is the property that additionally requires the
  -- appended transition value to equal the committed value (v0.4 P0-1).
}

pred baseAdmissionStep[e: AdmissionEvent] {
  rejectedAdmission[e] or admissionEffect[e]
}
```

There are no `Fact` atoms in v0.4: replacing the old `(record, field)` value is the pair-specific relation override shown above, and the whole-record version advance is the single `currentVersion` override. The update preserves all non-target fields of the record (P1-7), and the source update preserves all non-target fields' sources (P0-2).

**P0-2 unchanged-field example.** Record `r` has `committedSource[r,f1] = t1` and `committedValue[r,f1] = v1`. An effective admission later updates `(r,f2)` to `v2` and installs `committedSource[r,f2] = t2` while advancing `currentVersion[r]`. Because `setCommittedSource` only removes/installs the `(r,f2)` slot, `committedSource[r,f1]` remains `t1` and `committedValue[r,f1]` remains `v1`; `traceComplete[s,r,f1]` can therefore still find `t1` even though the record's whole-record version has advanced.

**P0-1 ABL_8 base witness.** With only `C-auth-value` removed, the base effect permits `e.value = Y` and `e.authorization.authorizedValue = X` with `X != Y`. It commits `Y` in `committedValue`, installs a source transition `t`, and the retained `C-transition` binds `t = committedSource[r,f]` and `t.value = X`. The strengthened P5 then fails exactly because `t.value = X != Y = e.post.committedValue[r,f]` (see §7.3 and §12.3).

**Important:** in `baseAdmissionStep`, a mismatched admission (wrong record, wrong field, wrong evidence, wrong declared version, wrong value, authorization bound to another certificate) *may still take `admissionEffect`*. This is intentional. Invalid successes are not excluded by definition; they are excluded only by the contract in §7. This is the structural device that makes P1 non-tautological.
### 6.2 Machine and tamper effects (P0-3; v0.6 P1-1 carried)

```
pred machineStep[e: MachineEvent] {
  -- may add candidates, certificates, evidence;
  -- MUST NOT add authorizations (P0-3):
  e.post.authorizations = e.pre.authorizations
  -- committed facts, sources, and transition history are never changed:
  e.post.committedValue  = e.pre.committedValue
  e.post.committedSource = e.pre.committedSource
  e.post.currentVersion  = e.pre.currentVersion
  e.post.transitions     = e.pre.transitions
  -- artifacts are monotonically added, never removed:
  e.pre.candidates   in e.post.candidates
  e.pre.certificates in e.post.certificates
  e.pre.evidence     in e.post.evidence
}

pred tamperStep[e: TamperEvent] {
  -- v0.4 P1-1: transition-only corruption/deletion/rebinding.
  -- State.transitions may change arbitrarily; committed facts, committed
  -- sources, versions, and ALL other artifacts never change:
  e.post.committedValue  = e.pre.committedValue
  e.post.committedSource = e.pre.committedSource
  e.post.currentVersion  = e.pre.currentVersion
  e.post.candidates      = e.pre.candidates
  e.post.certificates    = e.pre.certificates
  e.post.authorizations  = e.pre.authorizations
  e.post.evidence        = e.pre.evidence
}
```

P0 direct-write exclusion is the assertion that every reachable `MachineEvent` and `TamperEvent` step satisfies the equalities above, i.e. only `AdmissionEvent` can ever change committed values, committed sources, or whole-record versions. `MachineEvent` cannot fabricate an `Authorization`; if a pre-state has none, the post-state has none.

**v0.4 P1-1 boundary.** The formal tamperer can mutate only `State.transitions`. It can delete a transition, insert a replacement transition whose fields were rebound to other rows/values, or insert a duplicate. It **cannot** delete or mutate certificate rows, decision/authorization rows, evidence rows, `committedValue`, `committedSource`, or versions. Consequently the formal P6 corruption classes are exactly the transition-only classes listed in THREAT_MODEL.md §12; concrete certificate/decision/evidence-row deletion tests are implementation-level robustness evidence **outside** the Alloy P6 submodel and are never claimed as formally reachable P6 classes.

---

## 7. The full admission contract

The full contract is a conjunction of independent, individually removable conjuncts. **No single conjunct is named `Admit <=> ContextMatch`.**

```
pred Contract[e: AdmissionEvent] {

  -- P1-1: durable machine artifacts must PRE-EXIST the effective admission.
  -- Authorization may be newly persisted by this event; the certificate and
  -- the presented evidence row may not be conjured at admission time.
  e.certificate in e.pre.certificates                         -- C-cert-preexists
  e.targetEvidence in e.pre.evidence                          -- C-evidence-preexists

  -- S3 record binding (A3): attempt record equals the record frozen
  -- in the certificate content
  e.targetRecord = e.certificate.candidate.targetRecord       -- C-record

  -- S1 field binding (A1)
  e.targetField  = e.certificate.candidate.targetField        -- C-field

  -- S2 evidence-binding package, split per P1-3:
  -- 2a: same canonical evidence identity (content + locator), the same
  --     identity CandidateCertificate._content() freezes (P1-2)
  sameEvidenceIdentity[e.targetEvidence,
                       e.certificate.candidate.evidence]      -- C-evidence-id
  -- 2b: the presented evidence row is owned by the attempted record
  e.targetEvidence.record = e.targetRecord                    -- C-evidence-record

  -- S4a version binding (A4a): attempt version equals certificate version
  e.expectedVersion = e.certificate.candidate.expectedVersion -- C-version

  -- S4b freshness (A4b): attempt version equals the record's current
  -- whole-record version in the pre-state
  e.pre.currentVersion[e.targetRecord] = e.expectedVersion    -- C-fresh

  -- S5 authorization->certificate binding, stated in exact canonical
  -- certificate identity (certId), per v0.4 P1-2
  sameCanonicalCertificate[e.authorization.certificate, e.certificate]
                                                               -- C-auth-cert

  -- authorization must be attributable to an authorized principal
  e.authorization.principal in PrincipalRegistry.authorized    -- C-principal

  -- P0-1: the committed value is the human-authorized value. Accept has
  -- authorizedValue = candidate.value; Correction has authorizedValue !=
  -- candidate.value; both are allowed, unrecorded third values are not.
  e.value = e.authorization.authorizedValue                    -- C-auth-value

  -- P5 transition integrity: exactly one appended transition TOTAL,
  -- with every binding made explicit (v0.2 P1-1, v0.3 P0-1, v0.4 P0-2).
  -- NOTE: t.value is bound here to authorization.authorizedValue only.
  -- The property transitionIntegrity(e) (P5, §12.3) ADDITIONALLY binds
  -- t.value to e.post.committedValue[...]. Keeping the committed-value
  -- binding out of this conjunct is deliberate: it is what makes the
  -- v0.4 ABL_8 counterexample (committed Y, transition X, X != Y)
  -- satisfiable while P5 fails for the intended reason (P0-1).
  one t: e.post.transitions - e.pre.transitions {
    e.post.transitions = e.pre.transitions + t                -- exactly one appended
    t = e.post.committedSource[e.targetRecord][e.targetField] -- P0-2 fact-to-source
    t.targetRecord = e.targetRecord
    t.targetField  = e.targetField
    t.evidence     = e.targetEvidence
    t.fromVersion  = e.pre.currentVersion[e.targetRecord]
    t.toVersion    = e.post.currentVersion[e.targetRecord]
    t.toVersion    = successor[t.fromVersion]
    t.value        = e.authorization.authorizedValue
    t.producer     = e.certificate.candidate.producer
    t.certificate  = e.certificate
    t.authorization = e.authorization
  }                                                            -- C-transition
}
```

A full run is any `EnforcingTrace` (reachable ordered trace in which every effective admission satisfies `Contract`). Rejections need not satisfy `Contract`; they satisfy `sameState(pre, post)`.

**v0.4 contract changes.** (1) `contentAddressCorrect` is removed from the formal contract: certificate identity is primitive and concrete content-address verification is implementation-level (§4.5). (2) `C-transition` now also fixes `t = e.post.committedSource[e.targetRecord][e.targetField]` so the appended transition is exactly the fact's source transition. (3) `C-transition` still binds `t.value = e.authorization.authorizedValue`; the additional committed-state value check belongs to the strengthened P5 property (§12.3), not to this conjunct, for the ABL_8 reason stated above.
### 7.1 Intended conjunct roles

| Conjunct | Attack blocked | Property | Ablation |
|---|---|---|---|
| `C-record` | S3 record substitution | P1 | ABL_3 |
| `C-field` | S1 field substitution | P1 | ABL_1 |
| `C-evidence-id` | S2a evidence-identity substitution (different content or locator) | P1 | ABL_2a |
| `C-evidence-record` | S2b evidence-row owned by another record | P1 | ABL_2b |
| `C-version` | S4a certificate↔attempt version substitution | P1 | ABL_4a |
| `C-fresh` | S4b stale replay against current record version | P4 | ABL_4b |
| `C-auth-cert` | S5 authorization/certificate substitution | P1/P3 | ABL_5 |
| `C-principal` | unauthorized / unregistered principal (not real-world impersonation, v0.5 P2-1) | P3 | ABL_principal |
| `C-auth-value` | effective admission writes a value the authorization never carried (P0-1) | P3/P5 — P5 now fails because the transition value no longer matches the committed state | ABL_8 |
| `C-cert-preexists` | admission conjures its candidate certificate at commit time (P1-1) | P3/P5 | ABL_9 |
| `C-evidence-preexists` | admission conjures its evidence row at commit time (P1-1) | P3/P5 | ABL_10 |
| `C-transition` | missing/duplicate/misbound transition | P5 | ABL_6 |

**v0.4 P1-2 note.** There is no `contentAddressCorrect` conjunct in v0.4. The only certificate-identity facts retained in every attack ablation are the global one-way `certIdFaithfulToModeledBindings` and `certIdRowUnique` (§4.5); concrete `verify_content_address()` remains an implementation-level guard in the mapping table (§14.1).

### 7.2 Transition integrity details (v0.4 P0-1/P0-2)

`C-transition` requires **exactly one appended transition total**, not merely one matching transition:

- `one t: e.post.transitions - e.pre.transitions` forbids zero, duplicate, and multi-transition outcomes;
- `e.post.transitions = e.pre.transitions + t` with `t` drawn from the set difference enforces append-only and exact-one together;
- `t = e.post.committedSource[e.targetRecord][e.targetField]` makes the appended transition exactly the fact's source transition (P0-2);
- all nine transition bindings are explicit: `targetRecord`, `targetField`, `evidence`, `fromVersion`, `toVersion`, `value`, `producer`, `certificate`, `authorization`;
- the `value` obligation in the **contract conjunct** is `t.value = e.authorization.authorizedValue` (P0-1). It is deliberately **not** `t.value = e.certificate.candidate.value`, because a human Correction may commit a value different from the machine proposal.

The strengthened **property** `transitionIntegrity(e)` (§12.3) retains all of the above and additionally requires

```
t.value = e.post.committedValue[e.targetRecord][e.targetField]   -- v0.4 P0-1
```

so the transition describes the actual committed update. The committed-value check is deliberately **not** placed in `C-transition`: in the full contract `C-auth-value` plus the base effect implies `t.value = committedValue`, while in ABL_8 (only `C-auth-value` removed) the mismatch `committedValue = Y`, `authorizedValue = t.value = X`, `X != Y` remains satisfiable and P5 fails for exactly that reason (see §7.3).

`fromVersion` is bound to the pre-state whole-record version, not to `e.expectedVersion`. This is deliberate: in the full contract `C-fresh` makes them equal, while in ABL_4b (with `C-fresh` removed) the transition still records the true pre-state base of the write. It also prevents `C-transition` from accidentally implying `C-fresh` or `C-version`.

### 7.3 Dependency table (v0.6 re-run with `stateInvariant` enforced on every reachable state): can a removed conjunct be implied by the rest?

In each row, “remaining conjuncts” means every conjunct of `Contract` except the removed one, plus the structural `stateInvariant`, which v0.6 now enforces inside `orderedTrace` itself (§5.1) — not merely as a prose side condition. The global certificate facts `certIdFaithfulToModeledBindings` and `certIdRowUnique` are retained in every row because they fix only the one-way canonical-identity direction (§4.5).
| Removed conjunct | Implied by the remaining conjuncts? | Counterexample when only this conjunct is removed (every other mechanism retained) |
|---|---|---|
| `C-field` | **No.** No remaining conjunct mentions `candidate.targetField`; `C-transition` only copies `e.targetField` onto `t.targetField`. | S1: `e.targetField = f_B`, `candidate.targetField = f_A`; choose evidence owned by `e.targetRecord`, satisfy `C-record`, `C-version`, `C-fresh`, `C-auth-cert`, `C-principal`, `C-auth-value`, artifact-preexistence, and append one transition that mirrors `f_B`. |
| `C-record` | **No.** v0.1's implication chain is broken because the global axiom `candidate.evidence.record = candidate.targetRecord` is gone. `C-evidence-id`+`C-evidence-record` derive only `candidate.evidence.record = e.targetRecord`; `C-version`+`C-fresh`+`stateInvariant` derive only `candidate.expectedVersion.record = e.targetRecord`. Neither derivation mentions `candidate.targetRecord`. The v0.6 re-check confirms the derivation `stateInvariant => currentVersion[targetRecord].record = targetRecord` is available in every reachable pre/post state, but it never mentions `candidate.targetRecord`; therefore `C-record` remains independently ablatable. | S3: `candidate.targetRecord = r_A`, `e.targetRecord = r_B`; `candidate.evidence` has the identity of an evidence row owned by `r_B`; `candidate.expectedVersion` is a Version of `r_B`; `pre.currentVersion[r_B] = e.expectedVersion`. All other conjuncts hold, the write to `r_B` is effective, and both pre- and post-state satisfy the enforced invariant (post-currentVersion is the successor of `r_B`'s current version, hence `record = r_B`; `committedValue`/`committedSource` are both installed exactly on `(r_B, f)`). |
| `C-evidence-id` | **No.** `C-record` equates attempt and certificate record but says nothing about which evidence identity `e.targetEvidence` is; `C-evidence-record` only checks the row's owner; `C-transition` only copies `e.targetEvidence` onto `t.evidence`. | S2a: `e.targetEvidence = e_B`, `candidate.evidence = e_A`, with `sameEvidenceIdentity[e_A, e_B] = False` (different content or different locator) and `e_B.record = e.targetRecord`. |
| `C-evidence-record` | **No.** `C-evidence-id` gives `sameEvidenceIdentity[e.targetEvidence, candidate.evidence]`, but that identity is `(content, locator)` and says nothing about `Evidence.record`; `C-record` equates records, not evidence ownership. Without the removed candidate-coherence axiom nothing equates the evidence row's `.record` to `e.targetRecord`. | S2b: `sameEvidenceIdentity[e.targetEvidence, candidate.evidence]` but `e.targetEvidence.record != e.targetRecord`. |
| `C-version` | **No.** `C-fresh` equates `e.expectedVersion` with `pre.currentVersion`; `C-transition` binds versions to pre/post state. Neither mentions `candidate.expectedVersion`. | A4a: certificate embeds `expectedVersion = v_i`, attempt declares `e.expectedVersion = pre.currentVersion = v_j`, `v_i != v_j`; the fresh attempt writes and appends a transition from `v_j` to `v_j+1`. |
| `C-fresh` | **No.** `C-version` equates attempt and certificate expected versions, but neither is tied to `pre.currentVersion`; `admissionEffect` advances from `pre.currentVersion` regardless of `e.expectedVersion`; `C-transition` binds `fromVersion` to the pre-state version, not to `e.expectedVersion`. | A4b: `e.expectedVersion = candidate.expectedVersion = v_i` while `pre.currentVersion = v_j != v_i`; the stale attempt writes from `v_j` to `v_j+1` and appends the fully bound transition. |

| `C-auth-cert` | **No.** `C-transition` binds `t.authorization = e.authorization` and `t.certificate = e.certificate` but never equates `e.authorization.certificate` with `e.certificate`; no other conjunct mentions `Authorization.certificate`. | S5: `e.authorization.certificate = Cert_A`, `e.certificate = Cert_B`, `canonicalCertId[Cert_A] != canonicalCertId[Cert_B]`, `value(Cert_A) = value(Cert_B)`, `e.value = e.authorization.authorizedValue`; all other bindings hold. |
| `C-principal` | **No.** Nothing else mentions `PrincipalRegistry.authorized`. | One principal outside `PrincipalRegistry.authorized`; all other bindings hold. |
| `C-auth-value` | **No.** No remaining conjunct mentions `e.value`. `admissionEffect` commits `e.value`, and `C-transition` binds the unique appended transition to `committedSource` and to `authorization.authorizedValue`, not to the committed value; the committed-value check lives in the P5 property, not in any remaining contract conjunct. | **v0.4 P0-1 witness:** `e.authorization.authorizedValue = X`, `e.value = Y`, `X != Y`. The effective write commits `Y` in `committedValue`, installs `committedSource[r,f] = t`, and the retained `C-transition` appends exactly `t` with `t.value = X`. All other conjuncts hold. P5 now fails because `t.value = X != Y = e.post.committedValue[r,f]` — the transition no longer matches the committed state. This is exactly the reason the gate required. |
| `C-cert-preexists` | **No.** Base `admissionEffect` adds `e.certificate` to `post.certificates`; no other conjunct mentions `pre.certificates`. | Effective admission whose certificate atom first appears in `post.certificates`; every other conjunct holds (the certificate carries a well-formed primitive `certId` and all bindings agree). |
| `C-evidence-preexists` | **No.** Base `admissionEffect` adds `e.targetEvidence` to `post.evidence`; no other conjunct mentions `pre.evidence`. | Effective admission whose presented evidence row first appears in `post.evidence`; every other conjunct holds. |
| `C-transition` | **No.** Base `admissionEffect` leaves `post.transitions` unconstrained; it only installs `committedSource`. No other conjunct mentions `transitions` or identifies the appended transition with `committedSource`. | Effective admission with `post.transitions = pre.transitions` (missing source transition), two appended transitions, or one appended transition `t != committedSource[r,f]`; all other bindings hold. P5 fails in each case. |

**Conclusion:** in v0.6 no named conjunct is logically implied by the conjunction of the others, with `stateInvariant` now actually enforced on every state of every ordered trace. A1, A2a, A2b, A3, A4a, A4b, A5, A8, A9, A10, and A6 (for `C-transition`) each have a satisfiable counterexample when only its target mechanism is removed; `C-principal` has the same property, and ABL_7 covers the trace-validation layer of P6. The v0.4-introduced and still-required result is the ABL_8 row above: with only `C-auth-value` removed, committed value Y and authorization/transition value X (`X != Y`) are jointly satisfiable, and the strengthened P5 fails because the transition no longer matches the committed state.

**v0.6 P0 mandatory dependency re-check.** The table below records, ablation by ablation, why the named witness still lies in an ordered trace after `orderedTrace` gained `all s: tr.states.elems | stateInvariant[s]`. The invariant has four clauses: (I1) `currentVersion[r].record = r`; (I2) `(some committedValue[r,f]) iff (some committedSource[r,f])`; (I3/I4) any installed `committedSource[r,f]` has `targetRecord = r` and `targetField = f`. It intentionally has no transition-membership clause and no source-value/committed-value clause (§4.8).

| Ablation | Why the witness remains structurally satisfiable with the invariant enforced |
|---|---|
| `ABL_1` (S1, no `C-field`) | Base effect installs `committedValue`/`committedSource` on the same attempted pair `(r, f_B)` and sets the source transition's `targetRecord = r`, `targetField = f_B`; `currentVersion[r]` advances to a successor of the same record. I1–I4 hold; field substitution is unrelated to the invariant. |
| `ABL_2a` / `ABL_2b` (S2a/S2b, no evidence conjunct) | Evidence-identity/owner mismatches do not occur in any invariant clause. The effect writes the same `(r,f)` in both committed relations and advances `r`'s own version; I1–I4 hold. |
| `ABL_3` (S3, no `C-record`) | **Special gate case.** The retained `C-version` + `C-fresh` and the pre-state invariant I1 give `e.expectedVersion = e.pre.currentVersion[r_B]` with `record = r_B`; the base effect advances `r_B` to a successor of that same record. The post-state therefore satisfies I1 for `r_B`, and I2–I4 hold because `(r_B, f)` is written in both committed relations and the installed source transition is bound to `(r_B, f)`. The prior reasoning that used `stateInvariant => currentVersion[targetRecord].record = targetRecord` remains valid, and it still derives nothing about `candidate.targetRecord`; `C-record` is not implied. |
| `ABL_4a` (no `C-version`) | Attempt and certificate versions may differ, but the effect advances from `pre.currentVersion[targetRecord]` (I1 guarantees that version's record is `targetRecord`); the post-state advances that same record. I1–I4 hold. |
| `ABL_4b` (no `C-fresh`) | A stale `e.expectedVersion` does not enter any invariant clause. The effect still advances the true pre-state version of `targetRecord`; I1–I4 hold. |
| `ABL_5` (no `C-auth-cert`) | Authorization/certificate identity mismatch is outside the invariant. The effect writes the same `(r,f)` in both committed relations and binds the source transition to `(r,f)`; I1–I4 hold. |
| `ABL_6` (no `C-transition`) | The invariant deliberately says nothing about `State.transitions` (no membership, count, or source-identity clauses). Missing, duplicate, or source-detached transitions all leave I1–I4 intact. |
| `ABL_7` (no trace-validation conjuncts) | `tamperStep` preserves `committedValue`, `committedSource`, and `currentVersion`; deleting or replacing the source transition only changes `transitions`. Because the invariant has no `committedSource in transitions` clause, the post-tamper state satisfies I1–I4 while `traceComplete` (weakened) reports Complete. |
| `ABL_8` (no `C-auth-value`) | The invariant deliberately has no `committedSource.value = committedValue` clause. Committed value Y with source transition X (`X != Y`) therefore satisfies I1–I4; P5 fails exactly on that binding mismatch. |
| `ABL_9` (no `C-cert-preexists`) | The invariant does not constrain `certificates` (or `candidates`). Adding a conjured certificate in the post-state affects no invariant clause. |
| `ABL_10` (no `C-evidence-preexists`) | The invariant does not constrain `evidence`. Adding conjured evidence in the post-state affects no invariant clause. |

No ablation witness required alteration, and no named mechanism became implied by the newly enforced invariant. `ABL_3` remains a genuine ablation of `C-record`: the invariant only ties `currentVersion[targetRecord]` to its own record, never to `candidate.targetRecord`.

---
## 8. The substitution attacks in the model (S4 split and S2 split carried forward)

Each attack is one reachable `AdmissionEvent e` in which `Contract` would be violated by one conjunct. In the **full model** every such event is either absent from the trace or rejected (`rejectedAdmission[e]`). In the matching **ablation model** the removed conjunct lets `admissionEffect[e]` occur, so the check fails.

| Attack | Formal condition on `e` | Violated conjunct | Property |
|---|---|---|---|
| S1 field substitution | `e.targetField != e.certificate.candidate.targetField` | `C-field` | P1 |
| S2a evidence-identity substitution | `sameEvidenceIdentity[e.targetEvidence, e.certificate.candidate.evidence] = False` | `C-evidence-id` | P1 |
| S2b evidence-record substitution | `sameEvidenceIdentity[e.targetEvidence, e.certificate.candidate.evidence]` but `e.targetEvidence.record != e.targetRecord` | `C-evidence-record` | P1 |
| S3 record substitution | `e.targetRecord != e.certificate.candidate.targetRecord` | `C-record` | P1 |
| S4a certificate↔attempt version substitution | `e.expectedVersion != e.certificate.candidate.expectedVersion` while `e.expectedVersion = e.pre.currentVersion[e.targetRecord]` | `C-version` | P1 |
| S4b stale replay against current record version | `e.expectedVersion = e.certificate.candidate.expectedVersion` while `e.expectedVersion != e.pre.currentVersion[e.targetRecord]` | `C-fresh` | P4 |
| S5 authorization / certificate substitution | `canonicalCertId[e.authorization.certificate] != canonicalCertId[e.certificate]` even when `Value(auth cert) = Value(attempt cert)`; distinct modeled context guarantees distinct canonical ids by the one-way `certIdFaithfulToModeledBindings` fact | `C-auth-cert` | P1/P3 |
| S8 unrecorded final value (P0-1) | `e.value != e.authorization.authorizedValue` while every context/authorization binding holds | `C-auth-value` | P3/P5 |
| S9 conjured certificate (P1-1) | `e.certificate not in e.pre.certificates` | `C-cert-preexists` | P3/P5 |
| S10 conjured evidence (P1-1) | `e.targetEvidence not in e.pre.evidence` | `C-evidence-preexists` | P3/P5 |

S4a belongs to P1 (certificate context is version-bound); S4b belongs to P4 (the current record version must be the one the attempt claims). S2a and S2b are now separate ablations (P1-3).

S5 is the most important experiment: a legal `Authorize(Cert_A)` is attempted against `Cert_B` with an identical proposed value. The model constructs two distinct certificates with equal `value`, different modeled context; the one-way fact gives them **different canonical ids**, and the attempt rejects on exact `certId` equality. The model does **not** claim the converse direction (same modeled tuple ⇒ same canonical id); unmodeled `_content()` inputs such as policy/template/config identity may distinguish two canonical ids in the concrete system (§4.5).

S8 is the P0-1 payload-binding experiment: the certificate proposes `X`, the authorization authorizes `X` (or any Z), and the event attempts to commit an unrecorded `Y`. The full contract blocks the effective write unless `e.value = authorization.authorizedValue`. In ABL_8 (only `C-auth-value` removed) the effective write is allowed with `committedValue = Y` while the retained `C-transition` records `t.value = authorization.authorizedValue = X`; the strengthened P5 then fails on `t.value != e.post.committedValue[r,f]` (v0.4 P0-1). An **Accept** (`authorizedValue = candidate.value`) and a **Correction** (`authorizedValue != candidate.value`) are both valid; only a value the authorization never carried is invalid.
---

## 9. Why P1 is non-tautological

Lock §14 forbids the pattern: define `Admit <=> ContextMatch`, then assert `Admit => ContextMatch`. v0.4 avoids that pattern structurally and empirically.

### 9.1 Structural separation

1. **`admissionEffect` is defined before `Contract`.** It is a state-delta relation over independently supplied event fields (`targetRecord`, `targetField`, `targetEvidence`, `expectedVersion`, `value`) plus a base-level `committedSource` transition. It does not mention the certificate's candidate except for artifact persistence.
2. **`ContextMatch` is a derived comparison.** It compares event fields with certificate-candidate fields; it is not a primitive of the model.
3. **`Contract` is a conjunction of independent mechanisms** (`C-record`, `C-field`, `C-evidence-id`, `C-evidence-record`, `C-version`, `C-fresh`, `C-auth-cert`, `C-principal`, `C-auth-value`, `C-cert-preexists`, `C-evidence-preexists`, `C-transition`), not one `Admit <=> ContextMatch` axiom.
4. **Illegal successes exist in the base state space.** In `baseAdmissionStep`, a mismatched event can choose `admissionEffect`. The base universe is therefore not empty of bad states, and P1 is a substantive exclusion.
5. **Central assertions quantify over reachable traces.** `ReachableFull` is defined through `Init`/`eventStep` and the one-event-per-edge trace shape (§5), so P1 excludes effective bad events in ordered full histories, not merely in disconnected event atoms (v0.2 P0-3).

### 9.2 Empirical (Alloy) non-tautology protocol

| Check class | What must hold | Meaning |
|---|---|---|
| SAT-1 | `run ValidAdmission_accept` (contract + effect, `authorizedValue = candidate.value`) is **satisfiable** | The full contract admits at least one legal Accept |
| SAT-1-correction | `run ValidAdmission_correction` (contract + effect, `authorizedValue != candidate.value`) is **satisfiable** | The full contract admits a legal human Correction without requiring the committed value to equal the machine proposal (P0-1) |
| SAT-2 | `run InvalidAdmissionState` for each of S1, S2a, S2b, S3, S4a, S4b, S5, S8, S9, S10, unauthorized principal, and each tamper/interleaving state with contract off is **satisfiable** | Bad states really exist in the abstract space |
| PROVE | `check P0_full`..`check P6_full` over `ReachableFull` | No counterexample in the full model within scope |
| ABLATE | `check Ablation_i_has_counterexample` for i = 1, 2a, 2b, 3, 4a, 4b, 5, 6, 7, 8, 9, 10 | Each ablated model must **fail** with the expected counterexample |

The interleaving SAT-2 witness is the **sequentialized** pair required by P1-4: `A` generated for `v0` commits `v0 -> v1` at edge `i`; `B` generated for `v0` occurs at a later edge with `pre.currentVersion = v1`, `e.expectedVersion = v0`, and is rejected by `sameState`. No witness claims two events share one pre-state.

If any ablation check unexpectedly passes, the mechanism is not doing independent work and the model is rejected by the Semantic Gate.
---

## 10. How invalid states enter the Alloy state space

Invalid states are ordinary states whose relations violate one mechanism while satisfying the base event effects. They enter the space through:

1. **Unconstrained event parameters.** `AdmissionEvent.targetRecord / targetField / targetEvidence / expectedVersion / value` are free relations. Alloy can bind them to any object, including objects different from the certificate's candidate relations.
2. **Base effect allows mismatched success.** `baseAdmissionStep` explicitly permits `admissionEffect[e]` without `Contract[e]`. A mismatched attempt can therefore be a state-changing transition in the pre-contract universe.
3. **Distinct artifacts with equal payloads.** Alloy can generate `Cert_A != Cert_B` with equal `value` and different modeled context; the one-way fact then gives different canonical ids. It can also generate equal modeled tuples with different primitive `CertId`s, because no converse implication is asserted (v0.4 P1-2). Only the first case is needed for S5.
4. **Malformed candidates are representable.** Because there is no global candidate-coherence axiom (§4.4), a candidate may point at evidence or a version owned by a different record. Such candidates are excluded from effective admission only by the full contract, and their existence is exactly what makes A2/A3 independent.
5. **Unrecorded values and mismatched fact sources are representable.** `Authorization.authorizedValue` and `AdmissionEvent.value` are independent relations in the base universe; only `C-auth-value` ties them together (P0-1). The base effect also installs a `committedSource` transition whose `value` is left free, so ABL_8 can produce committed value Y with source/transition value X (`X != Y`) — the exact witness the v0.4 P0-1 dependency analysis requires.
6. **Conjured artifacts are representable.** Base `admissionEffect` adds `e.certificate` and `e.targetEvidence` to the post-state; only `C-cert-preexists` / `C-evidence-preexists` require them to pre-exist (P1-1).
7. **Tampering is an explicit reachable event.** `TamperEvent` may change `State.transitions` only (v0.4 P1-1): it can delete the source transition, replace it with a rebound transition (different producer, evidence, value, record/field, certificate, authorization, or version references), or insert a source-version duplicate. `committedSource` keeps pointing at the pre-corruption transition, so P6 sees deletion/rebinding as source-anchor loss and duplicate insertion as a source-version uniqueness failure (v0.5 P0-1/P1). Certificate/decision/evidence-row mutation is **not** a formal TamperEvent capability; such concrete faults are implementation-level evidence outside the Alloy P6 submodel.
8. **Duplicate evidence.** Two evidence atoms may be distinct rows with equal `(content, locator)`. They are distinct persisted rows but the **same canonical evidence identity**, so they are not distinct certificate contexts (P1-2). Two rows with equal content but different locator are distinct contexts.
9. **Sequential competing confirmation (P1-4).** In one ordered trace, `A` and `B` are both generated for `v0`. `A` is edge `i` and advances the record `v0 -> v1`. `B` is a **later** edge with the same `expectedVersion = v0`; its pre-state already has `currentVersion = v1`, so `C-fresh` rejects it. The model does not put A and B on the same edge or on the same pre-state.

A later `run` command must exhibit at least one instance of each (SAT-2 family); unsatisfiable witnesses would mean the model accidentally excluded the attack by construction.
---

## 11. Full model versus ablation models

The **full model** is `M_full = base effects + EnforcingTrace` (all contract conjuncts present). Ablation models remove exactly one mechanism and keep every other conjunct. The v0.2 P1-4 split and the v0.3 P1-3 split remain applied:

| Model | Removed conjunct / mechanism | Expected counterexample (must FAIL the check) |
|---|---|---|
| `ABL_1` | `C-field` | S1: cross-field admission is admitted |
| `ABL_2a` | `C-evidence-id` only | S2a: cross-evidence-identity admission is admitted |
| `ABL_2b` | `C-evidence-record` only | S2b: same evidence identity but wrong evidence owner is admitted |
| `ABL_3` | `C-record` | S3: cross-record admission is admitted |
| `ABL_4a` | `C-version` only | S4a: certificate expected version != attempt version, fresh attempt admitted |
| `ABL_4b` | `C-fresh` only | S4b: stale replay against current record version admitted |
| `ABL_5` | `C-auth-cert` | S5: authorization for Cert_A used against Cert_B with same value |
| `ABL_6` | `C-transition` | P5: missing source transition, duplicate transitions, or appended transition `t != committedSource[r,f]` with misbound fields |
| `ABL_7` | trace-validation conjuncts (source-anchor membership, source-version uniqueness, binding checks) | P6: deleted/replaced source anchor or duplicate `(r, f, src.toVersion)` is reported Complete |
| `ABL_8` | `C-auth-value` | S8: committed value Y while the source transition records authorized value X (`X != Y`); strengthened P5 fails because `t.value != e.post.committedValue[r,f]` |
| `ABL_9` | `C-cert-preexists` | S9: certificate conjured by the effective admission |
| `ABL_10` | `C-evidence-preexists` | S10: evidence row conjured by the effective admission |

The paper reports: full model => no counterexample in scope; each ablation => the named counterexample. That contrast, not any single formula, is the evidence that each mechanism contributes and that P1 is not a definitional tautology. **v0.6 P0:** every ablation run uses `orderedTrace`, so every witness state must satisfy the enforced `stateInvariant`; §7.3 records the ablation-by-ablation satisfiability check and shows no witness needed alteration.
---

## 12. Assertion catalog for the future `.als` model (all over reachable traces)

All full-model checks quantify over `EnforcingTrace` / `ReachableFullState` / `ReachableFullEvent` as defined in §5, hence over states that satisfy `stateInvariant` because `orderedTrace` enforces it (v0.6 P0). No check quantifies over arbitrary disconnected event atoms, and every trace edge is tied to its single indexed event (P1-5).

### 12.1 Central Non-Transferability Assertion (CNTA) — the renamed v0.1 “central theorem”

```
Central Non-Transferability Assertion (CNTA, bounded).

For every enforcing trace tau, every edge i, and every AdmissionEvent
e = tau.events[i] occurring at that edge with admissionEffect(e):

  e.certificate in e.pre.certificates
  and e.targetEvidence in e.pre.evidence
  and attemptContext(e) = certificateContext(e.certificate)
  and sameCanonicalCertificate(e.authorization.certificate, e.certificate)
  and e.authorization.principal in PrincipalRegistry.authorized
  and e.expectedVersion = e.pre.currentVersion[e.targetRecord]
  and e.value = e.authorization.authorizedValue
  and transitionIntegrity(e)

where
  attemptContext(e) = (e.targetRecord, e.targetField,
                       evidenceIdentity(e.targetEvidence), e.expectedVersion)
  certificateContext(c) = (c.candidate.targetRecord, c.candidate.targetField,
                           evidenceIdentity(c.candidate.evidence),
                           c.candidate.expectedVersion)
  evidenceIdentity(x) = (x.content, x.locator)

Consequently, for any Authorization a and any two distinct canonical
certificate ids id1 != id2, there is no effective e in any enforcing trace
with e.authorization = a, canonicalCertId[a.certificate] = id1, and
canonicalCertId[e.certificate] = id2 -- even when
Value(a.certificate) = Value(e.certificate).

The committed value is the authorization's authorizedValue, never an
unrecorded event value: e.value = e.authorization.authorizedValue, and
Accept (equal to candidate.value) and Correction (different from
candidate.value) are both admissible cases of that equality.
```

The paper reports: *“No counterexample was found within the explored scope”* (lock §15), never a universal proof unless a separate genuine proof exists.

### 12.2 Checks

| Name | Kind | Formula (abbreviated) | Expected result |
|---|---|---|---|
| `P0_stateInvariant_reachable` | check | for every `orderedTrace[tr]` and every `s in tr.states.elems`, `stateInvariant[s]` | no counterexample (definitional regression: the clause is inside `orderedTrace`, v0.6 P0) |
| `SAT_invariant_admission_tamper` | run | some ordered trace exists with an effective admission followed by a source-transition-deleting `TamperEvent` | satisfiable (both the normal and the post-tamper state satisfy the invariant; the latter still passes because the invariant has no `committedSource in transitions` clause) |
| `P0_no_machine_write` | check | every reachable `MachineEvent`/`TamperEvent` leaves `committedValue`, `committedSource`, and `currentVersion` unchanged, and every reachable `MachineEvent` leaves `authorizations` unchanged (P0-3) | no counterexample |
| `P1_no_cross_context_admission` | check | `EnforcingTrace` has no effective AdmissionEvent with `attemptContext != certificateContext` (evidence compared by `(content, locator)`) | no counterexample |
| `P1_auth_nontransfer` | check | `EnforcingTrace` has no effective AdmissionEvent with `canonicalCertId[e.authorization.certificate] != canonicalCertId[e.certificate]` | no counterexample |
| `P3_authorization_reference_integrity` | check | for every effective AdmissionEvent `e`, the unique transition appended by `e` carries `e.authorization`, `e.certificate`, canonical certificate agreement, an authorized principal, and `t.value = e.authorization.authorizedValue` | no counterexample |
| `P4_stale_reject` | check | `EnforcingTrace` has no effective AdmissionEvent with `e.expectedVersion != e.pre.currentVersion[e.targetRecord]` | no counterexample |
| `P5_transition_integrity` | check | every effective admission appends exactly one transition TOTAL, equal to `committedSource[r,f]`, with every binding of §7.2 and **both** value anchors (`t.value = e.authorization.authorizedValue` and `t.value = e.post.committedValue[r,f]`) | no counterexample |
| `P6_trace_soundness` | check | for every reachable full state `s` and committed fact `(r,f)`, source-anchor loss/replacement or a duplicate `(r, f, src.toVersion)` transition is never `traceComplete[s,r,f]` (v0.5 P0-1/P1) | no counterexample |
| `SAT_1_accept` | run | a legal Accept (`authorizedValue = candidate.value`) in one enforcing trace | satisfiable |
| `SAT_1_correction` | run | a legal Correction (`authorizedValue != candidate.value`) in one enforcing trace | satisfiable |
| `SAT_2_invalid_states` | run | one witness each for S1, S2a, S2b, S3, S4a, S4b, S5, S8 (committed Y / transition X mismatch), S9, S10, unauthorized principal, transition-only tamper/deletion/rebinding, source-version duplicate insertion, and the sequentialized interleaving pair — with contract off | satisfiable |
| `ABL_1`..`ABL_10` | expect | each weakened model has the named counterexample (`ABL_2a`/`ABL_2b`, `ABL_4a`/`ABL_4b` separate) | **counterexample found** |

### 12.3 P3, P5 and P6 exact forms (v0.6 carries v0.5 P0-1/P0-2)

P3 and P5 are **admission-time** properties: they quantify over the unique transition appended by an effective `AdmissionEvent`, never over every transition in an arbitrary post-tamper state. P6 is the only property that speaks about later corrupted states, and it now starts from a committed `(record, field)` query.

```
-- P3 (admission-time authorization necessity and reference integrity)
authReferenceIntegrity[e] :=
  one t: e.post.transitions - e.pre.transitions |
    e.post.transitions = e.pre.transitions + t
    and t = e.post.committedSource[e.targetRecord][e.targetField]
    and t.authorization = e.authorization
    and t.certificate   = e.certificate
    and sameCanonicalCertificate[e.authorization.certificate, e.certificate]
    and e.authorization.principal in PrincipalRegistry.authorized
    and t.value = e.authorization.authorizedValue
    and e.value = e.authorization.authorizedValue

-- P5 (transition integrity; exact-one-total + fact-source + both value anchors)
transitionIntegrity[e] :=
  exists! t in (e.post.transitions - e.pre.transitions).
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

The two value anchors together make P5 say: **the transition describes the actual committed update, and that update is the human-authorized value.** In the full model the two anchors agree because `admissionEffect` writes `e.value`, `C-auth-value` forces `e.value = e.authorization.authorizedValue`, and `C-transition` forces `t.value = e.authorization.authorizedValue`. In ABL_8 they disagree (`committedValue = Y`, `t.value = authorization.authorizedValue = X`, `X != Y`) and P5 fails on the committed-state anchor — the intended v0.4 counterexample.

`traceComplete` is defined in §13. **v0.6 P1 wording:** the formal trace predicate mirrors the producer/evidence/value/version/certificate/authorization binding checks, but the Alloy P6 corruption/minimality claim is restricted to source-anchor loss/replacement and source-version duplicates. Individual binding-corruption necessity is evaluated through executable conformance tests and is not claimed as a separate Alloy minimality result. P6 also deliberately does not claim detection of coherent rewrites or of any row-identity change that preserves all validated bindings.

---

## 13. Trace model (fact-to-source; v0.6 carries v0.5 P0-1/P0-2/P1)

The reverse trace is now anchored at a committed fact, not at an arbitrary transition:

```
CommittedFact(s, r, f) -> committedSource[s][r][f] -> Transition
    -> Authorization -> Certificate -> Evidence
```

Formal trace status:

```
enum TraceStatus { Complete, Incomplete }

pred traceComplete[s: State, r: Record, f: Field] {
  some s.committedValue[r][f]
  let src = s.committedSource[r][f]                     -- P0-2: the fact's source anchor
  {
    some t: Transition {
      t = src
      and t in s.transitions                            -- source transition still present
      and t.targetRecord = r
      and t.targetField  = f
      and t.value = s.committedValue[r][f]              -- transition matches committed fact

      -- v0.5 P0-1 source-version uniqueness. Exactly one transition in the
      -- tamperable set may carry (r, f, src.toVersion). This mirrors the
      -- concrete unique key (form_id, created_version, field_key). Historical
      -- transitions of the same field at OTHER toVersions remain valid.
      and (one u: s.transitions |
           u.targetRecord = r
           and u.targetField = f
           and u.toVersion = src.toVersion)

    and some a: Authorization, c: Certificate, e: Evidence |
        a = t.authorization
        and c = t.certificate
        and e = t.evidence
        and a in s.authorizations
        and c in s.certificates
        and e in s.evidence
        and sameCanonicalCertificate[a.certificate, c]  -- exact certId equality (P1-2)
        and sameEvidenceIdentity[c.candidate.evidence, e]
        and e.record = r
        and t.targetRecord = c.candidate.targetRecord
        and t.targetField  = c.candidate.targetField
        and t.value        = a.authorizedValue          -- authorized-value binding (P0-1)
        and t.producer     = c.candidate.producer
        and t.fromVersion  = c.candidate.expectedVersion
        and t.toVersion    = successor[t.fromVersion]
        and t.fromVersion.record = r
  }
}
```

`traceComplete[s,r,f]` no longer accepts a transition as its starting point: it starts from the committed `(record, field)` query and obtains the transition through `committedSource` (v0.4 P0-2). A deleted source transition makes `t in s.transitions` false, so verification is `Incomplete`.

**P0-1 duplicate insertion (v0.5).** The source-version uniqueness conjunct rejects the state where the valid `committedSource[r,f]` is still present but a tamperer added a second transition with the same `(r, f, toVersion)`. That duplicate makes `one u: s.transitions | u.targetRecord = r and u.targetField = f and u.toVersion = t.toVersion` false, so verification is `Incomplete`. The conjunct mirrors the concrete `UniqueConstraint(form_id, created_version, field_key)` on `fact_transitions`. A historical transition for the same field at an earlier or later `toVersion` does **not** trigger the uniqueness check: only the source version's slot must be unique.

**P0-2 unchanged-field behavior.** `admissionEffect` uses `setCommittedSource`, which changes only the target `(record, field)` slot. Suppose admission 1 updated `(r, f1)` and installed source `t1`, and admission 2 later updates `(r, f2)` and advances `currentVersion[r]`. Then `committedValue[r,f1] = v1` and `committedSource[r,f1] = t1` are preserved, while only `(r,f2)` gets the new source `t2`. `traceComplete[s,r,f1]` therefore still succeeds through the older `t1` even though the whole-record version has advanced.

**P0-1 trace verification.** `t.value` is verified against both `s.committedValue[r][f]` and `a.authorizedValue`. A transition whose value matches neither, or a source transition whose value was rebound away from the committed fact, is `Incomplete`.

**P1-2 certificate identity in the trace.** The transition↔authorization↔certificate hops use `sameCanonicalCertificate` — exact primitive `certId` equality — never modeled-tuple equality and never certificate-atom equality. The certificate↔evidence hop uses `sameEvidenceIdentity` (content + locator), matching `CandidateCertificate._content()`. The model does not require raw evidence-atom equality between `t.evidence` and `c.candidate.evidence`, because the concrete transition stores only `evidence_sha256` and `evidence_locator`, not a `file_id`. Duplicate evidence rows with equal `(content, locator)` are therefore not distinguishable certificate contexts, and a swap between such duplicates is not a detected corruption class; rows with different content or locator are detected. Two certificates with identical modeled components may have distinct primitive `certId`s; the trace checks the id, so unmodeled concrete hash inputs can never be collapsed.

**v0.6 P1 formal vs executable trace checks.** Alloy `Transition` atoms are immutable, so a SQL `UPDATE` of a transition field is represented by removing the source atom from `s.transitions` and inserting a different atom. Because `committedSource` is preserved by `tamperStep`, the formal P6 detection route for every rebound transition is **source-anchor loss/replacement** (the old source atom is no longer in `s.transitions`), plus **source-version duplicate detection** for an extra transition inserted alongside the source. The formal trace predicate mirrors these binding checks, but the Alloy P6 corruption/minimality claim is restricted to source-anchor loss/replacement and source-version duplicates. Individual binding-corruption necessity is evaluated through executable conformance tests and is not claimed as a separate Alloy minimality result. The same boundary appears in THREAT_MODEL.md §12 and PROPERTIES.md §1.

**P1-1 formal reachability boundary.** In the v0.6 formal model, only `State.transitions` is tamperable. The corruption classes for which P6 is **formally** claimed are therefore:

- deleting the fact's source transition (`committedSource[r,f] = t`, `t not in s.transitions`);
- replacing/rebinding the source transition (any transition-field corruption, modeled as removal of the old source atom and insertion of another atom, so the source anchor is lost);
- inserting a duplicate transition for `(r, f, committedSource[r][f].toVersion)`.

Missing authorization, certificate, or evidence artifacts are **not** formal TamperEvent classes because `tamperStep` preserves those sets. Concrete tests that delete decision/certificate/evidence rows remain valuable implementation-level robustness evidence and are labeled as such (THREAT_MODEL.md §13); the Alloy P6 submodel does not claim them.

**P2-2 narrowed claim (v0.5 carried).** `traceComplete` detects corruption **when the fact's source anchor is missing/replaced or when the source-version slot has a duplicate**. It does not claim to detect an arbitrary row-identity change, and it does not claim an Alloy minimality result for each individual field-binding check (v0.6 P1). In particular, a rebinding that replaces a referenced row with another row that still satisfies every validated hop and id check would not be detected by the formal source-anchor checks unless it also removes the source anchor or duplicates the source-version slot; such coherent rewrites are outside the locked threat model (lock §9: no arbitrary privileged DBA rewriting all data coherently). The paper may claim **trace soundness for source-anchor loss/replacement and source-version duplicates**, and nothing stronger.

---

## 14. Formal-to-concrete mapping

### 14.1 Mapping table

The abstraction relation `alpha : S_concrete -> S_formal` will be defined in the full paper. Draft mapping:

| Formal | Concrete Auto-Decte | Notes |
|---|---|---|
| `Evidence` / `EvidenceContent` / `EvidenceLocator` | `EvidenceFileRow` (file_id, form_id, sha256) + `CandidateCertificate.evidence_hash` / `evidence_locator` | row identity = `file_id` (persistence only); canonical evidence identity = `(sha256, evidence_locator)`, which is exactly what `CandidateCertificate._content()` freezes (P1-2) |
| `Record` | `form_id` (`FormRow`) | `target_record_id = form_id` |
| `Field` | `field_key` | appears in certificate, decision, transition |
| `Value` | frozen `value_payload` (canonical JSON) | `canonical_json()` makes equality deterministic |
| `Candidate` | candidate fields **embedded inside the persisted `CandidateCertificate` / `CandidateCertificateRow`** (v0.5 P2-2) | no independent governed candidate table; `C-cert-preexists` covers the embedded candidate |
| `Candidate.value` | machine-proposed `value_payload` | original proposal; never overwritten |
| `Authorization.authorizedValue` | planned `AuthorizationBindingRow.authorized_value_payload` / `authorized_value_hash` | human-authorized final value; not currently persisted on `HumanDecision` (P0-1) |
| `Certificate` | `CandidateCertificate` dataclass + `CandidateCertificateRow` | `certificate_id = sha256(canonical_json(_content()))` |
| `CertId` / `canonicalCertId` | `certificate_id` hex SHA-256 (primitive in the formal model) | `verify_content_address()` re-derives concrete-side only; formal model asserts only modeled-difference ⇒ different id (v0.4 P1-2) |
| `Authorization` | `HumanDecision` **plus the planned `AuthorizationBinding` artifact** (§14.2) | not yet implemented; see v0.2 P0-2 |
| `Authorization.certificate` | `AuthorizationBindingRow.certificate_id` (planned) | decision-time immutable binding to the reviewed machine certificate |
| `Principal` | `reviewer_id` | attributable and registered |
| `Producer` | `producer_id` + `producer_version` | carried by certificate and transition |
| `Version` | `RecordVersion.version` + `FormRow.current_record_version` | whole-record snapshot version |
| `State.committedValue` | latest `RecordVersionRow.values : dict[field_key, value]` | one value per (record, field) |
| `State.committedSource` | **planned** immutable `RecordVersionRow.fact_sources : dict[field_key -> transition_id]`, copied forward from the previous snapshot and overwritten for each field updated in this admission | the persisted source id is independent of `fact_transitions`; transition deletion leaves it unresolved (§14.3). NOT derivable as `MAX(created_version) among remaining transitions` (v0.5 P0-2) |
| `State.currentVersion` | `FormRow.current_record_version` | one whole-record counter |
| `Transition.value` | `RecordVersionRow.values[t.targetField]` for the version identified by `toVersion` | human-authorized final value |
| `Transition.fromVersion/toVersion` | `FactTransition.created_version - 1 / created_version`, `record_version_id`, `RecordVersion.version` | whole-record endpoints |
| `AdmissionEvent` | `ReviewForms.confirm()` | the only fact-writing path; atomic review+commit |
| `rejectedAdmission` | `AuthorityRejectionError` / `ConcurrentReviewError` before any write, or CAS returning False | `sameState(pre,post)`; no partial write |
| `C-fresh` | `expected_version == form.current_record_version` precheck + `UPDATE ... WHERE current_record_version = expected` CAS first write | OCC/CAS reused, not novel |
| `C-auth-value` | planned binding value payload/hash checked against `values[field_key]` before transition append | not yet a separate column |
| `C-transition` | per-field transition appended in the same transaction as RecordVersion/Decision/Certificate/Audit | all-or-nothing |
| `TamperEvent` (formal) | direct SQL mutation of `fact_transitions` rows only | formal transition-only tamper (v0.4 P1-1) |
| certificate/decision/evidence-row SQL faults (concrete-only) | direct SQL mutation of `candidate_certificates` / `human_decisions` / evidence rows in tests | implementation-level robustness evidence **outside** the Alloy P6 submodel (v0.4 P1-1) |
| `traceComplete[s,r,f]` | fact-query reconstruction for `(form_id, field_key)`: `fact_sources[field_key]` → transition → decision → certificate → evidence | starts from the committed fact via the persisted source id; additionally enforces `(form_id, created_version, field_key)` uniqueness at the source version (v0.5 P0-1) |
| `MachineEvent` | OCR/HOG-SVM, OMR, AI adapter, retrieval adapter | produce candidates/certificates/evidence only; never authorizations; `MachineOnlyTrace => CommittedStateUnchanged` |

### 14.2 Required concrete change: AuthorizationBinding with authorized value (planned only)

The abstract `Authorization.certificate : one Certificate` and `Authorization.authorizedValue : one Value` have no exact current concrete columns. The required conformance change is:

```
-- planned, NOT implemented during the locked formal phase
@dataclass(frozen=True, slots=True)
class AuthorizationBinding:
    binding_id: str
    decision_id: str
    certificate_id: str
    authorized_value_payload: str | None = None   # canonical JSON of the final value
    authorized_value_hash: str | None = None      # SHA-256 alternative / cross-check
    bound_at: datetime

class AuthorizationBindingRow(Base):
    __tablename__ = "authorization_bindings"
    binding_id:             str      (PK)
    decision_id:            str      (FK human_decisions.decision_id, UNIQUE, NOT NULL)
    certificate_id:         str      (FK candidate_certificates.certificate_id, NOT NULL)
    authorized_value_payload: str    (NOT NULL; canonical JSON of the final value)
    authorized_value_hash:   str     (NOT NULL; SHA-256 of the payload, for compact checks)
    bound_at:               datetime (NOT NULL)
```

Persistence rule: `AuthorizationBindingRow` is inserted **at authorization time**, in the same transaction as the decision and before the transition append, so that `Authorization.certificate` and `Authorization.authorizedValue` are real decision-time artifacts and not a reconstruction from `FactTransition` or from a later derived certificate. Verification then becomes:

```
decision -> AuthorizationBindingRow -> certificate_id
decision -> AuthorizationBindingRow -> authorized_value_payload
transition.decision_id = decision.decision_id
transition.certificate_id = AuthorizationBindingRow.certificate_id
committed values[field_key] == AuthorizationBindingRow.authorized_value_payload
```

**Correction path conformance note.** The current `ReviewForms.confirm()` implements human correction by deriving a new `MANUAL_ENTRY` certificate at confirm time and putting the machine certificate only in `lineage_parent_ids`. That concrete path does **not** yet match the v0.4 formal reading, in which `e.certificate` is the pre-existing machine certificate, `Candidate` is machine-derived only, and the correction is carried by `Authorization.authorizedValue` (v0.4 P2-3). After the gate PASS, conformance must either (a) keep the machine certificate as the reviewed/bound certificate and persist the corrected value in `AuthorizationBindingRow`, with `lineage_parent_ids` retained as provenance, or (b) surface a formal `CertificateDerivationEvent` as an explicit pre-admission machine step. Until that conformance work is done, the correction path is reported as **planned, not yet literal**.

The current `(decision_id, certificate_id)` pair on `FactTransition` remains useful for trace checks but is **not** the formal `Authorization.certificate` relation. `TransitionPolicy.authorize()` must receive the binding (or return it) so the in-memory path agrees with the persisted path. No code or schema is changed in this phase; the change is documented as a conformance prerequisite.

### 14.3 Concrete source anchor: locked planned design (v0.5 P0-2, preferred A)

The v0.4 derivation `committedSource(form, field) = remaining FactTransition with MAX(created_version)` is **withdrawn**. It is unstable under transition deletion: deleting the latest transition would silently promote an older transition to “source”, while the formal `committedSource` must keep its identity when `TamperEvent` removes a transition.

**Selected solution: A — planned persisted source binding.** After Gate PASS, implement an immutable per-field source map embedded in the immutable `RecordVersion` snapshot metadata:

```
-- planned, NOT implemented during the locked formal phase
RecordVersionRow.fact_sources:
    type   : JSON dict[field_key -> source_transition_id]
    rule   : NOT NULL on every RecordVersionRow created by AdmissionEvent
    content: full map for the whole record at that snapshot:
             fact_sources = previous_snapshot.fact_sources.copy()
             for each transition t appended by this admission:
                 fact_sources[t.field_key] = t.transition_id
    write  : same DB transaction as RecordVersionRow.values,
             FormRow.current_record_version CAS, and FactTransitionRow inserts
```

Concrete mapping after implementation:

```
committedSource(form_id, field_key)
  = latest RecordVersionRow.fact_sources[field_key]
    where latest = RecordVersionRow.version
                   == FormRow.current_record_version
```

Consequences:

1. **Deletion stability.** If `fact_transitions` later loses the source row, `fact_sources[field_key]` still stores the same `source_transition_id`. Resolution by id fails, so P6 returns `Incomplete`; no older transition is promoted, because older snapshots' `fact_sources` are not consulted.
2. **Source independence.** `fact_sources` lives in immutable `RecordVersion` metadata, not in the tamperable `fact_transitions` set; formal `TamperEvent` does not change `committedSource`, matching the planned concrete anchor.
3. **Unchanged fields.** Copying the full map forward means `(form, f1)` keeps its older `source_transition_id` when `(form, f2)` later advances the whole-record version — the exact v0.4 P0-2 behavior.
4. **Source-version uniqueness.** `fact_transitions` retains `UniqueConstraint(form_id, created_version, field_key)`, mirroring the new formal uniqueness conjunct (`one transition per (r, f, src.toVersion)`).

**Why B (independent derivation from current RecordVersion history) is not sufficient.** Current `RecordVersionRow` stores only full `values` snapshots. Comparing consecutive snapshots per field cannot distinguish a same-value re-admission (`X -> X` at a newer version, which still appends a transition and must update `committedSource`), so value-diff derivation is not exact. Therefore v0.6 does not claim B and does not use `MAX(created_version) among remaining transitions`.

**Current conformance status (reported honestly).** The current repository has **no** `fact_sources` column and therefore cannot yet anchor `committedSource` independently of `fact_transitions`. Until the planned `RecordVersionRow.fact_sources` change is implemented after Gate PASS, P6's executable conformance is **conditional on that conformance prerequisite**. The formal model remains the source of truth; the paper must not claim that the current Python code already implements the v0.6 P6 claim. No code or schema is changed during this locked formal phase.

**Initial/bootstrapped facts.** A field whose value existed before any transition has no source id in the empty-init abstraction. Such facts remain outside the current formal fact domain; if the later Alloy instantiation covers pre-existing records, trusted initialization must materialize bootstrap source ids in the same immutable metadata.

---

## 15. Scope and assumptions of the formal model

**In scope (lock §9):** wrong machine prediction; wrong LLM suggestion; irrelevant retrieval; direct machine fact-write attempt; S1–S5 substitutions (with S4 split S4a/S4b and S2 split S2a/S2b); unrecorded final value (S8); conjured certificate/evidence at admission (S9/S10); sequentialized concurrent/interleaved confirmation; duplicate evidence; **transition-only tampering**: source-transition deletion, source-anchor replacement/rebinding (any transition field), and source-version duplicate insertion. The formal trace predicate mirrors the detailed producer/evidence/value/version/certificate/authorization binding-corruption checks, but the Alloy P6 corruption/minimality claim is restricted to source-anchor loss/replacement and source-version duplicates; individual binding-corruption necessity is evaluated through executable conformance tests and is not claimed as a separate Alloy minimality result (v0.6 P1).

**Formal threat boundary (v0.4 P1-1):** the formal `TamperEvent` mutates only `State.transitions`. Certificate-row, decision-row, and evidence-row corruption/deletion are concrete fault-benchmark classes only; they are labeled implementation-level robustness evidence outside the Alloy P6 submodel and are **not** claimed as formally reachable P6 classes.

**Out of scope (lock §9):** OS/root compromise; arbitrary privileged DBA rewriting all data coherently; cryptographic hash collision; compromised trusted runtime; compromised DB engine; compromised dependency supply chain; forged real-world human identity; correctness of the human reviewer; confidentiality; availability; arbitrary physical destruction; general network security; universal Byzantine behavior.

**Cleanup — two reviewer failures are distinct:**

| Failure | Formal mechanism | System behavior |
|---|---|---|
| Wrong value approved by an **authenticated** reviewer | Same principal, same certificate binding, `authorizedValue` is the wrong value, `C-auth-value` and all context conjuncts hold | May commit a wrong but attributable, bound, fresh, traceable fact; this is reviewer correctness and is out of epistemic scope |
| A value the authorization **never carried** | `e.value != e.authorization.authorizedValue` (or the attempted authorization has no value binding) | Blocked by `C-auth-value` (P0-1) |
| **Unauthorized / unregistered** principal | `e.authorization.principal` is not in `PrincipalRegistry.authorized` (or principal is absent) | Blocked by `C-principal`; the system guarantees the attempted authorization references a registered authorized principal, not that the referenced human is always right |

**P0-3 identity scope (v0.5 P2-1).** A missing, unregistered, or unauthorized principal reference is rejectable via `C-principal`. This is formally called **unauthorized/unregistered principal**, not “forged identity”. Real-world impersonation of a valid reviewer identity is out of scope, exactly as forged real-world human identity is out of scope in lock §9.

**Modeling note on time:** the locked core context is `(record, field, evidence, expectedVersion)`; wall-clock age is not promoted to a core relation. Auto-Decte's `MAX_CERTIFICATE_AGE` remains an implementation-level freshness guard and is reported as engineering detail, not as formal novelty.

**P1 vs P4 scope:** P1 covers certificate-context binding, including version binding (`C-version`; A4a). P4 covers freshness against the **current record version** (`C-fresh`; A4b). They are separate mechanisms and separate experiments.

---

## 16. Novelty wording guardrails

Allowed:

> The contribution is not candidate/fact separation alone, but a formally analyzable admission contract in which candidate identity and authorization are context-bound and non-transferable across record, field, evidence, version, and certificate references; the appended transition describes the actual committed update; the committed value is the authorization's authorized final value; and every reachable state satisfies the structural `stateInvariant`, together with executable conformance evidence for individual binding-corruption checks.

Allowed P5/P6 wording:

> Every reachable state satisfies `stateInvariant` (current-version record ownership, committed-value/committed-source domain alignment, source target record/field), and the invariant intentionally neither requires the source transition to remain present nor equates its value with the committed value. P5 holds at admission time for the unique appended transition, which equals the fact's `committedSource` and whose value equals both the authorized value and the post-state committed value. Trace verification starts from a committed `(record, field)` fact and reports `Incomplete` when the fact's source anchor is missing/replaced or when the source-version slot has a duplicate transition. The formal trace predicate mirrors the detailed binding checks, but Alloy-level P6 claims only those source-anchor outcomes; individual binding-corruption necessity is evaluated through executable conformance tests and is not claimed as a separate Alloy minimality result.

Not allowed: first candidate–fact separation; first human-authorized AI database; first provenance-aware AI system; new CAS protocol; formal proof of all system security; formally verified Python system; universal security claims; OCR novelty; production deployment effectiveness.

Supporting-only items: direct-write exclusion; version freshness/CAS; correction-preserving lineage; reverse-trace soundness; append-only history; human attribution; reproducibility; content addressing.

---

## 17. What is deliberately deferred to full Alloy implementation

- Compilation of the bounded `seq State` / `seq Event` trace encoding; `util/ordering[State]` is **not** used (P1-6). The v0.6 `orderedTrace` clause `all s: tr.states.elems | stateInvariant[s]` is part of that compilation target and must not be dropped.
- Exact Int/ordered-`Version` choices (`Version.number` vs ordered `Version` atoms). `certAddress` is gone from the formal model: `CertId` is primitive (v0.4 P1-2).
- Exact scope sizes and symmetry-breaking for S5 same-value cases, for the primitive-`CertId` one-way fact, and for Accept/Correction witnesses.
- Full `PrincipalRegistry.authorized` population and machine-event artifact-generation clauses.
- `traceComplete[s,r,f]` implementation over `committedSource` and its scope; source-transition deletion/replacement witnesses and source-version duplicate witnesses (v0.5 P0-1).
- Concrete conformance prerequisites to implement only after Gate PASS: `AuthorizationBindingRow` (§14.2) and immutable `RecordVersionRow.fact_sources` (§14.3).
- Compilation, `run`/`check` execution, and the ablation harness (`ABL_1`, `ABL_2a`, `ABL_2b`, `ABL_3`, `ABL_4a`, `ABL_4b`, `ABL_5`, `ABL_6`, `ABL_7`, `ABL_8`, `ABL_9`, `ABL_10`).

No `.als` file may be written, and no Alloy checks may be reported, until the GPT Semantic Gate passes this draft together with `THREAT_MODEL.md`, `PROPERTIES.md`, `RED_TEAM_NOTES.md`, and `SEMANTIC_REWORK_CHANGELOG.md`.

---

## 18. Locked summary restated for the implementation phase

- What we study: `AI CandidateUpdate -> CommittedFact` under an explicit admission contract.
- What is central: **Certificate-Bound Non-Substitutability**.
- What it means: authorization or candidate validity created for one exact `(record, field, evidence, version, certificate)` context cannot be transferred to another, and the committed value is the exact value the authorization authorized.
- What is supporting: stale-safe commit; transition integrity; trace soundness; correction lineage; direct-write exclusion.
- Default venue: JSS first.
- Research status: **RESEARCH LOCKED**.
