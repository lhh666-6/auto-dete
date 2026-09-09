# Quota-aware checkpoint execution design

## Decision

Quota-limited OpenAI benchmark work advances by at most one new provider invocation per command.
The command preserves the complete frozen phase plan, writes one terminal run record, records an
append-only incomplete-phase checkpoint, and stops. A later `--resume` invocation verifies the
same frozen configuration and run plan, skips every terminal run, and advances the next missing
coordinate. DeepSeek and offline validation may use the same mechanism or run separately.

## Invariants

- `planned-runs.jsonl` always contains the complete selected locked plan; checkpointing does not
  shrink or regenerate it.
- Existing terminal run records, failed runs, and historical Pilot-1 evidence are immutable.
- An incomplete phase has no `normalized/`, qualification result, phase report, or manifest.
- Each incomplete stop adds `checkpoints/NNNN.json`, where `NNNN` is the terminal-run count.
- Final normalization, qualification, reporting, and manifest creation occur only when every
  planned coordinate is terminal.
- The frozen retry policy is executable rather than documentary. For quota-limited Pilot-2 it
  sets `max_transport_retry` to zero, so one logical run cannot consume a hidden second call.

## Interface and result

The live runner and CLI accept `max_new_invocations`, exposed as
`--max-new-invocations 1`. A partial command returns an `INCOMPLETE` checkpoint object containing
the phase, planned count, terminal count, remaining count, and number of new invocations. Values
less than one are rejected.

## Verification

Tests must first demonstrate that the current runner lacks the option, normalizes prematurely,
and ignores a zero-retry frozen policy. The implementation then passes tests proving one-run
advance, exact resume behavior, absence of premature derived artifacts, full-plan preservation,
and a single provider call after a pre-semantic transport failure.
