# Claim--artifact ledger

## Empirical sources

- Cell-level accuracy, calibration thresholds, coverage--risk values, and 90-cluster bootstrap intervals come from `artifacts/recognition_summary.json`.
- Whole-form and component-ablation claims come from `artifacts/form_raw.json` and `artifacts/form_summary.json`.
- Import-to-export traceability claims come from `artifacts/form_workflow.json`.
- Controlled fault, direct-write, candidate-isolation, and randomized-stress claims come from `artifacts/trust_faults.json`, `artifacts/trust_ablation.json`, and `artifacts/trust_stress.json`.
- Service-only microbenchmarks and availability checks come from `artifacts/resilience.json` and are reported only in the supplement.
- Tables and plots are programmatically rendered from these JSON files. All 27 copied artifacts reproduce the sizes and SHA-256 hashes in `artifacts/manifest.json`.

## Architectural scope

The machine-to-fact invariant is scoped to the exposed application-service paths. Recognition and AI services persist candidates; retrieval returns references; `ReviewForms.confirm` is the normal fact-creation path and requires an explicit reviewer action with an expected version. The candidate-isolation ablation demonstrates what changes when that wiring is deliberately bypassed.

The guarantee does not cover privileged database modification, host compromise, confidentiality, availability, compromised dependencies, or incorrect human decisions. The paper distinguishes these exclusions from the tested application-level property.

## Claims intentionally excluded

- No state-of-the-art recognition or universal safety claim.
- No claim that 2,610 condition rows are statistically independent.
- No real-production accuracy, speed, cost, wage, or organizational-effect claim.
- No FastAPI, React/Vite, PWA, authentication, or RBAC implementation claim.
- No Tesseract comparison because the executable was unavailable.
- No end-to-end latency claim; the supplemental timing excludes perception, UI, storage-device variance, and human review.
- No claim that zero observed errors means zero population risk.
