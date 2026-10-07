# Completed deployment-A follow-up integration

Author instruction (7 October 2026): contribution-first narrative; original 512-arm main analysis remains unchanged; the 117 selected deployment-A pairs form a separately frozen supplementary paired evaluation. Explain selection once in methods, report additional knowledge in results, and distinguish original B from follow-up A in plots. Do not pool the batches into one success rate or new independent-task count.

## Scope and responsibilities

- Independent analysis: rescore all 234 supplementary planned arms with the frozen original scorer, retain failures and attempt histories, verify manifest/task/source identity, report separate cohort estimates and provenance. Analysis package: `research/phase2-followup-analysis-2026-10-07`.
- Paper integration: update abstract, one methods paragraph, compact coverage table, short results subsection, S12 and scope wording, while retaining original estimates and all nine main sections.
- Figure: one comparison of original B and follow-up A with explicit denominators and sources; keep original figures available.
- Root: archive all completed raw recovery records, compile and inspect both documents, verify numbers and package consistency, preserve the cloud revision and original datasets, publish the completed handoff if Git permissions permit.

## Verification gates

1. Recovery ledger COMPLETE with exactly 117 selected pairs / 234 planned arms; no missing or substituted assignment.
2. Frozen input/scorer and original result hashes unchanged; all raw attempts retained.
3. Independently scored tables agree with authoritative events/states, with any mismatch explicitly investigated.
4. Main original result tables remain unchanged; supplemental summaries use their own denominators.
5. New supplementary uncertainty estimates are labeled as the separately reported, selected-cohort application of the method, rather than a newly preregistered primary result.
6. Final TeX sources compile, references resolve, all pages/figures inspected; source ZIP and receipts match the final PDFs.

## Status

- Collection completed 2026-10-07 17:46:49 Asia/Shanghai.
- Independent scoring, manuscript integration and comparative figure complete.
- Supplementary analysis: 18 tests, 468 exact score comparisons and 7,989 event validations pass. Sensitivity routing: 3 tests pass. Original evidence: 29 checks pass.
- Main and supplement compile successfully (13 and 28 pages), with no unresolved references or overfull boxes. Final receipts identify the current PDFs and package; detailed visual findings are in FOLLOWUP-PDF-QA.md.
