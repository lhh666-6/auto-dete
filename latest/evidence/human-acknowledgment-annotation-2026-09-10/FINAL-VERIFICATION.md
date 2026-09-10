# Final verification — 2026-09-10

The integrated candidate was verified from the `latest/` tree after the completed workbook was copied without modification.

| Check | Result |
|---|---|
| Exact workbook-to-audit join | 325/325 rows matched exactly once |
| Human--v2.1 headline | 286/325 agreement; Cohen's kappa 0.644171 |
| Analysis and manifest tests | 7/7 passed |
| Full Python implementation suite | 389/389 passed in a clean Python 3.11 dependency environment |
| Formal witness tests | 19/19 passed |
| Archived Alloy batch package gate | `BATCH_PACKAGE_STRUCTURE_PASS` |
| Main LaTeX PDF | 59 pages; SHA-256 `b459e7e8af58d47529a879dab2dd54232be2c3a91e57c6fc52ae67deea6f212b` |
| Supplement LaTeX PDF | 16 pages; SHA-256 `26b48606fe1732bff2c76e6ecf4ad9b236ea626c7c36d6dbce1f376b3d67d3f4` |
| LaTeX log scan | 0 errors, undefined references/citations, multiply defined labels, or overfull boxes |
| PDF visual QA | all 59 main-paper pages and all 16 supplement pages rendered; contact sheets and annotation/contribution pages inspected without clipping or overlap |

The 39 human--rule disagreements remain unadjudicated. The manual labels do not overwrite the frozen rule-hit labels, and no hosted-model run was repeated.
