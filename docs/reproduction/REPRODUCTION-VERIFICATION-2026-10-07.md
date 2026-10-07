# Reproduction verification — 7 October 2026

**PASS within the scope below.** A fresh archive extraction and isolated Python environment reproduced the original online analysis, supplementary A analysis, post hoc sensitivity and repaired Python witnesses. A separate portable replay reproduced the historical correction-chain audit. Original failures, unknown outcomes and separate collection denominators were preserved.

The scientific inputs were taken from commit `c66bab68f4e143c738e47e3c5d976add756c7ddc`. This report accompanies release `kais-reproducibility-2026-10-07`; the [artifact manifest](ARTIFACT-MANIFEST.json) identifies the release archives and current manuscript files. The editable manuscript ZIP is an overlay, not the complete raw-data deposit.

Machine-readable records: [analysis verification](REPRODUCTION-VERIFICATION-2026-10-07.json) and [historical audit verification](HISTORICAL-AUDIT-VERIFICATION.json). Reproduction instructions and paper mappings are in the [root guide](../../REPRODUCIBILITY.md) and [artifact map](ARTIFACT-MAP.md).

## Environment and preserved inputs

Verification used **Windows x64 and Python 3.11.9** in a newly created virtual environment. The complete resolved package set is recorded in [`requirements-offline-2026-10-07.txt`](requirements-offline-2026-10-07.txt). Installation succeeded and `python -m pip check` reported no broken requirements. This is the reproduction environment; it is not a retrospective claim that every original collection used these dependency versions. Another operating system was not executed in this check.

Both raw archives matched their recorded SHA-256 before extraction. After all analysis commands, every extracted archive file retained its expected hash:

| Archive | Files checked after reanalysis | Result |
|---|---:|---|
| Original `cloud-handoff/replication-package.zip` | 16,074 | All SHA-256 values unchanged |
| Complete supplementary `quota-recovery-complete.zip` | 16,951 | All SHA-256 values unchanged |

All new outputs were written into fresh analysis directories or disposable copies. The original 512-arm ledger was not replaced by supplementary results.

## Commands actually executed

All nine commands below exited with code zero. Exact argument arrays and observed elapsed times are retained in the analysis verification JSON. Paths are relative to the extracted reproduction workspace; the final witness command runs from the explicitly stated `formal/` directory.

| Step | Executed entry point and options | Result |
|---|---|---|
| Original freeze | `research/agent-policy-phase2-formal-2026-10-07/run_formal.py --verify-only` | Frozen identity checks passed; no collection started |
| Original analysis | `research/agent-policy-phase2-formal-2026-10-07/analyze_formal.py --output fresh-primary --figures` | Original analysis and result figures generated |
| Supplementary safeguards | `python -B -m unittest discover -s research/phase2-followup-analysis-2026-10-07 -p test_analysis.py -v` | 18 tests passed |
| Supplementary analysis | `research/phase2-followup-analysis-2026-10-07/analyze.py --output research/phase2-followup-analysis-2026-10-07/reproduction` | Independent scores and cohort outputs generated |
| Native usage audit | `research/phase2-followup-analysis-2026-10-07/audit_usage.py --output research/phase2-followup-analysis-2026-10-07/reproduction` | Native invocation/response accounting generated |
| Supplementary cross-file check | `research/phase2-followup-analysis-2026-10-07/verify_outputs.py --output research/phase2-followup-analysis-2026-10-07/reproduction` | Planned rows, scores, episodes, transitions, request identities and file digests reconciled |
| Sensitivity safeguards | `python -B -m unittest discover -s research/phase2-followup-sensitivity-2026-10-07 -p test_sensitivity.py -v` | 3 tests passed |
| S13 sensitivity | `research/phase2-followup-sensitivity-2026-10-07/sensitivity.py --output fresh-sensitivity` | Explicit source routing and post hoc outputs generated |
| Repaired witnesses | From `research/authorization-granularity-phase1-2026-10-06/formal/`: `python -B -m unittest discover -s tests -q` | 24 tests passed |

Script entry points without a displayed interpreter prefix were invoked with `python -B`. The witness working directory matters: discovery from the workspace root does not resolve the same local module imports. These Python witnesses do not run Alloy.

## Recomputed tables and summaries

All **18 CSV tables** and all **three analysis summaries** matched the archived scientific values. The row counts below are data rows, excluding headers.

| CSV file | Original | Supplementary A | S13 sensitivity |
|---|---:|---:|---:|
| `table1-outcomes.csv` | 24 | 12 | 24 |
| `table2-continuity.csv` | 261 | 231 | 492 |
| `table3-recovery.csv` | 99 | 83 | 182 |
| `table4-utility-friction.csv` | 512 | 234 | 512 |
| `paired-effects.csv` | 256 | 117 | 256 |
| `failure-archaeology-all-arms.csv` | 273 | 19 | 58 |
| Every listed table | PASS | PASS | PASS |
| `analysis-summary.json` | PASS | PASS | PASS |

Comparison parsed JSON summaries and CSV records. Where a CSV cell contains a JSON object, its decoded contents were compared rather than the order of serialized object keys. Reordering those keys can change file bytes without changing any classification or numeric result; the semantic comparison does not relax the required scientific values. Input preservation remains a separate exact SHA-256 check.

The original analysis retains 512 planned arms. Supplementary A retains its separate 117-pair/234-arm denominator and its failure rows. S13 routes each pair to exactly one declared source and remains explicitly post hoc with `formal_inference_allowed=false`; matching its mechanically reconstructed outputs does not promote it to the original frozen estimator.

## Historical correction-chain replay

The public adapter `reproduction/historical/reproduce.py` was executed using an explicit repository source and a fresh output directory. It verified all **1,854 historical ledger inputs**, restored their declared legacy paths inside a disposable workspace, and ran the original audit script byte-for-byte unchanged. The source files, copied inputs and source metadata remained unchanged; the regenerated summary, all chain records and input ledger matched the archived values semantically.

| Historical check | Reproduced result |
|---|---:|
| Databases scanned | 1,260 |
| Retained correction chains | 84 |
| Evidence associations checked | 252 |
| Record versions checked | 168 |
| Provenance traces checked | 168 |
| Chains with failed checks | 0 |
| Unchanged-field checks | 0 |

The adapter's public interface, refusal to overwrite existing output, protected-source-directory checks, invalid relative paths and symlink escape checks also passed. Its receipt records the executed adapter hash and guard results. Historical source/data files must be fetched separately from the repository; the original Phase 2 handoff ZIP alone does not contain them.

## Limits of this verification

- The commands reanalyze archived provider responses and persisted states. They do not make new model calls, reproduce hosted-model sampling, repeat historical task execution or reassess human annotations.
- The 72-command bounded Alloy suite, browser experiment and fresh E1–E3 performance executions were not rerun in this release check. Their separately pinned routes and archived evidence remain documented in the earlier reviewer guide.
- S13's archived `frozen-exporter-crosscheck` is supporting evidence; `sensitivity.py` does not regenerate that auxiliary directory.
- Numeric outputs and input preservation were verified as described above. Generated plot bytes, PDF metadata, renderer/font differences and fresh timing measurements are not claimed to be byte-identical across environments.
- The historical archive's single-field chains provide zero unchanged-field checks. Their successful replay supplies no additional evidence for that property.

Current PDF and editable-package identities are maintained in the artifact manifest. Manuscript compilation and layout receipts are separate from this raw-data reproduction report.
