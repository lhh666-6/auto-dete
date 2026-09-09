# Independent Oracle

> The G3b material below is historical context. R9's current oracle is
> `tests/conformance/oracle.py` and the finite denominator is
> `conformance/case_catalogue.json`.

## Principle

The conformance tests use an independent oracle expressed as low-level state
invariants and expected observable outcomes, not by calling the same
production validator decisions that are under test.

In particular:

- For legal cases, the oracle checks the persisted **rows**:
  - one `AuthorizationBindingRow` exists with the expected `certificate_id` and `authorized_value_payload`;
  - the `FactTransitionRow` remains bound to the original machine `certificate_id`;
  - `RecordVersionRow.fact_sources[field]` equals the transition that is the current source;
  - every `RecordVersionRow.values` domain equals its `fact_sources` domain (complete snapshot);
  - a `RuleBasedStateMachine` maintains its own independent `model` dict and compares it to the persisted complete snapshot and to `QueryForms.trace`.
- For rejection cases, the oracle asserts:
  - the application raised the expected public rejection type/code;
  - no new `RecordVersion`, `FactTransition`, or `AuthorizationBinding` rows were persisted.
- The oracle does **not** call `TransitionPolicy.authorize`, `verify_transition_authorization`, or
  `build_provenance_trace` as its expected-value source. Those production helpers are part of the
  system under test.

## Independent checks in this bundle

- `tests/conformance/test_g3b_conformance.py` contains:
  - deterministic legal/correction/copy-forward/rejection scenarios;
  - failure-closed trace checks for authorized-value/transition-value/committed-value mismatches;
  - repository-level admission-bundle hardening checks;
  - required substitution families (including evidence identity and evidence owner);
  - duplicate-source schema prevention;
  - a test-only concrete ablation guard oracle for ABL_3, ABL_4b, ABL_5, ABL_8;
  - a Hypothesis `RuleBasedStateMachine` that explores legal confirm/correct transitions.

## R9 raw-relational oracle

The R9 oracle reads every SQLite application table directly and does not call
the production admission planner, certificate validator, evidence-identity
helper, or trace builder. It independently checks exact declared snapshot and
source domains, adjacent source evolution, transition sets, record-version
anchors, decision/principal/certificate/authorization/evidence relations, and
authorized/transition/committed values. Five in-memory relation mutants
(source, authorization, evidence locator, principal, value) prove that the
oracle remains sensitive when production code is not involved.

`database_digest` covers `PRAGMA user_version`, identity sequences, and every
row/value in every application table in deterministic order. Rejection and
post-persistence corruption are separate catalogue classes: rejection expects
an unchanged digest; corruption expects a changed digest plus an incomplete
trace/oracle diagnosis.
