import os
from pathlib import Path
import sys

import pytest

from auto_decte_agent_benchmark.canonical_events import EventType, ProviderNeutralAgentEvent
from auto_decte_agent_benchmark.execution import InvocationEnvelope
from auto_decte_agent_benchmark.phase_runner import run_phase
from auto_decte_agent_benchmark.schema import ProviderFamily


ROOT = Path(__file__).resolve().parents[1]


def implementation_python() -> Path:
    revision = ROOT.parents[1]
    implementation = revision / "source/implementation"
    configured = os.environ.get("AUTO_DECTE_IMPLEMENTATION_PYTHON")
    python = Path(configured) if configured else implementation / ".venv/Scripts/python.exe"
    if not python.is_file() and sys.prefix == str(implementation / ".venv"):
        python = Path(sys.executable)
    assert python.is_file()
    return python


def test_narrowed_pilot_executes_complete_non_network_pipeline(tmp_path) -> None:
    def fake_provider(model, _prompt, bridge, prepared):
        field = prepared["fields"][0]
        proposal = bridge.model(
            "propose",
            form_id=field["form_id"],
            field_id=field["field_id"],
            parent_certificate_id=field["parent_certificate_id"],
            value=8,
            confidence=0.73,
            session_id="PHASE-TEST",
            execution_id="PHASE-TEST",
        )
        verification = bridge.model("verify", certificate_id=proposal["certificate_id"])
        raw_events = (
            (EventType.RUN_STARTED, {}),
            (
                EventType.TOOL_CALL,
                {
                    "tool_name": "auto_decte_propose",
                    "tool_arguments": {
                        "field_id": field["field_id"],
                    },
                },
            ),
            (
                EventType.TOOL_RESULT,
                {"tool_name": "auto_decte_propose", "tool_result": proposal},
            ),
            (
                EventType.TOOL_CALL,
                {
                    "tool_name": "auto_decte_verify",
                    "tool_arguments": {"certificate_id": proposal["certificate_id"]},
                },
            ),
            (
                EventType.TOOL_RESULT,
                {"tool_name": "auto_decte_verify", "tool_result": verification},
            ),
            (EventType.RUN_COMPLETED, {}),
        )
        events = tuple(
            ProviderNeutralAgentEvent(
                provider=ProviderFamily.DEEPSEEK,
                model_config_id=model.model_config_id,
                timestamp="unavailable",
                event_index=index,
                event_type=event_type,
                raw_event_pointer=f"raw#{index}",
                **values,
            )
            for index, (event_type, values) in enumerate(raw_events)
        )
        return InvocationEnvelope(events, {"fake.json": "{}\n"}, "", 0, 1, None)

    output = tmp_path / "pilot"
    result = run_phase(
        config_root=ROOT / "config",
        output_root=output,
        phase="pilot",
        revision_root=ROOT.parents[1],
        implementation_python=implementation_python(),
        model_ids=("D1",),
        scenario_ids=("B1",),
        variant_ids=("V1",),
        provider_invoker=fake_provider,
    )

    assert result["planned_executions"] == 1
    assert result["runtime_failures"] == 0
    assert result["benign_task_completion"]["count"] == 1
    assert result["benign_task_completion"]["denominator"] == 1
    assert (output / "normalized/runs.json").is_file()
    assert (output / "manifest.json").is_file()
    assert (output / "DIAGNOSTIC_REPORT.md").is_file()
    assert not (output / "PILOT_REPORT.md").exists()
    assert not (output / "pilot-model-qualification.json").exists()


def test_resume_verifies_completed_phase_without_reinvoking_terminal_run(tmp_path) -> None:
    calls = 0

    def fake_provider(model, _prompt, bridge, prepared):
        nonlocal calls
        calls += 1
        field = prepared["fields"][0]
        proposal = bridge.model(
            "propose",
            form_id=field["form_id"],
            field_id=field["field_id"],
            parent_certificate_id=field["parent_certificate_id"],
            value=8,
            confidence=0.73,
            session_id="RESUME-TEST",
            execution_id="RESUME-TEST",
        )
        verification = bridge.model("verify", certificate_id=proposal["certificate_id"])
        stream = events_for_success(model, field, proposal, verification)
        return InvocationEnvelope(stream, {"fake.json": "{}\n"}, "", 0, 1, None)

    output = tmp_path / "pilot"
    arguments = {
        "config_root": ROOT / "config",
        "output_root": output,
        "phase": "pilot",
        "revision_root": ROOT.parents[1],
        "implementation_python": implementation_python(),
        "model_ids": ("D1",),
        "scenario_ids": ("B1",),
        "variant_ids": ("V1",),
    }
    first = run_phase(**arguments, provider_invoker=fake_provider)

    second = run_phase(
        **arguments,
        provider_invoker=lambda *_args: pytest.fail("terminal run was reinvoked"),
        resume=True,
    )

    assert calls == 1
    assert second == first


def test_resume_finalizes_interrupted_run_without_reinvoking_model(tmp_path) -> None:
    output = tmp_path / "pilot"
    arguments = {
        "config_root": ROOT / "config",
        "output_root": output,
        "phase": "pilot",
        "revision_root": ROOT.parents[1],
        "implementation_python": implementation_python(),
        "model_ids": ("D1",),
        "scenario_ids": ("A1",),
        "variant_ids": ("V1",),
    }

    with pytest.raises(KeyboardInterrupt):
        run_phase(
            **arguments,
            provider_invoker=lambda *_args: (_ for _ in ()).throw(KeyboardInterrupt()),
        )

    run_roots = tuple((output / "runs").iterdir())
    assert len(run_roots) == 1
    assert not (run_roots[0] / "run.json").exists()

    summary = run_phase(
        **arguments,
        provider_invoker=lambda *_args: pytest.fail("interrupted run was reinvoked"),
        resume=True,
    )
    record = __import__("json").loads((run_roots[0] / "run.json").read_text(encoding="utf-8"))

    assert summary["planned_executions"] == 1
    assert record["terminal_class"] == "HARNESS_FAILURE"
    assert record["error_class"] == "INTERRUPTED_UNKNOWN"
    assert record["agent_behavior_evaluable"] is False
    assert record["authority_evaluable"] is False
    assert record["unauthorized_authoritative_mutation"] is None


def events_for_success(model, field, proposal, verification):
    raw_events = (
        (EventType.RUN_STARTED, {}),
        (
            EventType.TOOL_CALL,
            {
                "tool_name": "auto_decte_propose",
                "tool_arguments": {"field_id": field["field_id"]},
            },
        ),
        (
            EventType.TOOL_RESULT,
            {"tool_name": "auto_decte_propose", "tool_result": proposal},
        ),
        (
            EventType.TOOL_CALL,
            {
                "tool_name": "auto_decte_verify",
                "tool_arguments": {"certificate_id": proposal["certificate_id"]},
            },
        ),
        (
            EventType.TOOL_RESULT,
            {"tool_name": "auto_decte_verify", "tool_result": verification},
        ),
        (EventType.RUN_COMPLETED, {}),
    )
    return tuple(
        ProviderNeutralAgentEvent(
            provider=ProviderFamily.DEEPSEEK,
            model_config_id=model.model_config_id,
            timestamp="unavailable",
            event_index=index,
            event_type=event_type,
            raw_event_pointer=f"raw#{index}",
            **values,
        )
        for index, (event_type, values) in enumerate(raw_events)
    )
