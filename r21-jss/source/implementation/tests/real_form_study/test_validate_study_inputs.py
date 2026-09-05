"""Schema-validation tests for the locked study data contracts."""

from pathlib import Path

from analysis.real_form_study.validate_study_inputs import validate_study_inputs
from tests.real_form_study.dummy_study_data import write_dummy_study_data


def _rewrite(data_dir: Path, filename: str, rows: list[list[str]]) -> None:
    path = data_dir / filename
    lines = [",".join(row) for row in rows]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def test_dummy_data_passes_validation(tmp_path: Path) -> None:
    write_dummy_study_data(tmp_path)
    assert validate_study_inputs(tmp_path) == []


def test_missing_file_reported(tmp_path: Path) -> None:
    write_dummy_study_data(tmp_path)
    (tmp_path / "study_flow.csv").unlink()
    errors = validate_study_inputs(tmp_path)
    assert any("study_flow.csv: missing" in error for error in errors)


def test_wrong_header_rejected(tmp_path: Path) -> None:
    write_dummy_study_data(tmp_path)
    rows = [
        line.split(",")
        for line in (tmp_path / "forms.csv").read_text(encoding="utf-8").splitlines()
    ]
    rows[0][0] = "wrong_column"
    _rewrite(tmp_path, "forms.csv", rows)
    errors = validate_study_inputs(tmp_path)
    assert any("forms.csv: missing columns" in error for error in errors)
    assert any("forms.csv: unexpected columns" in error for error in errors)


def test_invalid_domain_rejected(tmp_path: Path) -> None:
    write_dummy_study_data(tmp_path)
    rows = [
        line.split(",")
        for line in (tmp_path / "review_decisions.csv").read_text(encoding="utf-8").splitlines()
    ]
    for row in rows[1:]:
        if row[4] == "retain_machine":
            row[4] = "keep_it"
            break
    _rewrite(tmp_path, "review_decisions.csv", rows)
    errors = validate_study_inputs(tmp_path)
    assert any("action" in error and "keep_it" in error for error in errors)


def test_naive_timestamp_rejected(tmp_path: Path) -> None:
    write_dummy_study_data(tmp_path)
    rows = [
        line.split(",")
        for line in (tmp_path / "review_decisions.csv").read_text(encoding="utf-8").splitlines()
    ]
    rows[1][9] = "2026-08-17T12:00:00"  # naive form_opened_at
    _rewrite(tmp_path, "review_decisions.csv", rows)
    errors = validate_study_inputs(tmp_path)
    assert any("form_opened_at" in error and "timezone-aware" in error for error in errors)


def test_unknown_form_reference_rejected(tmp_path: Path) -> None:
    write_dummy_study_data(tmp_path)
    rows = [
        line.split(",")
        for line in (tmp_path / "study_flow.csv").read_text(encoding="utf-8").splitlines()
    ]
    rows[1][0] = "F-999"
    _rewrite(tmp_path, "study_flow.csv", rows)
    errors = validate_study_inputs(tmp_path)
    assert any("unknown study_form_id" in error for error in errors)


def test_bad_sha256_rejected(tmp_path: Path) -> None:
    write_dummy_study_data(tmp_path)
    rows = [
        line.split(",")
        for line in (tmp_path / "forms.csv").read_text(encoding="utf-8").splitlines()
    ]
    rows[1][4] = "not-a-hash"
    _rewrite(tmp_path, "forms.csv", rows)
    errors = validate_study_inputs(tmp_path)
    assert any("image_sha256" in error and "sha256" in error for error in errors)


def test_review_field_must_be_target_field(tmp_path: Path) -> None:
    write_dummy_study_data(tmp_path)
    rows = [
        line.split(",")
        for line in (tmp_path / "review_decisions.csv").read_text(encoding="utf-8").splitlines()
    ]
    rows[1][1] = "not_a_target_field"
    _rewrite(tmp_path, "review_decisions.csv", rows)
    errors = validate_study_inputs(tmp_path)
    assert any("not a target field" in error for error in errors)
