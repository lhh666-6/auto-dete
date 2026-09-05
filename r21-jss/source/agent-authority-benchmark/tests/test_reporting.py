from pathlib import Path

import pytest

from auto_decte_agent_benchmark.reporting import (
    _count_label_x,
    build_behavior_rows,
    build_mechanism_rows,
    render_final_reporting_bundle,
)


def _row(model: str, scenario: str, **overrides):
    benign = scenario.startswith("B")
    negative = scenario.startswith("A")
    row = {
        "phase": "final",
        "model_config_id": model,
        "scenario_id": scenario,
        "terminal_class": "PASS_UTILITY_SAFE",
        "agent_behavior_evaluable": True,
        "benign_task_completion": True if benign else None,
        "agent_attempted_unavailable_capability": False,
        "agent_detected_context_mismatch": False,
        "agent_detected_stale_state": False,
        "recovery_success": True if scenario == "B4" else None,
        "authority_evaluable": negative,
        "unauthorized_authoritative_mutation": False if negative else None,
    }
    row.update(overrides)
    return row


def _rows():
    rows = []
    for model in ("G1", "D1"):
        rows.extend(
            [
                _row(model, "B1"),
                _row(model, "B4", agent_detected_stale_state=model == "G1"),
                _row(model, "A2", agent_detected_context_mismatch=True),
                _row(model, "A3", agent_detected_context_mismatch=model == "D1"),
                _row(model, "A6", agent_detected_stale_state=True),
                _row(model, "A10", agent_attempted_unavailable_capability=model == "G1"),
            ]
        )
    return rows


def test_reporting_rows_keep_agent_and_mechanism_evidence_separate() -> None:
    behavior = build_behavior_rows(_rows())
    mechanism = build_mechanism_rows(_rows())

    assert [row["model_config_id"] for row in behavior] == ["D1", "G1"]
    assert behavior[0]["benign_completion"] == "2/2"
    assert behavior[0]["context_recognition"] == "2/2"
    assert behavior[1]["unavailable_capability_attempt"] == "1/1"
    assert all("unauthorized" not in key for row in behavior for key in row)

    assert [row["model_config_id"] for row in mechanism] == ["D1", "G1"]
    assert mechanism[0]["unauthorized_mutation"] == "0/4"
    assert mechanism[0]["cross_record_violation"] == "0/1"
    assert mechanism[0]["cross_field_violation"] == "0/1"
    assert all("completion" not in key for row in mechanism for key in row)


def test_count_label_is_offset_from_a_boundary_marker() -> None:
    assert 1.0 < _count_label_x(1.0) < 1.08


def test_reporting_bundle_rejects_nonfinal_or_incomplete_inputs(tmp_path: Path) -> None:
    rows = _rows()
    with pytest.raises(ValueError, match="final"):
        render_final_reporting_bundle(rows, tmp_path / "pilot", phase="pilot")
    with pytest.raises(ValueError, match="complete locked plan"):
        render_final_reporting_bundle(
            rows,
            tmp_path / "partial",
            phase="final",
            complete_locked_plan=False,
        )


def test_reporting_bundle_writes_separate_tables_and_editable_vector_figure(
    tmp_path: Path,
) -> None:
    output = tmp_path / "reporting"
    paths = render_final_reporting_bundle(
        _rows(),
        output,
        phase="final",
        complete_locked_plan=True,
    )

    assert paths == {
        "behavior_table": output / "agent_behavior_table.tex",
        "mechanism_table": output / "admission_mechanism_table.tex",
        "statistics": output / "statistical_analysis.json",
        "svg": output / "behavior_vs_authority.svg",
        "pdf": output / "behavior_vs_authority.pdf",
        "png": output / "behavior_vs_authority.png",
        "qa": output / "FIGURE_QA.md",
    }
    for path in paths.values():
        assert path.is_file() and path.stat().st_size > 0

    behavior_tex = paths["behavior_table"].read_text(encoding="utf-8")
    mechanism_tex = paths["mechanism_table"].read_text(encoding="utf-8")
    assert "Agent-mediated behavior" in behavior_tex
    assert "Unauthorized authoritative mutation" not in behavior_tex
    assert "Admission-mechanism challenges" in mechanism_tex
    assert "Benign task completion" not in mechanism_tex

    svg = paths["svg"].read_text(encoding="utf-8")
    assert "<image" not in svg
    assert "G1" in svg and "D1" in svg and "Pooled" in svg
    assert "Benign task completion" in svg
    assert "Unauthorized authoritative mutation" in svg
    assert paths["png"].read_bytes().startswith(b"\x89PNG\r\n\x1a\n")
    assert paths["pdf"].read_bytes().startswith(b"%PDF")
