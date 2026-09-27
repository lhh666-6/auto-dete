> 历史记录：本文件记录提交 7e65d6a 的 33 页稿。当前 32 页稿见 submission-closeout.md / submission-closeout-check.json。

# High-yield narrative refinements

27 September 2026. Baseline: `2eb04fce5f753ea2a0e9b9265cd9f84484f02819`. This pass implements the author's six local priorities. No new scientific experiments, citations, research questions or claims are introduced.

## Editorial decisions

1. **Bridge to the five classes — Section 3.2.** Immediately before the distinction basis: “Equal-valued substitution exposes one missing distinction. Extending the analysis across the admission relation yields five information classes for the modeled failures:” The five classes now follow the core separator. Proposition 1, its proof, all contract mathematics and the complete scope paragraph remain verbatim.
2. **Experiment hierarchy — Section 7.1 and Figure 2.** E1 tests why exact binding matters under equal values/context; E2 locates the review-to-confirmation boundary; E3 measures enforcement and querying costs. The RQs remain verbatim. Cost comparisons remain implementation characterizations, not isolated exact-binding overhead estimates.
3. **Support counts — Introduction, protocol, results and Figure 2.** Repeat 15 substitutions and 165 exact/reference cases as the core memory points. Remove 72, 9/20, 35, 60 and 22,400 as repeated figure headlines; keep their primary definitions/results. In prose, remove the redundant 35 from C2/protocol/results, 85/ten from protocol, the 495 product from protocol, and per-profile Alloy subtotals from Results. Counts are retained in the locations below and the unchanged tables/supplement. Nothing is rescored or resampled.
4. **Related Work — Section 2.** Describe transaction, curated-provenance and reenactment precedents without ending each paragraph with the current contribution. Consolidate positioning at the end of the first subsection. Retain explicit acknowledgment of Guided Data Repair, Falcon, DBWiki, version-specific approval and Continuity Kernel; no new search or literature expansion.
5. **Conditional scope — Section 9.2.** Refer readers to the complete model/scope paragraph in Section 3 and selected-projection boundaries in Section 6 instead of restating every qualifier. Keep finite Alloy scopes, selected correspondence, all real trust/validity boundaries and the E3 cost caveat.
6. **Plain prose — Sections 2 and 9.1.** Replace “These layers establish different aspects ...” with what the paired histories, model checks, projections and E2/E3 actually check. No broad sentence-by-sentence rewrite.

## Main locations for support counts

| Count | Primary main-text location | Meaning retained |
|---|---|---|
| 72 Alloy outcomes | Section 8.1, formal and persisted support; detailed profiles in Table 3 | Outcomes matched their manifests within finite scopes |
| 20 mapping mutants / nine intended projections | Section 6 | Mapping sensitivity and selected correspondence |
| 35 catalogue cases | Section 6; abstract overview | Five legal and thirty failure/control cases, with results in Section 8.1 |
| 85 regressions / ten harness checks | Section 8.1 | Equality-repaired execution support, distinct from retained checks |
| 495 executions | Section 8.1 | Completion total; input/family/mechanism design remains in Section 7.2 |
| 60 browser cases | Section 7.3 (“sixty”); per-path outcomes in Table 5 | Local fixture coverage and separate outcomes |
| 22,400 timed calls | Section 7.4 | Complete timing denominator, warmups excluded |

The two uses of 35 in the abstract and catalogue definition are intentional. Design dimensions remain in Methods and the detailed evidence tables; the reduction targets repeated narrative scorecards, not reproducibility information.

## Three protected narrative choices

- Introduction: “Content/context equivalence does not make an unreviewed substitute the same authorization target.” Retained verbatim.
- E1: instance and value/context policies are evaluated on their own terms, including 15 extra exact-policy rejections under the looser policy. Separator/result paragraphs retained verbatim.
- Discussion: “What the results establish” precedes the consolidated “Trust and validity boundaries.” Structure retained.

## Figure 2

The existing deterministic script and layout are reused. Displayed counts come from archived E1/E2 tables; the 165 per-mechanism denominator is parsed from the comparator caption and checked. The 22,400 total is still computed from all three CSV summaries and validated, although no longer a figure headline. Neither Figure 1 nor any experiment table/CSV is changed. Figure 2 retains policy-neutral admitted/rejected wording and the extra-rejection interpretation. The existing caption and AI disclosure identify the assistance and renderer. Vector PDF/SVG and 300-dpi PNG were regenerated; overflowing card text was shortened and checked before compilation. This is an evidence-route figure, not a new Graphical Abstract.

## Verification and build

All contract content except the bridge remains verbatim. Abstract/title/authors, RQs, bibliography, disclosures, realization, formal analysis, conformance and conclusion remain unchanged. E1's separator/policy interpretation and all E2/E3/historical results remain verbatim. All 17 table/CSV files and 27 protected science assets outside the declared Figure-2/script exception remain byte-identical. Removed support-count mentions retain their original meanings and primary locations.

The final main manuscript compiled with the author's local MiKTeX installation. The initial build reached a clean PDF but WPS prevented copying it to `main.pdf`; after the file lock cleared, the final rebuilt PDF was copied and its SHA-256 checked. Supplement sources/PDF remain byte-identical; its earlier clean compilation record is retained. Final logs show no unresolved references/citations, LaTeX warnings, overfull or underfull boxes. All 26 bibliography entries are used, with no missing keys. Fonts and margins remain unchanged.

All 33 main pages were visually inspected in contact sheets, with the bridge, evaluation opening, evidence figure, related work and discussion enlarged. No clipping, overlapping labels or accidental blank pages remained. LaTeX production score: **100/100, PASS** for the checked compilation/reference/layout criteria; this is not a novelty or acceptance score.

Main: **33 pages**, 8,656 extracted PDF words (previously 8,720). Supplement: **21 pages**, unchanged. The net reduction in section prose is **50 English words**, using the same extraction before/after and excluding figures, tables, equations and citations. The aim is clearer hierarchy and less repetition; no page-reduction target is imposed.

## Section counts

| Section | Before | After | Reduction | Scientific claim changed |
|---|---:|---:|---:|---|
| 01-introduction.tex | 395 | 393 | 0.5% | No |
| 02-related-work.tex | 748 | 685 | 8.4% | No |
| 03-problem-contract.tex | 1303 | 1318 | -1.2% | No |
| 04-relational-analysis.tex | 309 | 309 | 0.0% | No |
| 05-transactional-realization.tex | 378 | 378 | 0.0% | No |
| 06-formal-concrete-conformance.tex | 297 | 297 | 0.0% | No |
| 07-evaluation-protocol.tex | 640 | 656 | -2.5% | No |
| 08-results.tex | 700 | 698 | 0.3% | No |
| 09-discussion-threats.tex | 570 | 556 | 2.5% | No |
| 10-conclusion.tex | 159 | 159 | 0.0% | No |

Abstract unchanged (202 prose words). Negative reduction denotes a short addition for the requested bridge or study hierarchy. Machine-readable checks and PDF hashes are in `micro-revision-check.json` and `final-build-check.json`.
