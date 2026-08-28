# AUTO-DECTE R21 progress

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
