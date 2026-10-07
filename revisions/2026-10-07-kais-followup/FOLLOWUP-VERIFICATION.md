# Final follow-up integration verification — 7 October 2026

The completed supplementary evaluation supports the continuity/recovery claims in the revised article. Original and supplementary results remain separate; the completed-A recombination is explicitly post hoc and confined to S13. No primary result was overwritten.

| Check | Result |
|---|---|
| Supplementary collection | 117 terminal pairs, 234 planned arms, all 117 review checkpoints |
| Independent frozen rescoring | 468 exact cached-score comparisons; 7,989 validated events; zero validation errors |
| Analysis and routing tests | 18 supplementary tests and 3 sensitivity tests pass |
| Original evidence verifier | All 29 checks pass; original 512-arm denominator and estimates retained |
| Independent exporter comparison | All five row-level supplementary tables match the routed frozen exporter |
| Native attempt accounting | 1,477 attempts; 1,474 completed responses; three failed attempts have unknown usage |
| Complete raw archive | 16,951 files verified by CRC and per-member SHA-256; all attempts retained |
| Final compilation | Existing MiKTeX pdfLaTeX; three final passes each; main 13 pages, supplement 28 pages |
| References and layout bounds | Zero unresolved references/citations, overfull boxes or missing-glyph warnings |
| Visual inspection | See `FOLLOWUP-PDF-QA.md`; final PDF hashes are in `QA-RECEIPT.json` |

## Scientific interpretation

The most direct new evidence is the 15 standardized G handoffs in supplementary A: context accepts 15 substituted instances; bound rejects and subsequently recovers all 15 with U=1/I=1, through eight reviewed-candidate reuses and seven reauthorizations. Mean paired friction is +1.6 calls and +17.9667 seconds; median friction is +1 call and +14.532 seconds.

Overall completion is 114/117 versus 116/117. The +1.7094-point supplementary contrast and [0, 4.2735] bootstrap interval are exploratory and conditional on the selected cohort and collection period. They do not establish general completion superiority. Four incomplete trajectories and fifteen completed-but-integrity-violating trajectories remain in the evidence.

The original primary effect stays +0.78125 points, interval [-1.953125, 3.515625]. S13 reports the source-routed post hoc view separately (+1.5625 points, interval [-1.171875, 4.296875]), retaining the original two unknown-integrity outcomes and an explicit `formal_inference_allowed=false` flag.

## Corrections made during verification

- Original B G costs had been described as exactly one extra call per pair. Raw paired differences are zero in two pairs, one in twelve and two in two. The mean and median are one. Both manuscripts now state this accurately; data and estimates did not change.
- Main Methods now distinguishes the original two provider lanes from the supplementary A-only lane.
- S12 reproduction instructions include independent scoring, native usage auditing and final output verification.
- The main outcomes table's column spacing and the supplement's original-results table headers were adjusted to remove overflow without omitting cells or scaling down the table.
- The app's built-in compiler could not locate its standard directories. The existing local MiKTeX installation compiled both documents successfully; no compiler or package was installed.

The independent content audit's two minor reproduction/wording findings were resolved before the final build. Its original report remains available for traceability.

## Build quality score and remaining scope

| Metric | Value |
|---|---|
| Scoped diagnostic score | 89 / 100 |
| Rubric verdict | Revise — remaining spacing polish |
| Deductions | 18 underfull h/vbox diagnostics, capped at -10; third final compilation pass, -1 |

This is a narrow LaTeX build/spacing score, not a scientific-quality score or journal acceptance estimate. There are no overfull boxes or unresolved references. The remaining underfull diagnostics concern justified text and column spacing; the PDFs are delivered as review drafts with these notes. Full source-style and publisher-template conformance are outside this build score.

Fresh solver execution, new online collection and provider billing reconciliation were not performed for this manuscript integration. Existing formal receipts are verified archived evidence. Returned provider model/revision identifiers remain unavailable; `DEPLOYMENT_CHANGED` is a runtime identity-check outcome, not proof that the provider changed a model revision. Author sign-off and journal submission remain separate steps.

## Artifact provenance

- Original cloud paper: `47b1168a36656ea998d36746a492eaaae512909d`.
- Original raw replication archive SHA-256: `1bc17338d18f198811e0e58eca9b64bded29f9b01cd61558862455e7e0d469d8`.
- Completed supplementary raw archive SHA-256: `536f8b7d784d1af118145affd90c3d613b67ad44d9c5b3607b463bcebeacbec1`.
- Current source files and editable ZIP: `EDITABLE-PACKAGE-MANIFEST.json` and `EDITABLE-PACKAGE-RECEIPT.json`.

The supplementary collector, original scorer, frozen input files and raw results remain unchanged. Local reconstruction reports for prior versions are not represented as current validation.
