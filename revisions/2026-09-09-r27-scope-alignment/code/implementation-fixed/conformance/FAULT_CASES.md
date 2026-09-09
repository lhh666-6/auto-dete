# Fault Cases

> The table below is the historical G3b list. The current finite denominator
> is the machine-readable 35-case `case_catalogue.json` (R9 v1).

| Case | Concrete action | Expected result | Test |
|---|---|---|---|
| Legal Accept | Confirm machine candidate with matching value | Version 1, original machine certificate, auth binding with same value, fact_sources anchors transition | `test_legal_accept_and_correction_preserve_machine_certificate` |
| Legal Correction | Confirm modified machine value at next version | Original machine certificate preserved; AuthorizationBinding holds corrected value; Transition.value holds corrected value | same test |
| Multi-field complete snapshot / copy-forward | Update one field at version 2 | `values` is a complete snapshot (`a=3,b=2`); unchanged field's fact_sources remains from v1; domains identical | `test_fact_sources_copy_forward_preserves_unchanged_field`, `test_complete_snapshot_and_historical_source_trace` |
| Unchanged-field historical trace | Trace version 2 after v2 changed only a | `b` traces to the v1 transition and is Complete | `test_complete_snapshot_and_historical_source_trace` |
| Field substitution | Use certificate for field A on field B | `FIELD_KEY_BINDING_MISMATCH`, no writes | `test_cross_field_substitution_rejected` |
| Record substitution (ABL_3) | Use certificate generated for FORM-1 on FORM-2 | `RECORD_BINDING_MISMATCH`, no writes | `test_abl3_record_substitution_rejected` |
| Evidence-owner substitution | Rebind machine certificate to evidence owned by another form | `EVIDENCE_FORM_MISMATCH`, no writes | `test_evidence_owner_substitution_rejected` |
| Evidence identity substitution | Tamper evidence row sha256 behind a machine certificate | `EVIDENCE_HASH_MISMATCH`, no writes | `test_evidence_identity_substitution_rejected` |
| Candidate-version substitution | Tamper certificate `expected_fact_version` | Authority rejection, no writes | `test_candidate_version_substitution_rejected` |
| True stale replay (ABL_4b) | Confirm expected_version=0 after v1 exists | `ConcurrentReviewError`, no new version | `test_stale_replay_rejected`, `test_abl4b_stale_replay_rejected` |
| Auth/cert transfer (ABL_5) | Binding certificate differs from transition certificate, same value | Repository rejects the admission bundle | `test_abl5_auth_certificate_transfer_rejected`, `test_repository_rejects_binding_certificate_mismatch` |
| Unauthorized final value (ABL_8) | Binding authorized value differs from transition value | Repository rejects the admission bundle; trace detects post-hoc tamper | `test_abl8_unauthorized_value_rejected`, `test_trace_detects_transition_value_tamper`, `test_trace_detects_authorization_value_tamper`, `test_trace_detects_committed_value_tamper` |
| Missing certificate | Confirm with unknown certificate id | `UNKNOWN_CERTIFICATE`, no writes | `test_missing_certificate_rejected` |
| Missing evidence | Delete the evidence row referenced by a machine certificate | Authority rejection, no writes | `test_missing_evidence_rejected` |
| Direct machine fact write | Call repository CAS with no AuthorizationBinding | ValueError before any write, no rows | `test_direct_machine_fact_write_without_binding_rejected`, `test_repository_rejects_missing_authorization_binding` |
| Source deletion | Delete FactTransitionRow after confirm | `QueryForms.trace` returns incomplete | `test_source_deletion_trace_incomplete` |
| Trace corruption families | Tamper transition producer/evidence/version/certificate/auth/value rows | Trace returns incomplete | conformance tests plus `tests/integration/test_authority_integration.py` trace parametrization |
| Duplicate source-version | Insert duplicate `(form, created_version, field)` | `IntegrityError` and transaction rollback; schema prevents the state | `test_duplicate_source_version_is_schema_prevention` |
| AuthorizationBinding immutability | Row reads after transaction | binding_id/decision_id/certificate_id/value frozen | legal accept/correction tests |

## Duplicate interpretation (resolved)

The concrete SQLite schema makes the duplicate-source state **unreachable** through the trusted schema
via the unique constraint `(form_id, created_version, field_key)`. This is recorded as a valid
refinement, not as an unresolved gap. `QueryForms.trace` is not claimed to detect a duplicate that
cannot normally be inserted; the Alloy model still analyzes the duplicate state formally.

## R9 denominator

The current catalogue contains 35 unique cases across legal, rejection,
post-persistence corruption, schema prevention, stateful, and oracle-mutant
classes, with explicit P0–P6 mappings. It includes every direct pre-repair
counterexample: hidden changed field, persisted evidence field/URI
substitution, and same-valued older-source replacement. The denominator is
verified by `test_r9_catalogue.py`; it is never described as arbitrary
corruption coverage.
