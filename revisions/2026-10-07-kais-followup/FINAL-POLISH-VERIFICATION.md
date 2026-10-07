# Final editorial pass — verification

This pass implements the author's supplied writing and presentation review. It reduces duplication, separates the roles of the main figures, corrects two visual ambiguities and formalizes three existing literature comparisons. It does not add or alter experimental results.

## Delivered structure

| Item | Previous integration | Final editorial pass |
|---|---:|---:|
| Main article pages | 13 | 11 |
| Main figures | 5 | 3 |
| Abstract words, whitespace-delimited | 204 | 183 |
| Numbered references | 17 | 20 |
| Supplement pages | 28 | 29 |

The contribution list and findings summary occur before the first large figure declaration. Ordinary page continuation is retained; figures do not interrupt the contribution passage. The three main figures explain the continuity relation, independent policy continuations and the original-B/supplementary-A comparison. The evidence-chain figure and original-only recovery figure are retained in S1 and S11.

The conceptual figure now uses unnumbered roles and groups the reviewed instance with its authorized correction. The online-loop diagram explicitly states that the procedure executes independently in each arm. Existing fonts, line spacing and scientific values are unchanged.

Methods retains the supplementary selection rule and collection relationship; the statistical section retains the separate estimands and exploratory interpretation. Results, Discussion and Conclusion lose repeated provenance explanations and definitions while retaining cohort labels and denominators. Continuation cost is distinguished from the cost of an isolated repair action.

## Scientific preservation and citations

- All 126 archived evidence/baseline files checked against the previous package match byte-for-byte, apart from the separately regenerated manuscript-verification receipt, which is excluded from that count.
- All eight main and two supplementary display-equation blocks are identical to the preceding version.
- Both main result-table blocks and all nineteen supplementary table blocks are identical.
- The prospective Methods section and author declarations are unchanged.
- The original, supplementary and post hoc sensitivity numbers are unchanged. This pass makes no provider/model calls and performs no new experimental analysis.
- The original evidence verifier passes all 29 checks with the updated 20-reference expectation.
- All 20 cited keys have exactly one bibliography entry; there are no unused or missing entries.

Primary arXiv records and full texts support the three existing descriptions of Cordon, Continuity Kernel and commit-time authorization. Each is formally entered as a 2026 preprint. No conference acceptance or published successor is inferred from template headers. Metadata, source links and the limitations of reference-manager checks are recorded in `FINAL-POLISH-CITATION-AUDIT.md`.

## Compilation and visual review

Both documents compile using the existing MiKTeX pdfLaTeX installation, with three passes for the final sources. There are zero unresolved references/citations, overfull boxes, missing-glyph warnings or extracted `??` placeholders. The app's built-in compiler remains unavailable because it cannot locate its standard directories; no compiler was installed.

All 40 pages are rendered under `qa/final-polish/`. `FINAL-POLISH-PDF-QA.md` identifies the actual page inspection and final PDF hashes. `FINAL-POLISH-FIGURE-QA.md` verifies the changed figure semantics, vector structure, embedded fonts and deterministic exports. `QA-RECEIPT.json` records the machine checks and source/PDF digests.

| Scoped build metric | Result |
|---|---|
| LaTeX build/spacing diagnostic score | 89 / 100 |
| Rubric verdict | Revise — spacing polish remains |
| Deductions | 19 underfull hbox diagnostics, capped at -10; third final compilation pass, -1 |

This narrow score concerns typography and build behavior, not scientific merit or acceptance likelihood. No font or line-spacing compression was used. Remaining underfull diagnostics are retained for transparency; this is an editable review draft, not a claim of completed publisher-template conversion or author sign-off.

The earlier FOLLOWUP reports are explicitly marked as historical integration audits. Their scientific provenance remains available; current layout and packaging are certified by the FINAL-POLISH reports and current manifests. The source ZIP is verified by CRC and every member's SHA-256 before publication to the existing handoff branch.
