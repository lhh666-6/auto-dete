# Final polish: integrated PDF visual QA

Date: 2026-10-07. Verdict: **PASS for the reviewed final PDFs; no blocking layout defects found.** Read-only review; this report is the only file changed by this QA task.

## Frozen files and actual coverage

| PDF | Pages | SHA-256 |
|---|---:|---|
| `main.pdf` | 11 | `5e45e768563b18c431ffb52121fdb3792252ef60425e1c0ca0feed32c363b9a3` |
| `supplement.pdf` | 29 | `eb268629c4bb95b3b6a847c47e064870ddbefcec58e3c5b38f35bdad233b8b8e` |

All **40 pages** were visually inspected in the newly regenerated contact sheets: `qa/final-polish/main-sheet-1.png` through `main-sheet-2.png`, and `supplement-sheet-1.png` through `supplement-sheet-5.png`. Enlarged individual-page inspection covered main pages **1, 2, 3, 7, 8, 9, 10, 11**, and supplement pages **1, 21, 22, 26, 27**. This is complete overview coverage plus targeted reading, not a claim that every page was enlarged or every sentence proofread.

Only the 11 main pages and 29 supplement pages reported by the current PDFs were counted. The stale `qa/final-polish/main/page-12.png` was excluded. All expected current page PNGs exist, and their modification times postdate their respective PDFs. Final hashes were rechecked after inspection and match the values above.

## Verified presentation

- **Contribution continuity:** main pages 1–2 present the four contributions without a figure inserted between them. The ordinary page break divides contribution 2, whose sentence continues directly at the top of page 2; contributions 3–4 and the compact findings paragraph follow. Reading order is clear.
- **Three main figures:** Figure 1 is on page 3, Figure 2 on page 7, and Figure 3 on page 9. Each figure and its caption is complete and readable, without clipping or overlapping text.
- **Figure 1 semantics:** four role cards have no step numbers or serial arrows. The review region groups authorized correction with reviewed instance. The diagram and caption explicitly retain proposal 100, authorize 101 from reviewed c1, distinguish equivalent c2 by identity, and state the context/bound/new-authorization distinction.
- **Figure 2 semantics:** the right-hand feedback/action loop visibly states “Executed independently in each arm.” The isolated policy continuations, feedback, next action, observed path and outcome oracle remain legible.
- **Figure 3 counts and denominators:** original B and supplementary A are separate rows. Delivered G coverage is 16/16 and 15/15; reuse is 16/16 versus 8/15, with 7/15 supplementary reauthorizations. Joint outcomes are 16/16 and 15/15 with U=1, I=1. Calls are explicitly means (+1.00, +1.60), time is explicitly median (+14.54 s, +14.53 s), and paired n is 16 and 15. The context footer retains 14/16 and 15/15 completion. The caption agrees and states that costs cover the complete suffix. No pooled cross-cohort rate is displayed.
- **Main Table 2:** all six cohort/policy rows fit on page 8. Planned pairs and checkpoint counts, all four joint cells, unknown integrity and task completion are readable. The caption defines CP and attributes both unknown N arms to original B. No column is clipped.
- **Results and shortened discussion:** main pages 8–10 retain the numerical cost results and uncertainty/scope qualifications. The cost discussion continues across pages 9–10 without a missing line or figure interruption.
- **Formal bibliography entries:** main page 11 includes all 20 numbered entries. The three added references appear as entries 15–17, with authors, year, titles, versioned arXiv identifiers and DOI URLs. Main page 2 uses the corresponding [15], [16], [17] citations. This confirms rendered citation presentation, not a new external source-fidelity audit.
- **Moved figures:** the evidence-chain diagram is Figure S1 on supplement page 1 in Section S1. The original recovery diagram is Figure S3 on page 21 in Section S11, alongside the original outcome Figure S2. Their captions and labels are complete. “S11” is the section placement, not the recovery figure number.
- **Supplement tables:** original outcome/recovery tables on page 22 and supplementary outcome/recovery/cost tables on pages 26–27 were enlarged and checked. Headers, wrapped cells, denominators and final rows fit. The all-page overview shows the continuation of Table S15 on page 23 and the remaining cost table S14 on page 24.

## Nonblocking layout observations

1. Table S15 spans supplement pages 22–23 before floating Table S14 appears on page 24. All tables are present and labeled; this is a float-order inconvenience, not missing content.
2. Caption-to-top-rule spacing is tight for Table S12 on page 22 and Table S18 on page 27. At enlarged inspection the ink does not overlap and the final caption lines remain readable.
3. The supplement retains some spacious float pages, notably the checklist on page 9 and two short tables on page 13. No repair is needed for completeness or legibility.

## Supporting checks and limits

PDF text-coordinate checks found **zero words outside either page rectangle**, **zero `??` markers**, and **zero Unicode replacement characters**. The current `out/main.log` and `out/supplement.log` each contain **zero overfull warnings and zero undefined citation/reference warnings**. The main PDF's dominant prose size is approximately 10 pt; the supplement's is approximately 11 pt. The visual review did not find crowded body typography introduced by the reduction from 13 to 11 main pages.

These mechanical checks supplement the visual review; they do not establish mathematical correctness, reproduce experimental results, or replace the separate evidence and figure-source audits. No additional source or layout changes are requested for release of these exact reviewed PDFs.
