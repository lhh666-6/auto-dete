# DKE manuscript writing and figure route

This is a revised DKE working draft. Sections 1–9 and four main-text figures are in manuscript.md, manuscript.tex, and a locally compiled manuscript.pdf. BUILD.md records the conversion, bibliography, and compilation steps. The frozen JSS submission and the September 19 editorial copy remain unchanged.

## Central claim

The paper studies a correction-aware record-admission relation: exact persisted candidate, explicit attributable authorization, complete successor, and total per-field source attribution. The 2026-09-23 DKE supplement supplies the cross-implementation, browser, and current-version cost evidence. The frozen paper supplies the conditional observation result, bounded model, formal–concrete checks, and fault catalogue.

## Sections after the introduction

| Section | Question that drives the section | Evidence or output | Main visual |
| --- | --- | --- | --- |
| 2. Related work | Which established ideas does the admission relation build on, and what does its candidate-instance test add? | Query and curation provenance, content-based approval, transaction provenance | Five verified references |
| 3. Admission semantics | What information must a corrected record retain at the commit boundary? | Candidate, authorization, changed-item batch, complete successor, field-source map | Fig. 2: semantic objects and links |
| 4. Failure distinguishability | Which history distinctions disappear if one information class is omitted? | Observation projection, five paired witnesses, conditional Proposition 1 | Table 1: five classes and paired histories |
| 5. Realizations | Can the same relation be enforced through different storage structures? | Transactional reference service; context-only and exact-binding event journals | Fig. 2 supplies the shared semantic relation |
| 6. Evaluation design | How are relation, persistence, review transfer, and cost tested? | Alloy commands, formal–concrete projections, 35-case catalogue, E1/E2/E3 protocols | Detailed grids in supplement |
| 7. Results | Where does exact binding separate equal-valued candidates, and does the relation survive persistence? | E1 first; formal and catalogue checks; E2 browser; E3 cost | Fig. 3: E1 separation; Fig. 4: cost |
| 8. Implications | What does this imply for data integrity, provenance queries, and review interfaces? | Cross-implementation behavior; distinct review and display boundaries | No new figure |
| 9. Conclusion | What did the evaluated relation establish? | Synthesis of model and evidence | No figure |

## Figure and table placements

1. **Fig. 1 — Same value, different history.** Inserted after the motivating candidate-substitution example in Section 1. New vector master and PNG preview are in `figures/`. It is a constructed example, not an empirical result.
2. **Fig. 2 — Admission relation and complete field sources.** Inserted after the semantic relation in Section 3. Shows candidate, explicit authorization, transaction, complete successor, and copy-forward source links.
3. **Table 1 — Five failure-distinguishing classes.** Inserted in Section 4 with the conditional Proposition 1 statement.
4. **Fig. 3 — Cross-implementation separation.** Inserted after the first result in Section 7. Generated from the deposited E1 comparison summary. The redundant numerical table stays out of the main text.
5. **Table 2 — Review-boundary cases.** Inserted with E2 in Section 7, separating request from display substitutions.
6. **Fig. 4 — Current-version trace cost.** Inserted with E3 in Section 7. Generated from all 36 paired cells of the deposited trace summary; full grids and storage results remain in the supplement.

The old model-behavior figure belongs with application material rather than the DKE main argument. The old evidence-map figure repeats prose and should not occupy a main-text figure slot.

## Evidence boundaries for drafting

- E1 has 495 constructed executions from 15 inputs, 11 case families, and three mechanisms. The exact journal and reference service have 165 paired cases; do not present 495 as independent workflows.
- E2 has 60 scripted browser cases. The server-held gate rejects nine request substitutions accepted by the original confirmation path, while three display-only substitutions remain for each path.
- E3 has 22,400 timed observations across current-version admission and trace comparisons. The complete-mechanism timing boundary and connection lifecycle must accompany any timing comparison.
- The formal observation result is conditional on its declared history, observation, and outcome model. The paper can state this once at the proposition and carry the scope through captions and conclusions without repeated defensive prose.
