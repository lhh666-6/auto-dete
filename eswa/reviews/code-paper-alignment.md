# Code--paper alignment

This ledger maps the revised ESWA manuscript to the frozen `eswa-v1` run generated from experiment commit `195355a27f3606bc070d8606ed299549067c5a6e`. The copied submission artifacts match all 27 SHA-256 values in `artifacts/manifest.json`.

| Paper claim | Artifact or code evidence | Verdict |
|---|---|---|
| 4,350 cell cases: 1,740 calibration and 2,610 evaluation | `artifacts/recognition_summary.json` | PASS |
| Evaluation rows retain the dependence of 90 base units across 29 conditions | benchmark configuration and `selective_models[*].base_unit_count` | PASS |
| Template gate: threshold 0.08, 11.19% coverage, 100% observed accepted accuracy | `selected_threshold` and `selected_metrics` | PASS |
| Template cluster-bootstrap coverage interval: 5.86--16.97% | `selective_models[0].cluster_bootstrap_ci95.coverage` | PASS |
| HOG--SVM: 2,605/2,610 correct, 99.81% accuracy, 0.19% selective risk | `baselines` and `selective_models[1]` | PASS |
| HOG--SVM cluster-bootstrap accepted-accuracy interval: 99.62--99.96% | `selective_models[1].cluster_bootstrap_ci95.accepted_accuracy` | PASS |
| Whole-form full pipeline: 300 condition rows, 86.03% digit accuracy, 100% OMR accuracy, 60% complete success | `artifacts/form_summary.json` | PASS |
| Clean, perspective, and JPEG forms complete; blur breaks QR and rotation breaks marker alignment | `artifacts/form_raw.json` and `artifacts/form_summary.json` | PASS |
| Removing QR or ArUco makes complete-form success zero | `artifacts/form_summary.json` ablations | PASS |
| 60 clean forms complete import-to-export and reverse trace, producing 1,200 candidates and versioned facts | `artifacts/form_workflow.json` | PASS |
| Six controlled faults are contained with audit evidence | `artifacts/trust_faults.json` | PASS |
| All 12 attempted direct fact-write methods are unavailable | `artifacts/trust_faults.json` direct-write case | PASS |
| Candidate isolation prevents an injected value from changing the fact; unsafe wiring changes it | `artifacts/trust_ablation.json` | PASS |
| 500/500 randomized fault trials preserve existing facts | `artifacts/trust_stress.json` | PASS |
| Median service-only latency is 0.300 ms cold and 0.073 ms warm | `artifacts/resilience.json`; supplementary only | PASS |
| 27 generated outputs came from a clean tracked source state | `artifacts/manifest.json` | PASS |
| 77 tests, Ruff, and mypy over 45 source files pass | fresh verification commands in the experiment repository | PASS |
| Evaluated application stack is Python 3.11, Streamlit, SQLite/SQLAlchemy/Alembic | `docs/eswa-implementation-inventory.md`, `app/ui/`, `app/db/` | PASS |

The preserved LNCS prose mentions FastAPI, React/Vite, PWA, authentication, and RBAC. Those descriptions have no corresponding tracked implementation in the currently available Auto-Decte repository or its Git history, so they are not carried into the ESWA manuscript. This does not establish that no private or lost prototype ever existed; it only defines the reproducible evidence boundary for this submission.
