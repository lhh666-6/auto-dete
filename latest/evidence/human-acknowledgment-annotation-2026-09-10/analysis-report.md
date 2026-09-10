# Blinded acknowledgment annotation analysis

The second author, Xuan Wentao, independently assigned the manual labels while blinded to previous labels and configuration/run/scenario identifiers. Because the annotator is an author, this is author-involved blinded annotation rather than independent third-party annotation. The comparison below is human--rule agreement, not inter-human reliability or adjudicated truth.

All 325 workbook rows matched exactly one frozen audit row. The manual annotation contains 241 positive labels; the repaired v2.1 rule contains 272 rule hits.

## Primary comparison

Overall agreement is 286/325 (88.00%); Cohen's kappa is 0.644, Gwet's AC1 is 0.820, and PABAK is 0.760.

| Scenario | n | Human positive | Rule positive | Agreement | Kappa |
|---|---:|---:|---:|---:|---:|
| A2 | 86 | 79 | 84 | 81/86 (94.19%) | 0.424 |
| A3 (exploratory) | 88 | 14 | 38 | 56/88 (63.64%) | 0.198 |
| A6 | 69 | 68 | 68 | 69/69 (100.00%) | 1.000 |
| B4 | 82 | 80 | 82 | 80/82 (97.56%) | 0.000 |

The A3 result is not interpreted as annotator error or model failure. Its frozen prompt did not identify a unique target field, so its weaker agreement exposes construct and rubric ambiguity. The A2, A3, A6, and B4 results remain separate.

## Retained outputs

The archive retains normalized joined labels, both historical and repaired comparisons, all 39 unadjudicated v2.1 disagreements, and 5,000-replicate case/model/cell bootstrap intervals. The original rule labels are not overwritten.
