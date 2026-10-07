> Historical report for the completed-follow-up integration at commit `7fe3a4ec2c18126440e631eb0a5b69e8725f801c`, before the final editorial pass. Current layout, citation and packaging verification is in `FINAL-POLISH-VERIFICATION.md`; the reported scientific data remain unchanged.

# Final integrated PDF visual QA

Date: 2026-10-07. Verdict: **PASS — no blocking visual defects found**.

This was a read-only review of the rebuilt PDFs and their current rendered pages. Only this report was written. It does not replace the data, claim, or citation audits.

## Reviewed versions

| Document | Pages | SHA-256 |
|---|---:|---|
| `main.pdf` | 13 | `0bc2181f83f392a728ddba28101db2cc762463aadb5d366510bea1c2eb02045c` |
| `supplement.pdf` | 28 | `09c92cc0d1ac6e3e60d9496eb0f061b1f560478388b338de452356919f11212f` |

All 41 individual PNG renders are newer than their corresponding PDFs. Main and supplementary files were rebuilt at 18:47:26 and 18:47:29 local time, respectively. The report applies to these hashes.

## Actual inspection coverage

All 41 pages were visually inspected in the eight contact sheets:

- `qa/main-sheet-1.png`: main pages 1–6.
- `qa/main-sheet-2.png`: main pages 7–12.
- `qa/main-sheet-3.png`: main page 13.
- `qa/supplement-sheet-1.png`: supplement pages 1–6.
- `qa/supplement-sheet-2.png`: supplement pages 7–12.
- `qa/supplement-sheet-3.png`: supplement pages 13–18.
- `qa/supplement-sheet-4.png`: supplement pages 19–24.
- `qa/supplement-sheet-5.png`: supplement pages 25–28.

The following twelve pages were additionally opened individually at their full rendered resolution:

- Main pages **9 and 10**: six-row cohort table, original recovery figure and caption, new Figure 5 and caption, surrounding cost text.
- Supplement pages **2, 6 and 10**: source-path table, information-class table, dense 36-cell cost grid.
- Supplement pages **20, 21 and 22**: original outcome figure, repaired original joint-outcome table, complete scenario table and continuation, original recovery and cost tables.
- Supplement pages **24, 25, 26 and 27**: complete supplementary outcomes, recovery paths, costs, provenance and reproduction commands, sensitivity source-composition table.

The remaining pages received page-level layout inspection through the contact sheets, not full-size word-by-word proofreading. No unviewed page is claimed as visually reviewed.

## Required checks

| Check | Result |
|---|---|
| Page coverage | PASS: 13 main and 28 supplementary pages present and rendered |
| Clipped content or missing page regions | PASS: none observed |
| Overlapping prose, tables or figures | PASS: none observed |
| Main Table 2, six cohort/policy rows | PASS: all columns and six rows fit within the text width; original A/B and supplementary A remain distinct |
| Figure 5 placement and caption | PASS: complete figure and caption on main page 10, with clear separation from following prose |
| Figure 5 typography | PASS: cohort labels, 16/16 and 15/15 exposure denominators, 8/15 and 7/15 path counts, joint outcomes, and paired-cost annotations readable at the integrated size |
| Figure 5 statistical labels | PASS: +1.00/+1.60 calls explicitly marked means; +14.54/+14.53 seconds explicitly marked medians; paired n=16/n=15 shown |
| Figure 5 cohort distinction | PASS: Original B and Supplementary A separately labelled; caption explicitly states separate reporting |
| Supplement Table S12, repaired original outcome table | PASS: multi-line headers and four data rows fit; checkpoint denominators and both original unknown cells remain visible |
| Supplement Table S15 continuation | PASS: all visible rows fit on pages 20–21 with repeated headers; continuation is not clipped |
| Supplement Tables S16–S19 | PASS: complete counts, paths, paired costs and sensitivity source rows remain legible and inside margins |
| Dense supplementary tables | PASS: enlarged S1, S4 and S9 contain complete visible columns; wrapped paths remain in their cells |
| Page numbering and end matter | PASS: coherent page sequence; main page 13 contains the remaining references and supplement page 28 contains the remaining reproduction instructions |

Figure 5 agrees with the intended comparison: original B has sixteen reuse paths; supplementary A has eight reuse and seven reauthorization paths; all delivered bound episodes reach U=1, I=1. The figure's footer preserves context completion counts of 14/16 and 15/15. Its caption accurately specifies complete-suffix paired differences, avoiding confusion with the number of post-rejection recovery actions.

The corrected original B call wording is visible on main page 9: the sixteen pairs have a **mean and median** of one extra suffix call. It no longer claims that every pair adds exactly one whole-suffix call. The supplementary component discussion also preserves the distinction between full-suffix paired costs and recovery actions alone.

## Nonblocking layout observations

1. **Supplementary table order:** Table S15 appears on pages 20–21 before floating Tables S13 and S14 on page 22. All three are present and correctly numbered. If consecutive physical table order is desired, a float barrier before the S15 longtable would address it, but the current layout has no missing content or ambiguous labels.
2. **Tight caption-to-rule spacing:** Several standard supplementary table captions, most visibly S12 and S18, sit close to their top rules. The text remains readable and no ink collision was observed. A few points of table-caption bottom spacing would be an optional typographic refinement, not a required correction.

The partial final pages (main 13 and supplement 28), and the generous whitespace on supplement page 12, contain expected continuation material. They are not blank or missing pages.

## Supplemental machine checks

Across both PDFs, extracted words did not extend beyond a page boundary. No replacement glyph (`U+FFFD`) or unresolved `??` placeholder was found in extracted text. Every page contains extracted words. These checks support the visual review; they were not treated as a substitute for rendering.

No mandatory source changes are requested by this review.
