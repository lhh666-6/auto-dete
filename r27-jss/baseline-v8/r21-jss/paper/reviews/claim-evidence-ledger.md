# Claim–evidence ledger

**Manuscript:** `paper/main.tex` and included section files  
**Citable baseline:** RC4/G10 final aggregation plus separately manifested lifecycle, harness,
performance, and repeated live-agent Final inputs.  
**Result-input rule:** baseline claims use only the ten R17 inputs; later lifecycle, harness, and
performance inputs retain separate manifests. Repeated-agent claims use only the no-overwrite
staging bundle `evidence/agent-authority-benchmark-v2/manuscript-input/2026-09-03-three-config-10x/`,
whose status is `READY_FOR_MANUSCRIPT_INTEGRATION`. Semantic acknowledgment claims additionally
use the row-complete derived audit under
`evidence/agent-authority-benchmark-v2/analysis/2026-09-05-recognition-semantic-audit/`.
Historical and diagnostic runs are excluded.

## Empirical claims

| ID | Location | Claim | Authoritative input and selector | Transformation | Boundary |
|---|---|---|---|---|---|
| P-ABS-1 | Abstract | five information classes and safe/unsafe history pairs whose removal makes each failure family indistinguishable | `source/formal/observation_witnesses.py` and `evidence/formal/observation-witness-report.json` | derived five-pair projection check; Proposition 1 witnesses | constructive conditional result for the five declared constructions; not universal minimality, schema uniqueness, or failure completeness |
| P-C2-1 | Section 3.3 | five information classes are class-wise irredundant for the declared five failure families and observation model | `source/formal/observation_witnesses.py`; `source/formal/tests/test_observation_witnesses.py`; `evidence/formal/observation-witness-report.json` | five complete safe/unsafe history pairs pass structural domain validation; commit effects/counts derive from connected snapshots (atomic versus fragmented for D_B); source checks resolve a registry and check local field/value consistency and unchanged-source retention; each pair has different derived outcomes, equal projection after removing the target class, and unequal full observation | constructive conditional result for the five declared constructions; not universal minimality, schema uniqueness, or failure completeness |
| FINAL-ABS-1 | Abstract | three qualified configurations, 1,260 planned; benign 320/335 (95.52\%); no unauthorized mutation across 0/720 fixed invalid-tuple calls and 0/179 capability-unavailable checks; 93 runtime failures | frozen `normalized/runs.json`, derived `statistical_analysis_semantic.json`, and Final manifest | exact count/proportion formatting plus host-branch classification | declared Final population only; no claim of 899 model-generated attacks |
| P-RQ1-1 | Results/RQ1 | all 66 matched; each profile 20 SAT and 13 UNSAT, class split 6/11/3 | `alloy_results.json`: `status`, `actual`, `expected`, `profile`, `class` | group/count | UNSAT means none found in scope |
| P-RQ2-1 | Results/RQ2 | eleven selected paired ablation witnesses | `alloy_results.json`: `class == "ablation-witness"` by profile | unique command suffixes; 11/profile | no universal necessity claim |
| P-RQ3-1 | Results/RQ3 | 9 intended SAT and 20 mutant UNSAT | `formal_refinement_summary.json`: counts and `cases[]` | none | selected executable projection |
| P-RQ4-1 | Results/RQ4 | catalogue 35/35, zero failed | `conformance_summary.json`: declared/executed/passed/failed | none | declared catalogue only |
| P-RQ4-2 | Results/RQ4 | stateful 2; rollback/concurrency 33; Python 354; Ruff/mypy zero; 52 typed files | `quality_summary.json.commands[]` by `command_id` | none | software regression evidence |
| P-RQ5-1 | Results/RQ5 | 2 versions; candidate 100; authorized 101; batch/operator copy-forward; complete trace/export equality | `lifecycle_summary.json`: `versions`, `correction`, `copy_forward_fields`, `trace_status`, `export_values_equal_final` | none | illustrative synthetic/public lifecycle |
| Q-RQ6-A | Results/RQ6 admission | p50 range, paired delta range, two negative cells, 128/all cell | `cost_summary.json.admission[]` | extrema and three-decimal rounding | lower arm is non-equivalent lower-bound comparator |
| Q-RQ6-T | Results/RQ6 trace | 36 cells, 7,200 obs, p50 range, max p95 and cell | `cost_summary.json.trace[]` | count, sum, extrema | fixed Windows/Python/SQLite grid |
| Q-RQ6-S | Results/RQ6 storage | three incremental byte counts, FK/WAL/SHM conditions | `cost_summary.json.storage[]` | none | main DB; one SQLite setup |
| R21-RQ6-A | Results/RQ6 admission | ten equivalent cells, 2,000 pairs, full/materialization p50 and paired mean delta | `r21_feature_baseline_summary.json.results[]` | extrema and three-decimal display | prevalidated persistence ablation, not a safe alternative path |
| R21-RQ6-T | Results/RQ6 trace | same 36 cells/7,200 observations; 12 SQL statements; optimized p50/p95 and descriptive ratio | `r21_trace_optimization_summary.json.results[]` | cellwise comparison to exact RC4/G10 baseline raw | sequential runs; no portable speedup claim |
| FINAL-RQ8-U | Results/RQ8 | benign completion 320/335; semantic context acknowledgment 117/174; semantic stale acknowledgment 150/151; recovery counts | derived `analysis/2026-09-05-recognition-semantic-audit/statistical_analysis_semantic.json`; row-level `recognition_semantic_audit.csv` with per-row rule and text; curated negated/echo/synonym cases in `semantic_audit_examples.json` | exact benign interval; deterministic rubric applied to every 325 behavior-evaluable target output; count/evaluable N | descriptive behavior; unequal denominators; single-rubric post-hoc coding, not general recognition ability |
| FINAL-RQ8-A | Results/RQ8 | aggregate authority accounting 0/899, decomposed into 0/720 fixed host invalid-tuple calls and 0/179 capability-unavailable branches; zero by mechanism/configuration | frozen `normalized/runs.json`; `source/agent-authority-benchmark/.../host_challenges.py`; staged `statistical_analysis.json.admission_mechanism` | branch/scenario count and pre/post digest/rejection checks; reference one-sided binomial bound | no model-generated-attack, population-rate, or universal zero-risk claim |
| FINAL-RQ8-F | Results/RQ8 | 93 runtime failures: D1 76/420, G1 4/420, G2 13/420; 64 authority-evaluable and 3 behavior-evaluable | frozen `normalized/runs.json`; `paper/scripts/build_runtime_endpoint_table.py` | terminal-class by endpoint-evaluability cross-tabulation | runtime success is not identical to endpoint evaluability |
| P-APP-1 | Artifact appendix | the baseline uses exactly ten normalized inputs, while lifecycle, harness, performance extensions, and repeated-agent evidence remain separately manifested | `r21-paper-input-manifest.json`; extension manifests; staged `MANUSCRIPT_INPUT_STATUS.json` | membership and path reconciliation | evidence-layer identity, not an outcome claim |
| P-APP-2 | Artifact appendix | the staged Final contains all 1,260 normalized rows and binds parent-manifest SHA-256 `6e41...33ec` | staged `MANUSCRIPT_INPUT_STATUS.json.final_manifest_sha256`; staged manifest and normalized-row set | exact hash transcription plus row-count reconciliation | declared Final bundle only; public DOI/URL pending author deposit |

## Generated tables and figures

| Artifact | Evidence | Generator/source | Status |
|---|---|---|---|
| Table `tab:alloy-outcomes` | `alloy_results.json` | `jss/scripts/build_evidence_tables.py` → `formal_evidence.tex` | generated and unit-tested |
| Table `tab:executable-evidence` | quality, refinement, conformance, lifecycle inputs | generator → `validation_evidence.tex` | generated and unit-tested |
| Table `tab:admission-cost` | `cost_summary.json.admission` | generator → `admission_cost.tex` | generated; negative cells retained |
| Tables `tab:trace-cost`, `tab:storage-cost` | `cost_summary.json.trace/storage` | generator → `trace_storage_cost.tex` | generated |
| Table `tab:feature-baseline` | `r21_feature_baseline_summary.json.results` | evidence-linked rendering → `feature_baseline_cost.tex` | all ten equivalent cells shown |
| Table `tab:trace-optimization` | `r21_trace_optimization_summary.json.results` | evidence-linked rendering → `trace_optimization.tex` | representative cells; extrema stated in prose |
| Figure `fig:admission-workflow` | formal contract plus author-approved Canva design `DAHUNAr-imw` | exact Canva export `figures/canva/admission-workflow-canva.pdf`; converted delivery master `figures/canva/admission-workflow.svg`; Canva rich-text content verified against the contract on 2026-09-04 | Exact author design included as a hybrid vector PDF; the SVG retains the same rendered content, including Canva-rasterized decorative layers |
| Figure `fig:evidence-chain` | evidence-layer design and normalized input lineage | same generator; independent vector construction | generated; SVG/PDF vector-audited |
| Figure `fig:cost` | all `cost_summary.json` admission/trace/storage cells | same generator; deterministic data visualization | generated and unit-tested; two negative cells retained |
| Table `tab:agent-behavior-final` | derived semantic audit statistics plus frozen benign/recovery endpoints | `scripts/audit_recognition.py`; generated after auditing all 325 target outputs | all configuration rows shown; acknowledgment labels replace lexical recognition proxies |
| Table `tab:runtime-endpoint` | frozen `normalized/runs.json` | `paper/scripts/build_runtime_endpoint_table.py` | all 93 runtime failures crossed with model configuration and endpoint evaluability |
| Table `tab:admission-mechanism-final` | staged Final `statistical_analysis.json.admission_mechanism` | frozen Final paper-reporting bundle; label added at integration | all configuration and mechanism counts shown |
| Figure `fig:behavior-authority` | derived semantic audit statistics, frozen primary endpoints, and host-branch authority decomposition | `paper/scripts/build_figures.py`; deterministic grouped-dot and zero-event-bound rendering | generated and unit-tested; runtime failures separate; descriptive interpretation only |

## Mechanism claims

| ID | Mechanism | Frozen source anchor | Limitation |
|---|---|---|---|
| M-CAP | separate candidate/read/fact ports and facades | `source/implementation/app/application/ports.py`; `authority_facades.py` | same-process application boundary |
| M-EID | canonical content+locator evidence identity | `source/implementation/app/domain/evidence_identity.py` | SHA-256 collision/host compromise excluded |
| M-SHAPE | exact initial/later field shape and no-op rejection | `source/implementation/app/domain/admission.py` | deletion not modeled |
| M-TXN | commit-time revalidation, CAS, complete source map, atomic inserts | `source/implementation/app/adapters/database/repositories.py` | SQLite configuration only |
| M-PRINCIPAL | role policy rechecked at commit | `source/implementation/app/domain/principal.py`; repository CAS unit | not authentication/session integrity |
| M-TRACE | full prefix source evolution and authority-chain validation | `source/implementation/app/application/query_forms.py` | pre-certificate legacy reported separately |
| M-FORMAL | batch relation, Full contract, P0–P6, paired ablations | `source/paper-repo/formal/alloy/batch/auto_decte_batch*.als` | bounded relational model |
| M-ALPHA | persisted pre/post to fixed Alloy instance | `source/implementation/tests/conformance/alloy_projection.py` | selected traces, not total proof |
| M-ORACLE | raw relational oracle and database digest | `source/implementation/tests/conformance/oracle.py` | finite declared relations/mutants |

## Audit rules

- Any changed number must be regenerated, never hand-edited in a table.
- Any new empirical sentence must receive an ID and exact JSON selector here.
- Raw evidence may explain a protocol but cannot substitute for a normalized result.
- Literature claims are tracked separately in `citation-ledger.md` and remain
  subject to R16 primary-full-text verification.
- A visible manuscript placeholder is not evidence and must be resolved or
  reported before the final readiness verdict.
