"""R9 finite-denominator catalogue integrity checks."""

import json
from pathlib import Path

from conformance.run_catalogue import run_catalogue

CATALOGUE = Path("conformance/case_catalogue.json")


def test_catalogue_has_unique_finite_denominator_and_p0_p6_coverage() -> None:
    payload = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    cases = payload["cases"]

    assert payload["catalogue_version"] == "auto-decte-r9-v1"
    assert payload["denominator"] == len(cases) == 35
    assert len({case["id"] for case in cases}) == len(cases)
    assert {property_id for case in cases for property_id in case["properties"]} == {
        f"P{number}" for number in range(7)
    }
    assert {case["kind"] for case in cases} >= {
        "legal",
        "rejection",
        "corruption",
        "prevention",
        "stateful",
        "oracle",
    }
    assert all(case["expected_status"] for case in cases)


def test_catalogue_node_ids_resolve_to_declared_test_functions() -> None:
    payload = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    for case in payload["cases"]:
        path_text, function_name = case["node_id"].split("::", maxsplit=1)
        source = Path(path_text).read_text(encoding="utf-8")
        assert f"def {function_name}(" in source


def test_rejection_and_corruption_digest_expectations_are_separate() -> None:
    payload = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    rejections = [case for case in payload["cases"] if case["kind"] == "rejection"]
    corruptions = [case for case in payload["cases"] if case["kind"] == "corruption"]

    assert rejections and corruptions
    assert all(case["digest_expectation"] == "unchanged" for case in rejections)
    assert all(case["digest_expectation"] == "changed" for case in corruptions)


def test_catalogue_disables_pytest_cache_for_nested_case_runs(tmp_path: Path) -> None:
    payload = json.loads(CATALOGUE.read_text(encoding="utf-8"))
    case_id = payload["cases"][0]["id"]
    output = tmp_path / "catalogue"

    assert run_catalogue(output, selected_case=case_id) == 0

    result = json.loads((output / "cases" / f"{case_id}.json").read_text(encoding="utf-8"))
    command = result["command"]
    assert command[3:5] == ["-p", "no:cacheprovider"]
