import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from auto_decte_agent_benchmark.bridge_client import (
    BridgeClient,
    BridgeConfig,
    BridgeRejectedError,
)


def config(tmp_path: Path) -> BridgeConfig:
    return BridgeConfig(
        data_root=tmp_path / "data",
        implementation_root=tmp_path / "implementation",
        python_executable=Path("C:/python/python.exe"),
    )


def test_bridge_client_separates_model_and_host_surfaces(tmp_path) -> None:
    requests: list[dict] = []

    def fake_run(command, **kwargs):
        request = json.loads(kwargs["input"])
        requests.append(request)
        assert "ANTHROPIC_AUTH_TOKEN" not in kwargs["env"]
        assert "OPENAI_API_KEY" not in kwargs["env"]
        response = {
            "ok": True,
            "bridge_version": "auto-decte.agent-benchmark-bridge.v2",
            "result": {"operation": request["operation"]},
        }
        return subprocess.CompletedProcess(command, 0, json.dumps(response), "")

    bridge = BridgeClient(config(tmp_path), command_runner=fake_run)

    assert bridge.model("verify", certificate_id="C1") == {"operation": "verify"}
    assert bridge.host("prepare-scenario", scenario_id="B1") == {
        "operation": "prepare-scenario"
    }
    assert [request["surface"] for request in requests] == ["model", "host"]
    assert all(request["data_root"].endswith("data") for request in requests)


def test_bridge_client_rejects_failed_or_wrong_version_envelopes(tmp_path) -> None:
    def fake_run(command, **_kwargs):
        response = {"ok": False, "bridge_version": "wrong", "error": {"code": "REJECTED"}}
        return subprocess.CompletedProcess(command, 1, json.dumps(response), "")

    bridge = BridgeClient(config(tmp_path), command_runner=fake_run)

    with pytest.raises(BridgeRejectedError, match="BENCHMARK_BRIDGE_REJECTED") as caught:
        bridge.model("verify", certificate_id="C1")

    assert caught.value.error_type == "unknown"
    assert caught.value.error_message == "REJECTED"


def test_bridge_client_retains_sanitized_validation_error_for_tool_feedback(tmp_path) -> None:
    def fake_run(command, **_kwargs):
        response = {
            "ok": False,
            "bridge_version": "auto-decte.agent-benchmark-bridge.v2",
            "error": {
                "type": "ValueError",
                "message": "field_id must be FIELD-BENCH-QUANTITY",
            },
        }
        return subprocess.CompletedProcess(command, 1, json.dumps(response), "")

    bridge = BridgeClient(config(tmp_path), command_runner=fake_run)

    with pytest.raises(BridgeRejectedError) as caught:
        bridge.model("propose", field_id="wrong")

    assert caught.value.error_type == "ValueError"
    assert caught.value.error_message == "field_id must be FIELD-BENCH-QUANTITY"


def test_real_bridge_candidate_round_trip_leaves_authority_version_zero(tmp_path) -> None:
    revision = Path(__file__).resolve().parents[3]
    implementation = revision / "source" / "implementation"
    configured = os.environ.get("AUTO_DECTE_IMPLEMENTATION_PYTHON")
    python = Path(configured) if configured else implementation / ".venv/Scripts/python.exe"
    if not python.is_file() and sys.prefix == str(implementation / ".venv"):
        python = Path(sys.executable)
    if not python.is_file():
        pytest.fail("the pinned implementation Python environment is missing")
    bridge = BridgeClient(
        BridgeConfig(
            data_root=tmp_path / "run-data",
            implementation_root=implementation,
            python_executable=python,
        )
    )

    fixture = bridge.host("init-fixture")
    proposal = bridge.model(
        "propose",
        form_id=fixture["form_id"],
        field_id=fixture["field_id"],
        parent_certificate_id=fixture["parent_certificate_id"],
        value=8,
        confidence=0.73,
        session_id="BENCHMARK-TEST",
        execution_id="BENCHMARK-TEST",
    )
    verification = bridge.model("verify", certificate_id=proposal["certificate_id"])
    receipt = bridge.host("export-receipt")

    assert verification["verified"] is True
    assert verification["current_fact_version"] == 0
    assert receipt["forms"][0]["current_record_version"] == 0
