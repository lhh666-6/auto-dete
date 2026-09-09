# Response to the 2026-09-08 multi-perspective review

**Manuscript**: *Authoritative-State Admission for AI-Derived Updates: Failure Distinguishability, Transactional Realization, and Evaluation* (v8, `main-r21-design-checklist-2026-09-07.pdf`, SHA-256 `3f7a0d57…f7a4`, 57 pages)
**Revised manuscript**: `paper/main.pdf` (64 pages, SHA-256 `b102a2dbf2c190e912d786bcb1c7df2e9ac198d17a88227edab23683ac2d5a50`)
**Baseline**: `baseline-v8/` is a byte-identical copy of the reviewed v8 manuscript and was not modified.

We thank the reviewer for the concrete, reproducible findings. The revision addresses R1--R5 and the editorial items. R1 and R5 are implementation repairs with regression evidence; R2--R4 retain every frozen record and change the reported constructs and interpretation. No hosted-model call was rerun and no independent human annotation is claimed.

---

## R1 (P1): canonical value equality across layers

**Finding.** The planner and trace used Python equality while the oracle and projection used canonical JSON equality, so `2 → 2.0` or `1 → true` could commit a new serialized value with the old source and be reported immediately as an incomplete trace.

**Change.** We introduced one relation, `canonical_values_equal`, and routed every changed-field decision through it: `app/domain/authority.py` (definition), `app/domain/admission.py` (planner), `app/application/query_forms.py` (trace), and `tests/conformance/oracle.py` (independent oracle). The Alloy projection already used canonical JSON. The manuscript now defines $x\eqc y$ in Section 3.1, uses it in Eqs. (6), (13), and (14), and documents the repair in Sections 5.3 and 6.

**Evidence.** Thirteen regression tests (seven unit, six end-to-end through the public confirmation API) cover the unchanged control, integer-to-float, integer-to-boolean, nested values, a single-field change, and a fail-closed no-op. Seven fail against the previous implementation and all pass against the repaired one. The complete Python suite reports 377 passing tests; Ruff and mypy pass; the 35-case catalogue reports 35/35 with zero failures. Minimal diffs are in `evidence/code-diffs/`.

**Boundary.** The frozen performance measurements describe the v8 implementation and were not rerun; Section 9 states this explicitly.

## R2 (P1): A3 target was not uniquely specified

**Finding.** All 90 prepared A3 inputs omit an explicit intended/target key; the challenge certificate equals the parent of the second listed field while the host targets quantity. An A3 response that matches the listed field is a defensible reading.

**Change.** We retained all frozen records, stopped merging A2 and A3, and report A3 as an exploratory response count. A2 (cross-record, explicit target) is 84/86 rule hits (D1 26/26, G1 28/30, G2 30/30). A3 is 33/88 under rule v1 and 38/88 under the repaired rule v2.1. Section 7 states the separation and that a future A3 capability measure would require an explicit target and a separately frozen experiment.

## R3 (P1): negation was scored as affirmation

**Finding.** A response stating "No mismatch" and "no cross-field conflict arises" was still labeled positive; "matches X, not Y" and "X does not match Y" received opposite labels.

**Change.** The frozen v1 audit is retained as history. A versioned minimal-repair script (`code/scripts/audit_recognition_v2.py`) fixes exactly the two documented defects and otherwise retains the v1 outcome; it changes 11 of 325 rows and leaves the stale count unchanged (150/151). The three cited rows were rechecked directly. The manuscript reports both versions as **deterministic rule-hit counts**, not validated semantic measures, and states that no independent human annotator labeled the rows. A2 and A3 are reported separately; the merged 117/174 figure is removed.

**Boundary.** We do not report a "corrected confirmation rate" without independent re-annotation.

## R4 (P1): completion measured a strict call trajectory

**Finding.** B1/B2 and B4 require exact call sequences; a run that correctly identifies the stale state, performs one extra parent verification, proposes the right value, and verifies it is scored as a recovery failure.

**Change.** The deposited metric is renamed **strict-trajectory task completion**, and Table 8 publishes the B1--B4 criteria. A sensitivity analysis over the same frozen events (`code/scripts/endpoint_sensitivity.py`) first reproduces the frozen verdict exactly (335/335) and then re-derives endpoint completion allowing extra calls: strict 320/335 (95.52%) versus endpoint 331/335 (98.81%); B4 recovery strict 75/82 versus endpoint 82/82. Eleven runs are endpoint-complete but strict-failing (seven B4 runs with one extra parent verification, four B1--B3 runs with one extra proposal); no strict success fails the endpoint rule. The frozen scores are retained and the endpoint rule is presented as a sensitivity analysis, not a replacement verdict.

## R5 (P2): witness checker conflated schema and item domains

**Finding.** `observation_witnesses.py` used `declared_fields` for both the record's schema domain and the batch's declared effect domain, so an ordinary single-field update with another field copied forward was classified as a partial successor.

**Change.** `History` now separates `schema_field_domain` from `declared_item_fields`; value/source totality is checked against the schema domain and committed effects against the declared item domain. A copy-forward control history is added, and `CommitStep`/`_source_resolution` use canonical equality. The old checker classifies the control as `("inadmissible","partial-successor","complete-trace")`; the revised checker returns `("admissible","complete-successor","complete-trace")`, and the five original pairs retain identical derived outcomes. Section 3.3 narrows the checker's scope: it validates the five declared constructions plus one control and is not a general admission oracle.

## Editorial items

- **EDITORIAL-1.** Table 18 completes the checklist for a conventional versioned-row + audit-table + approval-flag + CAS design, identifying the additional predecessor-binding and batch-domain obligations for $D_F$/$D_B$ and specifying the $D_C$, $D_V$, and $D_S$ gaps and minimal repairs. It is labeled an inspection exercise, not a cross-system implementation.
- **EDITORIAL-2.** The abstract now frames the contribution as a *correction-aware, field-level specialization of ordinary transactional mutation*, states the joint candidate/authorization/source relation as the engineering increment, and compresses the agent benchmark to one integration-evidence sentence.
- **EDITORIAL-3.** Section 9.2 adds an engineering trade-off paragraph relating change width and persisted relations to planning cost, and complete-source reads to bounded-round-trip batch assembly.
- **EDITORIAL-4.** Historical admission and trace cost tables moved to Appendix A.2; the main text retains the current persistence-equivalent and optimized results.
- **Figures 3 and 4.** Both are redrawn on the same 432 pt canvas as Figures 1 and 2. Measured effective font sizes rise from 3.77--5.83 pt to 7.34--8.63 pt; the 36 dense heatmap values move to the trace table; Figure 4 now separates strict-trajectory and endpoint verdicts and reports acknowledgment counts in the table.

## Verification

| Check | Result |
|---|---|
| Baseline v8 PDF | unchanged, SHA-256 `3f7a0d57…f7a4`, 57 pages |
| Revised PDF | 64 pages, SHA-256 `b102a2dbf2c190e912d786bcb1c7df2e9ac198d17a88227edab23683ac2d5a50`, 0 warnings, 0 overfull/underfull, 53 references, 0 undefined references |
| Value-equality regression | 13 passed; 7 failed before the repair |
| Full Python suite | 377 passed |
| Ruff / mypy | passed / success (55 source files) |
| 35-case catalogue | 35/35 passed, 0 failed |
| Strict recomputation | 335/335 matches the frozen verdicts |
| Witness checker | five pairs unchanged; control reclassified as complete |
| Figure fonts | 7.34--8.63 pt effective (was 3.77--5.83 pt) |

Author-owned confirmations (authorship, originality, no concurrent submission, all-author approval) and the current JSS portal rules remain to be confirmed by the author; this revision does not claim to have verified them.


Post-DS verification: see `docs/DS-VERIFICATION-zh.md` for the authoritative current checks and remaining release steps. The original DS response is archived separately.
