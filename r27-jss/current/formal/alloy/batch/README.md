# Auto-Decte Batch Alloy Package

## Status

Option A was approved on 2026-08-23. This directory contains the conservative batch extension required to map one concrete multi-field confirmation to one atomic formal version transition.

The active development freeze is named by `ACTIVE_FREEZE.txt`. It is not yet the final paper evidence freeze; R2 concrete projection and the later source/evidence freeze may require a fresh rerun.

## Historical evidence is immutable

The package does not replace or rewrite the historical singleton models:

| File | Locked SHA-256 |
|---|---|
| `../auto_decte.als` | `3e42226a642e458170b85671a56ff8438fdc7c8dba72b970c53822867e7f9d19` |
| `../auto_decte_s2.als` | `44e54ba1ba81358308b1cbd1fe7d4b38af79b05ea97e1487a48ed9e77781c4e9` |

`verify_batch_package.ps1` fails if either historical model changes.

## Model boundary

- `BatchAdmissionEvent.items` is nonempty.
- Under `Full`, all items share one target record, registered principal, current pre-version, and one successor post-version.
- Item fields are unique. Each item has one certificate, authorization, evidence object, attempted value, and transition.
- `transitionBijection` requires exactly one appended transition per item and no extra appended transition.
- All item effects occur simultaneously inside one record/version envelope; every non-target record is fully framed.
- Initial certificate-era admission covers the record's declared authoritative field set. Later admissions may cover a subset. Formal same-value admission remains legal, preserving the historical singleton semantics; the planned concrete no-op rejection is an explicit strict refinement.
- Candidate membership in `State.candidates` remains auxiliary. The mapped historical singleton contract requires the attempted certificate(s) and target evidence to preexist, not a separate candidate-state conjunct.

The permissive base effect keeps attempted item fields, records, evidence, versions, certificates, authorization values, principals, and transitions independently selectable. `Full` supplies the validity constraints. This permits effective malformed batches under one-conjunct ablations rather than defining bad states away globally.

## Non-circular checks

`StateInvariantPreserved` assumes only a structurally valid pre-state plus the base effect and `Full` contract, then checks the post-state invariant. It does not assume a post-state invariant or a globally well-formed trace.

Full-contract P0鈥揚5 checks are regression/consistency checks. The stronger scientific evidence is the combination of:

- reachable multi-item Accept, Correction, mixed, same-value, initial-snapshot, and singleton witnesses;
- eleven effective paired ablation witnesses, each with one corrupt item and one `fullItemOk` item;
- `FullRejectsAblatedAttempt` and `FullNoPartialItemEffects`;
- the explicit one-item historical-contract mapping;
- legal-prefix P6 attack witnesses; and
- the r27 conditional positive assertion `LegalAdmissionTraceCompleteUnderWellFormedPre` plus its mutation control under `evidence/r27-trace-mutation/` (34 commands per profile, 68 total). The assertion is UNSAT with the production model and SAT when the post-state certificate-binding conjunct is removed; its explicit preconditions match the predecessor trace checks, unique (form_id, created_version, field_key) transitions, and transactional compare-and-swap checks that the concrete service enforces.

## P6 boundary

The formal tamper step freezes `committedSource`. Each P6 witness begins with a legal `Full` admission and then performs a non-stuttering transition-set change:

1. remove the anchored transition;
2. remove it and insert a different replacement atom; or
3. keep it and insert a same-record/field/version duplicate.

Persisted `fact_sources` pointer rebinding remains a concrete-only corruption family.

## Reproduction

From `r27-jss/current/` in PowerShell:

```powershell
& 'formal/alloy/batch/run_batch_alloy.ps1' -FreezeId '<new-freeze-id>'
& 'formal/alloy/batch/verify_batch_package.ps1' -RequireRawResults
```

The runner refuses to overwrite an existing freeze. It records per-command stdout, Alloy receipts, SAT instances, a typed command summary, runtime/model/manifest hashes, and an artifact hash list. The active pointer is updated only when every manifest expectation passes.

The checked-in Alloy jar is `tools/alloy-6.2.0.jar`. This run used the project-local Temurin 21 JRE described in the active freeze metadata.

## Files

- `auto_decte_batch.als`: definitions and S1 command catalog.
- `auto_decte_batch_s2.als`: complete S2 catalog at larger bounds.
- `command_manifest.tsv`: expected result and command class for both profiles.
- `run_batch_alloy.ps1`: no-overwrite freeze runner.
- `verify_batch_package.ps1`: structure, historical-hash, active-source-hash, result-count, and artifact-hash verifier.
- `raw-results/<freeze-id>/`: immutable-by-convention development freezes.
- `RESULTS.md`: bounded result interpretation.
