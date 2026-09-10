# Current manuscript — post-r28 human-annotation integration

Source handoff tag: `r28-jss-2026-09-10`. Current integrated candidate: main 59 pages; supplement 16 pages; 54 citations.
The submission PDFs are compiled from `paper/main.tex` and `paper/supplement.tex`; edit the LaTeX sources rather than the PDFs.

Second author Xuan Wentao (X.W.) completed a blinded author annotation of all 325 textual-acknowledgment outputs and recorded a rationale for every label. The resulting human--rule agreement analysis is integrated into the manuscript and supplement, while the 39 disagreements remain unadjudicated and the frozen rule-hit labels are unchanged. The separate benign-endpoint annotation still comprises X.W. and one non-author volunteer, with adjudication by the first author; its 11 terminal-completion versus strict-trajectory disagreements remain visible. No hosted-model call was rerun.

The new evidence archive is `evidence/human-acknowledgment-annotation-2026-09-10/`; it contains the completed workbook, frozen joined inputs, hashes, normalized labels, all disagreements, deterministic analysis code and tests, bootstrap summaries, and the exact reproduction command. The earlier r28 handoff checks remain documented in `evidence/r28-handoff-verification/verification.json`.

Fresh post-r28 checks: 325/325 annotation rows matched once; 7 integration/manifest tests passed; the full Python implementation suite passed 389/389; 19 formal witness tests passed; the archived batch package structure gate passed; both LaTeX PDFs compiled with no errors, undefined references/citations, multiply defined labels, or overfull boxes. See `evidence/human-acknowledgment-annotation-2026-09-10/FINAL-VERIFICATION.md`.

The original 1,260 model-run records remain frozen. Performance describes the v8 snapshot. Old dated reports are historical, not the current verification summary. The current manifest retains the filename `MANIFEST-r27.json` for compatibility and identifies this post-r28 integration in its revision field.

Use new output paths outside this sealed tree for reruns. Formal gate, from this directory: `./formal/alloy/batch/verify_batch_package.ps1 -RequireRawResults`. Witness tests, from code/formal-fixed/: `python -B -m unittest discover -s tests -v`. Full package verification is one directory above.
