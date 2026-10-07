# Deployment-A supplementary evaluation revision

This revision extends the verified cloud manuscript at commit `47b1168a36656ea998d36746a492eaaae512909d`. The scientific narrative leads with review-to-execution continuity, observed recovery and execution costs. The original 512-arm evaluation and the separately frozen deployment-A follow-up remain distinct collection blocks.

## Current editing targets

- `main.tex` / `main.pdf`: main article, with the original results retained and the supplementary evidence explicitly identified.
- `supplement.tex` / `supplement.pdf`: complete original evidence plus supplementary cohort methods, outcomes and provenance.
- `make_followup_figure.py` / `figures/followup-*`: independently sourced comparison of original deployment B and supplementary deployment A.
- `evidence/followup/`: copies of verified supplementary analysis outputs for manuscript/figure reproduction.
- `FOLLOWUP-REVISION-NOTES.md`, `FOLLOWUP-FIGURE-QA.md`, and the final validation report: this revision's changes and checks.

The older audits, blueprint and staged logs inherited from the original reconstruction describe their stated versions. They do not certify this revision's later supplementary results and are excluded from the current editable source ZIP. QA-RECEIPT.json and EDITABLE-PACKAGE-MANIFEST.json identify the current deliverables; FINAL-POLISH-VERIFICATION.md records the current checks and limitations; earlier FOLLOWUP reports are explicitly historical.

## Scientific data boundaries

Original evaluation: 128 tasks × 2 deployments × 2 policies, 512 planned arms. All original failures and unknown outcomes remain in that analysis.

Supplementary evaluation: 117 selected deployment-A pairs / 234 planned arms. Selection used original quota-exhausted prefixes with no received model response. Task inputs, prompts, tools, policy order, requested deployment configuration and frozen scorer are retained. Collection completed on 7 October 2026 at 17:46:49 Asia/Shanghai. All final supplementary outcomes, including failures, remain in the supplementary denominator.

The manuscript does not sum the blocks into a larger independent task sample or silently substitute follow-up outcomes into the original estimates. Supplementary uncertainty quantification conditions on this selected cohort and additional collection period.

## Inputs for independent reproduction

1. Original complete evidence: `cloud-handoff/replication-package.zip` pinned at commit `475e66f549613aaaaa62c2ec81ffdee483636c54`, SHA-256 `1bc17338d18f198811e0e58eca9b64bded29f9b01cd61558862455e7e0d469d8`.
2. Completed follow-up: `research/phase2-results-snapshots/2026-10-07-complete/quota-recovery-complete.zip`, SHA-256 `536f8b7d784d1af118145affd90c3d613b67ad44d9c5b3607b463bcebeacbec1`.
3. Independent supplementary scorer adapter and tests: `research/phase2-followup-analysis-2026-10-07/`.

Extract the input archives into a separate working tree, preserve the original extracted references, and follow the analysis package's instructions. Reproduction is offline and requires no new model calls. A standard configured pdfLaTeX installation can compile the included sources and vector figures; Windows and Linux build scripts are supplied.

Final publisher formatting and author sign-off are separate from data and compilation verification. No journal submission is performed by this revision workflow.
