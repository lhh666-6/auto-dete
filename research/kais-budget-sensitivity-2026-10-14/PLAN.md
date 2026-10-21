# Budget sensitivity implementation plan

Goal: complete the user-approved 24-task, four-condition continuation study with preserved source evidence and a reproducible offline analysis.

Architecture: an isolated copy of the formal host, event audit and scorer; a thin checkpoint-to-arm runner; a separate analysis consuming the fixed allocation and raw records. All writes stay in this study directory. No Git push or submitted-manuscript edits.

- [x] Runner: tests first for balanced allocation, identical budget-arm inputs, inherited repair allowance, request budget, failures/resume and freeze protection. Implement `run.py`, `test_run.py`, `vendor/` and provenance notes. Do not use the six-step feedback-pilot loop.
- [x] Analysis: tests first for four-condition contrasts, missing-cell bounds, independent score verification, raw truncation/usage reconciliation, all-terminal timing and stratum/task denominators. Implement `analysis.py` and `test_analysis.py`; no API calls.
- [x] Preflight: run both test suites and deterministic scenario probes, check source hashes and compare first messages/wire bodies across budgets. Resolve blockers before any online call.
- [x] Freeze: include protocol, implementation, analysis, allocation, configurations and all source/checkpoint manifests; record the master hash and UTC timestamp. Verify freeze before every resumed collection.
- [x] Collect: one lane, frozen task/condition order, exactly 96 planned arms; retain every attempt and stop on infrastructure/configuration or audit blockers.
- [x] Verify and report: independently reconstruct scores, compare all raw request budgets and response counts, verify source protection and freeze, write RESULTS.md and a short reviewer-facing summary. Add the completed evidence to the revision index only after verification.

Validation uses the local Python311 runtime with `-B`; no original __pycache__ or archived outputs are modified. The protocol is the pre-analysis authority; this checklist tracks implementation only and is not itself an experimental outcome.
