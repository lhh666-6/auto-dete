# Reproducing the r27 human-annotation agreement statistics

This directory contains the published per-run labels and a standard-library
script that recomputes the agreement coefficients and bootstrap intervals
reported in the manuscript and supplement.

## Files

- `labels-A1-A2-normalized.csv` — 360 rows, one per planned B1--B4 benign run:
  `case_id`, `scenario_id`, `model_config_id`, `prompt_variant_id`,
  `repetition`, `evaluable`, `rule_label`, `A1_label`, `A2_label`,
  `adjudicated_label`.
  The labels are the authoritative corrected annotations. `evaluable=1` marks
  the 335 behavior-evaluable runs; `evaluable=0` marks the 25 runs the frozen
  scorer could not score. `rule_label` is the frozen strict-trajectory verdict.
- `recompute_irr.py` — recomputes percent agreement, Cohen's kappa, Gwet's AC1,
  PABAK, confusion matrices, and case-, model-, and cell-level bootstrap
  intervals. Only the Python standard library is required.
- `recomputed-irr.json` — output of the command below (5,000 bootstrap
  replicates, seed 20260910).

## Reproduce

```bash
python recompute_irr.py --labels labels-A1-A2-normalized.csv \
    --out recomputed-irr.json --replicates 5000 --seed 20260910
```

The script takes about 6 seconds on a standard laptop.

## Reference values

| Comparison | N | kappa | case-level 95% CI | model-level 95% CI | cell-level 95% CI | AC1 | PABAK |
|---|---:|---:|---|---|---|---:|---:|
| A1--A2 (1/0/9) | 360 | 0.974 | [0.910, 1.000] | [0.952, 1.000] | [0.935, 1.000] | 0.997 | 0.996 |
| A1--rule (1/0) | 335 | 0.410 | [0.106, 0.660] | [0.000, 0.885] | [0.000, 0.831] | 0.965 | 0.934 |
| A2--rule (1/0) | 335 | 0.410 | [0.106, 0.660] | [0.000, 0.885] | [0.000, 0.819] | 0.965 | 0.934 |

The case- and model-level recomputed intervals agree with the reference values
to Monte Carlo precision. The A1 cell-level interval reproduces
`[0.000, 0.831]`; the A2 cell-level reference is `[0.000, 0.819]`, and the
recomputation gives `[0.000, 0.831]` (both include zero, and the difference is
within bootstrap variation). The A1--A2 row is inter-human agreement; the
A1--rule and A2--rule rows are human--rule agreement, not inter-human
agreement.

## Raw-file hashes

The authoritative corrected xlsx files were archived under
`reviews/annotation-benign-task-completion-2026-09-09/returns/`. Their SHA-256
values are:

| File | SHA-256 |
|---|---|
| `FIRST-HUMAN-正式标注填写表-第一-原始.xlsx` | `2dc4e9506dae972fd1fa4cf212305a1315cc4dee84500af3e84429038d028b99` |
| `FIRST-HUMAN-第一-补0修正版.xlsx` | `f95582e7ce38f73fa1a23b6d46f259c39be911813353b99dd47a79fc6f737dbe` |
| `SECOND-HUMAN-正式标注填写表-第二-原始.xlsx` | `6d09db0cafc174c3d2d2863d4816e4008b7bd0dcdb47279d751faea59ea2cd54` |
| `SECOND-HUMAN-第二-补全版.xlsx` | `47265d16e3bd0531d2000fff3e8292e6991c78840cb1b9cf0e3e1e03f33d89ab` |

The raw xlsx files are not redistributed in this public package; the
normalized CSV is a complete 360-row extraction of their label columns, and the
hashes above allow an authorized recipient of the raw files to verify that the
extraction is consistent.

## Author adjudication

The 12 author-adjudicated items (T153 and the 11 pre-adjudication human--rule
disagreements) are recorded in `2026-09-10-case/adjudicated-labels.csv`. The
`adjudicated_label` column in the normalized CSV reproduces that file. The
adjudication is disclosed as author adjudication, not independent third-party
adjudication; the pre-adjudication disagreements remain visible in the
`disagreements-*.csv` files.
