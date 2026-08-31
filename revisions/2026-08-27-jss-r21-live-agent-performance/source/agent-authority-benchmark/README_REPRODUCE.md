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
