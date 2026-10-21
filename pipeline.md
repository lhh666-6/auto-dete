# ASE paper-to-artifact pipeline

Updated 2026-10-21 using the pipeline-manifest scan workflow. Scope: current manuscript, its two supplements and their reproducible evidence entry points. Collection runners are preserved as provenance; offline verification does not call them. Historical exploratory scripts not used by the paper are not promoted to primary analysis.

| Script / entry | Inputs | Outputs | Paper linkage |
|---|---|---|---|
| `reproduction/ase/reproduce.py prepare` | Manifest; original and supplementary ZIPs; curated later evidence | New disposable work tree | Dependency preparation only |
| Original `analyze_formal.py` (inside original ZIP) | 512-arm ledger, raw events and saved states | Outcome, integrity, recovery and paired-effect tables | §6.1–6.3; Table 6; OR1 S11 |
| `research/phase2-followup-analysis-2026-10-07/analyze.py` | Complete supplementary ZIP; frozen task definitions | Independent scores, 117-pair tables and summary | Table 6; §6; OR1 S12 |
| Same directory `audit_usage.py`, `verify_outputs.py` | All attempts, native usage and derived scores | Usage ledger, consistency receipt | OR1 S12; retains failed attempts |
| `research/phase2-followup-sensitivity-2026-10-07/sensitivity.py` | Original and supplementary records plus explicit source routing | Retrospective mixed-cohort view | OR1 S13; not primary inference |
| Current manuscript `qa/recovery_costs.py` | Two authenticated raw ZIPs; `figure-data.json` | Table 7, episode CSV, source receipt | §6.3 and Figure 4 cost interpretation |
| Current manuscript `qa/recovery_example.py` | Same two raw ZIPs | Event/state anchors for FORMAL-G-002-B | §6.3; OR1 S12.6 |
| `revisions/2026-10-18-kais-recalibrated/qa/n_exposure.py` | Both raw ZIPs | N-family exposure CSV | §6.4; OR2 A7 |
| `research/kais-revision-output-audit-2026-10-14/analysis.py` | Original B requests/responses, parser and original score snapshot | Attempts, arms, paired decomposition and summary | §6.2; OR2 A1 |
| `research/kais-budget-sensitivity-2026-10-14/analysis.py` | Allocation, 96 saved continuations, vendor scorer | Four-condition summaries, cells and pairs | §6.2; OR2 A2 |
| `research/kais-commit-uncertainty-2026-10-14/verify_outputs.py` functions via `check_later.py` | Both saved runs, transcripts and SQLite snapshots | Recomputed raw audit | OR2 A3 |
| `research/kais-native-baseline-probe-2026-10-14/run_probe.py` | Fixed CK model and original Host; frozen fixtures | 24 planned rows, 22 representable; 11 controls | OR2 A4; original saved outputs retained |
| `research/kais-approval-workflow-2026-10-14/run_workflow.py` | Pinned OpenTofu binary, local fixture and approval protocol | Native state/plan records and normalized results | OR2 A4; default runner verifies saved results only |
| Historical `audit_corrections.py` through `reproduction/historical/reproduce.py` | 1,260 archived databases and ledger-selected sources | 84-chain audit | §5.1; OR2 A5 |
| `reproduction/dke/reviewer.py` | Pinned E1–E3/reference sources | Archived aggregate verification or fresh controlled cases | §5.1; OR1 S1; OR2 A6 |
| `research/kais-toolgate-feasibility-2026-10-20/score_feasibility.py` | 16 saved control routes and actual SQLite | 8/8 per implementation | §5.2; OR2 A8 |
| `research/kais-toolgate-public-reference-2026-10-20/public_score.py` via portable `check_later.py` | 48 saved routes, input/output manifests, mapped frozen source hashes | Strict scores, business-state checks, preserved one log failure | Table 4; §5.2; OR2 A8 |
| `X1-X2-reproduction.zip`: `verify_saved.py` and independent X2 scorer | 111 authenticated v2 source/evidence files and two saved runs | Semantic/SQL equality and independent persisted-effect scores | Table 5; §5.3; OR2 A11 |
| Current manuscript `scripts/figures/build_all_figures.py` | Included glyphs, diagram specification and `figure-data.json` | Four figure PDFs plus QA outputs | Figures 1–4 |
| Current manuscript `build.py` | LaTeX, bibliography and all figure/table assets | Main PDF and two supplement PDFs | Complete manuscript |
| `reproduction/ase/compare_outputs.py` | Fresh exports and deposited references | Scientific-value comparisons | End-to-end readback check |

## Figure and table ownership

| Main paper item | Source / producer |
|---|---|
| Figure 1, review–execution gap | `conceptual_panels.py:build_gap`, using `build_gap.py` and supplied glyph assets; not a measured plot |
| Figure 2, design space | `conceptual_panels.py:build_design_space`; conditional relationships from §3–4 |
| Figure 3, paired design | `empirical_panels.py:build_paired`; frozen protocol |
| Figure 4, recovery/cost | `empirical_panels.py`, frozen `figure-data.json`; raw-event recovery checks above |
| Tables 1–3 | Editorial evidence map, related-work comparison and obligation positioning; not experimentally generated tables |
| Table 4 | Frozen ToolGate public scorer and separate diagnostic interpretation |
| Table 5 | Corrected X2 comparison of bindings and executor modes |
| Table 6 | Original and supplementary analysis exports; separate denominators |
| Table 7 | `qa/recovery_costs.py` event-order readback |

The aggregate `build_all_figures.py` is the supported figure regeneration entry point; all named producers are included in the current source package.

## Execution order and boundaries

`fixed deposit → hash verification → disposable extraction → original/supplementary/later analyses → scientific-output comparison`.

Manuscript compilation is independent of experimental execution because the measured figure data and figure assets are supplied. The raw-response collections are fixed input leaves, not outputs that the offline runner must regenerate. Optional formal, browser, native CLI and historical-database routes have their own dependencies and documented scopes.

No dependency cycle is needed for the documented route. The known historical absolute-path dependency is handled by authenticated path mapping for saved ToolGate rescoring. The earlier native execution runners retain their original freezes; the portable wrapper does not claim to have converted every fresh-execution route to every operating system.

Unreferenced tables or old figures in the preserved source ZIP are historical assets. Their presence does not create additional reported results or extra sample counts. Archived protocol labels, failed arms, quota attempts, unknown integrity and the one strict ToolGate failure remain visible.
