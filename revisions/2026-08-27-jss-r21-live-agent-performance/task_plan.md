# AUTO-DECTE R21 task plan

Date: 2026-08-28

## Goal

Strengthen the JSS revision with a real LLM tool-use experiment, an operational-necessity argument,
a feature-equivalent admission comparator, and an output-equivalent reverse-trace optimization,
without changing the frozen R17--R19 evidence or overstating the new results.

## Success criteria

- [x] A logged hosted Codex run invokes `auto_decte_propose` and `auto_decte_verify` through MCP;
  stale/cross-context cases additionally record actual rejected host confirmation attempts, and
  adversarial scenarios record both agent compliance and authoritative-state safety.
- [x] Three or four executable failure scenarios motivate the joint candidate/value/version/source
  bindings as operational necessities within the declared failure model.
- [x] The admission comparator persists the same successor values, complete source map, and
  transition-side rows as the full path; a semantic digest proves output equivalence per pair.
- [x] Reverse trace retains exact complete/incomplete diagnoses while replacing per-field database
  loads with one form-scoped snapshot; focused tests demonstrate red-green equivalence and query
  count reduction.
- [x] New receipts, configs, raw logs, manifests, paper inputs, claim ledger, manuscript, and PDF
  are mutually consistent and non-overwriting.
- [x] Full tests, lint/type checks, citation audit, proofread, LaTeX build, visual QA, and release
  manifest verification pass before any completion claim.

## Phases

### Phase 1 — locked design and baseline diagnosis

- [x] Preserve R20 and create isolated R21 workspace.
- [x] Confirm a real hosted-model channel without an API key (Codex ChatGPT login + local MCP).
- [x] Locate reverse-trace N+1 reads and existing index coverage.
- [x] Freeze the R21 design specification, scenario set, estimands, metrics, and stop rules.

### Phase 2 — live-agent experiment

- [x] Add test-first MCP adapter exposing only proposal and verification operations.
- [x] Add deterministic fixture/scenario preparation and canonical state-digest capture.
- [x] Execute the amended benign, prompt-injection, stale-replay, cross-record, cross-field, and
  attempted-confirmation cases with raw Codex JSONL plus host-attempt records retained.
- [x] Normalize separate tool-completion and authority-safety outcomes from the amended run.

### Phase 3 — equivalent admission comparator

- [x] Write failing tests for successor/source-map/row-set equivalence.
- [x] Implement a trusted prevalidated arm that executes the same persistence effects while omitting
  candidate/authorization validation.
- [x] Run paired randomized measurements; retain all paired observations and exact relational
  fingerprints. Treat the generic materializer gap as descriptive, not causal phase timing.

### Phase 4 — reverse-trace optimization

- [x] Add query-count and exact-output regression tests before production changes.
- [x] Add one form-scoped authority snapshot/batch-load API and switch QueryForms to it.
- [x] Verify corrupt, historical, copy-forward, and complete traces remain identical.
- [x] Benchmark reference versus optimized path and document complexity.

### Phase 5 — paper integration

- [x] Add operational-necessity scenarios and revise novelty language.
- [x] Supplement the lower-bound performance claim/table with equivalent-baseline evidence.
- [x] Report live-agent and optimized-trace results with one local boundary per experiment and
  consolidated limitations in Section 9.
- [x] Update appendix exact-input statement/table, evidence ledger, generated tables, and figures.

### Phase 6 — final gates

- [x] Run full Python/TypeScript/lint/type/citation checks.
- [x] Run `proofread`, `latex`, visual QA, and pre-submission checks.
- [x] Build and verify a non-self-referential R21 manifest and non-overwriting release package.
- [x] Update final handoff; author-controlled metadata and stable artifact URL/DOI remain explicitly open.

### Phase 7 — repeated multi-model live-agent benchmark design

- [x] Read the current production ports, transaction path, MCP adapter, DeepSeek Harness adapter,
  live-agent scenarios, digest logic, and evidence/manifest builders end to end.
- [x] Inventory reusable components, immutable frozen boundaries, and the exact non-overwriting
  directory tree for a new benchmark version.
- [x] Compare runner/model-integration architectures and select a recommended design without
  implementing or executing the benchmark.
- [x] Specify scenario, prompt, model, scoring, retry, result, statistical, manifest, pilot, freeze,
  resume, and failure-retention contracts.
- [x] Write and self-review `BENCHMARK_IMPLEMENTATION_PLAN.md`; stop for user approval before any
  benchmark source, pilot execution, or manuscript integration.

### Phase 8 — cross-provider benchmark v2 and implementation

- [x] Incorporate the approved 2 GPT/OpenAI + 2 DeepSeek design into a separate v2 plan.
- [x] Freeze the 112-run pilot, 1,680-run default final, 840-run resource fallback, two primary
  estimands, two evidence layers, provider-neutral events, and logical tool-equivalence gate.
- [x] Write `PLAN_V2_CHANGELOG.md` and self-review the plan for stale v1 assumptions.
- [x] Implement schemas, canonical events, generator, digests, and scorer test-first.
- [ ] Qualify OpenAI/Codex and DeepSeek configurations against the same logical tool surface
  (both live invocation layers, schema equivalence, MCP surface, and trusted bridge are implemented;
  live pilot qualification pending).
- [x] Execute deterministic real-boundary tests for all fourteen legal/invalid host challenges,
  including separate candidate/authority digests and the prepare/execute protocol.
- [ ] Complete normalization, statistics, and artifact generation (all fourteen scenarios, all
  three final prompts, the immutable ledger, and deterministic 112-run dry-run validation are done).
- [ ] Execute the 112-run non-citable pilot only after deterministic gates pass.
- [ ] Decide the resource gate, freeze the qualified balanced matrix, and execute final only if all
  stop conditions pass.
- [ ] Replace the old live-agent manuscript evidence, verify artifacts, and rerun submission gates.

**Status:** v2 design approved; implementation authorized and entering the test-first local phase.

## Errors and constraints

| Item | Evidence | Resolution |
|---|---|---|
| No standard hosted-model API key | Environment presence check: all four provider variables absent | Use authenticated Codex CLI with a dedicated local MCP server; do not infer DSH live-provider evidence. |
| Existing comparator is not feature-equivalent | `_lower_bound` writes an empty `fact_sources` map | Retain historically, but introduce a new prevalidated persistence-equivalent arm. |
| Existing trace repeats reads | Per-version transition scans plus per-field transition/certificate/evidence calls | Batch-load one form-scoped authority snapshot and validate in memory. |
| New benchmark request conflicts with the preceding no-new-large-experiment instruction | The later attached request explicitly defines a multi-model repeated benchmark and says to begin with a plan only | Treat the attached request as the new scope; create only the implementation plan and await approval before implementation. |
| v1 assumed three Codex-requested configurations | The approved v2 requires two GPT/OpenAI plus two DeepSeek configurations | Preserve v1 as history; implement only the provider-neutral v2 design. |
| DS API catalog presence does not prove tool compatibility | Three identifiers were discoverable, but none is qualified by catalog listing alone | Qualify D1/D2 through the same text-only two-tool pilot; do not fill slots with mocks or an incompatible experimental model. |
