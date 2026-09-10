# r27 standard-practice baseline: ordinary approval/audit log

This directory answers the P3/JSS review question: *does a conventional
approval/audit log already provide the paper's claimed increment?*

It contains a deliberately generous baseline policy, `approval_log`, that:

- persists an ordinary approval row (`approval_id`, record, expected version,
  principal, approved values) and a complete before/after audit log;
- validates candidate record/field context, approved-value equality,
  changed-field domain, and version CAS;
- can reconstruct every field's source by diffing the complete audit history;
- but **does not persist the exact reviewed candidate identity** and **does not
  persist an explicit per-field source map**.

It is therefore a fair conventional comparator, not a weakened straw man.

## Files

- `run_baseline.py` — self-contained SQLite baseline and case runner.
- `run-2026-09-10/db/*.db` — one SQLite database per case.
- `run-2026-09-10/runs.json` — complete case records (pre/post SQL state,
  requested actions, observations).
- `run-2026-09-10/summary.json` — derived comparison with the candidate-bound
  reference outcomes from `evidence/checklist-runs-verified-2026-09-09/`.

## Result

The ordinary approval/audit log **agrees with the candidate-bound policy on 7
of the 8 single-history cases**. It diverges only where the exact reviewed
candidate matters:

| Case | Ordinary approval/audit log | Candidate-bound policy |
|---|---|---|
| legal correction | accepts, complete successor | accepts, complete successor |
| equal-valued substitution | **accepts q100b after approving q100a** | rejects `candidate_binding` |
| cross-record candidate | rejects | rejects |
| stale expected version | rejects | rejects |
| wrong submitted value | rejects | rejects |
| partial approved batch | rejects | rejects |
| injected failure after writes | rolls back every table | rolls back every table |
| two-step copy-forward | accepts; sources reconstructable from audit | accepts; sources stored explicitly |
| paired reviewed-candidate histories | **states identical for q100a vs q101** | states differ in `approvals` |

Capability comparison:

| Capability | Ordinary approval/audit log | Candidate-bound policy |
|---|---|---|
| value-bound approval | yes | yes |
| complete before/after audit | yes | yes |
| immutable candidates | yes | yes |
| version CAS | yes | yes |
| exact reviewed-candidate binding | **no** | yes |
| unique proposal/authorized-value attribution | **no** (join on record/field is ambiguous) | yes |
| per-field source reconstruction | yes, from audit diff | yes, stored map plus audit |
| distinguish paired equal-valued reviewed candidates | **no** | yes |

## Interpretation

The baseline shows that the paper's demonstrated increment is narrower than a
general "audit versus no audit" claim: a conventional complete audit log already
supports value-bound approval, rollback, CAS, and per-field source
reconstruction. The remaining increment is **exact reviewed-candidate binding
and the resulting unique proposal/authorized-value attribution**. This is
consistent with the paper's own Supplement S3 disclosure. The baseline is not a
full comparison against event-sourcing/CQRS, temporal/bitemporal tables, or
four-eyes approval systems, and it does not establish that candidate binding is
always necessary; it shows exactly where the conventional policy diverges on the
declared cases.

## Reproduction

```bash
python run_baseline.py --out-dir <new-output-directory-outside-package>
```

The runner refuses to overwrite an existing output directory. It requires only
the Python standard library.

## Boundary

This is a deterministic design comparison, not a statistical or performance
claim. The case count (9) is the declared executable example count, not a
sample. The baseline is a minimal ordinary approval/audit log, not a deployed
commercial approval system.
