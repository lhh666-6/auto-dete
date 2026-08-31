# Benchmark execution amendment — quota-aware Pilot-2

## Scope

This amendment changes execution control only. It does not modify the attempted four-configuration
roster, fourteen scenarios, two Pilot prompt variants, primary estimands, qualification rules,
provider-neutral event schema, host challenges, frozen historical evidence, or Final gates in
`BENCHMARK_IMPLEMENTATION_PLAN_v2.md`.

## Why a new Pilot is required

Pilot-1 completed its 112-coordinate ledger but failed the cross-provider qualification gate. Its
OpenAI coordinates include quota exhaustion and pre-repair harness behavior, while the DeepSeek
adapter did not yet return structured bridge errors to the model. Those records remain immutable,
non-citable evidence. Later isolated diagnostics demonstrated that all four requested
configurations can reach the repaired two-tool surface. Because the adapter, prompt metadata, and
tool-isolation conditions changed, the repaired system requires a new, physically separate Pilot;
Pilot-1 cannot be resumed, replaced, or selectively edited.

## Quota-aware execution change

The original plan permitted one pre-semantic transport retry. The user subsequently imposed a
stricter resource constraint: OpenAI tests may need to advance one call per quota reset. Pilot-2
therefore freezes `max_transport_retry = 0` for every provider and uses
`--max-new-invocations 1` for quota-limited advancement. This preserves provider symmetry and
ensures a single command cannot consume a hidden second provider call.

Each incomplete command preserves the complete 112-run plan, adds at most one terminal run, writes
an append-only checkpoint, and stops before normalization. Resume verifies the frozen inputs and
skips terminal coordinates. Qualification and the phase manifest are created only after all 112
coordinates are terminal.

## Gates unchanged

The candidate Pilot remains non-citable. Final remains prohibited unless the completed candidate qualifies at
least one OpenAI and one DeepSeek configuration, the pre-result resource gate passes, and the
qualified balanced matrix is frozen and verified. Quota exhaustion is retained as a planned-run
failure; it is never rerun within the same Pilot root.

## Pilot-2 abort and repaired successor

Pilot-2 executed exactly one call and exposed a harness path-resolution defect: a relative MCP data
root was interpreted from the Codex agent workspace, creating an empty nested database and an
`unknown form` tool error. The complete Pilot-2 root is externally manifested and excluded from all
qualification and model-behavior claims. It must not resume.

Commit `1e7b0ac` resolves every MCP path at the provider boundary and adds the exact regression
test. Pilot-3 is the new physically separate candidate Pilot and is additionally protected by a
mandatory live `--launch-lock` gate.
