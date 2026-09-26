# Formal and implementation section audit

Revised files: sections 03--06 only. No implementation, experimental record, bibliography, main driver, or supplement was changed by this audit.

## Completed substantive revisions

- Distinguish the whole authoritative state `Sigma_v` from its per-field source map `S_v`; retain the original equation labels.
- State Accept and Correction using canonical JSON equality. Preserve integer/float, number/Boolean, and nested-value distinctions instead of Python equality.
- Preserve the observation table, complete-history tuple, paired construction, and Proposition 1. The result is explicitly class-wise irredundancy relative to the declared history, observation, outcome, and failure model. It is neither universal minimality nor a uniqueness claim for the relational schema.
- Shorten duplicate explanations while retaining opaque certificate-handle projection assumptions, derivation of effect domains and successor counts, separate schema/item domains, and the additional same-context identity pair.
- Explain that source origins retain the machine proposal, whereas a corrected committed value derives authority from the human authorization.
- Make ReviewForms.confirm's actual trust boundary explicit: caller-supplied certificate IDs, values, and principal ID are used to construct the immutable binding at confirmation. A valid database binding does not attest prior display contents or human attention.
- Specify admission-relative rollback: evidence, candidates, and review intent persisted before an attempt need not be rolled back. E1 zero-write checking starts after authorization preparation.
- Preserve the no-op restriction, changed-field domain, initial full coverage, exact source copy-forward, commit-entry role revalidation, and limited in-flight revocation semantics.
- Retain the bounded Alloy qualification and positive trace assertion's well-formed-predecessor restriction. Do not elevate the fourteen UNSAT commands into fourteen independent proofs or arbitrary-history verification.
- Keep concrete prefix validation distinct from the narrower formal trace predicate, and retain the selected-projection/refinement boundary.
- Move detailed historical harness prose out of the main narrative; refer to Supplement S5 rather than making old harness evidence part of the new experiments.
- Replace global engine-setting prose with experiment-specific reporting, consistent with current admission DELETE/FULL and storage WAL/NORMAL configurations.

## Evidence consulted

- DKE-supplement/REPORT.md, including E1 preparation timing, E2 original API/session-gate limitations, and E3 engine configurations.
- latest/code/implementation-fixed/app/application/review_forms.py: confirm signature and construction of HumanDecision and AuthorizationBinding (approximately lines 95--108 and 291--307).
- latest/code/implementation-fixed/app/domain/authority.py: canonical_json and canonical_values_equal (approximately lines 53--68).
- latest/code/implementation-fixed/tests/unit/test_canonical_value_equality.py: numeric, Boolean, nested, unchanged, and no-op boundaries.
- Existing formal_evidence table: 36 commands per scope, 72 total; 22 SAT and 14 UNSAT per scope, including two trace antecedent witnesses.

## Dependencies and checks

- No new appendix or bibliography dependencies.
- All original section, equation, and table labels in these four files are preserved.
- Supplement S2 must retain the formal scope/projection/equality-repair details and identify the executable observation histories.
- Supplement S5 should identify the historical agent-harness integration and its capability boundary.
- The sole explicit RQ reference in these four files is RQ2 for the review-session experiment, matching the new question scheme.
- Source whitespace-token count is approximately 4,525 across the four sections, including LaTeX table/formatting tokens. The actual prose word count is lower.
- This audit did not rerun experiments or the Alloy Analyzer; it reviewed and rewrote the existing verified evidence. Whole-document compilation and final visual QA are handled by the parent task after integration.
