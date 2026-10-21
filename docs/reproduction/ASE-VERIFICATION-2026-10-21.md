# ASE deposit verification — 21 October 2026

Result: **PASS for the documented offline route**. Python 3.11.9 on Windows; a new virtual environment with the 18 packages in the pinned offline dependency file passed dependency compatibility checks. A new disposable directory was prepared from the deposited archives and curated source manifest. No hosted-model experiment was launched.

The first preparation exposed a missing dependency: the October 7 original-analysis snapshot required by the later truncation audit. That snapshot is now included unchanged. The complete documented route was then rerun from a new workspace and all 14 commands exited successfully. The initial failure remains recorded in the maintainer's local audit, rather than being recast as a passing run.

- Manifest SHA-256: `ecc1ebf71c7cc795a44a5d150f7d308a41096deb9b9e2c78c48a8ca0df63c31b`.
- [Machine execution receipt](ase-verification-2026-10-21/RUN.json): 14/14 completed steps.
- [Scientific comparisons](ase-verification-2026-10-21/comparisons.json): 25 JSON/CSV outputs matched their deposited reference values. Only the budget summary's generation timestamp is excluded; nested JSON in CSV cells is compared by value.
- [Later evidence](ase-verification-2026-10-21/later-evidence.json): saved ToolGate workflows rescored, uncertain-commit raw audits recomputed, and both OpenTofu saved-run summaries checked against their per-record results.
- [Submission-source check](ase-verification-2026-10-21/UPLOAD-CHECK.json): the one-entry upload ZIP compiles to the same 24-page text and rendering as the reference main PDF. Both supplements remain 29 and 16 pages and match their prior text/rendering. No combined submission ZIP was generated.
- [Publication preflight](ase-verification-2026-10-21/PUBLISH-PREFLIGHT.json): no matches to the listed credential patterns, no credential filenames, and the documented sparse checkout covers every manifest input. This is a targeted check, not a general security certification.

## What passed

The original frozen-readiness check, original analysis, independent supplementary analysis/usage/verification, retrospective sensitivity, event-level recovery decomposition and anchored example, X1/X2 saved-run verification, original-B response-truncation audit, later budget study, saved later-evidence checks, N exposure reconstruction and final scientific comparison all passed. Input hashes were verified before and after the run. Original and supplementary cohorts were kept separate.

The strict public ToolGate result remains **23 PASS and 1 FAIL**, with the original unexpected diagnostic-output failure; its comparison has 24 PASS. The reproduction checks that specific failure and does not suppress arbitrary scorer errors. The 32 delivered G pairs span 16 task definitions and retain 24 reuse/eight reauthorization routes under the paper's deterministic-reviewer conditions.

## Scope and limits

This release verifies saved evidence and computations. It does not claim a new hosted-model collection, fresh native OpenTofu execution, fresh cross-platform ToolGate runtime, or a fresh Alloy/browser/historical-database run. Those supporting layers remain available through the fixed historical routes in the reproduction guide. Runtime installation and raw download need the internet; the analysis itself makes no model calls. PDF metadata can vary across TeX builds.

The manifest excludes root navigation documents and these verification receipts to avoid circular hashes; it includes computational inputs, analysis code and manuscript artifacts. The Git tag fixes the complete deposit, including this report.
