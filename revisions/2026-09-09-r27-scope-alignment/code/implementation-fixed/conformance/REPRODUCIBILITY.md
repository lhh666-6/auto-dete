# Conformance Reproducibility

> Historical G3b instructions are retained below. Current R9 execution uses
> the finite catalogue runner and schema v5; R11 will define the canonical
> clean-environment command before the source freeze.

## Environment freeze

- Git baseline commit (before changes): `33f4aef4a1d9db23b7ee33528f86d3141431936c`
- Current implementation/worktree: G3b rework changes on top of that baseline; see `git status`/`git diff --stat` in the delivery.
- Python: `3.11.9`
- Environment: `uv sync --offline --extra dev --extra research`
- Hypothesis: `6.165.10`
- SQLAlchemy: `2.0.51`

## Canonical commands

```bash
uv run python -m pytest -q
uv run python -m pytest tests/conformance/test_g3b_conformance.py -q
```

## Reproducibility reset

Historical counts 239/389/478/237+5 are not used. The accepted baseline is the fresh pre-change run in
`conformance/baseline-pytest.txt`; the accepted final result is the fresh post-rework run in
`conformance/current-pytest.txt` and the conformance-only run in `conformance/conformance-pytest.txt`.

## Schema

- `SCHEMA_VERSION = 4`
- New table: `authorization_bindings`
- New columns: `record_versions.fact_sources`, `fact_transitions.value_payload`
- Migration is idempotent: `stamp_schema_version` adds missing columns before stamping.
- Duplicate `(form_id, created_version, field_key)` is prevented by a SQLite unique constraint (documented refinement).

## Test families in this bundle

- Deterministic legal/correction/copy-forward
- Source-anchored reverse trace including copied-forward historical sources
- Trace corruption: transition value, authorization value, committed value, source deletion
- Repository admission-bundle hardening: missing binding, certificate mismatch, value mismatch
- Required substitution negatives: field, record, evidence owner, candidate version, auth/cert transfer
- Duplicate schema prevention
- Concrete ABL guard oracle and stateful Hypothesis `RuleBasedStateMachine`

## Current R9 command

```powershell
uv run python conformance/run_catalogue.py `
  --output conformance/raw-results/<new-run-id>
uv run python conformance/verify_catalogue_results.py `
  conformance/raw-results/<new-run-id>
```

The runner refuses an existing output directory and uses a separate pytest
base temp per case. Current schema is v5 with a canonical Python migration
chain, named single-use decision/certificate indexes, and a canonical locator
era marker. `schema_migration_v4.sql` is historical only.
