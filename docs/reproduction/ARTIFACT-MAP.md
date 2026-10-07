# Paper-to-artifact map

Applies to the 12-page article and 29-page supplement under [`revisions/2026-10-07-kais-followup/`](../../revisions/2026-10-07-kais-followup/README.md), included in release `kais-reproducibility-2026-10-07`. Start with the root [reproduction guide](../../REPRODUCIBILITY.md). Paths below are relative to the repository root or to the extracted `review-work` root, as stated.

## Directory identities

| Path | Role |
|---|---|
| `revisions/2026-10-07-kais-followup/` | Current article, supplement, editable sources, figure sources, copied evidence and editorial/build checks. |
| `cloud-handoff/replication-package.zip` | Original frozen 512-arm collection and necessary research/source siblings; extract to a new workspace. Its embedded earlier manuscript is historical. |
| `research/phase2-results-snapshots/2026-10-07-complete/quota-recovery-complete.zip` | Complete separately frozen A collection: 117 pairs / 234 arms, all attempts and raw records. |
| `research/phase2-followup-analysis-2026-10-07/` | Independent supplementary scoring, validation, provider accounting and derived outputs. |
| `research/phase2-followup-sensitivity-2026-10-07/` | Explicit post hoc completed-A sensitivity, with one-source-per-pair routing. |
| `reproduction/dke/` | Supported reviewer adapter for the earlier controlled E1–E3 deposit. This directory name is retained for historical source continuity. |
| `reproduction/historical/` | Portable historical audit adapter: verifies inputs, copies them into a fresh workspace with the legacy path layout, and executes the unchanged audit script. |
| `latest/`, `paper/`, older `revisions/`, partial result snapshots | Historical material. Do not choose an analysis or manuscript merely because its path says “latest.” |

The main article has **three figures and three tables**. Editorial receipts in the manuscript directory document source preservation and layout checks; they are distinct from fresh experimental execution.

## Main figures

Abbreviation `PAPER` means `revisions/2026-10-07-kais-followup`.

| Paper item | Source and generator | Output and interpretation |
|---|---|---|
| Figure 1: correction-aware continuity | `PAPER/make_revision_figures.py`, drawing definitions for the running example | `PAPER/figures/revised-figure1-concept.pdf` and companion SVG/PNG. Conceptual 100→101 example with reviewed `c_1` and equivalent distinct `c_2`; not a measured result. |
| Figure 2: shared review and independent online continuations | Same diagram generator | `PAPER/figures/revised-figure3-online-loop.pdf` and companions. Describes the paired protocol and independent auditing; not an extra experiment. |
| Figure 3: accountable recovery and paired costs | `PAPER/make_followup_figure.py`; reads `PAPER/evidence/online/` for original B and `PAPER/evidence/followup/` for supplementary A | `PAPER/figures/followup-behavior-comparison.pdf` and companions, plus `figures/followup-figure-source-audit.json`. Original B: 16 reuse paths; supplementary A: 8 reuse + 7 reauthorization. Calls are means; seconds are medians of paired whole-suffix differences. |

The first generator also produces the evidence-chain and original recovery-path diagrams retained in the supplement. Its `figures/revised-figure-source-audit.json` documents inputs. Diagram PDFs and rebuilt manuscript PDFs are not expected to be byte-identical across unpinned renderers.

## Main tables and nearby claims

| Paper item | Checkable source | Reproduction route |
|---|---|---|
| Table 1: related-work comparison | `PAPER/REVIEW-CLOSURE-COMPARISON.md`, `PAPER/.research/literature_matrix.md`, cited primary papers/docs | Conceptual comparison, not a cross-system benchmark. It acknowledges existing proposal-identity binding and recovery. No experimental regeneration. |
| Table 2: controlled mechanism evidence | `PAPER/evidence/controlled/results/e1/`, `results/e2/`, corresponding `tables/`; `PAPER/evidence/formal/` | Earlier reviewer guide: verify archived E1/E2 summaries, or rerun controlled cases. Formal evidence needs the separate pinned Alloy route. Counts use separate units: 165 cases per mechanism, 9 request substitutions, 3 display probes, 72 formal commands. |
| Table 3: checkpoint and joint outcomes | Original `PAPER/evidence/online/{table1-outcomes.csv,manuscript-aggregates.json}`; supplementary `PAPER/evidence/followup/table1-outcomes.csv` and independent analysis outputs | Root guide Steps 3–4. Original A, original B and supplementary A occupy separately labeled rows. Completion, integrity and unknowns retain their own denominators. |
| Original effect and friction claims | `PAPER/evidence/online/analysis-summary.json`, `paired-effects.csv`, `table3-recovery.csv`, `table4-utility-friction.csv`, `failure-archaeology-all-arms.csv` | `analyze_formal.py --output fresh-primary --figures`; `PAPER/derive_results.py` builds manuscript-level aggregates from the original raw ledger plus retained exports. The latter writes in the paper copy and does not independently regenerate the exporter. |
| Supplementary effect/recovery/cost claims | `research/phase2-followup-analysis-2026-10-07/outputs/`; exact paper copies in `PAPER/evidence/followup/` | `analyze.py`, `audit_usage.py`, `verify_outputs.py`, all with one common reproduction output directory. |
| Historical 84 correction chains | Extracted `research/authorization-granularity-phase1-2026-10-06/{correction-chains.jsonl,correction-summary.json,correction-input-hashes.json,audit_corrections.py}` | The verified historical adapter below checks all 1,854 ledger inputs and reruns the unchanged audit on 1,260 databases; these 84 chains are not a fresh online policy experiment. |

## Raw online evidence and scoring

After extracting both ZIPs in the documented layout:

| Extracted path | Contents and use |
|---|---|
| `research/agent-policy-phase2-formal-2026-10-07/frozen-formal/` | 128 task definitions, agent/prompt/tool manifests, balanced assignment order, scorer definition, failure rules and master/source/input hashes. |
| `research/agent-policy-phase2-formal-2026-10-07/formal-results/` | Original terminal collection ledger plus all 256 task/configuration pairs and their 512 planned policy arms. |
| `research/agent-policy-phase2-quota-recovery-2026-10-07/recovery-manifest.json` | Separate freeze, eligibility and relationship to the original experiment. |
| `research/agent-policy-phase2-quota-recovery-2026-10-07/results/` | All 117 supplementary pair attempts, prefixes, policy continuations, native provider records, hash-linked events and authoritative state. |

The original parent master hash is `7773563b40c8db30d6def121915f50fbad032537edde32afd4ba39ec3eea744b`; the recovery manifest digest is `3f11ebba8fb43b7ce2582e229678366a2338751505e61a667f02aea4c9b82e8f`. Exact archive bytes are identified in [`ARTIFACT-MANIFEST.json`](ARTIFACT-MANIFEST.json) and the root guide.

Original collection analysis stays unchanged. Supplementary eligibility is original pre-response quota failure; failures within the later cohort remain. Pilot trajectories are excluded from formal effect estimates. Provider-request attempts and task observations are different units.

## Supplement navigation

| Supplement coverage | Artifacts and boundary |
|---|---|
| S1–S3: artifact/protocol, formal/concrete checks and worked realization | TeX definitions, `PAPER/evidence/formal/`, the Phase 1 repaired witnesses and pinned earlier formal tools. Bounded checking is not an unbounded proof. |
| S4: admission/trace/storage measurements | `PAPER/evidence/controlled/results/e3/` and `tables/e3-*-summary.csv`; full E1–E3 raw reproduction via `reproduction/dke/reviewer.py`. Existing trace grid varies fields, history depth and background population; it does not establish cross-record transactional atomicity. |
| Historical audit discussion | Phase 1 chain outputs and input hashes above, linked to the earlier hosted workflow databases. Single-field chains provide no unchanged-field copy-forward tests. |
| S11: original online evaluation | `PAPER/evidence/online/`, original freeze and raw ledger. Keep 117 A quota failures and two B unknown-integrity outcomes. |
| S12: separately frozen supplementary A | `PAPER/evidence/followup/`, independent `outputs/`, `scored-arms.json`, `validation-ledger.json`, `attempt-ledger.json`, native usage ledgers and hashes. |
| S13: explicitly post hoc sensitivity | `research/phase2-followup-sensitivity-2026-10-07/outputs/` and paper copies in `PAPER/evidence/sensitivity/`; `pair-source-map.json` routes 117 A pairs to the supplementary source and all other pairs to original sources. `formal_inference_allowed=false`. |

## Earlier mechanism and formal deposits

The [earlier reviewer guide](../../REVIEWER_GUIDE.md) supplies exact commands for `reproduction/dke/reviewer.py`: `prepare`, `verify`, `test`, `e1`, optional `e2`, `e3` and `formal`. It pins E1–E3 deposit commit `2645e5e18c900ea91c9c980e44195dc71e410432` and source/input commit `c6d512843c905cab6d8521dd8c914f7fb26d85ae`. Network use belongs to Git/dependency/browser preparation; analysis is then local. E1's three mechanisms execute 165 cases each, so 495 executions do not create a 495-case agreement denominator.

The earlier adapter's `formal` runs 19 Python witness tests, not Alloy. The current repaired Phase 1 witnesses in the original archive are checked independently from `review-work` with:

```text
cd research/authorization-granularity-phase1-2026-10-06/formal
python -B -m unittest discover -s tests -q
cd ../../..
```

The working directory is required for local witness-module imports. All 24 tests passed in the release check, covering the repaired canonical comparison and observation/identity witnesses. Neither Python route reruns the 72-command Alloy batch. Use the guide's separate `r31-jss-2026-09-13` checkout for Alloy, the 29 formal–concrete projections and the 35-case catalogue, preserving that toolchain's own outputs. Those solver runs were not repeated in the current release verification.

## Historical audit portability

The original archive preserves the Phase 1 audit, its 84-chain output and source/input hashes. Its historical database dependencies are separate from the Phase 2 raw trajectories. The verified adapter `reproduction/historical/reproduce.py` resolves the archived script's filesystem assumptions by restoring its declared paths inside a disposable workspace; it preserves the scientific script byte-for-byte.

Follow the root guide's optional sparse-checkout step to obtain the historical sources/databases, then run from the clone root:

```text
python -B reproduction/historical/reproduce.py --output .reviewer-work/historical
```

`--source` defaults to the clone root; an explicit `--source REPO_ROOT` is available. The output must be a fresh path. The helper verifies all 1,854 ledger inputs, copies approximately 275 MB of inputs, executes the unchanged audit, compares chains/summary/ledger against archived outputs, and rehashes original and copied inputs. The [public CLI verification receipt](HISTORICAL-AUDIT-VERIFICATION.json) records 1,260 databases, 84 chains, 252 associations, 168 versions and 168 provenance traces, with zero failures and zero unchanged-field checks. Existing output and source paths are protected against overwriting. The route needs only Python 3.11+ standard-library modules after data preparation; no Java, Git LFS or provider calls are required. The verified execution used Windows/Python 3.11.9, not a separately tested Linux runtime.

## Meaning of a match

Input preservation uses SHA-256. Deterministic numeric/text analysis uses parsed values: JSON object order, JSON-valued CSV cell order, machine paths and receipt/environment metadata need appropriate comparison. Scientific counts, classifications, routing and paired estimates must match. Generated figure/manuscript bytes and fresh elapsed timings can vary for documented environmental reasons.

`PAPER/verify_evidence.py` writes a 29-check receipt against the manuscript's retained evidence. It complements, rather than replaces, raw reanalysis. S13's archived `frozen-exporter-crosscheck` is retained supporting evidence and is not regenerated by `sensitivity.py`. The [release verification record](REPRODUCTION-VERIFICATION-2026-10-07.md) documents nine successful offline verification/analysis commands, 18 supplementary tests, 3 routing tests, 24 repaired-witness tests, and semantic agreement for all 18 CSV tables and three analysis summaries. No route here establishes that a new provider call would yield the same agent behavior, nor turns the separately collected cohort or S13 sensitivity into the original frozen estimator.
