# R21 performance extension

This source directory contains two locked additions to the R17 performance protocol.

1. `r21_feature_baseline` compares full authority admission with a prevalidated
   materialization arm. The arm retains the exact full-admission relational post-state,
   the complete snapshot and source map, all authority rows, one transaction, and the
   form-version compare-and-swap. It removes validation, plan derivation, and authority
   object construction from the timed region. It is a persistence-cost ablation, not an
   alternative authority implementation.
2. `r21_trace_optimization` reruns the original 36-cell reverse-trace grid after replacing
   per-version and per-field database lookups with one form-scoped snapshot and in-memory
   indexes. It requires the frozen R17 `raw/trace.json` as its explicit baseline input and
   copies that input into the new output for self-contained comparison.

Run with the pinned implementation environment and both source roots on `PYTHONPATH`:

```powershell
$env:PYTHONPATH="source/performance-experiment;source/implementation"
python -m benchmarks.r21_feature_baseline --config source/performance-experiment/config/r21-feature-baseline.json --output evidence/reproduced/r21/feature-baseline-run-1
python -m benchmarks.r21_trace_optimization --config source/performance-experiment/config/r21-trace-optimization.json --baseline <frozen-r17-trace.json> --output evidence/reproduced/r21/trace-optimization-run-1
```

Both runners refuse to overwrite an existing output directory.
