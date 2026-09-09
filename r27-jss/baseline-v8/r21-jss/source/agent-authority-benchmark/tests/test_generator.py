from importlib import import_module


def require(name: str):
    try:
        module = import_module("auto_decte_agent_benchmark.generator")
    except ModuleNotFoundError:
        module = None
    assert module is not None, "generator module is missing"
    assert hasattr(module, name), f"generator is missing {name}"
    return getattr(module, name)


def test_fixture_generation_is_byte_deterministic_for_one_seed() -> None:
    build = require("build_fixture_spec")

    first = build(103)
    second = build(103)

    assert first == second
    assert first.canonical_json() == second.canonical_json()


def test_fixture_seed_changes_identity_without_changing_declared_vocabulary() -> None:
    build = require("build_fixture_spec")

    first = build(103)
    second = build(104)

    assert first.primary_form_id != second.primary_form_id
    assert tuple(field.field_key for field in first.fields) == tuple(
        field.field_key for field in second.fields
    )
    assert first.initial_fact_version == second.initial_fact_version == 0


def test_fixture_has_distinct_primary_foreign_and_field_identities() -> None:
    build = require("build_fixture_spec")

    fixture = build(105)
    identities = [
        fixture.primary_form_id,
        fixture.foreign_form_id,
        *(field.field_id for field in fixture.fields),
    ]

    assert len(identities) == len(set(identities))


def test_fixture_accepts_full_unsigned_64_bit_case_seed() -> None:
    build = require("build_fixture_spec")

    fixture = build((1 << 64) - 1)

    assert fixture.case_seed == (1 << 64) - 1
    assert fixture.generated_at.startswith("2026-")
