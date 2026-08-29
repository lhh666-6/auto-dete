# AUTO-DECTE R21 findings

1. A live-model experiment is feasible without borrowing or exposing provider credentials: the
   authenticated Codex CLI can act as the hosted LLM and invoke a dedicated local MCP server.
2. This experiment must remain distinct from R19. R19 establishes the pinned DSH plugin/runtime
   boundary by deterministic direct calls; R21 measures live model tool selection through Codex.
3. Agent behavior and authority safety need separate denominators. A refusal or malformed call can
   be a tool-completion failure while the authority boundary still passes by stuttering.
4. The existing lower-bound arm changes both validation work and persisted semantics because it
   writes an empty source map. It cannot answer incremental mechanism cost.
5. A defensible replacement is a prevalidated persistence-equivalent arm: same successor values,
   source map, transition/decision/binding rows, field updates, and audit effects; only validation
   is removed. Pairwise semantic digests must match before latency is analyzed.
6. Reverse trace is currently dominated by repeated repository calls rather than a missing basic
   index. Its source-history loop performs transition reads for each version and transition lookups
   for each field; the selected trace then rereads terminal chains one field at a time.
7. The optimization target is query shape, not weaker checking: load all form-scoped fields,
   versions, transitions, decisions, certificates, bindings, and evidence once, then preserve the
   existing validation order and failure strings in memory.
8. The necessity claim must be scoped to the declared operational failures, not universal logical
   necessity: substitution motivates candidate identity, correction motivates distinct authorized
   value, intervening updates motivate pre-version, and copy-forward/multi-field provenance
   motivates a total source map.
9. The formal live-agent run completed all six scenarios with zero Codex process failures. The
   embedded confirmation instruction did not alter the propose--verify sequence; stale state was
   reported from expected/current versions; cross-record and cross-field calls failed with full
   database stutter; and the agent declined unavailable confirmation without a substitute call.
10. Codex JSONL uses `status=failed` plus error text in `result.content` for these MCP failures.
    Treating a non-null top-level `error` field as mandatory would create false negatives; both the
    original derivation and corrected tested derivation are therefore retained.
11. The feature-equivalent materialization arm matched the full relational post-state in all ten
    cells. Full-path p50 was 17.820--194.862 ms versus 10.469--16.479 ms for prevalidated
    materialization; the paired mean combined validation/planning/object-construction delta was
    7.455--182.021 ms.
12. Form-scoped batch reads reduce the reverse-trace database query shape from growth in fields and
    versions to a 12-statement budget. In-memory checking remains O(VF+T+C+E), so the optimization
    removes round trips without weakening source-history validation.
13. Against the exact R17/G10 performance execution used by the paper, optimized trace p50 is
    4.338--53.049 ms versus 5.327--7,857.313 ms; maximum optimized p95 is 64.360 ms. Descriptive
    cellwise p50 ratios are 1.224x--152.462x, but the runs are sequential rather than paired.

14. The R21 appendix now states the input boundary without contradiction: ten baseline inputs are
    separated from exactly three R21 inputs, each covered by its own manifest and claim ledger.
15. The R21 manifest closes direct dependency gaps identified during audit. It includes the live
    host-confirmation records, locked experiment environment, performance modules/configuration,
    implementation regression tests, and all raw run-4 evidence needed to regenerate the tables.
16. The final manuscript is 47 pages. Its only remaining submission blockers are author-controlled
    metadata and a stable public artifact URL/DOI; these are not scientific or reproducibility
    failures and must be filled by the author before upload.
17. JSS's AI-image policy is respected: the AI-generated concept raster is retained as internal
    ideation provenance only, while the submitted core workflow figure is an independently built,
    editable SVG derived from verified semantics.

## Repeated multi-model benchmark planning — 2026-08-28

18. The new request is a plan-only gate for a separate repeated multi-model live-agent benchmark.
    It supersedes the preceding no-new-large-experiment scope only prospectively: no benchmark code,
    pilot, final execution, or manuscript result may begin before the user approves
    `BENCHMARK_IMPLEMENTATION_PLAN.md`.
19. The latest self-contained technical baseline is the isolated R21 overlay. It already contains
    the production implementation, a two-tool MCP live-agent experiment, a pinned DSH adapter,
    performance/formal overlays, and non-self-referential evidence-manifest builders. The new
    benchmark should extend this overlay in a new directory rather than modify frozen evidence.
20. Relevant code is concentrated under `source/implementation/app`,
    `source/live-agent-experiment`, `source/dsh-plugin-auto-decte`, and `scripts`; broad source scans
    must exclude bundled JREs, virtual environments, caches, and duplicated paper-repository trees.
21. Capability separation is structural. `CandidateWritePort` can append candidate/evidence/audit
    units but has no fact-write method; `AuthorityReadPort` is read-only; `FactAdmissionPort`
    exposes one atomic batch transition method. Narrow facades preserve the same split at runtime.
22. `ReviewForms.confirm` is the only application fact-writing path. It resolves the current form,
    requires a host-resolved actor, checks expected version and exact field maps, reloads persisted
    certificates/evidence, derives the complete successor snapshot, constructs explicit immutable
    authorized-value bindings, revalidates every certificate/transition attempt, then calls the
    admission port once for the whole batch.
23. Candidate certificates bind candidate id, canonical candidate value, record, field, evidence
    content and canonical locator, producer, selection artifact, lineage, expected pre-version, and
    creation time into a content-addressed certificate id. Corrections preserve the original
    machine certificate and store the human-authorized final value separately.
24. The admission-shape rule requires an initial complete declared-field snapshot and later exact
    changed fields over a complete value/source domain; post-initial no-ops reject. The independent
    raw-relational oracle canonicalizes every application table and identity sequence, providing a
    reusable full-database digest, but the new benchmark needs a separately defined
    authoritative-only digest so allowed candidate-side appends do not look like fact mutations.
25. The trusted repository repeats admission validation against persisted state inside the same
    transaction. The version CAS is the first write; principal role is rechecked before CAS; exact
    transition fields, certificate/record/field/version/evidence/producer/template bindings,
    authorized values, and complete `fact_sources` are re-derived before atomic persistence.
26. The current live-agent experiment already supplies reusable primitives: a two-tool stdio MCP
    server, a subprocess bridge into the pinned implementation environment, Codex JSONL parsing,
    six scenario setup/evaluation functions, raw traces, host confirmation attempts, run metadata,
    and separate tool-completion versus authority-safety scores.
27. Its present limitations match the new benchmark motivation: one Codex model alias, one prompt
    per scenario, one execution per scenario, six scenario classes, fixed numeric proposal schema,
    whole-database digest semantics, and summary logic that requires one locked ordered six-case set.
    The new design should reuse the bridge/tool surface but replace the orchestration and scoring
    layer rather than mutate the historical runner.
28. The existing MCP server structurally exposes exactly `auto_decte_propose` and
    `auto_decte_verify`; the Codex command uses an ephemeral, read-only workspace and explicitly
    enables only those tools. This is a strong reusable FULL_CONTRACT model-facing surface.
29. The historical runner is intentionally non-resumable and refuses any existing output root. It
    hashes five source files before/after a six-case run, gives each case a fresh data root, retains
    prompt/raw JSONL/stderr/parsed events/host attempt/authority receipt/outcome, and records runtime
    metadata. The new benchmark needs a new immutable run-ledger/resume controller rather than a
    behavioral change to this evidence-producing runner.
30. The DSH bridge has a strict surface allow-list: model operations are only `propose` and
    `verify`; `init-fixture`, confirmation/substitution probes, and receipt export are host-only.
    This bridge can be generalized for benchmark fixtures, but its current fixture schema is
    single-field and producer identity is pinned to DSH.
31. The pinned DSH experiment provides useful artifact patterns—fixed source pin, bounded subprocess
    behavior, exact tool registration, non-overwriting output, offline manifest verification, and
    one-byte tamper detection—but it is a deterministic ToolRuntime integration test, not a second
    live model configuration. It must not be counted as a live model in the new benchmark.
32. The existing bridge receipt's `authority_state_sha256` covers a compact form/record/certificate
    projection while `database_sha256` hashes file bytes. Neither directly implements the requested
    authoritative-state versus candidate-state split; the new plan should define explicit logical
    projections over authoritative and candidate table families.
33. `AISuggestionForms.propose` is already the correct candidate-only operation for the benchmark:
    it validates form/field/parent/evidence/freshness, writes content-addressed AI-output evidence,
    creates a parent-linked certificate at the current fact version, and appends only candidate-side
    rows/audit. It supports arbitrary JSON-like values even though the current MCP schema narrows
    `value` to a float.
34. The reverse-trace implementation batch-loads one form-scoped authority snapshot and validates
    the exact source-history evolution, authorization binding, certificate/evidence chain, and
    committed value. It can serve B2/B3 postcondition checks, but benchmark scoring should call a
    stable projection helper rather than parse display-oriented trace text.
35. The current paper-input builder regenerates normalized inputs and LaTeX tables byte-for-byte
    from raw receipts, while the revision manifest inventories all selected files and detects
    missing/extra/hash changes. The new benchmark should copy this two-level pattern: a benchmark
    evidence manifest for source/config/raw/normalized/table/figure lineage, plus a paper-input
    builder that consumes only the frozen final summary.
36. Run-4 confirms the evidence layout expected for each live execution (prompt, raw JSONL, stderr,
    parsed events, host action, authority receipt, outcome, isolated DB/evidence). The new run schema
    can preserve this layout under deterministic run ids and add candidate/authority digest pairs,
    latency, token fields, error taxonomy, model metadata, variant/repetition/seed, and expected
    outcome without altering historical run-4.
37. Existing synthetic utilities are image-recognition oriented, but the AI-origin lifecycle already
    supplies the closer pattern: deterministic fresh database per case, declared multi-field values,
    production facades, logical digest checks, correction/copy-forward assertions, and non-overwrite
    output. The new operational-state generator should be a new small deterministic module rather
    than overload the image generator.
38. The formal/concrete mapping needed by the benchmark is already explicit: P1 exact candidate
    identity; P2 record/field/evidence/version context; P3 explicit authorized value and principal;
    P4 pre-version freshness/CAS; P5 item-transition bijection, atomic successor, and total source
    map; P6 trace reconstruction. The four-failure necessity story in the paper maps directly to
    equal-value substitution, correction, stale/intervening update, and partial/source-ambiguous
    successor scenarios.
39. Existing conformance tests already contain reusable trusted host probes for stale stutter,
    invalid-item whole-batch stutter, Accept/Correction, mixed multi-field batches, and unchanged
    source copy-forward. These should inform scenario ground truth, but final benchmark attempts
    must execute through the actual admission boundary and retain their own records.
40. The available authenticated live channel is Codex CLI 0.150.0-alpha.8; it supports explicit
    model selection, JSONL, output schemas, ephemeral execution, MCP configuration, and read-only
    sandboxing. No OpenAI/Anthropic/Gemini/DeepSeek API-key environment variable is present. The
    pilot should therefore qualify multiple Codex model aliases as distinct declared model
    configurations, while recording provider/model revision/temperature/seed as unavailable when
    the host does not expose them. No unavailable provider may be simulated.
41. Historical evidence already separates diagnostic live runs 1--3 from canonical run-4 and
    contains multiple independent frozen manifests. The new benchmark must live under a new sibling
    root such as `evidence/agent-authority-benchmark-v1/`, with `pilot/` and `final/` physically
    separate and neither referenced by the old R21 paper-input or revision manifests.
42. The benchmark source/config freeze should bind a new source subtree and its own dependency lock;
    the existing `evidence/frozen/**`, `evidence/reproduced/r19-*`, and
    `evidence/reproduced/r21/**` directories, their receipts, normalized inputs, and manifests are
    immutable inputs/reference evidence only.
43. The recommended architecture is a new provider-neutral benchmark core with a real Codex CLI
    adapter. The default final matrix is 3 qualified configurations × 14 scenarios × 3 variants ×
    10 repetitions (1,260); if only two configurations qualify, it is frozen honestly at 840.
    DSH/direct/mock executions cannot fill a missing live-model slot.
44. The plan retains all fourteen requested benign/failure classes, uses host-driven invalid tuples
    to exercise the real boundary even when an agent is compliant, caps transport retry at one
    pre-semantic retry, retains every planned run, reports runtime failures separately, and uses
    exact-binomial intervals without interpreting 0/N as proof.
45. The user approved a v2 architecture with a four-slot attempted roster: two GPT/OpenAI live
    configurations and two DeepSeek live configurations. Final scientific scoring must consume
    provider-neutral events and identical logical tool semantics, not provider response schemas.
46. The host currently has both an authenticated Codex/OpenAI channel and an authenticated
    Anthropic-compatible DeepSeek endpoint. A read-only model-catalog query returned
    `deepseek-v4-flash`, `deepseek-v4-pro`, and `deepseek-v4-flash-vision-exp`; catalog presence is
    not qualification, and the experimental vision configuration may be excluded if text/tool
    equivalence fails.
47. The approved pilot remains 112 executions by changing the factorization to
    4 configurations × 14 scenarios × 2 variants × 1 repetition. It is non-citable and cannot enter
    final normalization.
48. The target final matrix is 1,680 locked executions (4 × 14 × 3 × 10). A pre-result resource
    gate may freeze the balanced 840-run fallback (4 × 14 × 3 × 5). Results cannot influence the
    repetition choice.
49. Benign Task Completion Rate and Unauthorized Authoritative Mutation Rate are the only primary
    endpoints. Agent-mediated observations and trusted-host mechanism challenges require separate
    schema fields, normalization, denominators, result tables, captions, and interpretations.
50. A run identity and a case identity are not the same object. Prompt-variant and model fields
    belong in the immutable run id, but the deterministic case seed must exclude them so every
    provider and prompt variant receives the same scenario ground truth for a repetition.
51. Full SHA-derived unsigned 64-bit case seeds are valid identity inputs but cannot be used
    directly as seconds in a calendar offset. Fixture timestamps now reduce the seed modulo the
    number of seconds in 2026, preserving determinism without narrowing the recorded seed.
52. Provider-exposed JSON schemas can differ only by presentation metadata such as generated
    `title` fields. The equivalence gate strips only those declared presentation keys and still
    rejects any changed tool set, property, required field, type, or constraint.
53. The historical DSH root fixture certificate intentionally uses a fixture locator that is valid
    for candidate-parent testing but does not satisfy the current fact-admission locator check.
    Benchmark baseline commits therefore use the explicit manual-evidence path, then create a fresh
    version-bound parent when a legal correction or stale recovery requires one.
54. The real boundary emits stable, scenario-specific rejection evidence: cross-record and
    cross-field binding failures, certificate-identity mismatch, evidence-form mismatch, stale
    version, authorized-value mismatch, initial-field-set mismatch, and unavailable capability.
    None of the ten invalid challenges changed the logical authority projection.
55. A long-running benchmark needs two distinct failure treatments. Ordinary provider/adapter
    exceptions are known failures and can be sealed immediately as terminal API/tool/timeout
    classes. A process or power interruption leaves semantic progress unknown; resuming that run
    would risk favorable rerun, so it is sealed as `INTERRUPTED_UNKNOWN`, never reinvoked, and
    excluded from both authority and utility evaluable denominators while remaining in planned T.
56. Exact-binomial outputs must be produced during normalization, not added while writing the
    manuscript. JSON uses `null` rather than non-standard NaN when a one-sided zero-event bound is
    inapplicable, and every primary endpoint carries its explicit denominator.
57. Narrow connectivity diagnostics and the full 112-run Pilot require separate report identities.
    A selector-narrowed execution now emits `DIAGNOSTIC_REPORT.md`; only exact coverage of the locked
    Pilot ledger may emit `PILOT_REPORT.md` and `pilot-model-qualification.json`.
