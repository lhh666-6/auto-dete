# Reproducing the repeated authority benchmark

This package implements the approved provider-neutral benchmark. Pilot and Final outputs are
append-only and physically separate. Pilot results are non-citable and cannot be normalized into
the manuscript.

## Local deterministic gate

```powershell
uv sync --frozen
.venv\Scripts\python.exe -m pytest -q
.venv\Scripts\ruff.exe check auto_decte_agent_benchmark tests
.venv\Scripts\python.exe -m auto_decte_agent_benchmark.runner --pilot --config config --dry-run
```

The dry run must report 112 planned executions, four configurations, fourteen scenarios, two
prompt variants, zero model calls, zero database writes, and logical tool-surface equivalence.

## Pilot history and quota-aware Pilot-3

Pilot-1 is complete and immutable. Its failed qualification and blocking resource-gate disposition
are preserved outside the Pilot root. It must never be resumed or edited.

Pilot-2 is an externally manifested aborted harness run. Its relative MCP data path opened an empty
nested database, so its sole observation cannot qualify or characterize G1. It must not resume.

Pilot-3 is the repaired, physically separate candidate Pilot. Start its locked root exactly once
with `--max-new-invocations 1 --launch-lock <PILOT3_LAUNCH_LOCK.json>`. Every later command uses the
same root with `--resume` and the same two controls. The runner verifies selected source, config,
plan, output identity, and frozen zero retry before it can call a provider; it then stops after one
new invocation. An incomplete Pilot has checkpoints but no normalized data, qualification, phase
report, or manifest.

Each absent run is prepared just in time, immediately before its provider invocation. This is a
correctness requirement: production certificates have a one-hour age bound, so a phase-wide cache
would make later or post-pause runs inherit expired lineage. The run directory retains the exact
prepared context and isolated database that were actually used.

## Resource gate and Final freeze

`config/resource-policy.json` was frozen before Final outcomes. It permits only a balanced ten-run
default or balanced five-run fallback, requires both provider families, limits expected serial wall
time to 72 hours, and prohibits scientific outcome fields from entering the decision. A complete
Pilot and confirmed provider credit are required before `FINAL_RESOURCE_GATE.json` can pass.

No Final configuration or `FROZEN.json` is valid until the complete Pilot qualification and
resource gate pass. The Final must run from a verified freeze copy and write to a fresh Final root.

The post-Pilot commands are deliberately separate and do not call a provider. First, create an
operator attestation with schema `agent-authority-provider-credit.v2` and one Boolean entry for
each attempted slot under `model_configurations`. `true` means the provider budget is independently
confirmed sufficient for the complete balanced Final; it must not be inferred from a favorable
Pilot outcome. Then run:

```powershell
.venv\Scripts\python.exe -m auto_decte_agent_benchmark.post_pilot gate `
  --pilot-root <complete-pilot-root> `
  --pilot-config config `
  --provider-credit <provider-credit.json> `
  --output <new-gate-root>\FINAL_RESOURCE_GATE.json
```

A `BLOCK` decision is a hard stop: do not create a Final configuration or call a provider. If the
decision is `PASS` or `PASS_FALLBACK`, bind the exact qualification file selected by the gate:

```powershell
.venv\Scripts\python.exe -m auto_decte_agent_benchmark.post_pilot final-config `
  --pilot-config config `
  --qualification <complete-pilot-root>\pilot-model-qualification.json `
  --resource-gate <new-gate-root>\FINAL_RESOURCE_GATE.json `
  --output <new-final-config-root>
```

Create a JSON object containing only pre-execution runtime metadata (for example Python, OS,
Codex/API client versions, and `scientific_outcomes_read: false`). Stage a fresh source freeze:

```powershell
.venv\Scripts\python.exe -m auto_decte_agent_benchmark.post_pilot freeze `
  --benchmark-root . `
  --implementation-root ..\implementation `
  --final-config <new-final-config-root> `
  --runtime-metadata <runtime-metadata.json> `
  --output <new-final-freeze-root>

.venv\Scripts\python.exe -m auto_decte_agent_benchmark.post_pilot verify-freeze `
  --root <new-final-freeze-root>
```

Run the Final module from `source\agent-authority-benchmark` inside that freeze, using Python
environments outside the immutable root. The output must also be outside the freeze. A dry run is
network-free; every live command verifies `FROZEN.json` before and after dispatch:

```powershell
<external-python> -m auto_decte_agent_benchmark.runner --final `
  --config <new-final-freeze-root>\source\agent-authority-benchmark\config `
  --dry-run

<external-python> -m auto_decte_agent_benchmark.runner --final `
  --config <new-final-freeze-root>\source\agent-authority-benchmark\config `
  --output <new-final-output-root> `
  --frozen-root <new-final-freeze-root> `
  --max-new-invocations 1

<external-python> -m auto_decte_agent_benchmark.runner --final `
  --config <new-final-freeze-root>\source\agent-authority-benchmark\config `
  --output <new-final-output-root> `
  --frozen-root <new-final-freeze-root> `
  --resume --max-new-invocations 1
```

The single-invocation form is quota-safe but does not change the complete locked Final ledger.

## Final reporting

Only a complete locked Final plan can call `render_final_reporting_bundle`. It writes:

- `agent_behavior_table.tex`;
- `admission_mechanism_table.tex`;
- `statistical_analysis.json`;
- editable `behavior_vs_authority.svg`;
- vector `behavior_vs_authority.pdf`;
- 300-dpi `behavior_vs_authority.png`;
- `FIGURE_QA.md`.

The behavior and mechanism tables have disjoint meanings and denominators. The figure reports
Clopper--Pearson intervals and separate one-sided zero-event upper bounds; it does not rank provider
families or claim general security.
