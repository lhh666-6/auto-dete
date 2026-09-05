# Batch Abstraction Mapping

`alpha : ConcretePersistedPrePost -> BatchAlloyInstance`

The canonical formal target is
`formal/alloy/batch/auto_decte_batch.als`. The earlier singleton model is
historical evidence; its one-item correspondence is checked inside the batch
package and is not the direct target of a multi-field Python confirmation.

## Persisted relation mapping

| Concrete artifact | Batch Alloy artifact | Executable mapping |
|---|---|---|
| `FormRow.form_id` | `Record` | One selected form becomes the event target record. The selected declared field domain becomes `Record.authoritativeFields`. R3 will make that domain an adapter-derived persisted input rather than a test argument. |
| `EvidenceFileRow` plus certificate locator | `Evidence` | `form_id -> record`, `sha256 -> content`, and the persisted certificate locator -> `locator`. Row IDs name projection atoms but are not formal evidence identity. R4 must replace the current locator with the canonical persisted `EvidenceIdentity`. |
| `CandidateCertificateRow` | `Candidate` + `Certificate` + primitive `CertId` | `target_record_id`, `field_key`, evidence row, `expected_fact_version`, canonical `value_payload`, producer pair, and `certificate_id` map directly. Concrete content addressing is a one-way realization of primitive formal identity, not an injectivity proof. |
| `HumanDecisionRow` + `AuthorizationBindingRow` | one `Authorization` | The decision supplies `reviewer_id -> principal`; the binding supplies the exact certificate and independently frozen `authorized_value_payload`. One pair is projected per admitted item. |
| one `FactTransitionRow` created at the successor | one `AdmissionItem.transition` | Record, field, evidence, from/to version, committed value, producer, certificate, and authorization are constrained from persisted rows. Each current transition yields exactly one item. |
| `RecordVersionRow.values` | `State.committedValue` | Canonical JSON equality classes become Alloy `Value` atoms. A complete snapshot is fixed for both pre and post. |
| `RecordVersionRow.fact_sources` | `State.committedSource` | Each field points to its exact persisted transition atom. Unchanged fields must retain the same atom across a delta successor. |
| form/current version plus record-version chain | `State.currentVersion` + `Version.succ` | Concrete integer versions map to one exact linear Alloy chain for the selected record. |
| persisted certificate/evidence/binding/transition identity sets | the corresponding `State` sets | Candidate certificates and evidence preexist review. Current bindings and transitions appear only in the committed post-state. Historical members remain present. Candidate state is auxiliary and fixed empty. |
| one `ReviewForms.confirm` + repository CAS unit | one `BatchAdmissionEvent` | The outer event shares one record, principal, pre-version, successor, and atomic pre/post. Its nonempty item set is the set of transitions created at that successor. |
| rejected `confirm` | `rejectedAdmission` | Canonical before/after snapshots must be byte-equivalent across every authority identity sequence and committed snapshot. Attempt-only authorization/transition atoms are outside both states; the generated wrapper requires a stutter and a failing Full contract. |
| machine candidate generation | `MachineEvent` | Recognition persists candidate authority inputs but is not a fact-writing event. R6 will enforce the narrow runtime capability boundary. |
| direct SQL fault injection in tests | formal tamper only where boundaries coincide | Formal P6 covers transition-set anchor loss/replacement/duplicate with a frozen source pointer. Concrete pointer rebinding remains a separate concrete-only family. |

## Executable R2 oracle

`tests/conformance/alloy_projection.py` reads repository query results and
writes a canonical `projection.json`. It then generates an exact Alloy wrapper
that opens the canonical batch model. Committed projections ask for
`legalAdmission[ConcreteAdmission, Full]`; rejected projections require
`fullAdmissionStep`, `rejectedAdmission`, and `not batchContract[..., Full]`.

The active raw freeze contains these positive cases:

- singleton Accept and singleton Correction;
- multi-field all-Accept, all-Correction, and mixed batches;
- a three-field initial snapshot;
- a later one-field delta with unchanged-source copy-forward;
- a stale rejection and a one-invalid-item whole-batch rejection.

Twenty independent mapping mutants alter field, evidence, version, freshness,
authorization certificate/principal/value, transition bijection and bindings,
preexisting authority membership, committed value/source effects, or initial
snapshot coverage. Every mutant is UNSAT. The rejection projection separately
fails before Alloy if an expected rejection changes any captured authority
relation.

## Refinement boundary

The formal batch relation permits a legal same-value admission because it is a
conservative extension of the locked singleton model. The intended concrete
contract rejects post-initial no-op confirmation, so concrete post-initial
events form a strict value-changing subset of formal legal events. R2 is a
bounded executable refinement check for selected traces, not a proof that all
possible Python executions refine the model.

R2 also does not close known production gaps. R3–R8 still must derive the full
declared field domain at the central transaction boundary, validate exact
changed-field/item equality, rebuild canonical persisted evidence identity,
validate full source history, narrow capabilities, and recheck principal
authorization. Until those repairs pass, the projection freeze is mapping
evidence rather than a production-conformance verdict.

## Explicit scope statements

- Manual entry remains outside the AI-derived candidate conformance claim.
- SQLite's unique `(form_id, created_version, field_key)` constraint prevents a
  true duplicate source-version row in trusted storage; the formal model still
  analyzes that state.
- No claim covers a root/DBA rewriting every trusted authority relation,
  process isolation, authentication, arbitrary corruption, or unbounded proof.
