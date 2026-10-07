# Current integrated PDF visual QA

Date: 2026-10-07. Final clarification pass. Verdict: **PASS for the exact PDFs below; no blocking layout defect found.** This report supersedes prior main-PDF hashes and inherits the unchanged supplement inspection.

| PDF | Pages | SHA-256 |
|---|---:|---|
| `main.pdf` | 12 | `f203d9fa4d6f4420c7022c3b49c1f340c8c59bc4a97c75093ca405e78095f9a9` |
| `supplement.pdf` | 29 | `2e47b8537dd2c45bb078a5ac31d112ec70b1e0dbda3d5c89a6a8407a60592a7b` |

## Actual inspection coverage

All twelve current main pages were rendered at 144 dpi under `qa/self-containment/` and visually inspected in its two overview sheets. Main pages **1, 4, 5, 6, 7 and 11** were additionally inspected as enlarged page images. This is complete main overview coverage with targeted reading, not a claim that every sentence was proofread.

The supplement source and PDF are byte-identical to the preceding review closure. Its 29 pages were previously inspected in `qa/review-closure/supplement-sheet-1.png`–`supplement-sheet-5.png`, with enlarged checks on pages 6, 8, 9, 10, 11, 21, 27 and 29. That inspection remains applicable to the same PDF hash. Earlier main renders are historical; the current main inspection uses `qa/self-containment/`.

## Final changes

- **Abstract, page 1:** recovery is attributed to continuations; additional calls are expressly scoped to standardized handoff pairs. All text fits, and the abstract remains within the required 150–250-word interval used by the verifier.
- **Commit boundary, pages 4–5:** the clarified sentence continues across a normal page break. Both its pre-commit limitation and its post-commit response qualification are present and readable.
- **Deployment identities, page 6:** the A alias/CLI version and B alias/interface are legible. The paragraph continues from the left column to the right, preserving the qualification that neither route exposes an immutable model revision.
- **Frozen task and G construction, page 6:** the 3379/3368/3367 task example and the fixed-context/new-identity explanation are complete. The G description ends before the page break; E/V/R descriptions continue normally below Figure 2 on page 7.
- **Reproduction guide and AI declaration, page 11:** the short linked guide label appears in Data and software availability. The PDF contains the exact fixed-tag URL. The 51-word AI declaration is unchanged and does not name Claude. Remote tag resolution is a separate publication check.

## Retained presentation

All four contributions precede Figure 1. The three main figures remain complete on pages 3, 7 and 9. The conceptual comparison remains Table 1 on page 3, the controlled evidence remains Table 2 on page 5, and the six-row outcome table remains Table 3 on page 9. There is no clipping, missing figure region, truncated row or text/rule overlap. All twenty reference entries remain on pages 11–12.

The unchanged supplement retains the previously recorded nonblocking observations: Table S9 continues from page 10 with repeated headers on page 11; Table S15 appears before S14; captions for S12 and S18 lie close to their table rules without ink overlap. Main page 12 retains unused right-column space. Main pages 8–9 show uneven vertical whitespace due to column/page balancing, with no missing content. No additional layout changes were made.

## Mechanical checks and limits

The current main PDF has no extracted `??` markers, replacement characters or words outside page boundaries. Its final log has no overfull or unresolved reference/citation warnings. The supplement retains its prior identical build and PDF checks. These checks support reading and artifact delivery, not mathematical correctness, experimental reproduction or journal acceptance.
