# Completed supplementary evaluation and revised manuscript

Open `main.pdf` (article) and `supplement.pdf` (technical supplement). Their editable sources are `main.tex` and `supplement.tex`. This revision builds on cloud manuscript commit `47b1168a36656ea998d36746a492eaaae512909d` and adds the completed, separately frozen deployment-A evaluation.

The current review closure has a 12-page article with three main figures, three tables and 20 numbered references, plus a 29-page supplement. It refines the editorial version at commit `a72845f95d05399ad0ff2dfac203566ce60f5daf` with a compact related-work comparison, a running example and explicit scope limits; experimental results are unchanged. The subsequent AI disclosure correction removes an incorrectly named tool and gives a concise account of assistance and author responsibility; see `AI-DISCLOSURE-UPDATE.md`.

The final main-text clarification identifies the observable deployments, illustrates frozen task `FORMAL-G-001`, explains the fixed-context candidate construction, and links the fixed-version reproduction guide. Current checks and source mappings are recorded in `FINAL-POLISH-VERIFICATION.md`.

The main narrative follows continuity, recovery, utility and friction. One main table distinguishes original A, original B and supplementary A. Methods explain selection and the additional collection period before using the supplementary results. S11 retains original detailed results; S12 reports the supplementary cohort and attempt accounting; S13 labels the reconstructed completed-A view as post hoc sensitivity.

## Verified evidence

- Original: 128 tasks, two deployments, two policies; 512 planned arms. All original failures and unknowns remain. The original completion contrast is +0.78125 percentage points, interval [-1.953125, 3.515625].
- Supplementary A: 117 selected pairs / 234 arms, completed 7 October 2026 at 17:46:49 Asia/Shanghai. Context completes 114/117; bound completes 116/117. All 15 standardized G mismatches recover under bound: eight reviewed-candidate reuses and seven fresh authorizations. Their context counterparts execute substituted candidates.
- G paired continuation costs: mean paired +1.6 calls and +17.9667 seconds in supplementary A. Original B has mean +1 call; individual differences vary (two zero, twelve one, two two). Cohorts retain separate denominators.
- The supplementary completion contrast (+1.7094 percentage points, interval [0, 4.2735]) is exploratory and conditional on the selected cohort. S13 sensitivity is also explicitly post hoc. Neither replaces the original primary estimate or creates additional independent tasks.

## Compile and regenerate figures

Use an existing configured pdfLaTeX installation. Run `./build.ps1` on Windows or `bash build.sh` on Linux. Intermediate outputs go to `out/`; final PDFs stay beside their sources. Standard package dependencies are listed in the TeX preambles. Compilation needs no Python, model calls or shell escape.

The main article has three figures: the concept, independent online continuations and recovery/cost comparison. The evidence chain and original-only recovery figure are retained in the supplement. With Python and matplotlib, run `python make_revision_figures.py` to reproduce the four concept/design/evidence diagrams, or `python make_followup_figure.py` for the comparative result figure. Figure sources and data hashes accompany the PDF/SVG/PNG exports. The original outcome chart is retained in the supplement.

## Reproduce the results offline

1. Extract the [original pinned replication archive](https://github.com/lhh666-6/auto-dete/blob/475e66f549613aaaaa62c2ec81ffdee483636c54/cloud-handoff/replication-package.zip) into a separate workspace. SHA-256: `1bc17338d18f198811e0e58eca9b64bded29f9b01cd61558862455e7e0d469d8`.
2. Extract `research/phase2-results-snapshots/2026-10-07-complete/quota-recovery-complete.zip` into that workspace. SHA-256: `536f8b7d784d1af118145affd90c3d613b67ad44d9c5b3607b463bcebeacbec1`. The archive retains all 117 pair attempts, provider records and transport retries.
3. Copy the published `research/phase2-followup-analysis-2026-10-07` and `research/phase2-followup-sensitivity-2026-10-07` packages into the same relative locations. Follow each package's README. Use the original pinned dependencies plus Python 3.11 and jsonschema; no credentials or new online collection are needed.
4. Overlay this manuscript directory at `revisions/2026-10-07-kais-followup`. `python verify_evidence.py` checks the retained original evidence. The independent analysis package reproduces all 234 supplementary scores, native usage accounting and cross-file checks. S13's package uses the unchanged original exporter with explicit source routing.

The compact `KAIS-editable-sources.zip` contains the manuscript and its derived evidence, not the full raw archives. Its exact contents and hashes are recorded in `EDITABLE-PACKAGE-MANIFEST.json`; `EDITABLE-PACKAGE-RECEIPT.json` verifies the ZIP. Preserve untouched raw archive extractions when reproducing.

## Current reports and scope

- `REVIEW-CLOSURE-NOTES.md`: current changes and exact source diff.
- `AI-DISCLOSURE-UPDATE.md`: subsequent author-requested disclosure correction, exact wording and preservation checks.
- `REVIEW-CLOSURE-COMPARISON.md` and `.research/literature_matrix.md`: nearby-work comparison and primary-source grounding.
- `FINAL-POLISH-NOTES.md`: preceding editorial cuts, figure relocation and word-count comparison.
- `FINAL-POLISH-CITATION-AUDIT.md`: primary-source verification of the three formally added references.
- `FINAL-POLISH-FIGURE-QA.md` and `FINAL-POLISH-PDF-QA.md`: revised diagram semantics and integrated page review.
- `FINAL-POLISH-VERIFICATION.md` and `QA-RECEIPT.json`: current build and verification results.
- Reports prefixed `FOLLOWUP-` retain the previous integration audit and its numerical evidence, with their version explicitly marked.
- `evidence/followup/` and `evidence/sensitivity/`: the exact derived inputs used in this revision.

Older reconstruction reports and generator fragments that may remain in the local working copy refer to earlier versions and are excluded from the current editable package. Do not run legacy `complete_supplement.py`; the active supplement is the fully integrated `supplement.tex`.

The draft uses a two-column article layout. Publisher-template conversion, author sign-off and journal submission are separate steps. This work does not claim broader model generalization, immutable provider revision identity, complete billing for failed calls, or a new prospective estimand.
