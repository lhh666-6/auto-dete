# Reproduce the blinded acknowledgment annotation analysis

## Scope

Second author Xuan Wentao manually labeled 325 shuffled assistant outputs while the previous labels, model configurations, run identifiers, scenario identifiers, and prompt/repetition identifiers were withheld. Because the annotator is an author, this is author-involved blinded annotation, not independent third-party annotation. The output is a human--rule agreement analysis, not inter-human reliability or adjudicated truth.

The completed workbook is preserved without modification as `completed-blind-annotation.xlsx`. `frozen-semantic-audit-with-text.csv` is a byte-identical copy of the frozen r21 semantic audit required to recover the run mapping. The repaired comparison labels remain in `../r3-audit-verified/recognition_semantic_audit_v2.csv`. Their hashes are recorded in `input-hashes.sha256`.

## Requirements

- Python 3.11 or newer. The analysis uses NumPy and openpyxl and was verified on CPython 3.11.9, which is also the version the reference implementation targets, so one environment covers both.
- NumPy
- openpyxl

## Run

From this directory:

```powershell
python -B .\analyze_acknowledgment_annotation.py `
  --workbook .\completed-blind-annotation.xlsx `
  --source-audit .\frozen-semantic-audit-with-text.csv `
  --repaired-audit ..\r3-audit-verified\recognition_semantic_audit_v2.csv `
  --output-dir <fresh-output-directory-outside-package> `
  --latex-table <fresh-table-path-outside-package.tex> `
  --bootstrap-replicates 5000 `
  --bootstrap-seed 20260910
```

Expected terminal summary:

```text
matched=325 agreement=286/325 kappa=0.644171
```

Run the tests:

```powershell
python -B -m unittest discover -p "test_*.py" -v
```

Only after an intentional revision and validation, regenerate the manifest from `latest/`; page counts are read from the PDFs. Ordinary verification uses `python verify_latest.py` and does not rewrite the manifest. Build directories are excluded automatically:

```powershell
python -B .\evidence\human-acknowledgment-annotation-2026-09-10\build_latest_manifest.py `
  --root . `
  --manifest .\MANIFEST-r27.json `
  --citations 54
```

## Outputs

- `normalized-labels.csv`: deblinded case-to-run join and both rule versions.
- `agreement-summary.csv`: confusion counts and coefficients by overall set, endpoint, scenario, and model configuration.
- `disagreements-v2.csv`: all 39 unadjudicated human--v2.1 disagreements.
- `bootstrap-intervals.csv`: 5,000-replicate case-, model-, and model-by-scenario-cell intervals with valid and undefined replicate counts.
- `analysis-report.json`: machine-readable provenance, results, and interpretation constraints.
- `analysis-report.md`: concise narrative summary.
- `../../paper/tables/generated/acknowledgment_human_rule.tex`: generated supplement table.
- `TEXTUAL-ACKNOWLEDGMENT-RUBRIC-2026-09-07.md`: the shared rubric issued with the blind package, byte-exact (SHA-256 `eb064e5f26d9d35157e248890d4283dfa00cf57e4337cb8b3090ddc1b579f3ee`). It states that a human--script agreement statistic is not two-human inter-rater reliability and that adjudicated agreement must not be described as pre-adjudication agreement.

The script fails closed on missing or duplicate case IDs, non-binary labels, missing rationales, unexpected endpoint/scenario denominators, duplicate assistant text, missing matches, ambiguous matches, endpoint mismatches, and inconsistent frozen audit metadata.
