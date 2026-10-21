# Reproduce the KAIS manuscript

This guide accompanies **Review-to-Execution Continuity for Corrected Agent State Changes**, the 12-page article and 29-page supplement in [`revisions/2026-10-07-kais-followup/`](revisions/2026-10-07-kais-followup/README.md). It provides an offline route from archived trajectories to analysis outputs. Fresh model calls are a different experiment and are unnecessary here.

中文入口：先获取固定版本和两个原始档案，再在独立目录中重算；原始 512 条轨迹、补采 234 条轨迹和事后敏感性分析始终分别报告。

## 1. Obtain the fixed version

Prerequisites: Git, Python 3.11 and enough disk space for both archives and their extracted working copies. Use a short local path on Windows. Downloading Git objects and installing packages require network access; the analysis steps below do not.

```text
git clone --branch kais-reproducibility-2026-10-07 --filter=blob:none --sparse https://github.com/lhh666-6/auto-dete.git auto-dete-review
cd auto-dete-review
git sparse-checkout set cloud-handoff research/phase2-results-snapshots/2026-10-07-complete research/phase2-followup-analysis-2026-10-07 research/phase2-followup-sensitivity-2026-10-07 revisions/2026-10-07-kais-followup reproduction/dke reproduction/historical docs/reproduction
git rev-parse HEAD
```

Keep the printed commit with your results. Do not add `--depth`: the separate E1–E3 entry point reads pinned historical Git objects. The working branch is `codex/phase2-formal-512-handoff`; the dated tag fixes this documented release. The default-branch landing page links this release. Follow that fixed link for reproduction; the historical `latest/` tree is not the current manuscript.

| Raw input | SHA-256 |
|---|---|
| `cloud-handoff/replication-package.zip` | `1bc17338d18f198811e0e58eca9b64bded29f9b01cd61558862455e7e0d469d8` |
| `research/phase2-results-snapshots/2026-10-07-complete/quota-recovery-complete.zip` | `536f8b7d784d1af118145affd90c3d613b67ad44d9c5b3607b463bcebeacbec1` |

The original archive is also pinned at commit `475e66f549613aaaaa62c2ec81ffdee483636c54`. [The artifact manifest](docs/reproduction/ARTIFACT-MANIFEST.json) identifies the published archives and current PDFs; archive receipts record member-level preservation. Verify the two raw downloads before extraction:

```text
python -c "import hashlib,pathlib; p=pathlib.Path('cloud-handoff/replication-package.zip'); assert hashlib.sha256(p.read_bytes()).hexdigest()=='1bc17338d18f198811e0e58eca9b64bded29f9b01cd61558862455e7e0d469d8'; print('Original archive: PASS')"
python -c "import hashlib,pathlib; p=pathlib.Path('research/phase2-results-snapshots/2026-10-07-complete/quota-recovery-complete.zip'); assert hashlib.sha256(p.read_bytes()).hexdigest()=='536f8b7d784d1af118145affd90c3d613b67ad44d9c5b3607b463bcebeacbec1'; print('Supplementary archive: PASS')"
```

## 2. Prepare a disposable working copy

Run these commands from the clone root. `review-work` must not exist; this deliberately prevents replacing an earlier reproduction. The archive paths and sibling research directories must remain intact.

```text
python -c "from pathlib import Path; import zipfile; r=Path.cwd(); w=r.parent/'review-work'; w.mkdir(exist_ok=False); zipfile.ZipFile(r/'cloud-handoff/replication-package.zip').extractall(w); zipfile.ZipFile(r/'research/phase2-results-snapshots/2026-10-07-complete/quota-recovery-complete.zip').extractall(w); print(w)"
python -c "from pathlib import Path; import shutil; r=Path.cwd(); w=r.parent/'review-work'; names=['research/phase2-followup-analysis-2026-10-07','research/phase2-followup-sensitivity-2026-10-07','revisions/2026-10-07-kais-followup']; [shutil.copytree(r/n,w/n) for n in names]"
cd ../review-work
python -m venv .venv
```

Activate this environment in the current shell:

| Shell | Command |
|---|---|
| PowerShell | `.\.venv\Scripts\Activate.ps1` |
| POSIX shell | `. .venv/bin/activate` |

If activation is unavailable, replace the leading `python` in every remaining command with `.venv/Scripts/python.exe` on Windows or `.venv/bin/python` on POSIX. For the manuscript step, use the environment's absolute executable path after changing directory.

```text
python -m pip install -r ../auto-dete-review/docs/reproduction/requirements-offline-2026-10-07.txt
python --version
python -m pip check
```

The environment lock records the tested Python 3.11.9/Windows package set, including transitive dependencies; installation and `pip check` passed in a fresh environment. The frozen experiment's own `research/agent-policy-phase2-formal-2026-10-07/requirements.txt` pins its three direct dependencies: jsonschema 4.26.0, PyYAML 6.0.2 and matplotlib 3.10.8. If a different platform cannot install the recorded transitive set, resolve that original requirements file in a new Python 3.11 environment and retain `pip freeze` and platform details with the reproduction; do not claim the same environment. TeX, Java/Alloy and browser tools are separate optional routes below.

Preparation is now complete. The following analysis commands use local files and make no provider or network requests. Preserve the clone as the published reference and run all write-producing commands only in `review-work`.

## 3. Reproduce the original frozen collection

```text
python -B research/agent-policy-phase2-formal-2026-10-07/run_formal.py --verify-only
python -B research/agent-policy-phase2-formal-2026-10-07/analyze_formal.py --output fresh-primary --figures
```

`--verify-only` verifies readiness and frozen identities without starting collection. `fresh-primary` must not already exist. The analysis independently reads the original 512-arm collection, retaining quota failures, other failures and unknown integrity.

Expected original completion counts: context **126/256**, bound **128/256**. The frozen paired completion contrast is **+0.78125 percentage points**, with interval **[-1.953125, 3.515625]**. Deployment A reached 11/128 review checkpoints; B reached 128/128. The 117 original A quota-failed prefixes remain in this analysis.

Compare `fresh-primary` with `revisions/2026-10-07-kais-followup/evidence/online/`: the six CSV tables and `analysis-summary.json` carry the reproducible scientific values. CSV fields containing JSON objects can differ in key order; compare their decoded values. Plot PDF/SVG metadata, fonts and renderer details can differ between environments, so generated figure bytes are not a scientific equality criterion.

## 4. Reproduce the separately frozen supplementary A cohort

```text
python -B -m unittest discover -s research/phase2-followup-analysis-2026-10-07 -p test_analysis.py -v
python -B research/phase2-followup-analysis-2026-10-07/analyze.py --output research/phase2-followup-analysis-2026-10-07/reproduction
python -B research/phase2-followup-analysis-2026-10-07/audit_usage.py --output research/phase2-followup-analysis-2026-10-07/reproduction
python -B research/phase2-followup-analysis-2026-10-07/verify_outputs.py --output research/phase2-followup-analysis-2026-10-07/reproduction
```

Expected: **18 tests**; **117 pairs / 234 arms**, including failures; **468 exact score comparisons** and **7,989 validated events**. Completion is **114/117** versus **116/117**. All 15 bound G arms recover with utility and integrity both one: **8 reuse** and **7 reauthorization** paths. Paired G costs are mean **+1.6 calls** and median **+14.532 seconds**.

All three analysis commands must use the **same output directory**, which must be inside this package. Compare generated tables and analysis outputs with its published `outputs/`. `verification.json` records the cross-file checks and hashes. Native accounting retains all 1,477 invocation records, including three failed attempts with unknown usage; it is not complete billable usage.

This cohort was selected by original pre-response quota failure and collected later. Its completion contrast is exploratory and conditional on that selection. It does not replace the original 512-arm estimate.

## 5. Reproduce S13's explicitly post hoc sensitivity

```text
python -B -m unittest discover -s research/phase2-followup-sensitivity-2026-10-07 -p test_sensitivity.py -v
python -B research/phase2-followup-sensitivity-2026-10-07/sensitivity.py --output fresh-sensitivity
```

Expected: **3 tests**. `fresh-sensitivity` must not exist. Inspect `pair-source-map.json`: each pair has exactly one explicitly routed source. The derived view yields **240/256** versus **244/256**, while retaining the two original unknown-integrity arms; `formal_inference_allowed` remains **false**. Compare its tables and summary semantically with the package's `outputs/`, including decoded JSON fields in CSV cells. This retrospective view creates no new independent tasks and is not a new prospective primary estimator.

The archived S13 `frozen-exporter-crosscheck` is supporting verification evidence; `sensitivity.py` does not regenerate that auxiliary directory.

## 6. Check the manuscript and regenerate its figures

```text
cd revisions/2026-10-07-kais-followup
python -B verify_evidence.py
python -B make_revision_figures.py
python -B make_followup_figure.py
```

`verify_evidence.py` runs **29 manuscript/evidence checks** and writes `evidence/final-number-verification.json`; it is not read-only, hence the disposable copy. The diagram generator produces four design/evidence diagrams used across main text and supplement. The comparison generator reads the archived cohort tables and writes `figures/followup-behavior-comparison.*` and its data/source audit. The primary exporter in Step 3 regenerates the original online result charts.

To plot directly from your supplementary export, use `python make_followup_figure.py --followup-dir ../../research/phase2-followup-analysis-2026-10-07/reproduction`. Compare counts, paired-cost statistics and labels with the published data audit before examining graphical differences.

With an existing pdfLaTeX installation and packages from the source preambles, run `./build.ps1` in PowerShell or `bash build.sh` on POSIX. The scripts produce main and supplement PDFs, use no shell escape, and check build diagnostics. Building does not rerun experiments. Exact PDF bytes and page breaks can depend on TeX/font versions; retain build logs. The published reference PDFs have 12 and 29 pages.

## 7. Check the earlier supporting layers

Return to the **clone root**, not the extracted workspace, for the independent [`REVIEWER_GUIDE.md`](REVIEWER_GUIDE.md) route. That guide documents the earlier JIIS/E1–E3 deposit used as supporting scientific evidence; its manuscript labels do not designate the current KAIS article.

| Layer | Supported route and comparison |
|---|---|
| Controlled mechanisms E1–E3 | `reproduction/dke/reviewer.py prepare`, `verify`, `test`, `e1`; optional `e2` and `e3`, using the exact `uv` commands in the earlier guide. Preparation downloads pinned Git objects/dependencies. `verify` reaggregates archived inputs; E1 executes fresh cases. |
| Bounded Alloy and formal–concrete projection | The earlier guide links a **separate** `r31-jss-2026-09-13` checkout and its Java/Alloy tools. Expected archived evidence is 72 command outcomes and 29 projection checks (9 SAT / 20 UNSAT). Python witness tests do not rerun Alloy. |
| Canonical-equality/identity witnesses | In `review-work`, the repaired Phase 1 files are under `research/authorization-granularity-phase1-2026-10-06/formal/`; see the [artifact map](docs/reproduction/ARTIFACT-MAP.md) for the exact test command and scope. |
| Historical correction chains | The original archive retains the audit outputs, input hashes and source. The verified optional route below separately fetches historical databases, restores the archived script's declared paths inside a disposable copy, and reproduces all 84 chains. These are chains, not 84 independent task successes. |

Fresh timing measurements depend on hardware and load. Compare decisions, query answers, workload sizes and timing distributions; do not expect identical milliseconds or generated identifiers.

### Optional: replay the historical correction-chain audit

From the **clone root**, hydrate the additional historical source/data directories. This Git preparation needs network access; the following Python audit uses only local files and the Python 3.11+ standard library.

```text
git sparse-checkout add research/authorization-granularity-phase1-2026-10-06 r21-jss/evidence/agent-authority-benchmark-v2/final/2026-09-01-three-config-10x r21-jss/source/implementation/app/domain r21-jss/source/implementation/app/application r21-jss/source/agent-authority-benchmark/auto_decte_agent_benchmark latest/code/implementation-fixed/app/domain
python -B reproduction/historical/reproduce.py --output .reviewer-work/historical
```

The output path must be new. The helper validates all **1,854 ledger inputs**, copies them and the unchanged audit script into its own workspace, reruns the script, compares archived outputs, and verifies that both original and copied inputs remain unchanged. Allow approximately **275 MB** for the copied input files, plus outputs. It reproduces **1,260 databases / 84 chains / 252 associations / 168 versions / 168 provenance traces**, with zero failures and zero unchanged-field checks. It requires no Git LFS, Java, browser or provider calls. The [historical audit receipt](docs/reproduction/HISTORICAL-AUDIT-VERIFICATION.json) records the verified Windows/Python 3.11.9 run; Linux execution has not been separately verified.

## Reporting a discrepancy

Record the release commit, exact command, Python/OS and dependency versions, output receipt, and the first mismatching pair/file. A hash failure should be investigated from a fresh extraction; do not edit frozen manifests or source hashes to make validation pass. Keep original failures, unknowns, transport attempts and separate cohort denominators.

The [artifact map](docs/reproduction/ARTIFACT-MAP.md) links paper items to inputs, scripts and outputs. The [verification record](docs/reproduction/REPRODUCTION-VERIFICATION-2026-10-07.md) records the fresh release run: all nine offline verification/analysis commands passed; 18 supplementary, 3 routing and 24 repaired-witness tests passed; all 18 CSV tables and three analysis summaries matched their archived scientific values. It also states the remaining scope limits; the bounded Alloy suite was not freshly rerun in this release check. Archived provider responses permit offline rescore/reanalysis, not deterministic reproduction of a new hosted-model run.
