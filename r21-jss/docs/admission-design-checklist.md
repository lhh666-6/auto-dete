# Admission design checklist

A reusable inspection worksheet derived from manuscript C1–C2. It is a way to apply the declared contract and observation model, not a fifth contribution, an independently validated assessment instrument, or proof that an implementation is correct. No worksheet row has been completed on behalf of another system.

## Before using the checklist

Identify a system in which a persisted machine candidate can prompt a human-authorized value and an atomic authoritative record successor. Declare the target record, field domain, legal no-op behavior, initial-state rules, and trusted admission interface. Record authentication and principal-policy assumptions separately. A different system may use a key, certificate, digest, epoch, or another representation; map observable relations rather than matching table names.

For every row, run a legal positive control as well as the failure probe. Inspect persisted values, authorization bindings, versions, sources and commit histories through an independent reader where possible. A plausible final value or an error message alone is not sufficient evidence. Use isolated test fixtures for faults and corruption, never a production database.

## Five inspection cards

| Class | Information to retain | Enforcement time | Failure family and test | Expected evidence |
|---|---|---|---|---|
| D_C — candidate/context | Exact persisted candidate identity; target record/field; evidence identity and producer; authorization target | Bind at review; reload and check inside admission | Candidate substitution: submit an equal-valued candidate from a different context while keeping the legal control valid | Substitute is rejected without authority writes; the accepted control resolves to the exact original candidate, not value equality |
| D_V — value roles | Proposal x_c, authorized x_a, committed value, and their distinct roles; original candidate unchanged | Record human decision; enforce committed = authorized at admission; verify attribution in persisted reconstruction | Correction erasure/false attribution: propose 100 and authorize 101; inspect a test reconstruction with machine/human roles erased or mislabeled | Legal Correction stores 101 while retaining candidate 100 and its identity; the independent comparison detects erased or false role attribution. Do not expect a legitimate Correction to be rejected |
| D_F — freshness | Expected and transactionally observed predecessor discriminator; concurrency protection | Inside admission, with the comparison protected through atomic update/commit | Stale replay: capture authorization at v, commit another legal successor, then replay. Also race two admissions from the same predecessor | Replay leaves the already-updated state unchanged; no more than one contender commits from that predecessor. Compare against the state immediately before replay, not the older v snapshot |
| D_B — batch/successor | Declared admitted change domain, actual effect domain, commit grouping, successor count, full record frame | Validate planned effects before commit; preserve atomicity during persistence | Fragmentation: change two fields and inject failure between writes; compare with a legal atomic control | All or none of that admission persists; no partial state or two-successor replacement of the declared one-successor admission. Inspect intermediate visibility and commit grouping as well as final values |
| D_S — field sources | Exactly one resolving source per successor field; matching field/value; exact prior source for unchanged fields | Validate successor construction before commit and check persisted sources on trace | Source ambiguity: retain values but remove/duplicate a source, attach a wrong field/value source, or replace an unchanged field's prior source | Invalid construction is rejected if injected before commit; post-persistence corruption is diagnosed as incomplete/ambiguous rather than silently repaired. Correct values alone must not produce a complete trace |

## Interpretation boundaries

- D_B concerns the admitted change set. In the reference service, a mixed submission can include unchanged review items: those fields retain exact prior sources and do not receive new transitions. Initial full-domain and subsequent no-op rules must be stated for the target system.
- D_S is the local source-relation distinction. Complete P6 tracing additionally validates authorization, candidate, evidence, producer and version relations. Passing the local check does not establish the full chain or factual truth.
- The operational probes may exercise more than one implementation check. They are not themselves the mathematical one-coordinate projections used in Proposition 1; the separate executable paired-history checker establishes that construction.
- For corruption probes, record whether a schema constraint prevents constructing the faulty fixture. If so, record that prevention evidence and do not invent a downstream trace result.
- A five-row pass does not cover compromised hosts, external authentication, every schedule, or revocation linearizability. The reference policy check is commit-entry revalidation; a later revocation does not cancel an already checked in-flight admission.

## Fillable record (copy once per class)

- Class:
- System/revision and environment:
- Target record/field domain and relevant assumptions:
- Persisted representation (object/field or evidence path):
- Enforcement location and transaction boundary:
- Legal-control setup and expected outcome:
- Failure/corruption setup and expected outcome:
- Actual outcome:
- Persisted evidence/receipt location:
- Status: NOT RUN / SUPPORTED FOR THIS PROBE / VIOLATED / BLOCKED BY PRECONDITION
- Reviewer, date, and remaining uncertainty:

All fields are intentionally blank. SUPPORTED FOR THIS PROBE requires both the legal control and the specified probe evidence; it is not an overall system certification. BLOCKED BY PRECONDITION requires an explanation and the constraint/precondition evidence.

## Existing source anchors

These are source anchors for the derived checklist, not new evaluation results:

- `paper/sections/03-problem-contract.tex`: observation functions, five paired histories, batch and source rules, P0–P6, and authorization timing.
- `paper/sections/05-transactional-realization.tex`: transaction, CAS, copy-forward and trace implementation description.
- `source/formal/observation_witnesses.py` and `evidence/formal/observation-witness-report.json`: executable construction and derived observations/outcomes.
- `source/formal/tests/test_observation_witnesses.py`: paired-projection, connected-commit and source-resolution regression tests.
- `paper/tables/generated/validation_evidence.tex`: previously frozen implementation/test counts. Those counts do not measure this worksheet's cross-system usability.
