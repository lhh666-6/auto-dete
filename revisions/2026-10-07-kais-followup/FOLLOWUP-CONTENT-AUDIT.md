> Historical report for the completed-follow-up integration at commit `7fe3a4ec2c18126440e631eb0a5b69e8725f801c`, before the final editorial pass. Current layout, citation and packaging verification is in `FINAL-POLISH-VERIFICATION.md`; the reported scientific data remain unchanged.

# Follow-up content audit — 2026-10-07

**Verdict: numerical and inferential checks PASS; two minor clarity/reproduction fixes recommended.** No manuscript, analysis, or raw-data file was edited during this audit.

## Actionable findings

1. **Minor — qualify the collection lane count.** `main.tex:195` says “Two provider lanes execute one pair each” after Section 6 has introduced both collections. This describes the original collection; the supplementary collection used one A lane (`supplement.tex`, S12, correctly states this). Suggested replacement: “The original collection uses two provider lanes, each executing one pair at a time; the supplementary A collection uses one lane.” Numerical results are unaffected.

2. **Minor — include the native-usage reproduction command.** `supplement.tex:822` attributes native usage exports to `analyze.py`, and lines 824–829 display only that script. In fact, `audit_usage.py` creates `native-attempt-usage-ledger.json` and `native-usage-summary.json`; `verify_outputs.py` creates the cross-file verification/digest report. Identify these as package outputs and add both scripts with the same `--output research/phase2-followup-analysis-2026-10-07/fresh-output` argument (or link the package README's complete sequence). The displayed command currently reproduces the seven principal tables/summary and scoring ledgers, but not every stated ancillary output.

## Checks passed

- All twelve S12 scenario/policy rows exactly match `table1-outcomes.csv`, including scheduled denominators, checkpoints, utility, integrity, unknowns, rejected-arm counts and runtime failures. The cohort is 117 pairs / 234 arms, with L29/N29/G15/E14/V16/R14 and 117 reached checkpoints.
- Main joint-outcome cells and S12 prose reconcile with independent scores: context U=114/117, cells (1,1)=99, (1,0)=15, (0,1)=3; bound U=116/117, cells (1,1)=116, (0,1)=1. Unknown integrity is zero. The four incomplete arms and fifteen completed G context violations are correctly retained as nineteen failure-archaeology arms.
- Failure classifications match the raw termination payloads and frozen scorer: L-010/context quota; E-015/context deployment-check failure; E-015/bound `prefix_failure` with the same deployment code despite shared checkpoint success; E-009/context agent-final abandonment. Wording correctly avoids interpreting `DEPLOYMENT_CHANGED` as a proven model-revision change.
- All G recovery numbers match: 15 delivered recoverable bound episodes; 8 reviewed-candidate reuse and 7 reauthorization; all U=1/I=1. Component action counts are exactly one post-feedback call for each reuse and two for each reauthorization. Context has fifteen executed substitutions. N has 29 compatible transitions per policy.
- The 83 feedback episodes, E/V/R first-action/path counts, and the distinction between R terminal utility and a recorded recovery endpoint match `table3-recovery.csv` and the full scores.
- Every S12 friction-table cell was recomputed from the 117 paired rows and G's fifteen rows. G mean extra calls=1.6, median=1; mean actual suffix difference=17.9666667 s, median=14.532 s. All-cohort means/medians, extra turns/authorizations and capped-time endpoints match to the displayed precision. Original B G mean=8.8445625 s and median=14.539 s also match; whole-suffix and recovery-action costs are distinguished in the text.
- Supplementary completion difference 2/117, interval [0, 5/117], McNemar p=.50, continuity difference −15/117 and its fixed-stratum degeneracy match the outputs. Main/S12 explicitly identify the A-only bootstrap as exploratory, selected-cohort, scenario-stratified, 10,000 draws/seed 20261007, distinct from the original two-deployment estimator. No general completion improvement is claimed.
- Original outcome estimates remain unchanged and separately denominated. S13's post hoc view correctly uses 11 original A pairs + 117 supplementary A pairs + 128 original B pairs, preserving failed and unknown outcomes. A completion=123/128 versus 125/128; combined completion=240/256 versus 244/256. The +1.5625-point effect, interval [−1.171875, 4.296875], A-specific interval [0, 3.90625], and continuity identification endpoints/intervals all match the sensitivity summary. The section labels the view post hoc and conditional, not a new frozen study or replacement primary estimator.
- Every copied follow-up and sensitivity evidence file with a corresponding source file matched that source byte-for-byte at the audit time. The 1,474 received response count, 7,989 validated events, 468 score comparisons and 15,832 preserved original files match the verification artifacts.

## Evidence and scope

Compared final manuscript source with `research/phase2-followup-analysis-2026-10-07/outputs/`, `research/phase2-followup-sensitivity-2026-10-07/outputs/`, and the unchanged original exports in `evidence/online/`. Performed direct CSV/JSON comparisons and independently recalculated means/medians. This is a content/numerical audit; it does not certify PDF layout or independently re-review unrelated theoretical/citation claims.

Audited source hashes before any corrective edits:

- `main.tex`: `1311ee05425ff5f1067488a19d64059bec6e38d550984f65518d641798350bc2`
- `supplement.tex`: `57c29dac806a078e2d98ea85a8ad796cbc321b7b661f950659e0ec8d7a99b8c4`
