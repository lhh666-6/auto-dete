# Reproducing the local ASE revision v15

The current source revision is [v15](revisions/2026-10-25-ase-revision-v15/README.txt), dated 25 October 2026. Repository availability does not assert journal submission or a separate release tag. Historical v13 and [v14](revisions/2026-10-24-ase-framing-v14/README.txt) freezes remain unchanged; this checkout retains the v14 revision and inherited experimental payloads. The v15 packaging tool generates `SOURCE-MANIFEST.json`, `upload-package/FILES.json` and `FINAL-FREEZE-v15.json` after current PDF/scientific validation.

## Sources and offline readback

After packaging, extract `Manuscript-sources.zip` from `revisions/2026-10-25-ase-revision-v15/upload-package/ESM_3.zip` and work inside `Manuscript-sources/`. It contains complete sources for all three PDFs, QA/checker tests, analysis scripts and current v15 audits. The separate `Manuscript-source.zip` is the single-entry main manuscript source for the submission system.

Use Python 3.11 or later. Read [REPRODUCE-RECOVERY.md](revisions/2026-10-25-ase-revision-v15/REPRODUCE-RECOVERY.md) for the two immutable raw ZIP URLs, SHA-256 hashes and placement under `INPUT_ROOT`. Run from the extracted source directory, replacing `INPUT_ROOT` with the directory containing those two ZIPs. Outputs go to new directories.

```text
python qa/scientific_statistics.py --repository-root INPUT_ROOT --output scientific-readback
python qa/feedback_strata.py --pairs tables/feedback-sensitivity/pairs.csv --output scientific-readback/feedback-strata.json
python qa/recovery_costs.py --repository-root INPUT_ROOT --output recovery-readback
python qa/recovery_example.py --repository-root INPUT_ROOT --output recovery-readback
python qa/recovery_availability.py --repository-root INPUT_ROOT --output recovery-availability
```

These five scripts use only the Python standard library. The expected archived readback covers 32 recovery pairs, 64 exposed N pairs, 128 checkpoint events and 127 summary flags. Supplementary A has 15 recovery pairs, mean call difference 1.60 and exploratory paired-bootstrap interval [0.87, 2.33] (10,000 draws; seed 20261023). The three feedback permission states contribute call differences +2, +1 and -3, summing to zero over 12 pairs from four reused tasks. The guide identifies comparison files and separates original/supplementary cohorts. These expectations do not imply new hosted or SDK collection.

## v15 checker correction

The corrected checker is [qa/observation_witnesses_v15.py](revisions/2026-10-25-ase-revision-v15/qa/observation_witnesses_v15.py). Read its CLI help and current `audit/` reports for regression commands and results. The checker, tests and upstream fixture are separate from historical frozen experiment archives. The correction concerns canonical JSON equality in an auxiliary observation projection; it does not rewrite saved experimental records or claim a new production-gate result.

## Build and verify

Install pdfLaTeX and BibTeX, then run `python build.py` from the v15 source directory; `python build.py --main-only` builds the manuscript alone. Supplied figure PDFs, bibliography, class and style suffice for compilation. Optional figure regeneration has the dependencies in `requirements-figures.txt`.

The following maintainer packaging commands require this repository layout and
the preserved v14 ESM_3.zip. They are not required for an extracted source package's
PDF build or standalone checker regression. From the repository's v15 directory:

```text
python scripts/package_v15.py --check
python scripts/package_v15.py --package --validated
python scripts/package_v15.py --verify
```

Use `--package --validated` only after current PDF/scientific checks pass. The tool reads actual PDF page counts, records hashes and inventories, verifies ZIP CRCs and local TeX dependencies, and mirrors five payloads to `submission/ASE-2026-10-25-v15/ready-to-upload/`. Verification needs `pdfinfo` on PATH or Python `pypdf`. The final freeze excludes itself to avoid a self-hash cycle. Packaging does not publish, commit, push or submit anything.

## Experiment archives

These are members of `ESM_3.zip`, alongside the complete three-document `Manuscript-sources.zip`. Their bytes are inherited from v14 without modification.

| Archive | Entry point and evidence |
|---|---|
| Correction-consumption-reproduction.zip | `START-HERE.md`; `verify_offline.py`; 504 cells, 444 matches |
| Agno-entrypoint-reproduction.zip | `START-HERE.md`; `verify_offline.py`; 54 cells, 42 matches |
| Reviewed-instance-substitution-reproduction.zip | `START-HERE.md`; `verify_offline.py`; 16 cells, 12 matches |
| X1-X2-reproduction.zip | Included offline verification guide |
| Native-contract-reproduction.zip | Native-contract study guide |
| Feedback-sensitivity-reproduction.zip | Archived feedback-study guide |
| Dynamic-recovery-reproduction.zip | Archived dynamic-recovery guide |

In the three SDK archives, `START-HERE.md` and `REPRODUCE-V4.md` take precedence over historical README instructions. Raw per-cell databases are included. Do not overwrite historical freezes for verification. Counts across archives are not pooled as independent samples. Fresh SDK/model executions require their own pinned environments and are not implied by saved-record checks. Historical evidence pointers remain in [EXTERNAL-INPUTS.json](revisions/2026-10-25-ase-revision-v15/EXTERNAL-INPUTS.json); v15 does not claim a fresh rerun of every experiment or Alloy command.
