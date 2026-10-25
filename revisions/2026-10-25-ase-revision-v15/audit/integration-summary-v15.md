# v15 integration and validation

Prepared 25 October 2026 after the author's requested GPT-6.1 Sol medium-effort collaboration. Four sub-agents handled the checker/supplements, manuscript, packaging/navigation and independent validation. The integrating agent reviewed changes, reproduced the equality checks, built the PDFs and tested the extracted packages.

## Scientific scope

The correction is to a derived auxiliary observation checker. The historical `c6d5128` source, v14, and all seven experiment ZIPs are preserved. The new checker encodes value/discriminator observations and validates history connections/endpoints using the declared canonical JSON comparison. Its local outcome function remains conditional on a well-formed history; rejecting the malformed endpoint is a domain check, not a new production admission result.

All 38 new regressions and the seven preserved witness/control constructions pass. The portable test reads a bundled byte-exact original blob after hash verification, requires no Git, and can write to a separate output file. Original experimental totals and the 32/24/8 observations remain unchanged.

The paper now distinguishes policy-defined admission, interface-defined route minima and observed route/confirmation choices. The RefineAct comparison acknowledges its existing recovery measurements without comparing incompatible success rates. Re-preview's matching-grant requirement is scoped to instance binding. AI-assisted preparation now covers actual manuscript and verification-code assistance. Online Resource 3 identifies the current source revision separately from the historical experimental freeze.

## Validation

- The independent review, including extra checks and its limitations, is in `independent-validation-v15.md`.
- `build-v15.json` records final local TeX Live 2025 diagnostics and PDF identities. There are no undefined references, unresolved `??`, or overfull boxes. Underfull spacing messages are preserved rather than suppressed.
- `packaged-source-validation-v15.json` records a clean-extraction rebuild of the single-entry manuscript and the full three-document source package. Every page's extracted text and 72-dpi rendered pixels match the distributed PDFs; the extracted checker regression passes.
- That receipt lists compilation/checker input hashes rather than its containing archive hash, avoiding a self-reference. Adding this audit narrative to the final source ZIP does not change the validated compilation inputs. Final packaging validates every current member and payload hash.
- The initial clean-package check exposed an implicit bibliography-style dependency. `sn-basic.bst` is now included explicitly with `sn-jnl.cls`; the corrected extracted package was rebuilt successfully.

## Delivery state

The scientific upload set contains the main PDF, a single-entry manuscript-source ZIP, two supplementary PDFs and Online Resource 3. It is mirrored under `submission/ASE-2026-10-25-v15/ready-to-upload/`. The old cover letter is not reused. Preparing these files neither submits the article nor confirms a prior withdrawal. The author should review the revised scientific text and factual declarations before submission.

No new hosted study, API experiment, complete Alloy rerun or production-gate security audit was performed in this revision. No Git commit, push or journal submission is part of this integration step.
