# Reproduce the ASE manuscript (21 October 2026)

This is the current entry point for **The Review–Execution Gap in Agentic Software: Specification, Design Space, and Empirical Characterization**. The main paper has 24 pages; Online Resources 1 and 2 have 29 and 16 pages. The paper and all three source trees are in [the manuscript directory](revisions/2026-10-21-narrative/). Earlier KAIS/JIIS labels inside frozen records identify their collection history, not the current manuscript.

The default route reanalyses existing raw records. It makes no model calls, requires no API key, and preserves the original and supplementary denominators. Download and package installation require the internet; the subsequent analysis is offline.

## 1. Get the fixed deposit

```text
git clone --branch ase-reproducibility-2026-10-21 --filter=blob:none --sparse https://github.com/lhh666-6/auto-dete.git auto-dete-ase
cd auto-dete-ase
git sparse-checkout set reproduction/ase research/agent-policy-phase2-formal-2026-10-07 cloud-handoff docs/reproduction research/phase2-results-snapshots/2026-10-07-complete research/phase2-results-snapshots/2026-10-07T021002Z/original-formal-analysis research/phase2-followup-analysis-2026-10-07 research/phase2-followup-sensitivity-2026-10-07 research/kais-revision-output-audit-2026-10-14 research/kais-budget-sensitivity-2026-10-14 research/kais-commit-uncertainty-2026-10-14 research/kais-native-baseline-probe-2026-10-14 research/kais-approval-workflow-2026-10-14 research/kais-toolgate-public-reference-2026-10-20 research/kais-toolgate-feasibility-2026-10-20 research/kais-external-baseline-sprint-2026-10-15 research/authorization-granularity-phase1-2026-10-06 research/ase-x1-x2-2026-10-21/v2 revisions/2026-10-21-narrative revisions/2026-10-07-kais-followup revisions/2026-10-18-kais-recalibrated/qa revisions/2026-10-20-external-baselines reviews/kais-execution-plan-2026-10-14/baseline-audit/sources reviews/multi-perspective/2026-10-09-work reviews/multi-perspective/2026-10-18-kais-submitted-assets reviews/kais-rejection-2026-10-20
git rev-parse HEAD
```

Keep the printed commit with your results. A full clone of the same tag also works. The long sparse command explicitly includes the historical files named in preserved protection manifests; these are provenance inputs, not extra current papers to read. Use a short checkout/work path on Windows. Reserve several GB for extracted trajectories and the disposable copy. Do not add `--depth` if you also intend to use the pinned historical Git routes in Section 5.

## 2. Prepare an isolated environment and workspace

Use Python 3.11. From the clone root:

```text
python -m venv .venv
```

Activate with `.\.venv\Scripts\Activate.ps1` in PowerShell or `. .venv/bin/activate` in a POSIX shell. If activation is unavailable, substitute the environment's Python executable in subsequent commands.

```text
python -m pip install -r docs/reproduction/requirements-offline-2026-10-07.txt
python -m pip check
python reproduction/ase/reproduce.py verify
python reproduction/ase/reproduce.py prepare --work ../ase-work
```

`../ase-work` must be new and outside the checkout. Preparation verifies SHA-256 identities, safely extracts both original archives, restores the expected source layout, and copies the later experiments and current manuscript. It does not replace deposited files. The original archives remain separately authenticated:

| Archive | SHA-256 |
|---|---|
| `cloud-handoff/replication-package.zip` | `1bc17338d18f198811e0e58eca9b64bded29f9b01cd61558862455e7e0d469d8` |
| `research/phase2-results-snapshots/2026-10-07-complete/quota-recovery-complete.zip` | `536f8b7d784d1af118145affd90c3d613b67ad44d9c5b3607b463bcebeacbec1` |

The [current manifest](reproduction/ase/MANIFEST.json) authenticates the supplied inputs, scripts, current PDFs and source package. The dependency lock is the tested offline-analysis environment; framework/CLI execution dependencies are separate and are not needed for these saved-evidence checks.

## 3. Run the offline reproduction

Remain in the clone root:

```text
python reproduction/ase/reproduce.py run --work ../ase-work
```

The command stops at the first unexpected failure. Logs, comparisons and the overall `RUN.json` are under `../ase-work/ase-reproduction-results/`. Never remove a failed receipt to present it as success; fix the cause and prepare a fresh work directory. Each underlying command is listed in `reproduce.py`, so a failure can be investigated individually. Analysis scripts that historically write next to themselves run only in the disposable copy.

| Check | Expected scientific result |
|---|---|
| Original cohort | 512 planned arms; completion 126/256 context, 128/256 bound; quota failures and unknowns retained |
| Supplementary A | 117 pairs / 234 arms; completion 114/117 vs 116/117; separate collection and exploratory estimate |
| Historical post hoc sensitivity | 240/256 vs 244/256; `formal_inference_allowed=false`; not a replacement primary estimator |
| Recovery decomposition | 32 delivered G pairs / 16 task definitions; 24 reuse, 8 fresh authorization; mean complete-suffix differences 1.00 original B and 1.60 supplementary A |
| Recovery example | FORMAL-G-002-B: one recovery commit, one subsequent receipt query, zero context-side agent calls |
| X1/X2 saved runs | 111 pinned file hashes, semantic run comparisons, actual SQLite effects and independent X2 scoring |
| Original-B truncation | 1,372 responses, 79 capped responses; original outcomes retained |
| Later budget study | 96 continuations, 24 tasks; low-budget completion 23/24 vs 22/24, high-budget 24/24 vs 24/24 |
| Uncertain commit outcomes | Both saved 32-record runs recomputed from raw transcripts and SQLite snapshots |
| ToolGate development controls | T-configured 8/8 and C 8/8 |
| ToolGate public workflows | 48 routes: T strict 23 PASS / 1 FAIL and C 24 PASS; the original diagnostic-output failure is retained |
| OpenTofu saved-plan workflows | Two saved 32-record runs; per-record results and normalized summaries agree; native CLI is not rerun |
| N preview exposure | Archived arm-level exposure CSV regenerated and compared; 124 delivered equivalent previews, 123 reuse and one reauthorization |

The final step compares regenerated scientific JSON/CSV values to the deposited outputs. Only the budget summary's generation timestamp is excluded. Nested JSON CSV cells are compared by value. Input/output byte hashes and statistical units are different checks and are reported separately.

Some historical ToolGate freezes contain absolute source paths. `path-map.json` maps those exact files to this deposit, preserving their expected hashes. `check_later.py` verifies every mapped hash and translates paths only in the scorer's in-memory input. It does not change a gate, score definition, deposited freeze or saved run. The reported frozen failure is checked explicitly; an arbitrary exit code 1 is never treated as successful reproduction.

## 4. Build the manuscript

With Python and pdfLaTeX/BibTeX installed:

```text
cd revisions/2026-10-21-narrative
python build.py
```

This builds `main.pdf`, `Online-Resource-1.pdf` and `Online-Resource-2.pdf`. The reference main PDF is `main-submission.pdf`; the source ZIP includes all figures and both supplements. Building needs no experimental downloads. Fonts, TeX versions and PDF metadata can change binary hashes; compare content and retain logs. Optional figure regeneration is documented in the manuscript README. Figure 4 uses frozen measured data; the other three figures are authored diagrams.

The AI declaration follows the authors' correction: DeepSeek assisted Agent-experiment data collection; ChatGPT 6 Astra assisted experimental verification and selected language polishing. Glyph-generation provenance remains separately disclosed.

## 5. Supporting historical layers and fresh executions

These routes remain available at their original fixed versions. They are distinct from the standard saved-data pass above.

| Layer | Entry point and dependency |
|---|---|
| E1–E3 controlled experiments | [Earlier reviewer guide](REVIEWER_GUIDE.md), `reproduction/dke/reviewer.py`: prepare/verify/test/e1; browser E2 and timing E3 are separate. Pins DKE `2645e5e18c900ea91c9c980e44195dc71e410432` and reference `c6d512843c905cab6d8521dd8c914f7fb26d85ae`. Add `reproduction/dke` to sparse checkout. |
| Bounded formal evidence | `r31-jss-2026-09-13` guide and Java/Alloy tools: 72 command outcomes, 9 SAT / 20 UNSAT projections. No claim that the standard route reruns Alloy. |
| Historical correction chains | `reproduction/historical/reproduce.py` and the [historical guide](REPRODUCIBILITY-KAIS-2026-10-07.md): hydrate the listed database/source directories first. 1,260 databases, 84 chains, 252 associations, 168 versions and 168 provenance traces. |
| Fresh X1/X2 | Extract the current `X1-X2-reproduction.zip` and follow its `REPRODUCE.md`; install its own pinned requirements. Use new run directories. |
| Fresh native baseline probe | Archived `run_probe.py`, fixed CK source and original Host, with jsonschema; existing results include two unrepresentable conditions. |
| Fresh OpenTofu runs | Archived downloader and `software_sources.json` pin OpenTofu 1.13.1. The optional Windows binary is fetched and checksum-checked rather than redistributed. Follow its frozen workflow protocol. |
| Fresh ToolGate/public workflows | Archived runners and dependency locks are supplied with their sources. Their original machine-specific freeze checks require explicit relocation; the portable standard route covers saved-evidence rescoring, not a claimed fresh cross-platform framework run. |

Fresh hosted-model runs require provider access and are new realizations, not deterministic reproductions of the saved responses. They are deliberately absent from the default runner.

See [pipeline.md](pipeline.md) for the paper-to-script mapping and [the verification record](docs/reproduction/ASE-VERIFICATION-2026-10-21.md) for exactly what was executed in this release.
