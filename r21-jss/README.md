# Auto-Decte R21 reproducibility package

This directory is the complete citable package for the JSS manuscript
*Authoritative-State Admission for AI-Derived Updates: Failure
Distinguishability, Transactional Realization, and Evaluation*.

The package preserves the candidate-to-authorization-to-authoritative-state
implementation, Alloy models, constructive C2 witness checker, transactional
and conformance tests, performance experiments, repeated live-agent benchmark,
raw run records, normalized paper inputs, semantic acknowledgment audit,
manuscript source, final PDF, and integrity manifests used by the paper.

## Start here

- `paper/main-r21-submission-ready-2026-09-06.pdf`: compiled 58-page manuscript with the derived C2 witness construction.
- `source/implementation/`: Python/SQLite implementation and regression suite.
- `source/formal/`: Alloy models, batch command manifest, and executable C2 witnesses.
- `source/agent-authority-benchmark/`: repeated live-agent benchmark code.
- `source/live-agent-experiment/`: six-scenario live-agent adapter.
- `source/performance-experiment/`: admission and reverse-trace benchmarks.
- `evidence/agent-authority-benchmark-v2/final/2026-09-01-three-config-10x/`:
  all 1,260 planned final executions and terminal records.
- `evidence/agent-authority-benchmark-v2/manuscript-input/2026-09-03-three-config-10x/`:
  frozen normalized manuscript inputs.
- `evidence/agent-authority-benchmark-v2/analysis/2026-09-05-recognition-semantic-audit/`:
  all 325 audited outputs, old/new labels, rubric, confusion matrices, and derived statistics.
- `evidence/frozen/`: frozen correctness and performance evidence.
- `evidence/reproduced/`: retained R19/R21 rerun receipts and outputs.
- `evidence/r21-paper-input-manifest.json`: paper-input lineage.
- `evidence/r21-revision-manifest.json`: revision-level integrity record.
- `evidence/formal/observation-witness-report.json`: raw C2 histories and all derived observations/outcomes.
- `PACKAGE_MANIFEST.json`: SHA-256 inventory of this deposited package.

## Main reported evidence

- Five constructive C2 witness pairs under the declared failure/observation model.
- 66/66 bounded relational outcomes across S1 and S2 profiles.
- 9 intended projection cases SAT and 20 projection mutants UNSAT.
- 35/35 finite catalogue cases and 354 Python tests in the frozen paper run.
- 2,000 admission pairs and 7,200 reverse-trace observations.
- 1,260 planned live-agent executions; 320/335 behavior-evaluable benign completions.
- Semantic acknowledgment audit: 117/174 context mismatch and 150/151 stale state.
- Authority accounting: 0/720 fixed invalid-tuple calls and 0/179
  capability-unavailable branches; 93 runtime failures reported separately.

## Verification

From `r21-jss/`:

```powershell
python scripts/build_r21_inputs.py verify
python source/formal/observation_witnesses.py `
  --json evidence/formal/observation-witness-report.json
python scripts/build_r21_manifest.py verify `
  --paper-pdf paper/main-r21-submission-ready-2026-09-06.pdf --paper-pages 58
python scripts/verify_package_manifest.py
python source/dsh-plugin-auto-decte/experiment/verify_receipt.py verify `
  evidence/reproduced/r19-dsh-2026-08-27-final
python -m unittest scripts.test_audit_recognition source.formal.tests.test_observation_witnesses
```

Paper-generator checks:

```powershell
Set-Location paper/scripts
python -m unittest test_build_evidence_tables.py test_build_figures.py `
  test_build_runtime_endpoint_table.py
```

Implementation checks:

```powershell
Set-Location source/implementation
uv sync --frozen --extra dev --extra research
uv run pytest -q
uv run ruff check app tests
uv run mypy app
```

The live-agent adapter has a separate frozen environment under
`source/live-agent-experiment/`. Replaying hosted calls requires provider access;
the completed run records allow inspection of manuscript claims without paid reruns.

## Data and privacy boundary

The evaluation uses synthetic or public benchmark inputs. The package contains
no research-participant data, personal records, production records, API keys, or
credentials. Historical diagnostics, superseded pilots, local environments,
caches, and duplicate dependency runtimes are excluded from the citable package.

## Integrity and large files

`PACKAGE_MANIFEST.json` records every deposited file by relative path, byte
length, and SHA-256 digest. The largest frozen SQLite performance artifact is
stored through Git LFS; its digest remains covered by the package manifest.

## Authorship and contact

Liang Hanghao  
College of Computer Science and Electronic Engineering, Hunan University  
Correspondence: zwu691403@gmail.com

## Version

This C2-closure and semantic-audit clarification package is pinned by Git tag
`r21-jss-2026-09-06-v4`.

## License

The repository's existing review-release terms remain in effect. Public
availability does not add permissions beyond those terms.
