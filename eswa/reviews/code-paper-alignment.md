# Code--paper alignment

| Paper claim | Artifact source | Verdict |
|---|---|---|
| 4,350 total cases; 1,740 calibration; 2,610 evaluation | `artifacts/recognition_summary.json` | PASS |
| Threshold 0.08, selected for 1% calibration-risk target | `recognition_summary.json` | PASS |
| 292 accepted; 11.19% coverage; 88.81% routing | `selected_metrics` | PASS |
| 100% observed accepted accuracy; Wilson lower 98.70% | `accepted_accuracy_wilson_ci95` | PASS |
| HOG--SVM 2,605/2,610 = 99.81% at full coverage | `baselines` | PASS |
| Five faults contained with complete audit evidence | `artifacts/trust_faults.json` | PASS |
| AI disabled, duplicate/stale rejected, reverse trace valid | `artifacts/resilience.json` | PASS |
| Cold 0.280 ms median; warm 0.070 ms median | final `latency_summary` | PASS |
| 15 hashed outputs and clean tracked source at generation | `artifacts/manifest.json` | PASS |
| 70 tests; Ruff pass; mypy pass over 65 files | final verification commands | PASS |

The robustness figure was initially found to plot conditional accepted accuracy while its caption described coverage. The generation code was fixed test-first, the plot now uses coverage with a data-sensitive axis, all artifacts were regenerated, and all 15 copied outputs were revalidated against the final manifest.
