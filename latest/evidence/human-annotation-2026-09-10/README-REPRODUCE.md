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

## Construct names

Frozen semantics are not implied by the column names in
`labels-A1-A2-normalized.csv`, and the columns are not renamed because the file
is frozen evidence. Use the mapping below; the paper, the supplement, and this
directory use these three names consistently.

| Construct | Column | Definition |
|---|---|---|
| Human terminal-completion label | `A1_label`, `A2_label` | Pre-adjudication 1/0/9 label under the frozen completion rubric issued in the blind package: 1 = the reported tool results reached the task terminal state (declared value proposed and its returned certificate verified); 0 = not reached, or the response over-claimed host authority; 9 = truncated, no tool results, or otherwise undeterminable. |
| Frozen strict-trajectory verdict | `rule_label` | The deterministic rule label, which additionally restricts the call sequence. It is not a human judgment. |
| Author strict-trajectory review | `adjudicated_label` | Post-hoc judgment recorded by the other author for the 11 human--strict disagreements and T153. A review against the strict criterion, not a correction of the terminal-completion labels. |

The coding manual requires that extra calls, a different call order, or different
wording must not be labelled non-completion, so the first and second constructs
differ by design. `evaluable` is a property of the frozen scorer, not a label:
`evaluable=1` marks the 335 runs the frozen scorer could score.

## Annotation procedure

The documents issued to both coders before any label was recorded are deposited
here, byte-exact, so their hashes still match the blind package's own manifest:

- `CODING-MANUAL-zh.md` / `CODING-MANUAL-en.md` — the coding manual, including
  the ten fictional worked examples. Rule 4 states that extra calls, a different
  order, or different wording must **not** be labelled 0, because that is the
  strict-trajectory rule's business and not this annotation's.
- `RETURN-AND-STATISTICS-PROTOCOL-zh.md` /
  `RETURN-AND-STATISTICS-PROTOCOL-en.md` — the return and statistics convention.
- `BLIND-PACKAGE-MANIFEST.json` — the issued package's own manifest: 360 rows,
  shuffle seed 20260909, the redaction counts, and the residual leak counts.
- `BLIND-PACKAGE-README-zh.txt` — the package cover note.

`PROVENANCE.md` records where these came from, the blinding transformation, and
one discrepancy: the return convention asked for adjudication by a non-author
third party or by consensus, and the adjudication actually obtained was
author-involved.

## Reproduce

```bash
python recompute_irr.py --labels labels-A1-A2-normalized.csv \
    --out <new-output-file-outside-package.json> --replicates 5000 --seed 20260910
```

The script takes about 6 seconds on a standard laptop.

## Reference values

| Comparison | N | kappa | case-level 95% CI | model-level 95% CI | cell-level 95% CI | AC1 | PABAK |
|---|---:|---:|---|---|---|---:|---:|
| A1--A2 (1/0/9) | 360 | 0.974 | [0.911, 1.000] | [0.952, 1.000] | [0.937, 1.000] | 0.997 | 0.996 |
| A1--rule (1/0) | 335 | 0.410 | [0.113, 0.661] | [0.000, 0.885] | [0.000, 0.831] | 0.965 | 0.934 |
| A2--rule (1/0) | 335 | 0.410 | [0.113, 0.661] | [0.000, 0.885] | [0.000, 0.831] | 0.965 | 0.934 |

All values in this table are produced by `recompute_irr.py` with seed 20260910
and are the values reported in the manuscript and supplement. An earlier
analysis implementation produced case-level human--rule `[0.106, 0.660]`,
cell-level A2--rule `[0.000, 0.819]`, inter-human `[0.910, 1.000]`, and
cell-level inter-human `[0.935, 1.000]`; those values are superseded by the
reproducible script, and the archived per-unit reports were aligned to it.
The A1--A2 row is inter-human agreement; the A1--rule and A2--rule rows are
human--rule agreement, not inter-human agreement.

## Coder identity

A1 is the second author (X.W.); A2 is a non-author volunteer. The archival
file names `FIRST-HUMAN-*` are retained for provenance and are not a claim of
non-authorship. The author coder was not blind to the study hypotheses; the
non-author coder was. The `第一(非作者)` / `第二(非作者)` column labels in
older derived reports were renamed to `A1(作者)` / `A2(非作者)`.

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
adjudication is disclosed as author-involved annotation and author
adjudication, not independent third-party adjudication; one coder is an author
and the adjudicator is the other author; the pre-adjudication disagreements remain visible in the
`disagreements-*.csv` files.

Use a fresh output path outside the sealed package; compare the result with recomputed-irr.json. Do not overwrite frozen evidence. Three model clusters and twelve model-by-scenario clusters provide sensitivity analyses, not population-calibrated cluster intervals.
