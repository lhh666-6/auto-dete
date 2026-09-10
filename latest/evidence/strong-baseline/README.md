# Strong-baseline evidence: strengthened transactional value-audit control

This directory answers the question *does a stronger conventional transactional
audit baseline already provide the candidate-level authorization relation?*

It is versioned separately from the frozen standard-practice baseline in
`evidence/r27-standard-practice-baseline/` and does not replace or modify it.

## Files

- `manifest.json` — schema, anchor commit, SHA-256 pins of every frozen artifact
  this run read, policy inventory, and counts.
- `raw/<stamp>/b1_cases/` — the nine declared cases under the strengthened
  `transactional_value_audit` policy (B1): one SQLite database per case plus
  `runs.json` and `summary.json`.
- `raw/<stamp>/b2_cases/`, `raw/<stamp>/b2plus_cases/` — the same nine cases
  under the optional enriched review-context and used-candidate-aware variants.
- `raw/<stamp>/full_cases/` — the same nine cases under the candidate-bound
  policy, executed in the same harness, used as the in-process comparator.
- `raw/<stamp>/e1/` — the identity-isolation control (E1). Two histories per
  policy share one fixed candidate pool and differ only in which equal-valued
  candidate admission selects.
- `normalized/` — machine-readable results, parity, E1 summary, the per-field
  candidate-pair difference table, the section 46 self-audit, and the
  formal-to-concrete witness mapping.
- `paper/` — derived tables: parity, E1 matrix, the three-column capability
  table, the per-field judgement, the evidence anchors, and the completion
  checklist.

## Reproducing

```bash
AUTODECTE_REPO=<path-to-repository> \
python code/strong-baseline/run_strong_baseline.py \
       --out <fresh-directory> --stamp 2026-09-10
```

The runner refuses to overwrite an existing output directory, verifies the
SHA-256 of every frozen artifact it reads, and reads the repository without
modifying it.

## Result

The strengthened control preserves immutable candidates, complete before/after
audits, value-bound approvals, and compare-and-swap, and adds schema versioning,
a principal registry, persisted evidence hashes and locators, a content-addressed
candidate identity, an explicit per-field source map checked against the audit
reconstruction, an approval-consumption guard, an admission decision log that
records no candidate identity, transaction grouping, and a tamper-evident audit
chain. Its authorization remains a function of principal, record, expected
version, authorized values, and scope only: no authority relation names a
persisted candidate.

On the nine declared cases it reproduces the frozen control's outcomes case for
case, including the equal-valued candidate-substitution divergence. In the
identity-isolation control the two histories remain indistinguishable under the
declared authority-relevant projection, and a diagnostic reconstruction reports
several candidates compatible with the recorded authorization, whereas
candidate-bound admission retains an explicit authorization-to-certificate
relation.

The optional enriched review-context variant separates the two candidates
whenever their recorded proposal, producer, or evidence observations differ. It
is reported as a boundary result rather than as an alternative standard practice.

## Boundary

This is a deterministic design comparison, not a statistical, performance, or
external-system comparison. The nine cases are the declared executable example
count, not a sample. The constructed candidate pair is an analogue of the formal
identity pair, not a demonstration that byte-identical duplicate certificates
occur in production.
