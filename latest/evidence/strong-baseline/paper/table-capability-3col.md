# Section 5 three-column capability table

| capability | B0 has it | B0 anchor | B1 increment | B1 anchor |
|---|---|---|---|---|
| immutable candidate persistence | yes | `run_baseline.py:49-51, 67-71` | re-expressed with content-addressed identity and UNIQUE(content_hash) | `policies.py candidates DDL` |
| complete before/after value audit | yes | `run_baseline.py:61-65, 139-140` | re-expressed with changed_fields, before/after digests and a hash chain | `policies.py audits DDL` |
| authorized value | yes | `run_baseline.py:55-58 approved_values_json` | re-expressed with scope_json and policy_version | `policies.py approvals DDL` |
| expected / current version | yes | `run_baseline.py:56` | none | `-` |
| compare-and-swap | yes | `run_baseline.py:133-137 rowcount!=1 -> stale_version` | none | `-` |
| atomic transaction + rollback | yes | `run_baseline.py:108-150 BEGIN IMMEDIATE + ROLLBACK` | none | `-` |
| stale-replay rejection | yes | `run_baseline.py:133-137` | none | `-` |
| direct-write exclusion | yes | `run_baseline.py:67-71 freeze triggers` | none | `-` |
| failure injection / rollback | yes | `run_baseline.py:141-142 fail_after_writes` | none | `-` |
| same database backend | yes | `run_baseline.py:45-46 SQLite` | none | `-` |
| canonical JSON equality | yes | `run_baseline.py:29-30 canonical()` | none | `-` |
| reviewer / principal policy | partial (hard-coded 'reviewer-1') | `run_baseline.py:97-98, 104-105` | principal registry with role and authorized-field set; FK from approvals | `policies.py principals DDL + _principal()` |
| evidence persistence | no | `approvals/candidates have no evidence column (run_baseline.py:49-58)` | evidence_hash + evidence_locator persisted on the immutable candidate record | `policies.py candidates DDL` |
| explicit per-field source map | no (reconstructable from audit) | `run_baseline.py:173-182 reconstruct_sources()` | fact_sources table + per-version sources_json + stored==reconstructed check | `policies.py fact_sources DDL, _commit_successor()` |
| candidate registry richness | 4 columns | `run_baseline.py:49-51` | producer, producer_version, selection_artifact_id, expected_fact_version, evidence_hash, evidence_locator, created_at, content_hash, UNIQUE(content_hash) | `policies.py candidates DDL` |
| schema versioning / migration marker | no | `-` | schema_meta table | `policies.py schema_meta DDL` |
| explicit approval-consumption guard | implicit only (changed_domain incidentally refuses replay) | `run_baseline.py:127-130` | explicit approval_consumption row inside the transaction | `policies.py approval_consumption DDL + submit()` |
| admission decision log with reason codes | no | `-` | admission_attempts (records no candidate identity) | `policies.py admission_attempts DDL` |
| transaction grouping | no | `-` | tx_log | `policies.py tx_log DDL` |
| tamper-evident audit chain | no | `-` | before/after digests plus prev_row_digest/row_digest chain | `policies.py audits DDL, _commit_successor()` |
| post-commit source-map consistency check | no | `-` | stored source map compared with the audit reconstruction (case observation 'stored_matches_reconstruction') | `cases.py two-step-copy-forward observations` |
| exact reviewed-candidate binding | no | `run_baseline.py:193-195 (comment: stores no candidate identity)` | still absent in B1 by design (section 7) | `self_audit.json implements_exact_candidate_obligation=false` |
| admission-used candidate identity | no | `-` | still absent in B1 by design (section 20) | `self_audit.json section_20_used_candidate_recorded=false` |
| distinguish paired equal-valued reviewed candidates | no | `run_baseline.py:458-460 (states identical)` | still absent in B1 (identical case outcome reproduced) | `case_results.json B1 paired-reviewed-candidate` |
| single-history agreement with candidate-bound | 7 of 8 | `evidence/r27-standard-practice-baseline/run-2026-09-10/summary.json` | 7 of 8 reproduced, same two divergences | `normalized/parity.json strengthened_control_B1_vs_Full` |

Rows marked *yes* are capabilities B0 already satisfies and are explicitly **not** claimed as B1 increments (section 5).
