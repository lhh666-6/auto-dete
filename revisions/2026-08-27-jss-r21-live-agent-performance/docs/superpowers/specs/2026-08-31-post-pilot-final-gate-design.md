# Post-Pilot Final Gate Design

## Purpose

Close the gap between a complete non-citable Pilot and a citable Final run. The existing resource
decision and freeze primitives are correct but are not joined by a stable operator-facing command,
and the Final runner does not yet require a verified `FROZEN.json` before a provider call.

The approved overall benchmark plan already requires this gate. This addendum chooses the smallest
implementation that makes that requirement executable without changing Pilot-1, Pilot-2, Pilot-3,
or any R17--R21 evidence.

## Considered approaches

1. **Document manual Python calls.** Smallest code change, but it leaves path selection, input
   binding, and write ordering to an operator. A copy/paste error could create an invalid Final.
2. **Add a narrow post-Pilot CLI plus mandatory Final freeze verification.** Recommended. It joins
   existing primitives, refuses overwrite, records input hashes, and still keeps execution separate.
3. **Build one monolithic command that gates, freezes, and immediately runs Final.** Rejected because
   it collapses the pre-result freeze boundary and could make an accidental provider call.

## Architecture

`post_pilot.py` is a non-networked orchestration layer. It verifies a complete Pilot manifest,
checks that the normalized ledger covers the locked plan, reads the qualification file, derives
latency and failure-rate resource rows, combines them with a separately supplied provider-credit
attestation, and writes an append-only `FINAL_RESOURCE_GATE.json`. A blocked decision writes only
the gate. A passing decision may then create a new Final configuration with the existing
`build_final_configuration` primitive.

`freeze.py` gains a narrow staging function that copies only the benchmark runtime source,
dependency locks, selected implementation runtime inputs, and generated Final configuration into a
new root. It then writes a non-self-referential `FROZEN.json` with pre-execution runtime metadata.
Caches, environments, raw Pilot records, prior evidence, and secrets are excluded.

`runner.py` requires `--frozen-root` for every live Final command. It verifies `FROZEN.json` before
dispatch and again after the phase runner returns. Dry runs remain network-free and do not require a
freeze. Pilot behavior and the Pilot launch lock remain unchanged.

## Data and trust boundaries

- Pilot scientific result rows are used only to prove ledger completeness; the resource decision
  receives only qualification eligibility, latency, runtime-failure rate, and explicit credit.
- Provider-credit attestation is an operator fact, never inferred from favorable Pilot outcomes.
- All output roots are create-only. A `BLOCK` result cannot create Final configuration or source
  freeze files.
- The Final output root remains outside the frozen source root, so Final evidence cannot alter the
  source manifest.
- The freeze contains no provider token or environment secret.

## Failure behavior

The command fails closed on an incomplete or tampered Pilot, roster mismatch, malformed credit
attestation, contaminated resource row, nonpassing gate, existing destination, incomplete source
allow-list, or frozen-manifest drift. No failure path starts a provider call. Failed staging is
preserved with a failure marker rather than cleaned or overwritten.

## Verification

Tests are written and observed failing before implementation. They cover a complete passing Pilot,
an incomplete/tampered Pilot, a blocking credit attestation, no-overwrite behavior, allow-list
exclusion, freeze tamper detection, and Final runner rejection before a live runner can be called.
The final gate is the full test suite, Ruff, a 112-run zero-call Pilot dry run, and a frozen Final
dry run whose plan count matches the selected gate.
