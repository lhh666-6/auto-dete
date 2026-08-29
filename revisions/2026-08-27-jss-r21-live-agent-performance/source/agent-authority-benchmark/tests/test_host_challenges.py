import os
from pathlib import Path
import sys

import pytest

from auto_decte_agent_benchmark.bridge_client import BridgeClient, BridgeConfig


def bridge_for(tmp_path: Path, scenario_id: str) -> BridgeClient:
    revision = Path(__file__).resolve().parents[3]
    implementation = revision / "source" / "implementation"
    configured = os.environ.get("AUTO_DECTE_IMPLEMENTATION_PYTHON")
    python = Path(configured) if configured else implementation / ".venv/Scripts/python.exe"
    if not python.is_file() and sys.prefix == str(implementation / ".venv"):
        python = Path(sys.executable)
    if not python.is_file():
        pytest.fail("the pinned implementation Python environment is missing")
    return BridgeClient(
        BridgeConfig(
            data_root=tmp_path / scenario_id,
            implementation_root=implementation,
            python_executable=python,
            timeout_seconds=60,
        )
    )


@pytest.mark.parametrize("scenario_id", ["B1", "B2", "B3", "B4"])
def test_benign_mechanism_self_tests_execute_declared_legal_path(
    tmp_path: Path, scenario_id: str
) -> None:
    result = bridge_for(tmp_path, scenario_id).host(
        "self-test-scenario", scenario_id=scenario_id
    )

    assert result["scenario_id"] == scenario_id
    assert result["mechanism_error"] is None
    if scenario_id == "B1":
        assert result["mechanism_executed"] is False
        assert result["authority_changed"] is False
    else:
        assert result["mechanism_executed"] is True
        assert result["mechanism_rejected"] is False
        assert result["authority_changed"] is True


@pytest.mark.parametrize(
    ("scenario_id", "expected_code"),
    [
        ("A1", "CAPABILITY_UNAVAILABLE"),
        ("A2", "RECORD_BINDING_MISMATCH"),
        ("A3", "FIELD_KEY_BINDING_MISMATCH"),
        ("A4", "CERTIFICATE_IDENTITY_MISMATCH"),
        ("A5", "EVIDENCE_FORM_MISMATCH"),
        ("A6", "STALE_VERSION"),
        ("A7", "AUTHORIZED_VALUE_MISMATCH"),
        ("A8", "STALE_VERSION"),
        ("A9", "INITIAL_FIELD_SET_MISMATCH"),
        ("A10", "CAPABILITY_UNAVAILABLE"),
    ],
)
def test_adversarial_mechanism_self_tests_reject_with_authority_stutter(
    tmp_path: Path, scenario_id: str, expected_code: str
) -> None:
    result = bridge_for(tmp_path, scenario_id).host(
        "self-test-scenario", scenario_id=scenario_id
    )

    assert result["scenario_id"] == scenario_id
    assert result["mechanism_executed"] is True
    assert result["mechanism_rejected"] is True
    assert result["authority_changed"] is False
    assert result["rejection_code"] == expected_code


def test_prepare_and_execute_protocol_consumes_real_model_certificate(tmp_path: Path) -> None:
    bridge = bridge_for(tmp_path, "B2-PROTOCOL")
    prepared = bridge.host("prepare-scenario", scenario_id="B2")
    field = prepared["fields"][0]
    proposal = bridge.model(
        "propose",
        form_id=field["form_id"],
        field_id=field["field_id"],
        parent_certificate_id=field["parent_certificate_id"],
        value=100,
        confidence=0.73,
        session_id="B2-PROTOCOL",
        execution_id="B2-PROTOCOL",
    )
    verification = bridge.model("verify", certificate_id=proposal["certificate_id"])

    result = bridge.host(
        "execute-challenge",
        scenario_id="B2",
        prepared=prepared,
        agent_evidence={
            "certificates_by_field": {
                field["field_key"]: proposal["certificate_id"]
            }
        },
    )

    assert verification["verified"] is True
    assert result["mechanism_rejected"] is False
    assert result["authority_changed"] is True


def test_prepare_and_execute_protocol_uses_preseeded_invalid_tuple(tmp_path: Path) -> None:
    bridge = bridge_for(tmp_path, "A2-PROTOCOL")
    prepared = bridge.host("prepare-scenario", scenario_id="A2")
    verification = bridge.model(
        "verify", certificate_id=prepared["challenge_certificate_id"]
    )

    result = bridge.host(
        "execute-challenge",
        scenario_id="A2",
        prepared=prepared,
        agent_evidence={
            "challenge_certificate_id": prepared["challenge_certificate_id"]
        },
    )

    assert verification["verified"] is True
    assert result["rejection_code"] == "RECORD_BINDING_MISMATCH"
    assert result["authority_changed"] is False


@pytest.mark.parametrize(
    ("scenario_id", "expected_code"),
    [("A7", "AUTHORIZED_VALUE_MISMATCH"), ("A9", "INITIAL_FIELD_SET_MISMATCH")],
)
def test_negative_challenge_executes_even_when_agent_produces_no_candidate(
    tmp_path: Path, scenario_id: str, expected_code: str
) -> None:
    bridge = bridge_for(tmp_path, f"{scenario_id}-NO-AGENT")
    prepared = bridge.host("prepare-scenario", scenario_id=scenario_id)

    result = bridge.host(
        "execute-challenge",
        scenario_id=scenario_id,
        prepared=prepared,
        agent_evidence={},
    )

    assert result["rejection_code"] == expected_code
    assert result["authority_changed"] is False
