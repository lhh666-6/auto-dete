# Review-based manuscript refinement — 2026-09-11

Based on teammate commit `c317093dddd69a94267fb667a0cc1aaf1f9d10d4` and the local multi-perspective review. This revision changes manuscript interpretation, presentation, and derived assets; it does not rerun hosted experiments or change original human labels.

## Changes

- Corrected the remaining 68-command results sentence to 72 commands (22 SAT and 14 UNSAT per profile), consistent with the deposited trace-precondition witnesses.
- Distinguished original terminal-completion labels, the frozen strict-trajectory rule, and post-hoc author strict-trajectory review throughout methods, results, discussion, and declarations. The eleven disagreements are not treated as errors in the original human labels; T153 is a separate inter-human disagreement.
- Removed a duplicated paragraph heading. Clarified that the demonstrator persists approval before the tested attempt, whereas the production confirmation request constructs the binding; faithful correspondence to prior review remains an external assumption.
- Added C5 to the contribution figure and clarified the unchanged-value review boundary.
- Added all 36 frozen reverse-trace cells, including p50 and p95, in Supplement Table S4, generated directly from the archived JSON. Updated the cost figure and caption consistently.
- Regenerated all four vector figures, fixed the fourth figure's label margins, and documented the current AI-assisted scripting provenance without inventing historical tool versions.
- Replaced the unsupported release-level-manifest claim with the actual current-directory and historical-tag scope.
- Replaced the unsubstantiated institutional-policy exemption claim with an explicit unresolved author-confirmation statement.

## Fresh verification

- `latexmk -pdf main.tex` and `latexmk -pdf supplement.tex` using the repository `.latexmkrc`: 63 and 20 pages, respectively.
- Final logs: no errors, undefined references/citations, multiply defined labels, or overfull boxes.
- All four figure layout checks passed with zero text overlaps; revised figure and supplement-table pages were visually checked.
- Seven annotation integration/manifest tests passed; the formal batch structure gate with `-RequireRawResults` passed. This gate is not a new solver run.
- The complete trace-table generator validates 36 unique cells, 200 observations per implementation per cell, 7,200 observations per implementation, zero command failures, and 12 SQL statements in every optimized observation.
- The previous 389-test implementation run remains historical; no implementation behavior changed in this refinement.

## Reproduction

From the repository root, using Python with Matplotlib installed:

```powershell
python latest/paper/scripts/build_trace_grid.py
python latest/paper/scripts/build_flowcharts.py
python latest/code/figure-work/paper/scripts/build_figures_revised.py --stats latest/code/figure-work/evidence/agent-behavior-revised.json --output-root latest/paper/figures/generated
```

Then compile both LaTeX sources from `latest/paper`. Regeneration changes derived files; rebuild the current manifest after an intentional revision, and run `python latest/verify_latest.py` to verify the sealed package.

## Author decisions before submission

1. Confirm the institutional ethics requirement for the volunteer annotation and supply a documented policy/approval/exemption basis as applicable. The available records do not establish one. Do not submit the current unresolved statement as if exemption had been confirmed.
2. Both authors should approve the interpretation, authorship, consent/privacy statements, and final manuscript. Historical assistant versions not archived are disclosed as unavailable, not guessed.
3. After approval, publish an immutable commit/tag for this final candidate and use that identifier in the submission; `main/latest` is a mutable navigation link.

No original experiment outputs or manual labels were overwritten. This revision was committed by the second author as `c5e891c4` and pushed to `main`; follow-up corrections were applied on top of it. No freeze tag has been cut yet.
