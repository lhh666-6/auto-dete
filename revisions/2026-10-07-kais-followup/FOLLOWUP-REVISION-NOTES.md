> Historical report for the completed-follow-up integration at commit `7fe3a4ec2c18126440e631eb0a5b69e8725f801c`, before the final editorial pass. Current layout, citation and packaging verification is in `FINAL-POLISH-VERIFICATION.md`; the reported scientific data remain unchanged.

# Follow-up manuscript revision notes — 2026-10-07

## Scope and narrative

- Active sources are `main.tex` and `supplement.tex` in this revision directory. Original source directories and raw records were not edited.
- The main paper retains nine numbered sections, three related-work subsections, four contributions, and the existing author, ethics, contribution and AI-assistance declarations.
- The revised abstract has 204 whitespace-delimited words. It leads with the continuity contribution and compares supported recovery/cost findings in original B and supplementary A, while identifying the original and separately frozen supplementary collections.
- Methods explains the two collection blocks once: 117 A tasks selected by pre-response quota exhaustion, unchanged inputs/tools/policy order/requested deployment/scoring, later period, separate denominators and unchanged original 512-arm analysis.
- Results follows continuity, recovery paths, task completion and execution cost. One main outcomes table reports original A, original B and supplementary A with planned pair counts, checkpoint coverage and joint utility/integrity cells. Original detailed aggregate, recovery and cost tables are retained in S11.
- Figures 1–4 are preserved. New Figure 5 compares original B and supplementary A recovery paths and paired suffix costs without pooling. The figure uses mean additional calls and median additional time; prose also reports verified median calls.

## Verified supplementary results

Source: `research/phase2-followup-analysis-2026-10-07/outputs/`, independently rescored by the analysis worker with the unchanged frozen scorer.

- 117/117 pairs reached review; all 234 planned arms are terminal. Coordinator completion: 2026-10-07 09:46:49 UTC (17:46:49 Asia/Shanghai).
- Context: 114/117 completions; joint cells U1/I1=99, U1/I0=15, U0/I1=3. Bound: 116/117 completions; U1/I1=116, U0/I1=1. No unknown integrity.
- G: 15 context substitutions; all fifteen corresponding delivered bound mismatch episodes recover with U=1,I=1, using reviewed-candidate reuse in eight cases and reauthorization in seven.
- Supplementary G paired suffix costs: mean +1.60 calls, median +1 call; mean +17.9667 seconds, median +14.532 seconds.
- Supplementary completion difference: +1.7094 percentage points; exploratory scenario-stratified bootstrap interval [0,4.2735] points, 10,000 draws, seed 20261007. This is explicitly an exploratory application to a selected cohort, not the original frozen A+B estimator.
- Four unsuccessful arms are retained: L010 context runtime quota failure; E015 context deployment-identity check failure; E015 bound recorded prefix_failure under the same check; E009 context abandonment. All retain I=1. The full failure ledger also retains fifteen completed but instance-violating G-context arms.
- `DEPLOYMENT_CHANGED` is described as an observable deployment-identity check failure, never proof of an actual provider model revision change. Returned model/revision remains unavailable.
- S12 replaces the obsolete 45-pair partial-snapshot gate with complete outcomes, delivered-feedback, friction, failure, provenance, hashes and offline reproduction details. Original attempts and data remain available.

## Exploratory sensitivity

S13 adds a separately labeled post hoc completed-A view: original B128 + original A11 + supplementary A117 selected pair records, mapped to their existing task positions. It does not replace the original primary estimate. A completion is 123/128 context versus 125/128 bound; B remains 117/128 versus 119/128. The assembled paired effect is +1.5625 points, interval [-1.171875,4.296875], conditioning on selected sources and collection periods. Both original unknown-integrity arms remain unknown. The export is explicitly `formal_inference_allowed=false`.

## Corrected inherited wording

The original manuscript incorrectly stated that every B G pair had exactly one additional suffix tool call. The verified paired-cost distribution is zero calls in two pairs, one in twelve, and two in two; mean and median are one. Main and S11 now state this correctly. Each observed B post-rejection reuse sequence still consists of one commit. This corrects prose, without changing source data, aggregate means or original estimands.

## Checks and ownership

The paper worker edited only `main.tex`, `supplement.tex` and this file. Main/supplement counts were copied from verified summaries or imported directly from the outcome CSV; no new online collection was performed. Parent agent owns compilation, PDF rendering, package verification and release artifacts. Those final checks are reported by the parent rather than claimed here.
