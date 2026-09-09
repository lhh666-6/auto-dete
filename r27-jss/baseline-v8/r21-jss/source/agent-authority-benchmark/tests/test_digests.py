from importlib import import_module


def require(name: str):
    try:
        module = import_module("auto_decte_agent_benchmark.digests")
    except ModuleNotFoundError:
        module = None
    assert module is not None, "digests module is missing"
    assert hasattr(module, name), f"digests is missing {name}"
    return getattr(module, name)


def database_state() -> dict[str, object]:
    return {
        "user_version": 1,
        "identity_sequences": [{"name": "candidate_certificates", "seq": 1}],
        "tables": {
            "forms": [{"id": "F1", "current_fact_version": 0}],
            "form_fields": [{"form_id": "F1", "field_name": "quantity"}],
            "record_versions": [{"form_id": "F1", "version": 0, "values": {"quantity": 7}}],
            "human_decisions": [],
            "fact_transitions": [],
            "authorization_bindings": [],
            "authority_meta": [{"singleton": 1, "schema": "v1"}],
            "candidate_certificates": [{"certificate_id": "C0"}],
            "evidence_files": [{"file_id": "E0"}],
            "ai_reviews": [],
            "recognition_attempts": [],
            "audit_events": [],
        },
    }


def test_candidate_append_changes_candidate_digest_but_not_authority_digest() -> None:
    digest_state = require("digest_state")
    before = database_state()
    after = database_state()
    after["tables"]["candidate_certificates"].append({"certificate_id": "C1"})  # type: ignore[index]
    after["identity_sequences"] = [{"name": "candidate_certificates", "seq": 2}]

    assert digest_state(before).candidate != digest_state(after).candidate
    assert digest_state(before).authority == digest_state(after).authority


def test_fact_transition_changes_authority_digest() -> None:
    digest_state = require("digest_state")
    before = database_state()
    after = database_state()
    after["tables"]["fact_transitions"].append(  # type: ignore[index]
        {"transition_id": "T1", "form_id": "F1", "created_version": 1}
    )

    assert digest_state(before).authority != digest_state(after).authority


def test_digest_is_independent_of_table_key_order() -> None:
    digest_state = require("digest_state")
    first = database_state()
    second = database_state()
    second["tables"] = dict(reversed(list(second["tables"].items())))  # type: ignore[union-attr]

    assert digest_state(first) == digest_state(second)
