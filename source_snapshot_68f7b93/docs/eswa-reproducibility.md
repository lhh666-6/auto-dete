# ESWA reproducibility guide

## Scope and data boundary

The package uses deterministic synthetic digit cells, OMR cells, forms, and named image
perturbations. It contains no employee identities, payroll data, plant records, production
images, recordings, database extracts, or exports from a real deployment. This privacy and
governance boundary is a limitation, not evidence that an undisclosed field experiment was
performed.

## Frozen environment

- Python 3.11
- Dependency resolution from `uv.lock`
- Experiment grid: `benchmarks/config/eswa-v1.json`
- Software baseline: the source snapshot and artifacts in this package

On Windows PowerShell or another shell with `uv` installed:

```text
uv sync --extra dev --extra research
uv run python -m benchmarks.run_all --config benchmarks/config/eswa-v1.json --output artifacts/eswa-v1
uv run python -m pytest -q
uv run ruff check .
uv run mypy app config benchmarks
```

Tesseract is optional. The runner records its executable version and includes it only when
`tesseract --version` succeeds. An unavailable executable is reported explicitly; no result is
fabricated and the deterministic Auto-Decte, always-predict template, and HOG+SVM comparisons
still run.

## Artifact contract

`artifacts/eswa-v1/manifest.json` records the source commit, tracked dirty state before the run,
configuration hash, seeds, package versions, commands, timestamps, and the SHA-256 and size of
every generated artifact. Primary files are:

- `recognition_raw.json`: one prediction row per case and available model;
- `recognition_summary.json`: threshold sweep, robustness, baselines, and bootstrap interval;
- `trust_faults.json`: five application-path fault outcomes;
- `resilience.json`: AI-off, duplicate, stale-write, traceability, and latency checks;
- `paper/*.pdf` and `paper/*.svg`: editable/vector Trust Teal figures;
- `paper/*.tex`: generated booktabs tables.

Latency is environment-dependent. Predictions, labels, perturbations, thresholds, and aggregate
accuracy/coverage metrics are deterministic for the frozen seeds; raw latency fields and runtime
timestamps are expected to vary.
