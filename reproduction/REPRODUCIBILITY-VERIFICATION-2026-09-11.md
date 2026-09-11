# Independent reproducibility verification — 2026-09-11

Scope: does the code and evidence in this repository reproduce the experiments
reported in *Authoritative-State Admission for AI-Derived Updates* (JSS
submission candidate, main 63 pages + supplement 20 pages)?

Verification baseline: commit `61f99f72433f446385aa8c2501bf33382c32bb63`
(`origin/main`). Every check below was executed against that revision. All
reruns wrote to scratch paths **outside** the sealed trees, so no frozen
evidence was modified; `git status` was empty before and after, and
`python verify_latest.py` passed at 1306 files both times.

## Verdict

**Reproducible**, for every result that does not require a hosted model or the
external DeepSeek Harness host. The two excluded categories are disclosed in
the manuscript itself and are not hidden.

| RQ | Experiment | Verdict | Evidence from this verification |
|---|---|---|---|
| RQ1 | Alloy: Full separates legal / rejected / trace-corrupt histories | **Exact** | Re-executed all 72 commands on the bundled `tools/jre21` runtime: `BATCH_ALLOY_FREEZE_PASS COMMANDS=72`. Field-level diff against the frozen `command_results.json`: **0 differences**; SAT 44 / UNSAT 28 identical. |
| RQ2 | Alloy: per-conjunct ablation sensitivity | **Exact** | Same 72-command rerun; all 22 `*-effective_pair` witnesses reproduced. |
| RQ3 | 9 intended projections + 20 mapping mutants | **Exact (after regeneration)** | `generate_formal_refinement_records.py` → `CASES=29 SAT=9 UNSAT=20`; `verify_formal_refinement_records.py` → `PASS`. The frozen records are now deposited; see "Gaps found" below. |
| RQ4 | 35-case fault catalogue | **Exact** | `run_catalogue.py` → `executed_denominator 35, passed 35, failed 0`; `verify_catalogue_results.py` → `PASS`. |
| RQ5 | Transactional lifecycle + executable relation controls | **Exact** | Checklist control: 18 runs / 11 rejected / 16 single-history records, `outcome_agreement_cases` = the same 7 cases, `outcome_divergent_cases = ['equal-value-substitution']`, `paired_history_states_equal = {candidate_bound: False, value_audit: True}`. Strengthened baseline: `B1_vs_Full` agreement 7/8, divergence `equal-value-substitution`. |
| RQ6 | Admission / trace / storage cost | **Protocol exact, latencies environment-dependent** | The structural invariants are exact: 10 admission cells × 200 trials, 36 trace cells, and **every trace observation issued exactly 12 SQL statements** (`[12, 12]` in both the frozen and rerun data). Wall-clock medians differ (admission p50 19.0–223.0 ms vs the frozen 17.8–194.9 ms; optimized trace p50 4.28–96.47 ms vs the frozen 4.34–53.05 ms) because they are timings on different hardware. The numbers printed in the manuscript trace **exactly** to the deposited JSON: `17.820..194.862`, `10.469..16.479`, `7.455..182.021`, `4.338..53.049`, max p95 `64.360`. |
| RQ7 | Pinned agent-harness integration | **Source present, host external** | The plugin, driver, and `SOURCE_PIN.json` (project + tag + commit `b150a551b` + three SHA-256 pins) are in `r21-jss/source/dsh-plugin-auto-decte/`. Re-running the ten cases additionally needs the pinned DeepSeek Harness release (`deepseek-harness-dsh-v0.1.1-rc.2.zip`), which is **not** redistributed here. No API key or live model is needed for the deterministic ToolRuntime experiment itself. |
| RQ8 (analysis) | 1,260-run endpoints, authority counts, failure classes | **Exact** | Recomputed 23 headline claims directly from the frozen normalized records: **23/23 exact** — 1,260 runs; 360 benign; 335 behavior-evaluable; 25 unscored; 320/360 and 320/335 strict; 93 runtime failures = 76 D1 + 4 G1 + 13 G2; 64 of 93 retaining an authority verdict; 899 authority-evaluable challenges; 720 admission-call + 179 capability-unavailable; 0 unauthorized mutation in both. The endpoint sensitivity re-derivation produced `strict-vs-endpoint-completion.json` and `strict-vs-endpoint-runs.jsonl` **byte-identical** to the frozen files, including `strict_recomputation_matches_frozen: true` and the 11-decision decomposition (7 B4 extra parent verification + 4 B1–B3 extra proposal). |
| RQ8 (generation) | The 1,260 live model runs themselves | **Not reproducible** | Requires the hosted OpenAI and DeepSeek configurations. The manuscript states this and reports the runs as frozen records; no hosted-model call is made by any verification step here. |
| S2 | Human annotation agreement | **Exact** | `recompute_irr.py` (5,000 replicates, seed 20260910) → **72/72 values identical**, including inter-human κ 0.974440895 and human–rule κ 0.409927942. `analyze_acknowledgment_annotation.py` → `matched=325 agreement=286/325 kappa=0.644171`, and all five output files **byte-identical** to the frozen versions. |
| S2 | Software tests | **Exact** | `pytest` in `code/implementation-fixed/`: **389 passed**. `code/formal-fixed/` witness tests: **19 passed**. `code/checklist-example/`: **27 passed**. `code/strong-baseline/`: **9 passed**. |

## Environment used

| Component | Value |
|---|---|
| Python | CPython 3.11.9 (matches the recorded target) |
| Java | bundled `tools/jre21/jdk-21.0.12.1+1-jre` (Temurin 21.0.12.1) — no system Java needed |
| Alloy | bundled `tools/alloy-6.2.0.jar` |
| SQLAlchemy | **2.0.23** on the verifying machine; `uv.lock` pins **2.0.51** |
| Hypothesis / pytest / NumPy | 6.165.10 / 9.0.3 / 2.3.5 |

The SQLAlchemy version is the one recorded-environment deviation in this
verification: the checks were run against the interpreter already present on the
verifying machine rather than inside `uv sync`-resolved environment. Everything
passed anyway, which is a robustness observation and not a claim that the pinned
environment is unnecessary. Anyone reproducing with `uv sync --extra dev
--extra research` will get the lock-pinned 2.0.51.

## Gaps found and resolved in this round

1. **RQ3 refinement freeze was not deposited.** `verify_formal_refinement_records.py`
   reads `conformance/ACTIVE_REFINEMENT_FREEZE.txt` and
   `conformance/raw-results/<freeze-id>/`, neither of which shipped in the
   previous revision, so the verifier failed out of the box with
   `No such file or directory`. Resolved by regenerating the 29-case freeze with
   `generate_formal_refinement_records.py` and depositing it (175 files, 2.1 MB,
   no absolute paths in the artifacts) together with the active-freeze pointer.
   The verifier now passes on a clean checkout.
2. **`latest/README.md` reproduction path did not mention RQ3 refinement
   verification, and did not document the out-of-tree Alloy rerun.** Both are now
   included, including the `-OutputRoot` parameter that lets a reviewer re-execute
   the 72 Alloy commands without writing into the sealed tree.

## Known non-bit-reproducible items (expected, not defects)

- **Wall-clock latencies (RQ6).** Timing is hardware- and load-dependent. The
  manuscript already describes these as measured in a fixed recorded
  environment, and labels the admission gap as descriptive.
- **`clock_wallclock` variant of the identity-isolation control.** Of the 148
  differing values in `e1_results.json`, **all 148 are confined to the variant
  that deliberately reads the real wall clock**; conclusion-level fields differ
  in **0** places. The `clock_deterministic` variant is stable.
- **`checklist-runs/summary.json`.** The deposited frozen file is a strict subset
  of what the current runner emits: the rerun adds `database_executions`,
  `paired_history_records`, `run_definition`, and `single_history_records`. All
  scientific values are identical. `runs.json` is byte-identical.

## How to repeat this verification

```bash
# 0. work from a checkout of the verified revision, with scratch space outside it
mkdir -p /tmp/autodecte-verify

# 1. package integrity
cd latest && python verify_latest.py                 # -> 1306 files, pages main 63 / supplement 20

# 2. Alloy, re-executed (needs only the bundled JRE); writes outside the tree
pwsh -c "& './formal/alloy/batch/run_batch_alloy.ps1' -FreezeId verify-1 -OutputRoot /tmp/autodecte-verify/alloy"
pwsh -c "& './formal/alloy/batch/verify_batch_package.ps1' -RequireRawResults"

# 3. conformance catalogue and formal-concrete refinement freeze
cd code/implementation-fixed
python -B conformance/run_catalogue.py --output /tmp/autodecte-verify/catalogue
python -B conformance/verify_catalogue_results.py /tmp/autodecte-verify/catalogue
python -B conformance/verify_formal_refinement_records.py

# 4. implementation and formal witness tests
python -B -m pytest -q -p no:cacheprovider           # -> 389 passed
cd ../formal-fixed && python -B -m unittest discover -s tests   # -> 19 passed

# 5. annotation agreement (standard library + NumPy + openpyxl only)
cd ../../evidence/human-annotation-2026-09-10
python -B recompute_irr.py --labels labels-A1-A2-normalized.csv \
  --out /tmp/autodecte-verify/irr.json --replicates 5000 --seed 20260910

# 6. RQ8 recomputation from the frozen records and raw traces
#    normalized records: code/figure-work/evidence/agent-authority-benchmark-v2/
#                        manuscript-input/2026-09-03-three-config-10x/normalized/
#    raw traces:         r21-jss/evidence/agent-authority-benchmark-v2/final/
#                        2026-09-01-three-config-10x/runs/<run_id>/
cd ../../../code/scripts
python -B endpoint_sensitivity.py \
  --runs-root ../../../r21-jss/evidence/agent-authority-benchmark-v2/final/2026-09-01-three-config-10x/runs \
  --normalized ../../figure-work/evidence/agent-authority-benchmark-v2/manuscript-input/2026-09-03-three-config-10x/normalized/agent_authority_benchmark_runs.json \
  --output-dir /tmp/autodecte-verify/endpoint
```

The probe scripts used for this verification are archived under
`reproduction/tools/`.

## What this verification does and does not establish

It establishes that the deposited code, inputs, and frozen records regenerate
the reported numbers for every experiment that can be replayed without a hosted
model, and that the reported numbers trace back to the deposited artifacts.

It does **not** establish independent replication. The verification ran the
authors' own code against the authors' own frozen inputs. It did not
re-implement the admission relation, re-derive the failure model, re-code the
annotations, or obtain a second environment. Independent reproduction in a
different environment remains separate evidence.
