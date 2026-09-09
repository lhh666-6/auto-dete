# Pilot launch-lock enforcement design

## Problem

Pilot-2 has a verified preflight lock, but the live runner does not consume it. A later working-tree,
implementation, config, plan, or output-path drift could therefore spend a quota-limited provider
call before the discrepancy is noticed.

## Decision

Add an optional `--launch-lock` live-run argument. When present, dispatch performs a read-only hard
gate before it creates the output root or invokes a provider. Official Pilot-2 commands always pass
this argument; diagnostics may omit it.

The gate verifies:

- lock schema and Pilot phase;
- exact requested output root and first-run/resume state;
- `--max-new-invocations 1` and frozen `max_transport_retry = 0`;
- all four config SHA-256 values;
- the benchmark-source and implementation-source manifest identities and every selected file;
- complete 112-run dry-run identity, including zero model calls and the frozen plan hash.

Any mismatch raises a preflight error before the live runner is called. The lock and manifests are
read-only and no failure is converted into a benchmark run record.

## Boundaries

The enforcement is opt-in at the generic CLI so historical diagnostics and reproduction commands
remain usable. Pilot-2's documented first and resume commands make it mandatory. Final continues to
use its separate `FROZEN.json` verifier.

## Test strategy

Tests first prove that the parser/dispatch lacks lock enforcement. They then cover a valid lock,
config tampering, implementation-source tampering, wrong output root, incorrect resume state, and
the guarantee that the live runner is never called on a failed lock. Full deterministic tests,
Ruff, and the 112-run zero-call dry-run must pass before the lock is regenerated.
