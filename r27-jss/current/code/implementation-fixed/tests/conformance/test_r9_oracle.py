"""R9 self-tests for the independent raw-relational oracle."""

from copy import deepcopy

from tests.conformance.oracle import (
    canonical_database_state,
    relational_authority_violations,
    state_digest,
)
from tests.conformance.test_r5_source_history import _four_version_history


def _row(state: dict[str, object], table: str, **where: object) -> dict[str, object]:
    tables = state["tables"]
    assert isinstance(tables, dict)
    rows = tables[table]
    assert isinstance(rows, list)
    return next(row for row in rows if all(row[key] == value for key, value in where.items()))


def test_raw_relational_oracle_accepts_legal_multi_hop_history(tmp_path) -> None:
    engine, _ = _four_version_history(tmp_path)
    state = canonical_database_state(engine)

    assert relational_authority_violations(state, "FORM-1") == ()
    assert state_digest(state) == state_digest(canonical_database_state(engine))


def test_oracle_catches_source_auth_evidence_principal_and_value_mutants(
    tmp_path,
) -> None:
    engine, _ = _four_version_history(tmp_path)
    baseline = canonical_database_state(engine)
    mutants: list[tuple[str, dict[str, object]]] = []

    source = deepcopy(baseline)
    v4 = _row(source, "record_versions", form_id="FORM-1", version=4)
    v1 = _row(source, "record_versions", form_id="FORM-1", version=1)
    v4["fact_sources"]["a"] = v1["fact_sources"]["a"]
    mutants.append(("unchanged source", source))

    authorization = deepcopy(baseline)
    binding = _row(
        authorization,
        "authorization_bindings",
        decision_id="FORM-1:1:a",
    )
    binding["authorized_value_payload"] = "999"
    mutants.append(("authorization value", authorization))

    evidence = deepcopy(baseline)
    evidence_row = _row(evidence, "evidence_files", file_id="EVID-1")
    evidence_row["uri"] = "manual/other.png"
    mutants.append(("persisted evidence locator", evidence))

    principal = deepcopy(baseline)
    decision = _row(principal, "human_decisions", decision_id="FORM-1:1:a")
    decision["reviewer_id"] = "other-reviewer"
    mutants.append(("principal", principal))

    value = deepcopy(baseline)
    transition = _row(
        value,
        "fact_transitions",
        form_id="FORM-1",
        created_version=1,
        field_key="a",
    )
    transition["value_payload"] = "999"
    mutants.append(("transition value", value))

    for dimension, mutant in mutants:
        assert relational_authority_violations(mutant, "FORM-1"), dimension
        assert state_digest(mutant) != state_digest(baseline), dimension


def test_digest_covers_schema_sequences_and_every_application_table(tmp_path) -> None:
    engine, _ = _four_version_history(tmp_path)
    baseline = canonical_database_state(engine)
    tables = baseline["tables"]
    assert isinstance(tables, dict)

    schema_mutant = deepcopy(baseline)
    schema_mutant["user_version"] = 999
    assert state_digest(schema_mutant) != state_digest(baseline)

    sequence_mutant = deepcopy(baseline)
    sequence_mutant["identity_sequences"] = [{"name": "x", "seq": 1}]
    assert state_digest(sequence_mutant) != state_digest(baseline)

    for table in tables:
        mutant = deepcopy(baseline)
        mutant_tables = mutant["tables"]
        assert isinstance(mutant_tables, dict)
        rows = mutant_tables[table]
        assert isinstance(rows, list)
        rows.append({"__digest_probe__": table})
        assert state_digest(mutant) != state_digest(baseline), table
