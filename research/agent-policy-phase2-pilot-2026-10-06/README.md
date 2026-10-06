# Phase 2 pilot package

This directory is separate from the manuscript and from the immutable phase-one
artifacts. Original v0.1 design remains in the adjacent design directory.

- `frozen-design/`: approved four-definition v0.2 pilot design and local freeze hashes.
- `src/phase2/`: deterministic host, independent oracle, real provider transports,
  shared-prefix/two-suffix runner, schema/artifact/cross-state audit.
- `tests/`: deterministic engineering and adversarial regression tests; these are
  **not** real model experiment results.
- `reviews/independent-review.md`: fresh-context code review and final retest.
- `preflight/`: retained availability diagnostics and test outputs. Initial network
  timeout/insufficient-balance probes are retained alongside successful connection
  and user-authorized DSH-credential checks.
- `frozen-execution/`: actual inputs, public configurations, tool action interface,
  ordering, environment and source hashes fixed before online pilot.
- `pilot-results/`: eight shared prefixes plus sixteen policy arms, raw provider
  records, complete visible model inputs, hash-chained events, SQLite state,
  before/after snapshots, independently computed scores.
- `PILOT-REPORT.md`: engineering observations and limitations, generated only
  after all sixteen online arms finish.

## Local verification

From the repository root in PowerShell:

```powershell
$env:PYTHONPATH = 'research\agent-policy-phase2-pilot-2026-10-06\src'
python -m unittest discover -s research\agent-policy-phase2-pilot-2026-10-06\tests -v
```

After the pilot finishes, regenerate the engineering audit and report with:

```powershell
python research\agent-policy-phase2-pilot-2026-10-06\build_pilot_report.py
```

The runner intentionally refuses to overwrite the execution freeze or prior raw
results. Do not delete failed arms to create a successful rerun. The pilot driver
has no formal 128-arm acquisition mode. Formal E/V/R workflows and all formal
inputs must be implemented, checked and separately frozen before formal collection.

## Credentials and external setup

OpenAI uses the existing account-backed Codex CLI and the user's already enabled
Windows system proxy. DeepSeek uses the user-authorized DSH API key, stored outside
the repository with Windows user encryption. No key is embedded in prompts,
source code, configs or event logs. The encrypted credential path in public config
is host-specific; external replicators must supply their own API credentials and
update the configuration in a new execution freeze. Immutable model snapshots
and CLI monetary pricing are unavailable and must not be invented.

Provider invocation timeout is 90 seconds; prefix/suffix wall budgets are
300/720 seconds, with 8/20 responses and 12/24 tool calls. At most two outer
transport retries precede any semantic tool execution. Successful JSON tool
results continue the actual model conversation. Authorization rejection is an
observed workflow event, never a reason to restart a whole task. Format repair
feedback is limited to one across each logical prefix-plus-suffix history.

4096 upstream output-token cap applies to the DeepSeek transport. Account-backed
Codex CLI lacks that supported upstream cap, an explicit pilot execution deviation;
both retain request/response/tool/time limits. The package does not claim a common
hard currency or output-token cap. Provider-internal CLI reconnects are visible
where emitted in raw logs and distinct from outer runner retries.

The four pilot fixtures are controlled host workflows. They are held out from
the 32 proposed formal cases and provide engineering checks rather than a general
failure-rate estimate. G is a harness-constructed challenge. Only the post-feedback
suffix tool selections are Agent behavior; the queued executor is never described
as an autonomous Agent attack.
