# Reproducing ASE manuscript v17

Use the [fixed v17 snapshot](https://github.com/lhh666-6/auto-dete/tree/ase-framing-v17-2026-10-25). The [five scientific payloads](https://github.com/lhh666-6/auto-dete/tree/ase-framing-v17-2026-10-25/submission/ASE-2026-10-25-v17/ready-to-upload) and [FILES.json](https://github.com/lhh666-6/auto-dete/blob/ase-framing-v17-2026-10-25/submission/ASE-2026-10-25-v17/FILES.json) identify the exact review files. Main/Online Resources 1/2 have 29/31/26 pages. This guide reads archived records; it does not recollect agent or SDK runs.

## Obtain the complete sources

1. Download [ESM_3.zip](https://github.com/lhh666-6/auto-dete/blob/ase-framing-v17-2026-10-25/submission/ASE-2026-10-25-v17/ready-to-upload/ESM_3.zip), then extract its `Manuscript-sources.zip` member. Work inside `Manuscript-sources/`.
2. Use Python 3.11 or later. The supplied QA scripts use its standard library.
3. Read [REPRODUCE-RECOVERY.md](https://github.com/lhh666-6/auto-dete/blob/ase-framing-v17-2026-10-25/revisions/2026-10-25-ase-framing-v17/REPRODUCE-RECOVERY.md). Download the two pinned raw ZIPs and retain their exact bytes under the stated `INPUT_ROOT` paths. Their hashes are checked automatically. These two historical datasets are external to ESM_3; downloads require network access, while the readback commands below are offline.

The separate `Manuscript-source.zip` is the one-entry source for compiling the main manuscript. The full three-document source and scientific readback scripts are in ESM_3.

## Portable observation-checker regression

From `Manuscript-sources/`, run:

```text
python -B qa/test_observation_equality_v15.py --output scratch/equality.json
```

Expected: 38 equality regressions pass, with five omission pairs, the instance-identity pair and copy-forward control preserved. The bundled upstream source is hash-checked; no Git checkout, model API or third-party Python package is needed. This is the unchanged v15 auxiliary checker, with its finite scope documented in Online Resource 1 S2.6–S2.8 and Online Resource 2 A9. It is separate from historical production-gate and Alloy results.

## Scientific readback

Replace `INPUT_ROOT` with the directory holding the two raw ZIPs. Run from the complete-source directory, with outputs separate from supplied tables:

```text
python qa/scientific_statistics.py --repository-root INPUT_ROOT --output scientific-readback
python qa/feedback_strata.py --pairs tables/feedback-sensitivity/pairs.csv --output scientific-readback/feedback-strata.json
python qa/recovery_costs.py --repository-root INPUT_ROOT --output recovery-readback
python qa/recovery_example.py --repository-root INPUT_ROOT --output recovery-readback
python qa/recovery_availability.py --repository-root INPUT_ROOT --output recovery-availability
```

Expected readback includes 32 recovery pairs (24 reuse/eight fresh authorization), 64 exposed N pairs, 128 checkpoint events and 127 retained summary flags. These have different units and do not imply complete suffix observation. The availability audit checks 13 predicates per delivered mismatch episode. Original A, original B and supplementary A remain labelled separately.

Supplementary A's 15 delivered recovery pairs have mean call difference 1.60 and the exploratory A12 interval [0.87, 2.33] (10,000 paired resamples, seed 20261023). The historical interval uses a separately recorded seed; the detailed guide explains both. The feedback strata contain 12 pairs over four reused task definitions; permission-state call differences sum to +2, +1 and -3, with aggregate zero. Compare derived scientific fields and CSVs with the supplied `tables/` records.

## Compile the PDFs

Install pdfLaTeX and BibTeX. From the full source directory:

```text
python build.py
```

Expected pages: 29, 31 and 26. `python build.py --main-only` builds only the main paper. Supplied class, style, bibliography and figure PDFs suffice; optional figure regeneration has separate dependencies. The standalone main-source ZIP supports `python build.py --main-only` from its archive root.

The [packaged-source validation](https://github.com/lhh666-6/auto-dete/blob/ase-framing-v17-2026-10-25/revisions/2026-10-25-ase-framing-v17/audit/packaged-source-validation-v17.json) records clean-extraction builds. Every rebuilt page has matching text and 72-dpi rendering to its issued PDF. Underfull spacing warnings are retained; there are no unresolved citations/references or overfull boxes in those builds.

## Seven separate study archives

These ZIPs are members of ESM_3 alongside the full-source ZIP. All seven retain the prior frozen bytes.

| Archive | Entry point and evidence |
|---|---|
| Correction-consumption-reproduction.zip | `START-HERE.md`; `verify_offline.py`; 504 cells, 444 matches |
| Agno-entrypoint-reproduction.zip | `START-HERE.md`; `verify_offline.py`; 54 cells, 42 matches |
| Reviewed-instance-substitution-reproduction.zip | `START-HERE.md`; `verify_offline.py`; 16 cells, 12 matches |
| X1-X2-reproduction.zip | Included independent offline verification guide |
| Native-contract-reproduction.zip | Scripted native-to-store study guide and SQL scoring |
| Feedback-sensitivity-reproduction.zip | Archived feedback-study guide |
| Dynamic-recovery-reproduction.zip | Archived pilot guide, saved scoring and offline replay |

For the three SDK archives, read `START-HERE.md` and `REPRODUCE-V4.md` before historical README instructions. Raw per-cell records are included. Readback does not imply portable recollection or independent pooled samples. Fresh SDK/model runs require their pinned dependencies and, where relevant, provider access.

The [external-input inventory](https://github.com/lhh666-6/auto-dete/blob/ase-framing-v17-2026-10-25/revisions/2026-10-25-ase-framing-v17/EXTERNAL-INPUTS.json) preserves historical evidence identities. Wider E1–E3 and Alloy rerun instructions remain in their pinned historical deposits. The v17 publication verifies packaging and existing records; it does not claim new hosted runs or a fresh rerun of every historical experiment.
