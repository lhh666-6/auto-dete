# Section 16 per-field judgement for the concrete equal-valued pair

| field | differs in pair | stored by B1 | owner tables | discriminates SAFE vs UNSAFE | verdict |
|---|---|---|---|---|---|
| `candidate_id` | True | True | candidates | False | no candidate-level discriminating power: the field is stored only inside a registry that is identical in both histories |
| `content_hash` | True | True | candidates | False | no candidate-level discriminating power: the field is stored only inside a registry that is identical in both histories |
| `created_at` | True | True | candidates, schema_meta | False | no candidate-level discriminating power: the field is stored only inside a registry that is identical in both histories |
| `evidence_hash` | False | None | - | False | identical in both candidates |
| `evidence_locator` | True | True | candidates | False | no candidate-level discriminating power: the field is stored only inside a registry that is identical in both histories |
| `expected_fact_version` | False | None | - | False | identical in both candidates |
| `field` | False | None | - | False | identical in both candidates |
| `producer_id` | False | None | - | False | identical in both candidates |
| `producer_version` | False | None | - | False | identical in both candidates |
| `proposed_json` | False | None | - | False | identical in both candidates |
| `record_id` | False | None | - | False | identical in both candidates |
| `selection_artifact_id` | False | None | - | False | identical in both candidates |
