# Final polish: integrated PDF visual QA

Date: 2026-10-07. Review-closure update. Verdict: **PASS for the exact PDFs below; no blocking layout defects found.** This report supersedes its earlier 11-page-main inspection. This QA task changed only this report.

## Files and actual inspection coverage

| PDF | Pages | SHA-256 |
|---|---:|---|
| `main.pdf` | 12 | `bc7ccac7e6496fcc5c1069111c85db9173164825275e4b9e8257b139f950d532` |
| `supplement.pdf` | 29 | `2e47b8537dd2c45bb078a5ac31d112ec70b1e0dbda3d5c89a6a8407a60592a7b` |

All **41 pages** were visually inspected through the current `qa/review-closure/main-sheet-1.png`–`main-sheet-2.png` and `supplement-sheet-1.png`–`supplement-sheet-5.png`. Enlarged individual-page inspection covered main pages **1, 2, 3, 4, 7, 9, 11, 12**, and supplement pages **6, 8, 9, 10, 11, 21, 27, 29**. This is full overview coverage with targeted reading; it is not a claim that every sentence was proofread or every page enlarged.

The current PDFs determine the page counts. Earlier QA folders were not used for this review. Every expected current page PNG exists and postdates its PDF. Hashes were checked again after the targeted inspection and remained unchanged.

## Review-closure additions

- **Comparison table:** new main Table 1 is complete on page 3, below Figure 1. All five rows, three columns and citation numbers are readable. The table's main text is approximately 9 pt. Its caption explicitly identifies a conceptual comparison rather than a cross-system benchmark. The Continuity Kernel row visibly includes proposal identity, and the Commit-time authorization row includes witness-revalidation recovery. No column clipping, rule/text collision or truncated row was found.
- **Main example:** page 2, Section 3.1, presents the quantity-90/batch-B-008 record, proposal 100, authorization 101, retained batch source, unchanged proposal and receipt/replay distinction. The paragraph fits completely before the page break. Page 3 continues with canonical JSON equality and visibly distinguishes integer 101 from floating serialization 101.0.
- **Supplementary example:** Section S3 is readable across pages 8–9. It separates the explanatory construction from measured cases, preserves the exact unchanged source, explains candidate substitution, concurrent predecessor invalidation and consumed-grant replay, and states that a typed adapter would require shared semantics and renewed validation. The ordinary page break divides the typed-adapter sentence; its continuation is present at the top of page 9.
- **Scope:** main page 4 explicitly limits the multi-field guarantee to one record and states that cross-record/distributed atomicity is not validated. Supplement page 11, Section S4.2, states that the record-count dimension is background population for trace access rather than cross-record atomicity. Section S4.3's storage-population boundary is intact below it. The existing authorization timing/revocation qualification on supplement page 6 is also readable.

## Retained presentation

- **Contributions precede the first figure.** Main pages 1–2 contain all four contributions and the findings paragraph before Figure 1 on page 3. Contribution 2 continues normally across the page break; no figure interrupts the list.
- **All three main figures remain complete.** Figure 1 is on page 3, Figure 2 on page 7 and Figure 3 on page 9. Each figure and caption was enlarged and checked. Figure 1 retains the review grouping without numbered chronology. Figure 2 visibly labels the feedback/action loop “Executed independently in each arm.”
- **Behavioral figure and denominators:** Figure 3 retains separate original B and supplementary A rows: delivered G coverage 16/16 and 15/15; reuse 16/16 versus 8/15; supplementary reauthorization 7/15; successful intact joint outcomes 16/16 and 15/15. Mean calls (+1.00, +1.60), median time (+14.54 s, +14.53 s), paired n (16, 15), and context completion (14/16, 15/15) remain legible and consistent with the caption.
- **Six-row outcome table:** now main Table 3 on page 9, above Figure 3. All cohort/policy rows and joint-outcome columns fit. The caption defines planned pairs and checkpoint counts and attributes the two unknown N arms to original B.
- **References:** all 20 numbered entries are present across main pages 11–12. Entries 15–17 retain full author/title/preprint/DOI information. The comparison table cites these entries and LangChain [1] correctly in the rendered document. This checks presentation, not a new external citation-fidelity audit.
- **Supplementary figures and tables:** Figure S1 remains on page 1; Figures S2 and S3 are complete on page 20 in Section S11. All 19 supplement table captions appear in extracted text and their pages were included in the visual overview. Targeted checks included the example checklist, cost-grid pagination and original/supplementary tables with close caption spacing.

## Remaining nonblocking layout observations

1. **Long-table pagination:** Table S9 starts with its caption, header and one data row at the bottom of supplement page 10; the remaining rows continue with repeated headers on page 11. This is less convenient than keeping more rows together, but no row or label is missing.
2. **Float order:** Table S15 spans supplement pages 21–22, before Table S14 appears on page 23. All content is present and labeled.
3. **Caption spacing:** the final caption lines lie close to the top rules in Table S12 (page 21) and Table S18 (page 27). Enlarged inspection shows readable text without ink overlap.
4. **Final-page whitespace:** main page 12 contains the remaining references in the left column; supplement page 29 contains the final reproduction command and closing lines. The whitespace is a pagination effect, not evidence of missing content.

These observations do not prevent reading or release of this review draft. No additional source changes are requested by this QA.

## Mechanical checks and limits

For each PDF, text-coordinate diagnostics found **zero words outside the page rectangle**, **zero `??` markers**, and **zero Unicode replacement characters**. The current `out/main.log` and `out/supplement.log` each contain **zero overfull warnings and zero undefined citation/reference warnings**.

These checks support the visual findings but do not prove mathematical correctness, reproduce experiments, or replace the separate evidence and source-comparison audits. The report applies only to the PDF hashes recorded above.
