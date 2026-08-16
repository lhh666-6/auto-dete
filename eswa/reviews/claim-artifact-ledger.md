# Claim--artifact ledger

## Empirical claims

All quantitative recognition claims derive from `artifacts/recognition_summary.json`; no value was transcribed from a screenshot. Latency claims derive from `artifacts/resilience.json`. Fault-containment claims derive from `artifacts/trust_faults.json`. Plot and table files are generated from these JSON artifacts, and the copied files match the hashes recorded in `artifacts/manifest.json`.

## Architectural claims

The machine-to-fact invariant is scoped to exposed application services. Supporting code paths persist recognition attempts and AI reviews separately, restrict export to confirmed records, reject stale expected versions, reject duplicate evidence, and provide reverse trace. The paper explicitly excludes privileged database modification, host compromise, confidentiality, availability, and human decision correctness from the guarantee.

## Claims intentionally not made

- No state-of-the-art recognition claim.
- No zero-risk claim.
- No real-production accuracy, speed, cost, wage, or organizational-effect claim.
- No FastAPI, React, PWA, authentication, or RBAC implementation claim.
- No Tesseract comparison because the executable was unavailable.
- No general security certification or exhaustive penetration-test claim.
