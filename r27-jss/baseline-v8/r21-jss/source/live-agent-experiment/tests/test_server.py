import os
import sys
from pathlib import Path

import pytest

from auto_decte_live_agent.experiment import prepare_scenario, scenario_specs
from auto_decte_live_agent.runner import probe_database_digest
from auto_decte_live_agent.server import BridgeClient, BridgeConfig, create_server


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


def _implementation_python(implementation: Path) -> Path:
    configured = os.environ.get("AUTO_DECTE_IMPLEMENTATION_PYTHON")
    if configured:
        candidate = Path(configured)
    else:
        candidate = implementation / ".venv" / "Scripts" / "python.exe"
    if candidate.is_file():
        return candidate
    if (implementation / "app").is_dir() and sys.prefix == str(implementation / ".venv"):
        return Path(sys.executable)
    raise FileNotFoundError(
        "run `uv sync --frozen --extra dev --extra research` in source/implementation "
        "or set AUTO_DECTE_IMPLEMENTATION_PYTHON"
    )


@pytest.fixture
def bridge(tmp_path: Path) -> BridgeClient:
    revision = Path(__file__).resolve().parents[3]
    implementation = revision / "source" / "implementation"
    python = _implementation_python(implementation)
    return BridgeClient(
        BridgeConfig(
            data_root=tmp_path,
            implementation_root=implementation,
            python_executable=python,
        )
    )


@pytest.mark.anyio
async def test_server_exposes_exactly_candidate_proposal_and_verification(
    bridge: BridgeClient,
) -> None:
    server = create_server(bridge)

    names = sorted(tool.name for tool in await server.list_tools())

    assert names == ["auto_decte_propose", "auto_decte_verify"]


def test_real_bridge_round_trip_keeps_fact_version_zero(bridge: BridgeClient) -> None:
    fixture = bridge.host("init-fixture")
    proposal = bridge.model(
        "propose",
        form_id=fixture["form_id"],
        field_id=fixture["field_id"],
        parent_certificate_id=fixture["parent_certificate_id"],
        value=8,
        confidence=0.73,
        session_id="TEST-SESSION",
        execution_id="TEST-EXECUTION",
    )

    verification = bridge.model("verify", certificate_id=proposal["certificate_id"])

    assert verification["verified"] is True
    assert verification["current_fact_version"] == 0
    receipt = bridge.host("export-receipt")
    assert receipt["forms"][0]["current_record_version"] == 0


def test_cross_field_setup_builds_a_rejecting_tuple(bridge: BridgeClient) -> None:
    spec = next(spec for spec in scenario_specs() if spec.kind == "cross_field")

    prepared = prepare_scenario(spec, bridge)

    assert prepared["form_id"] == "FORM-DSH-1"
    assert prepared["other_field_id"] == "FIELD-DSH-2"
    with pytest.raises(RuntimeError, match="BRIDGE_REJECTED"):
        bridge.model(
            "propose",
            form_id=prepared["form_id"],
            field_id=prepared["other_field_id"],
            parent_certificate_id=prepared["parent_certificate_id"],
            value=8,
            confidence=0.73,
            session_id="CROSS-FIELD-TEST",
            execution_id="CROSS-FIELD-TEST",
        )


def test_independent_database_probe_changes_after_candidate_append(
    bridge: BridgeClient, tmp_path: Path
) -> None:
    revision = Path(__file__).resolve().parents[3]
    implementation = revision / "source" / "implementation"
    server_source = revision / "source" / "live-agent-experiment"
    python = _implementation_python(implementation)
    fixture = bridge.host("init-fixture")
    before = probe_database_digest(
        implementation_python=python,
        server_source=server_source,
        implementation_root=implementation,
        database_path=tmp_path / "database" / "demo.db",
    )

    bridge.model(
        "propose",
        form_id=fixture["form_id"],
        field_id=fixture["field_id"],
        parent_certificate_id=fixture["parent_certificate_id"],
        value=8,
        confidence=0.73,
        session_id="DIGEST-SESSION",
        execution_id="DIGEST-EXECUTION",
    )
    after = probe_database_digest(
        implementation_python=python,
        server_source=server_source,
        implementation_root=implementation,
        database_path=tmp_path / "database" / "demo.db",
    )

    assert before != after
