# Reproducing ASE revision v7

Use the [fixed v7 release](https://github.com/lhh666-6/auto-dete/tree/ase-review-v7-2026-10-24) and [eleven-file upload directory](https://github.com/lhh666-6/auto-dete/tree/ase-review-v7-2026-10-24/revisions/2026-10-24-ase-review-v7/upload-package). Check downloaded files against [FILES.json](https://github.com/lhh666-6/auto-dete/blob/ase-review-v7-2026-10-24/revisions/2026-10-24-ase-review-v7/upload-package/FILES.json). These instructions analyse saved evidence; they do not recollect hosted or SDK runs.

## Manuscript and scientific readback

1. Download and extract [Manuscript-sources.zip](https://github.com/lhh666-6/auto-dete/blob/ase-review-v7-2026-10-24/revisions/2026-10-24-ase-review-v7/upload-package/Manuscript-sources.zip). Work inside `Manuscript-sources/`.
2. Use Python 3.11 or later. Read [REPRODUCE-RECOVERY.md](https://github.com/lhh666-6/auto-dete/blob/ase-review-v7-2026-10-24/revisions/2026-10-24-ase-review-v7/REPRODUCE-RECOVERY.md) for the two immutable raw ZIP URLs, SHA-256 hashes and exact local placement under `INPUT_ROOT`. The original download is named `cloud-handoff/replication-package.zip` on GitHub; the guide explicitly maps it to the local historical path expected by the scripts.
3. Run the following from the extracted directory, replacing `INPUT_ROOT` with the directory holding those two ZIPs. Output goes into new directories; supplied tables are preserved.

```text
python qa/scientific_statistics.py --repository-root INPUT_ROOT --output scientific-readback
python qa/feedback_strata.py --pairs tables/feedback-sensitivity/pairs.csv --output scientific-readback/feedback-strata.json
python qa/recovery_costs.py --repository-root INPUT_ROOT --output recovery-readback
python qa/recovery_example.py --repository-root INPUT_ROOT --output recovery-readback
python qa/recovery_availability.py --repository-root INPUT_ROOT --output recovery-availability
```

All five scripts use only the Python standard library. The scientific readback checks 32 recovery pairs, 64 exposed N pairs, 128 checkpoint events and 127 summary flags. Supplementary A has 15 recovery pairs, mean call difference 1.60 and exploratory paired-bootstrap interval [0.87, 2.33] (10,000 draws; seed 20261023). The three feedback permission states contribute call differences +2, +1 and -3, summing to zero over 12 pairs from four reused tasks. The guide identifies outputs and comparison files. Original and supplementary cohorts remain separate.

To compile all three PDFs, install pdfLaTeX and BibTeX, then run `python build.py`; `python build.py --main-only` builds the main manuscript. The class, style, bibliography and figure PDFs are supplied. Figure regeneration is optional and has separate dependencies in `requirements-figures.txt`.

## Experiment archives

Each ZIP is a separate sibling deliverable in the upload directory:

| Archive | Entry point and evidence |
|---|---|
| Correction-consumption-reproduction.zip | Start with `START-HERE.md`; portable `verify_offline.py`; 504 cells, 444 matches |
| Agno-entrypoint-reproduction.zip | Start with `START-HERE.md`; portable `verify_offline.py`; 54 cells, 42 matches |
| Reviewed-instance-substitution-reproduction.zip | Start with `START-HERE.md`; portable `verify_offline.py`; 16 cells, 12 matches |
| X1-X2-reproduction.zip | Follow its included offline verification guide |
| Native-contract-reproduction.zip | Follow its native-contract study guide |
| Feedback-sensitivity-reproduction.zip | Follow its archived feedback-study guide |
| Dynamic-recovery-reproduction.zip | Follow its archived dynamic-recovery guide |

In the three SDK archives, current `START-HERE.md` and `REPRODUCE-V4.md` take precedence over historical README instructions. Raw per-cell databases are included. Do not regenerate or overwrite historical freezes for offline verification. Counts across archives are not pooled as independent samples. Fresh SDK/model executions require their own pinned environments and are not implied by a successful saved-record check.

See [VERIFICATION.json](https://github.com/lhh666-6/auto-dete/blob/ase-review-v7-2026-10-24/revisions/2026-10-24-ase-review-v7/audit/VERIFICATION.json), [SDK navigation verification](https://github.com/lhh666-6/auto-dete/blob/ase-review-v7-2026-10-24/revisions/2026-10-24-ase-review-v7/audit/sdk-navigation.json) and [V7-CHANGELOG.md](https://github.com/lhh666-6/auto-dete/blob/ase-review-v7-2026-10-24/revisions/2026-10-24-ase-review-v7/V7-CHANGELOG.md) for exactly what this release checked. The [21 October guide](https://github.com/lhh666-6/auto-dete/blob/ase-reproducibility-2026-10-21/REPRODUCIBILITY.md) remains the entry point for the wider historical pipeline; this v7 release does not claim a fresh rerun of every experiment or Alloy command.
