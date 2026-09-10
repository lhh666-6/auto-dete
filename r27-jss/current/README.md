# Current manuscript — r28 coauthor handoff

Fixed tag: `r28-jss-2026-09-10`. Main: 58 pages; supplement: 15 pages; 54 citations.
Read [the handoff](../SECOND-AUTHOR-HANDOFF-zh.md) first. Edit paper/main.tex, paper/sections/, and paper/supplement.tex.

A1 is the second author; A2 is a non-author volunteer; the first author adjudicated disagreements. The 11 terminal-completion versus strict-trajectory disagreements remain visible. No new annotations or hosted runs were made for this handoff.

Fresh checks: 19 witness tests; nine approval-log cases reproduced exactly; agreement statistics reproduced exactly; S1 positive Alloy check UNSAT and its mutant SAT; archived 68-command package structure gate passed. Implementation/test Python sources match r26; its 389-test result is inherited, not a fresh full-suite run. See evidence/r28-handoff-verification/verification.json.

The original 1,260 model-run records remain frozen. Performance describes the v8 snapshot. Old dated reports are historical, not the current verification summary. The current manifest retains the filename MANIFEST-r27.json for compatibility and identifies r28 in its revision field.

Use new output paths outside this sealed tree for reruns. Formal gate, from this directory: `./formal/alloy/batch/verify_batch_package.ps1 -RequireRawResults`. Witness tests, from code/formal-fixed/: `python -B -m unittest discover -s tests -v`. Full package verification is one directory above.
