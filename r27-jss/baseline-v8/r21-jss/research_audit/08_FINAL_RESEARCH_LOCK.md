# 08 — Final Research Lock

**Date:** 2026-08-28

**Gate:** `R21 EVIDENCE LOCKED / FINAL PAPER GATES CLOSED`

**Scope:** this lock authorizes an evidence-bounded paper rewrite and records the completed R21 technical gates. It does **not** assert an unbounded proof, external validity, or reviewer-fetchable artifact hosting.

## 1. Authoritative baseline

The only citable source/evidence baseline is:

`release-staging/2026-08-24-option-a-r13-v14/`

| Item | Locked value |
|---|---|
| Source manifest SHA-256 | `9ed1fdd1a6969675b742756944910d298edbc39cf456538334b9efd702ad4547` |
| Runner config SHA-256 | `32383f25468d768a4b3e418b242df21ffb0b00e01a2ec2290fb6ac300be6f329` |
| Dependency lock SHA-256 | `698e7fc510a93c15bc2dc69d2a1f4ade1ceba3f8beda2e54ee9b05e643a477ad` |
| Frozen evidence manifest SHA-256 | `8f0d604ecf9cbe8e2974492ed3e031cec13a680d1be3046d98b46895d773d85d` |
| Paper-input manifest SHA-256 | `dab2f250e4b6eadbd5c38955c8cf7f8f80e54d49ccc33c6ef825083b60dd6f2c` |
| Raw-to-paper lineage SHA-256 | `d3baf74d02690b0477d0fd3d7409a64b75826a51beb46597c791952dfe13451e` |
| Platform | Windows 10 build 26200, CPython 3.11.9, SQLite 3.45.1 |

Both correctness and performance metadata bind the same source, config, and dependency-lock hashes. The staged package verifier passed after the evidence manifest was created.

Historical v5–v13 candidates and the first interrupted v14 performance attempt remain failure/provenance evidence. They are not alternative result baselines and must not be combined selectively with the citable v14 inputs.

## 2. G7 evidence verdict

### 2.1 Correctness and conformance

The consolidated raw-receipt summary records 10/10 successful commands: nine correctness commands and one performance command, with zero timeouts and zero failed commands.

The correctness evidence locks the following bounded observations:

- Python full suite: 354 passed.
- Ruff static check: exit 0.
- Mypy: exit 0 over 52 typed source files.
- Paper-strength stateful profiles: 2 passed.
- Rollback and concurrency profiles: 33 passed.
- Batch Alloy matrix: 66/66 classified outcomes, with S1 and S2 each containing 20 SAT and 13 UNSAT outcomes.
- Formal–concrete projection freeze: 9 intended SAT projections and 20 UNSAT mapping mutants.
- Independent production-facing catalogue: 35/35 declared cases passed.
- Illustrative document lifecycle: status and reverse trace complete; final export equals the committed final values.

These results support bounded model-analysis and executable-conformance claims only. They are not a general mathematical proof, security proof, industrial validation, or proof of correct human judgments.

### 2.2 Fixed-grid cost characterization

The successful non-overwriting v14 performance rerun is `evidence/frozen/performance-rerun-2/`. Its receipt records exit 0, no timeout, and 8,688.81 seconds.

| Experiment | Frozen coverage |
|---|---|
| Admission | 2,000 paired observations; 10 cells; 200 measured pairs per cell |
| Reverse trace | 7,200 observations; 36 cells; 200 trials per cell |
| Storage | 3 populations: 1,000, 10,000, and 100,000 transitions |

Structural checks passed for every cell: complete pair/trial indices, positive latency and SQL-statement counts, the exact declared grid, empty foreign-key failure lists, exact incremental-byte arithmetic, and zero residual WAL/SHM bytes after the measurement protocol.

The observed admission full-path p50 ranges from 17.996 ms to 214.759 ms across the declared cells. Paired mean deltas range from -6.138 ms to 186.393 ms. The negative deltas in two 128-field sparse-change cells are retained rather than normalized away; they describe this comparator and setup, not a universal speed advantage.

The observed trace p50 ranges from 6.138 ms to 7,681.505 ms. The maximum p95 is 8,122.484 ms in the 128-field, 100-version, 1,000-record cell. Version depth and field count dominate the exercised grid; no asymptotic or workload-external claim is authorized.

Incremental main-database bytes are 1,085,440; 10,772,480; and 111,230,976 for 1k, 10k, and 100k transitions. These are SQLite/configuration-specific measured values, not cross-database storage guarantees.

### 2.3 Evidence integrity and paper inputs

The final aggregation root copies, without overwriting, the verified v14 correctness run and the successful performance rerun into `evidence/frozen/final-input-root/{correctness,performance}`. The BOM-capable staged runner reproduced normalized inputs into `evidence/frozen/paper-final/`.

Exactly ten paper inputs are locked:

1. `run_summary.json`
2. `quality_summary.json`
3. `alloy_results.json`
4. `formal_refinement_summary.json`
5. `conformance_summary.json`
6. `lifecycle_summary.json`
7. `cost_summary.json`
8. `cost_run_metadata.json`
9. `correctness_environment.json`
10. `performance_environment.json`

The lineage ledger has ten paper-input entries and 28 hashed source references. Every paper-input hash and every referenced raw-source hash was independently recomputed and matched. The whole frozen-evidence manifest covers 1,244 files and 496,220,355 bytes, excluding only its own non-self-referential manifest file.

A deliberate one-byte/whitespace mutation of a copied `paper-final` tree was detected exactly as `hash:paper_inputs/run_summary.json`. The mutated validation copy is retained outside the v14 package as `release-staging/2026-08-24-option-a-r13-v14-tamper-probe-RETAINED/`; it is intentionally invalid, non-citable, excluded from the frozen manifest, and must be excluded from R17 packaging.

## 3. Locked research claim

The paper may claim a conservative composite contribution:

> A certificate-bound admission contract for AI-derived candidate updates in versioned authoritative records, together with a bounded relational analysis of why the selected bindings are necessary, a concrete transactional realization, and executable evidence that selected persisted executions refine the contract and fail closed under the declared catalogue.

The contribution must remain at the exact composite relation established by R0. The paper must not claim novelty for any component in isolation, including provenance, proposal/certification/execution separation, context-bound authorization, non-transferability, freshness/CAS/OCC, append-only evidence, candidate/fact separation, human review, or traceability.

## 4. Required qualifications

Every draft must preserve all of the following boundaries:

- Alloy results are bounded SAT/UNSAT analyses under S1/S2, not unbounded proofs.
- The executable projection covers selected legal and rejected cases; it is not a proof that all implementations refine all formal executions.
- The independent catalogue is declared and finite (35 cases).
- Principal authentication/session integrity is an external prototype assumption; the implementation rechecks an allow-list role but does not solve identity security.
- The lifecycle is illustrative synthetic/public evidence, not a human study or production-effectiveness evaluation.
- Performance and storage results apply only to the frozen Windows/Python/SQLite configuration and fixed grid.
- Human authorization does not establish value truth or reviewer correctness.
- The contract establishes attributable, fail-closed admission under its trust boundary; it does not make arbitrary compromise or silent machine error impossible in all systems.
- Formal same-value admissions remain legal, while the concrete post-initial no-op rejection is an explicitly documented strict refinement.
- Formal P6 covers pointer-stable transition-anchor loss/replacement/duplication; additional concrete pointer/evidence/binding corruptions are separate executable faults.

## 5. Paper construction lock

The paper must consume only `evidence/frozen/paper-final/paper_inputs/` for quantitative and pass/fail statements. Raw files may be consulted for audit and explanation but may not be selectively substituted for normalized inputs. Historical manuscript counts (239, 389, 478, or any other pre-v14 number) are forbidden.

The target remains Journal of Systems and Software unless the venue-evidence step documents a better fit. Paper construction must follow the user-approved workflow exactly:

`literature → paper-skill → latex-template → academic-figure-skill → pre-submission-report`

The user requested an AI-first core workflow figure followed by editable SVG conversion. JSS's current official guide, checked 2026-08-25, prohibits generative-AI or AI-assisted creation/alteration of images submitted in manuscripts. Accordingly, an AI raster may be generated and retained only as a **non-submitted ideation artifact**. The submitted SVG must be rebuilt independently from verified system semantics using deterministic/manual vector tooling; it must not auto-trace, embed, or visually derive from generated pixels. Both artifacts retain provenance and a clear submission-status label. The final SVG must pass vector, text, LaTeX inclusion, grayscale/print, and accessibility checks. If submission of an AI-derived SVG remains mandatory, JSS is blocked absent explicit editorial permission and the target venue must be reconsidered.

## 6. Closed gates and author-only items

- **R15 / G8:** closed. The JSS paper is compiled and visually inspected at 35
  pages with independently constructed editable vectors.
- **R16 / G9:** closed. All 20 novelty/attribution claim groups are accurate
  against primary sources with no Critical/Major/Minor finding.
- **R17 / G10:** closed technically. The RC4 post-paper candidate has a clean
  external extraction, final correctness/performance reruns, typed comparisons,
  clean-before/one-byte-after tamper evidence, and independent audits. The
  quantitative manuscript candidate is `paper-new-all`, generated from the
  final RC4 `paper-from-new-all` inputs.
- Author names, affiliations, acknowledgments, funding, conflicts, data-hosting
  URL/DOI, AI-disclosure approval, and upload authority remain author-only
  metadata and must be marked rather than invented.

## 7. Decision

No mandatory research stop condition is triggered. R15–R17/G8–G10 are closed
for the declared Windows/JSS scope. The remaining work is author-controlled
submission metadata and minor reproducibility documentation; no new scientific
experiment is required by the final gate.

## 8. RC4/G10 final identity and verification

- RC4 ZIP SHA-256:
  `85f5a31d1fdda9b561a650aecfc515232af6df1da5de4fb7277d939e5167dfb9`;
  release manifest SHA-256:
  `29250194d3637fcc725a56aa653efa1335e373c0476d0f7154e794a02fc817c2`.
- Frozen source/config/lock SHA-256 values remain
  `9ed1fdd1a6969675b742756944910d298edbc39cf456538334b9efd702ad4547`,
  `32383f25468d768a4b3e418b242df21ffb0b00e01a2ec2290fb6ac300be6f329`, and
  `698e7fc510a93c15bc2dc69d2a1f4ade1ceba3f8beda2e54ee9b05e643a477ad`.
- Final correctness: 9/9 commands, zero failures; typed comparison PASS 6/6.
- Final performance: exit 0, no timeout, zero command failures; 2,000 admission,
  7,200 trace, and three storage observations. Descriptive comparison PASS on
  the 10/36/3 grid.
- Final paper regenerated from the final RC4 performance input: 35 pages,
  0 fatal/undefined/overfull diagnostics, 1 benign underfull row, 36/36
  active citation keys, and code-paper rerun PASS (10/10 admission rows,
  15/15 trace/storage summaries; appendix hashes PASS).
- Tamper probe `tamper-probe-20260826-2` records verifier PASS before a one-byte
  README mutation and exact `hash:README.md` FAIL afterward. The earlier failed
  sequencing probe is retained as historical evidence.
- Artifact-coherence found no unsupported scientific headline; reproducibility
  records four non-blocking Windows/toolchain/documentation gaps. The current
  dated pre-submission report is `reviews/pre-submission-report/2026-08-26.md`.

## 9. G10 sealed delivery package

- Derived delivery ZIP:
  `release-staging/2026-08-26-option-a-r17-rc4-g10-final.zip` (the final hash
  is recorded in the session progress/findings log, avoiding a circular
  self-reference inside the package).
- Derived release manifest covers 2,210 files; release, declared-source, and
  frozen-evidence verification all PASS after clean extraction. Package
  regression tests pass 19/19 (11 release tools, 6 table, 2 figure tests).
- The synchronized PDF SHA-256 is
  `93e8cb07f754288671a40adffdd0226f47c00e02860c56adc7b8bd5d348fa28a`.
- Code-paper revision report `reviews/code-paper-auditor/2026-08-26-1735-r3.md`
  is PASS 17/17 with zero open issues. G10 tamper-probe-2 is exact: clean
  PASS, one-byte README mutation, then only `hash:README.md` FAIL.

## 10. R18/R19 isolated additions

R18 and R19 do not alter the locked R17 baseline. R18 adds exactly one hosted-AI fixture input,
`ai_origin_lifecycle_summary.json`, for six bounded admission cases. R19 adds exactly one DSH
integration input, `dsh_plugin_integration_summary.json`, for ten bounded adapter cases. Neither
input may be silently counted among the ten R17 baseline inputs.

R19 pins official DeepSeek Harness tag `dsh-v0.1.1-rc.2`, commit
`b150a551b8d465e31e418e1b2eaf5e79bbb7d28e`, release ZIP SHA-256
`9a21c7a347ec59a7e7c91e7c805d8759d5b4357b2245d2e7d85a346c953c845f`, and lock SHA-256
`6f20c268e76df1294c16f016ab10a7fa1271608b4db0f4fafe8f7c21ec90013e`.

The plugin exposes exactly `auto_decte_propose` and `auto_decte_verify`; model-callable fact writes
remain absent and confirmation is host-only. The final ten-case receipt passes 10/10. Its 30-file
manifest verifies cleanly, while the retained one-byte copied receipt fails with only `receipt.json`
changed. Full R19 regression passes 363 Python tests, Ruff, strict mypy over 53 files, and strict
TypeScript. The 41-page paper resolves 42 citations with no undefined reference or blocking LaTeX
warning.

These results establish one fixed-version, keyless external-verifiability demonstration. They do not
establish live-model accuracy, usability, process isolation, industrial scale, production
effectiveness, cross-harness generality, or independent reproduction. The only remaining submission
blockers are the author-controlled items listed in `paper/AUTHOR_INPUT_NEEDED.md`.

## 11. R21 isolated evidence lock

R21 adds exactly three separately manifested paper inputs and does not alter the ten R17 baseline
inputs or the R18/R19 inputs:

1. `r21_live_agent_summary.json`;
2. `r21_feature_baseline_summary.json`;
3. `r21_trace_optimization_summary.json`.

The R21 paper-input manifest SHA-256 is
`022cbb890600789293c377a78cd8920b762dac6bb1dff3324b62b66b2a5b1ca0`. It covers the three
inputs, two generated tables, and 88 source-evidence files / 4,982,570 bytes. Build and verify both
pass by exact content regeneration.

The canonical live-agent run is `evidence/reproduced/r21/live-agent-run-4/`. It records 6/6 tool
completion, 6/6 authority safety, six zero Codex return codes, and identical live experiment source
hashes before and after the run. In L3--L5, model verification is followed by an actual host
confirmation attempt; the recorded rejections are, respectively, version conflict,
`RECORD_BINDING_MISMATCH`, and `FIELD_KEY_BINDING_MISMATCH`, with exact digest stutter. The
requested model alias is `gpt-5.6-luna` at low reasoning effort; the exact two enabled MCP tools are
proposal and verification. The six single executions are not a prompt-robustness rate or a security
proof.

The feature-equivalent persistence ablation completed ten cells and 2,000 pairs. All ten
materialized post-states matched their full-admission reference fingerprints. Full p50 is
17.820--194.862 ms; prevalidated materialization p50 is 10.469--16.479 ms. The arm retains the
complete relational effects but uses a generic delta materializer. Its descriptive gap mixes
excluded validation/planning/object construction with implementation-path differences; it is not a
causal phase decomposition or an authorized alternative fact path.

The clean optimized trace measurement is `trace-optimization-run-2`; comparison-3 binds its raw
SHA-256 `fc4629c6179a82f4b9b1f6949729c6019f3cad1ff6a9ce19015f6a1801b7e0a0` to the exact
RC4/G10 paper-baseline raw SHA-256
`fec36ef9278e8976a92c525a698d0a11a1be53bc7d58a26d1f63cb478b5cf8e3`. The 36 cells and 7,200
trials per side match; every optimized observation executes exactly 12 SQL statements. Optimized
p50 is 4.338--53.049 ms and maximum p95 is 64.360 ms. Cellwise ratios compare sequential recorded
runs and are not hardware-independent guarantees.

Live-agent run-2 remains diagnostic evidence for the earlier verification-only protocol. Run-3 is
an incomplete, non-citable execution retained after Windows locale decoding stopped at L3; its L1
and L2 files are preserved and it has no receipt. Trace run-1 and trace run-2's first comparison
against an earlier performance execution also remain diagnostic. None is an alternative paper
input.

## 12. R21 final-gate closure

The final R21 manuscript was rebuilt at 47 pages and passed the citation, reference, overfull-box,
visual-QA, and paper-input checks. The complete implementation suite passed 364 tests; Ruff and
strict mypy passed; the locked live-agent suite passed 15 tests. The non-self-referential R21
revision manifest was built and verified after all document edits, and an isolated one-byte
mutation probe produced an exact hash failure while the clean copy remained valid. The dated
post-fix audit reports and pre-submission report record no unresolved Critical or Major finding.
The only open items are author-controlled metadata and stable public artifact hosting/DOI.
