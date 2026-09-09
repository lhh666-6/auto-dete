"""The DSH bridge exposes two model operations and keeps confirmation host-only."""

from pathlib import Path

import pytest

from app.integrations.dsh_bridge import BRIDGE_VERSION, handle_request


def _request(data_root: Path, surface: str, operation: str, **values: object) -> dict[str, object]:
    return {
        "bridge_version": BRIDGE_VERSION,
        "data_root": str(data_root),
        "surface": surface,
        "operation": operation,
        **values,
    }


def test_bridge_candidate_then_host_confirmation(tmp_path: Path) -> None:
    fixture = handle_request(_request(tmp_path, "host", "init-fixture"))["result"]
    proposal = handle_request(
        _request(
            tmp_path,
            "model",
            "propose",
            form_id=fixture["form_id"],
            field_id=fixture["field_id"],
            parent_certificate_id=fixture["parent_certificate_id"],
            value=8,
            confidence=0.73,
            session_id="SESSION-1",
            execution_id="EXEC-1",
        )
    )["result"]

    verified = handle_request(
        _request(tmp_path, "model", "verify", certificate_id=proposal["certificate_id"])
    )["result"]
    assert verified["verified"] is True
    assert verified["current_fact_version"] == 0

    confirmed = handle_request(
        _request(
            tmp_path,
            "host",
            "host-confirm",
            certificate_id=proposal["certificate_id"],
            value=8,
            expected_version=0,
            actor_id="reviewer-1",
        )
    )["result"]
    assert confirmed["fact_version"] == 1
    assert confirmed["values"] == {"total_quantity": 8}


def test_bridge_rejects_host_confirmation_on_model_surface_without_state_change(
    tmp_path: Path,
) -> None:
    fixture = handle_request(_request(tmp_path, "host", "init-fixture"))["result"]
    with pytest.raises(PermissionError, match="not exposed"):
        handle_request(
            _request(
                tmp_path,
                "model",
                "host-confirm",
                certificate_id=fixture["parent_certificate_id"],
            )
        )
    receipt = handle_request(_request(tmp_path, "host", "export-receipt"))["result"]
    assert receipt["forms"][0]["current_record_version"] == 0


def test_bridge_verify_detects_tampered_ai_evidence(tmp_path: Path) -> None:
    fixture = handle_request(_request(tmp_path, "host", "init-fixture"))["result"]
    proposal = handle_request(
        _request(
            tmp_path,
            "model",
            "propose",
            form_id=fixture["form_id"],
            field_id=fixture["field_id"],
            parent_certificate_id=fixture["parent_certificate_id"],
            value=8,
            confidence=0.73,
            session_id="SESSION-1",
            execution_id="EXEC-1",
        )
    )["result"]
    evidence_path = tmp_path / "evidence" / proposal["evidence_uri"]
    evidence_path.write_bytes(evidence_path.read_bytes() + b"x")

    result = handle_request(
        _request(tmp_path, "model", "verify", certificate_id=proposal["certificate_id"])
    )["result"]
    assert result["verified"] is False
    assert result["failures"] == ["EVIDENCE_FILE_HASH_MISMATCH"]


def test_bridge_fixture_can_add_a_second_field_to_the_same_form(tmp_path: Path) -> None:
    first = handle_request(_request(tmp_path, "host", "init-fixture"))["result"]
    second = handle_request(
        _request(
            tmp_path,
            "host",
            "init-fixture",
            form_id=first["form_id"],
            field_id="FIELD-DSH-2",
            field_key="batch_code",
            initial_value="B-7",
        )
    )["result"]

    assert second["form_id"] == first["form_id"]
    assert second["field_id"] == "FIELD-DSH-2"
    assert second["field_key"] == "batch_code"
    assert second["parent_certificate_id"] != first["parent_certificate_id"]
    assert second["fact_version"] == 0
