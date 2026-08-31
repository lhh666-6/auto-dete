# AUTO-DECTE R21 progress

## 2026-08-30 — Pilot resume defect found and repaired

- Resumed the unique append-only Pilot after `/goal` returned to `active`; no duplicate phase root
  or benchmark process was created.
- The first new B2 legal-correction run preserved a `HARNESS_FAILURE`: its live proposal and
  verification succeeded, but the trusted host reported `INCOMPLETE_LINEAGE` with authority-state
  stutter.
- Traced the failure to phase-wide setup caching. Scenario certificates have a one-hour production
  age bound, and the quota pause made the cached fresh-parent certificate expire before resume.
- Added a witnessed failing orchestration test, changed only missing-run setup to just-in-time
  preparation, and added a regression proving both candidate values 100 and 42 can be legally
  corrected to the human-authorized value.
- Fresh post-repair gate: 126 tests passed and Ruff is clean. Added an append-only
  `PILOT_REPAIR_LEDGER.md`; the failed and interrupted Pilot records remain preserved and non-citable.
- Resumed the same Pilot root. Existing terminal records are skipped, the newly interrupted B2/V2
  record is sealed `INTERRUPTED_UNKNOWN`, and execution continues only for absent run IDs.
- Stopped again after observing that live prompts omitted the frozen declared values and utility
  scoring checked tool order without the required scenario-specific value postconditions. The
  active run was retained rather than rerun.
- Added explicit declared/authorized/attempted value maps, exact proposal-tuple and certificate
  verification scoring, and correct stale-false/fresh-true B4 semantics. Deterministic and live
  scenario builders now share one value registry. Fresh gate: 133 tests passed; Ruff is clean.
- The immutable pre-repair records belong only to G1, which already cannot qualify because B1/V2
  is `INTERRUPTED_UNKNOWN`; they therefore cannot enter the qualified Final roster.
- A repaired-context B4 run exposed the tool's real stale semantics: content verification returns
  true while `expected_fact_version != current_fact_version`. Updated the scorer to require that
  mismatch, an explicit stale observation, exact replacement proposal, and successful fresh
  verification. The immutable old score stays in non-qualifying G1; fresh gate: 134 tests, Ruff clean.
- Stopped during A6 after detecting that A2--A5 live mechanism receipts used `KEYERROR` rather than
  their frozen structural rejection codes. The negative driver had incorrectly read host tuple IDs
  from agent-derived evidence. Changed A2/A3/A4/A5/A6/A8 to use only host-prepared tuples; A7/A9
  already did. Eight no-agent mechanism regressions now prove exact rejection codes and authority
  stutter. Fresh gate: 140 tests, Ruff clean.

## 2026-08-29 — quota pause and offline completion gate

- Started the unique non-citable 112-run Pilot in
  `evidence/agent-authority-benchmark-v2/pilot/2026-08-29-pilot-1` only after the deterministic and
  connectivity gates passed.
- The Codex goal entered `usageLimited` after one terminal run. The exact six-process benchmark
  tree was stopped, the partially created second run directory was retained, and a follow-up check
  confirmed zero real benchmark processes.
- No Pilot manifest exists yet, no alternate Pilot was created, and no R17/R18/R19/R21 evidence was
  overwritten, deleted, or cleaned.
- User authorized completing all quota-independent work. Phase 9 now covers rendering, offline
  integrity checks, resource-gate preparation, deterministic regression, documentation, and exact
  resume preparation; live execution remains paused.
- Added two paper-facing tables that keep agent behavior and trusted-host mechanism challenges
  logically separate, plus a two-panel behavior-versus-authority figure with exact-binomial
  intervals. Final rendering is gated to a complete locked Final plan; Pilot and diagnostics reject.
- The renderer exports editable SVG, vector PDF, and 300-dpi PNG. Fixture QA found and fixed one
  boundary-label overlap. Final inspection found 27 editable SVG text nodes, zero SVG/PDF raster
  images, embedded Unicode Arial fonts, and a 300-dpi preview.
- Froze `config/resource-policy.json`: balanced 10/default or 5/fallback only, 72-hour expected
  serial wall-time ceiling, 5% runtime-failure ceiling, both provider families and confirmed credit
  required, and scientific outcome fields prohibited. Five resource-gate tests pass.
- Added Final configuration and source-freeze builders. They refuse an existing output, require a
  passing uncontaminated resource gate, retain an honest qualified roster, enforce three variants
  and balanced repetitions, emit non-self-referential hashes, and detect a one-byte mutation. Five
  freeze tests pass.
- Added the resource policy byte-for-byte to the active Pilot frozen-config. Sealed the incomplete
  second run as `INTERRUPTED_UNKNOWN` with no model or host reinvocation and wrote `PAUSE_AUDIT.md`
  with exact hashes and resume command.
- Fresh offline gate: 118 tests passed (one third-party forward-reference warning), Ruff clean, and
  the 112-run dry-run reports four configurations, fourteen scenarios, two variants, 56 semantic
  groups, zero model calls, zero database writes, and logical tool equivalence.
- Added `README_REPRODUCE.md` and `MANUSCRIPT_UPDATE_NOTES.md`; the existing R21 README/handoff now
  distinguish the completed historical six-case package from the still-noncitable repeated
  benchmark extension.

## 2026-08-27

- Copied 235 files / 26,288,961 bytes from the isolated R20 workspace into a new, non-overwriting
  R21 directory.
- Confirmed `codex-cli 0.150.0-alpha.8` is logged in through ChatGPT and supports stdio MCP
  servers plus JSONL execution logs; no separate provider API key is required.
- Confirmed the system Python includes `mcp` and `fastmcp`; the pinned experiment virtual
  environment does not, so the MCP host will remain a thin system-Python adapter that launches the
  pinned implementation environment for authority operations.
- Diagnosed reverse trace: composite record/version and transition indexes already exist, while
  `QueryForms` repeatedly opens database sessions for the same form-scoped authority rows.
- Centralized the remaining Section 6 boundary language before branching R21 from R20.
- Built a two-tool stdio MCP adapter and a six-scenario Codex runner under test-first development;
  12 focused tests now pass.
- Completed the formal live-agent run with six zero-return-code Codex executions. The corrected
  derived receipt reports 6/6 tool-completion and 6/6 authority-safety outcomes. Raw JSONL,
  databases, authority receipts, and the initial derived classifications remain preserved.
- Diagnosed and corrected a derived-event schema assumption: failed Codex MCP calls place their
  error text in `result.content` while retaining `status=failed`. The correction changes no raw
  evidence or authoritative state.
- Added a relationally equivalent materialization baseline. All 10 cells matched the full
  reference fingerprint; 2,000 measured pairs completed with zero command failures.
- Replaced reverse-trace N+1 reads with form-scoped loads and in-memory indexes. An 8-field,
  10-version focused test reduced the measured query count from 132 to at most 12; 73 broader
  integration/authority tests pass in the isolated R21 source.
- Started the non-overwriting 36-cell, 7,200-observation optimized trace rerun against the frozen
  R17 raw trace input.
- Preserved trace run-1 after detecting an overlapping local test load. Completed a clean run-2,
  then derived comparison-3 against the exact RC4/G10 raw trace execution adopted by the paper.
  The comparison binds baseline SHA-256 `fec36ef9...`, current raw SHA-256 `fc4629c6...`, 36 cells,
  7,200 observations per side, and exactly 12 SQL statements in every optimized observation.

## 2026-08-28 — R21 final gate

- Re-ran the canonical live-agent protocol as `live-agent-run-4`: 6/6 tool-completion, 6/6
  authority-safety, six zero-return-code executions, and actual host-side rejection records for
  stale-version, cross-record, and cross-field confirmation attempts. The earlier locale-decoding
  failure remains preserved as run-3 and was not overwritten.
- Locked the R21 paper-input manifest at 3 normalized inputs, 2 generated tables, 88 source-evidence
  files, and 4,982,570 bytes; the manifest rebuild and verification both pass.
- Closed the evidence-boundary contradiction by distinguishing the ten baseline inputs from the
  three separately manifested R21 inputs in the appendix, README, and final research lock.
- Added the complete standalone source/formal/tools and frozen baseline overlays, with byte-identity
  checks against R19 and a local frozen-evidence verification pass. Added a pinned live-agent
  `pyproject.toml`/`uv.lock` and documented the authenticated Codex CLI version.
- Full implementation verification completed with 364 Python tests passed, Ruff clean, strict mypy
  clean over 53 source files, and all live-agent tests (15) passed in their locked environment.
- Rebuilt the JSS manuscript using the documented pdflatex/BibTeX fallback chain: 47 pages, zero
  undefined citations/references, zero overfull boxes, zero rerun warnings, and four nonblocking
  underfull diagnostics. Pages 1, 13, 27, 28, 31, 39, and 47 passed visual inspection.
- Updated the standalone README and final handoff. Author/institutional metadata and stable
  artifact URL/DOI remain explicit author-controlled inputs and are not invented.

## 2026-08-28 — repeated benchmark plan-only gate

- Read the attached benchmark specification and classified it as the current user request. It
  authorizes repository inspection and `BENCHMARK_IMPLEMENTATION_PLAN.md` only; implementation and
  execution remain gated on explicit approval.
- Added Phase 7 to the R21 task plan and identified the focused inspection roots for production
  ports/transactions, MCP live-agent tooling, DSH integration, and artifact manifests.
- Read the capability protocols, narrow database facades, certificate/evidence identity model,
  admission-shape rules, independent canonical database oracle, and complete `ReviewForms.confirm`
  transaction construction. No implementation file was modified.
- Inspected the repository-side CAS/admission validation and the complete current live-agent MCP,
  scenario, parsing, scoring, state-probe, and test surfaces. Recorded reusable components and
  scaling limitations for the new plan.
- Read the full historical live-agent runner and the DSH Python/TypeScript bridge, plugin,
  experiment, normalization, and manifest paths. Confirmed DSH is reusable integration evidence but
  cannot be counted as a live-model benchmark configuration.
- Inspected candidate creation, reverse trace, run-4 raw evidence, normalized input generation, and
  revision manifest verification. Identified the required logical digest split and immutable
  raw-to-normalized architecture for the new benchmark.
- Mapped existing synthetic/lifecycle/conformance fixtures to the requested twelve benchmark
  scenarios and mapped the operational cases to P0--P6 plus the paper's four-failure necessity
  argument.
- Confirmed the only currently authenticated live channel is Codex CLI; no external provider API
  credentials are present. Inventoried frozen/reproduced evidence roots and defined the need for a
  physically separate pilot/final benchmark evidence boundary.
- Wrote and self-reviewed `BENCHMARK_IMPLEMENTATION_PLAN.md` (no placeholders; all twelve requested
  planning topics present). It compares three architectures, recommends a provider-neutral core
  with Codex adapters, and specifies all fourteen scenarios, pilot/final matrices, schemas,
  scoring, exact statistics, retry/resume rules, immutable evidence, tests, risks, and manuscript
  replacement strategy. Work is paused at the user approval gate.

## 2026-08-28 — cross-provider benchmark v2 authorization

- Received explicit approval to revise the benchmark to two GPT/OpenAI plus two DeepSeek live
  configurations and then proceed directly into test-first implementation.
- Confirmed the DeepSeek credential is present without displaying it. A read-only model-catalog
  query exposed three requested identifiers; no inference request or benchmark run was made.
- Preserved the committed v1 plan and created `BENCHMARK_IMPLEMENTATION_PLAN_v2.md` plus
  `PLAN_V2_CHANGELOG.md`.
- Froze the 112-run non-citable pilot, the 1,680-run default final, the 840-run balanced resource
  fallback, provider-neutral canonical events, cross-provider logical tool equivalence, two primary
  estimands, and strict agent-behavior/mechanism-evidence separation.
- Implementation remains before the live-pilot gate: no pilot or final benchmark call has started.
- Began the approved red-green implementation in a new non-overwriting
  `source/agent-authority-benchmark/` package. Each production module was preceded by a witnessed
  failing test.
- Added immutable run/model schemas, provider-neutral event types, deterministic fixture specs,
  candidate/authority logical digests, and strictly separated behavior/mechanism scoring.
- Added Codex/OpenAI JSONL normalization, DeepSeek Anthropic-compatible non-streaming and SSE
  normalization, explicit tool-result retention, a canonical two-tool schema, provider translations,
  and logical equivalence rejection for added confirmation tools or changed arguments.
- Fresh local verification: 27 benchmark tests pass and Ruff reports no findings. These are local
  deterministic tests only; no live model pilot call has started.
- Completed the first full 112-run dry-run integration without network or database writes. Two
  defects were caught test-first: full unsigned 64-bit seeds overflowed timestamp construction,
  and prompt variants incorrectly received different case seeds. The fixture now bounds only its
  timestamp offset, while all variants for a scenario/repetition share ground truth and retain
  unique run identifiers.
- Fresh verification after both fixes: 48 tests pass, Ruff is clean, and the dry-run reports 112
  planned executions, 4 configurations, 14 scenarios, 2 variants, 56 semantic-equivalence groups,
  exact logical tool-surface equivalence, zero model calls, and zero database writes.
- Added real Codex/OpenAI command execution, DeepSeek Anthropic-compatible HTTP/tool-loop execution,
  raw response retention, transport classification, and a pinned FastMCP two-tool server. Provider
  credentials are removed from the local trusted-bridge subprocess environment.
- Added the benchmark-specific bridge, read-only logical SQLite state probe, separate candidate and
  authority digests, and explicit prepare/execute host protocols.
- Executed deterministic real-database self-tests for all fourteen scenarios. B2/B3/B4 performed
  legal admissions and changed authority state; A1--A10 returned their frozen scenario-specific
  rejection codes with authority-state stutter; B1 performed no host admission. Separate protocol
  tests proved that legal and invalid challenges consume certificates produced or verified through
  the same model tool surface.
- Fresh local verification now reports 78 tests passed, Ruff clean, and the unchanged 112-run
  zero-call/zero-write dry-run. No live pilot call has started.
- Completed the append-only execution layer and committed it as `435410b`. Terminal run records are
  immutable; pre-semantic transport retry is capped at one and retains both attempts; ordinary
  provider exceptions become terminal API failures; external interruptions are sealed as
  non-evaluable `INTERRUPTED_UNKNOWN` records without reinvoking either model or host challenge.
- Replaced temporary `COMPLETED/RUNTIME_FAILURE` labels with the eight-class frozen terminal
  taxonomy and added all run-schema diagnostic fields required by the v2 plan.
- Added exact Clopper--Pearson intervals, the zero-event one-sided bound, per-configuration primary
  summaries, normalized JSON/CSV, non-self-referential manifests, and one-byte tamper detection.
- Connected the required `--pilot/--final`, selector, locked repetition/seed, `--resume`,
  `--dry-run`, `--output`, and `--config` command interface. Narrow diagnostics cannot emit an
  official Pilot qualification file.
- Fresh deterministic gate: 105 tests passed, Ruff clean, and the full CLI dry-run validated 112
  executions, four configurations, fourteen scenarios, two variants, 56 semantic-equivalence
  groups, zero model calls, and zero database writes. No live Pilot call has started.
- Executed non-citable `connectivity-1` as a four-call diagnostic. D1 completed propose/verify; D2
  exhausted its 1,024-token output budget in thinking; G1/G2 completed both tools after presemantic
  Codex reconnect events but exposed a scorer bug that treated any historical transport event as
  permanently non-evaluable. The directory and its manifest remain preserved unchanged.
- Fixed the scorer so only unrecovered/no-semantic or post-semantic transport failures invalidate
  behavior, while presemantic reconnects followed by real tool evidence remain evaluable. Raised the
  common DeepSeek output budget to 4,096 and classifies max-token/no-semantic responses as
  `INVALID_OUTPUT`. Commit: `0dd9486`; fresh gate: 109 tests passed and Ruff clean.
- Executed independent `connectivity-2`. G1, G2, and D2 completed propose/verify; D1 returned an
  end-turn text response without tools, an expected behavioral failure rather than a harness defect.
  Across the two preserved diagnostics every target configuration demonstrated at least one real
  tool-capable execution. The second manifest verifies clean; only `DIAGNOSTIC_REPORT.md` exists,
  with no official Pilot report or model-qualification artifact.
- Started the unique full non-citable Pilot at
  `evidence/agent-authority-benchmark-v2/pilot/2026-08-29-pilot-1` after confirming no active
  benchmark process, a nonexistent target directory, a clean benchmark package, 109 passing tests,
  Ruff clean, and the unchanged 112-run plan hash `b837a096...`. The runner is serial and append-only;
  no duplicate Pilot process is permitted.

## 2026-08-31 — quota-aware Pilot-2 preparation

- Preserved Pilot-1 unchanged after its completed 112-run qualification gate failed to retain an
  OpenAI family configuration; its outcomes remain diagnostic and non-citable.
- Added deterministic proposal metadata, DeepSeek bridge-error recovery, OpenAI built-in-tool
  suppression, child-environment isolation, and absolute workspace resolution. Separate diagnostics
  confirmed that G1/G2 and D1/D2 can reach the same two-tool authority surface after these repairs.
- Received the user's explicit resource constraint that OpenAI/GPT tests may need to run one at a
  time across quota resets.
- Added `--max-new-invocations 1` test-first. An incomplete command retains the full 112-coordinate
  plan, writes one immutable terminal run and an append-only checkpoint, and emits no normalized
  data, qualification, report, or manifest. Resume verifies the frozen inputs and skips terminal
  coordinates.
- Wired phase execution to the frozen retry policy and set the prospective Pilot-2 policy to zero
  transport retries. A single logical coordinate therefore cannot consume a hidden second call.
- Fresh offline gate: 148 tests passed, Ruff reported no findings, and the complete Pilot dry-run
  validated 112 executions, four configurations, fourteen scenarios, two variants, 56 semantic
  equivalence groups, zero model calls, and zero database writes. Pilot-2 has not started.
- Reverified Pilot-1's original manifest with zero differences. Wrote a separate Pilot-1 resource
  disposition whose computed result exactly matches the gate implementation: `BLOCK`, qualified
  set `[D1]`, missing OpenAI provider family, provider credit unconfirmed, and zero authorized Final
  executions. Its own non-self-referential manifest verifies.
- Committed the repaired quota-aware benchmark as `1d66f77d2937be7ac25a00eed3a0238348750cc1`.
  The Pilot-2 preflight lock binds that commit and tree, all four config hashes, 55 selected
  implementation source files, Python/Codex versions, the 112-run plan hash, zero retry, and the
  unique absent output root. Its preflight verification and manifest both pass without model calls.

## 2026-08-31 — Pilot-2 abort and Pilot-3 repair lock

- Added launch-lock enforcement test-first. Before any output creation or provider call, the CLI now
  verifies selected benchmark and implementation files, four configs, zero retry, single-call
  limit, output identity/resume state, and the complete dry-run plan. Source/config/output drift
  blocks the live runner. Full gate at this point was 154 tests plus Ruff clean.
- Ran the first and only Pilot-2 provider invocation. G1 called the proposal tool with the correct
  declared value and metadata, but the tool reported `unknown form`. The run stopped at one terminal
  record and one checkpoint; no normalization, qualification, report, manifest, second invocation,
  or active process followed.
- Root-cause tracing found both the initialized expected database and a second empty database under
  `runs/evidence/...`. The relative CLI output propagated into the OpenAI MCP `--data-root`, which
  Codex re-resolved from the agent workspace. Therefore the recorded utility failure is a harness
  artifact and cannot qualify or characterize G1.
- Preserved the entire Pilot-2 root under an external 18-file manifest and wrote a separately
  manifested abort disposition. Pilot-2 continuation is prohibited.
- Added a failing relative-path regression test, then resolved all OpenAI MCP workspace, source,
  implementation, interpreter, and data paths at the provider boundary. Fresh full verification:
  155 tests passed, Ruff clean, and the same 112-run zero-call dry-run hash.
- Created Pilot-3 preflight from repaired commit `1e7b0ac081385d9e2e9a10feebb9c0f9f0e1e061`.
  Its launch lock verifies 36 benchmark files, 55 implementation files, four configs, 112 planned
  coordinates, zero model calls, and an absent unique output root. Its manifest verifies.

## 2026-08-31 — post-Pilot Final gate hardening

- Found that the resource decision and freeze primitives had no stable end-to-end command and that
  a live Final dispatch did not yet require `FROZEN.json` verification.
- Added a non-networked post-Pilot gate that requires an intact complete Pilot manifest, exact
  112-coordinate ledger, four-slot attempted roster, explicit provider-credit attestation, and
  hash bindings to the Pilot manifest, qualification, policy, and credit file. A blocked gate writes
  zero authorized Final executions.
- Added a bound Final-config command and minimal create-only freeze staging for benchmark runtime
  source, Final config, implementation runtime source, and dependency locks. Environments, caches,
  secrets, Pilot records, and unrelated evidence are excluded.
- Added mandatory live-Final verification before and after dispatch. A missing, wrong-schema,
  tampered, or non-active frozen root stops before a provider call or invalidates the return.
- Fresh offline gate: 171 tests passed; Ruff reported no findings; the Pilot dry run remained exactly
  112 executions, four configurations, fourteen scenarios, two variants, 56 semantic groups, zero
  model calls, zero database writes, and plan hash `b837a09632fdb77eea86bd0a461ac632be0a979eb7c71e989ee2b5debc832fe4`.
- No Pilot-3 output root or provider invocation was created during this work.
