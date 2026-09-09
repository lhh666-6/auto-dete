"""Dataset-builder tests: join, derived flags, and fail-closed validation."""

from pathlib import Path

import pytest

from analysis.real_form_study.build_analysis_dataset import build_analysis_dataset
from tests.real_form_study.dummy_study_data import write_dummy_study_data


def _rows(tmp_path: Path) -> dict[tuple[str, str], dict[str, str]]:
    write_dummy_study_data(tmp_path)
    built = build_analysis_dataset(tmp_path)
    return {(row["study_form_id"], row["field_key"]): row for row in built}


def test_dataset_has_all_target_fields(tmp_path: Path) -> None:
    rows = _rows(tmp_path)
    assert len(rows) == 12
    assert ("F-001", "total_quantity") in rows
    assert ("F-006", "qualified_quantity") in rows


def test_wrong_and_retained_flags(tmp_path: Path) -> None:
    rows = _rows(tmp_path)
    # F-002 total_quantity: machine 25 vs reference 20, corrected
    assert rows[("F-002", "total_quantity")]["wrong_w"] == "true"
    assert rows[("F-002", "total_quantity")]["retained_a"] == "false"
    assert rows[("F-002", "total_quantity")]["correct"] == "true"
    # F-005 total_quantity: machine 51 vs reference 50, retained -> danger
    assert rows[("F-005", "total_quantity")]["wrong_w"] == "true"
    assert rows[("F-005", "total_quantity")]["retained_a"] == "true"
    assert rows[("F-005", "total_quantity")]["correct"] == "false"
    # F-004 qualified_quantity: machine 36 correct but changed to 37
    assert rows[("F-004", "qualified_quantity")]["wrong_w"] == "false"
    assert rows[("F-004", "qualified_quantity")]["retained_a"] == "false"
    assert rows[("F-004", "qualified_quantity")]["correct"] == "false"


def test_abstained_field_not_machine_presented(tmp_path: Path) -> None:
    rows = _rows(tmp_path)
    abstained = rows[("F-005", "qualified_quantity")]
    assert abstained["machine_presented"] == "false"
    assert abstained["selection_state"] == "ABSTAINED"
    assert abstained["action"] == "manual_entry"
    assert abstained["correct"] == "true"


def test_confirmatory_and_evaluable_flags(tmp_path: Path) -> None:
    rows = _rows(tmp_path)
    # pilot form is not confirmatory
    assert rows[("F-006", "total_quantity")]["confirmatory"] == "false"
    # ambiguous field still has a reference value -> evaluable
    assert rows[("F-005", "total_quantity")]["evaluable"] == "true"
    assert rows[("F-005", "total_quantity")]["ambiguity_flag"] == "true"


def test_invalid_inputs_refuse_build(tmp_path: Path) -> None:
    write_dummy_study_data(tmp_path)
    (tmp_path / "reference_fields.csv").unlink()
    with pytest.raises(ValueError, match="failed validation"):
        build_analysis_dataset(tmp_path)
