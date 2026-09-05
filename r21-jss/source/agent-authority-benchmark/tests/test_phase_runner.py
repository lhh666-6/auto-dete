import os
from pathlib import Path
import sys
import json

import pytest

from auto_decte_agent_benchmark.canonical_events import EventType, ProviderNeutralAgentEvent
from auto_decte_agent_benchmark.execution import InvocationEnvelope
from auto_decte_agent_benchmark.bridge_client import BridgeClient
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
        metadata = prepared["required_proposal_metadata_by_field"][field["field_key"]]
        proposal = bridge.model(
            "propose",
            form_id=field["form_id"],
            field_id=field["field_id"],
            parent_certificate_id=field["parent_certificate_id"],
            value=8,
            confidence=0.73,
            session_id=metadata["session_id"],
            execution_id=metadata["execution_id"],
        )
        verification = bridge.model("verify", certificate_id=proposal["certificate_id"])
        raw_events = (
            (EventType.RUN_STARTED, {}),
            (
                EventType.TOOL_CALL,
                {
                    "tool_name": "auto_decte_propose",
                    "tool_arguments": {
                        "form_id": field["form_id"],
                        "field_id": field["field_id"],
                        "parent_certificate_id": field["parent_certificate_id"],
                        "value": 8,
                        "session_id": metadata["session_id"],
                        "execution_id": metadata["execution_id"],
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
    assert (output / "frozen-config/resource-policy.json").read_bytes() == (
        ROOT / "config/resource-policy.json"
    ).read_bytes()
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


def test_scenarios_are_prepared_just_in_time_not_cached_before_provider_invocation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A long pause must not age later runs' one-hour certificates in a cache."""
    events: list[str] = []
    original_host = BridgeClient.host

    def recording_host(self, operation, **values):
        if operation == "prepare-scenario":
            events.append(f"prepare:{values['scenario_id']}")
        return original_host(self, operation, **values)

    def interrupt_on_first_invocation(_model, _prompt, _bridge, prepared):
        events.append(f"invoke:{prepared['scenario_id']}")
        raise KeyboardInterrupt

    monkeypatch.setattr(BridgeClient, "host", recording_host)
    with pytest.raises(KeyboardInterrupt):
        run_phase(
            config_root=ROOT / "config",
            output_root=tmp_path / "pilot",
            phase="pilot",
            revision_root=ROOT.parents[1],
            implementation_python=implementation_python(),
            model_ids=("D1",),
            scenario_ids=("B1", "B2"),
            variant_ids=("V1",),
            provider_invoker=interrupt_on_first_invocation,
        )

    assert events == ["prepare:B1", "invoke:B1"]


def test_checkpoint_mode_adds_one_terminal_run_per_resume_without_normalizing(
    tmp_path: Path,
) -> None:
    calls: list[str] = []

    def text_only_provider(model, _prompt, _bridge, _prepared):
        calls.append(model.model_config_id)
        events = (
            ProviderNeutralAgentEvent(
                provider=model.provider,
                model_config_id=model.model_config_id,
                timestamp="unavailable",
                event_index=0,
                event_type=EventType.RUN_STARTED,
                raw_event_pointer="raw#0",
            ),
            ProviderNeutralAgentEvent(
                provider=model.provider,
                model_config_id=model.model_config_id,
                timestamp="unavailable",
                event_index=1,
                event_type=EventType.ASSISTANT_MESSAGE,
                raw_event_pointer="raw#1",
                message_text="No tool call.",
            ),
            ProviderNeutralAgentEvent(
                provider=model.provider,
                model_config_id=model.model_config_id,
                timestamp="unavailable",
                event_index=2,
                event_type=EventType.RUN_COMPLETED,
                raw_event_pointer="raw#2",
            ),
        )
        return InvocationEnvelope(events, {"fake.json": "{}\n"}, "", 0, 1, None)

    output = tmp_path / "pilot"
    arguments = {
        "config_root": ROOT / "config",
        "output_root": output,
        "phase": "pilot",
        "revision_root": ROOT.parents[1],
        "implementation_python": implementation_python(),
        "provider_invoker": text_only_provider,
        "max_new_invocations": 1,
    }

    first = run_phase(**arguments)

    assert first == {
        "schema_version": "agent-authority-phase-checkpoint.v2",
        "phase": "pilot",
        "status": "INCOMPLETE",
        "planned_executions": 112,
        "terminal_executions": 1,
        "remaining_executions": 111,
        "new_invocations": 1,
    }
    assert calls == ["G1"]
    assert len((output / "planned-runs.jsonl").read_text(encoding="utf-8").splitlines()) == 112
    assert len(tuple((output / "runs").glob("*/run.json"))) == 1
    assert (output / "checkpoints/0001.json").is_file()
    assert not (output / "normalized").exists()
    assert not (output / "pilot-model-qualification.json").exists()
    assert not (output / "manifest.json").exists()

    second = run_phase(**arguments, resume=True)

    assert second["terminal_executions"] == 2
    assert second["remaining_executions"] == 110
    assert second["new_invocations"] == 1
    assert calls == ["G1", "G1"]
    assert len(tuple((output / "runs").glob("*/run.json"))) == 2
    assert (output / "checkpoints/0002.json").is_file()
    assert not (output / "normalized").exists()
    assert not (output / "manifest.json").exists()


def test_phase_uses_frozen_zero_retry_policy_for_quota_limited_execution(
    tmp_path: Path,
) -> None:
    config = tmp_path / "config"
    config.mkdir()
    for name in ("pilot.models.json", "pilot.matrix.json", "resource-policy.json"):
        (config / name).write_bytes((ROOT / "config" / name).read_bytes())
    retry_policy = json.loads((ROOT / "config/retry-policy.json").read_text(encoding="utf-8"))
    retry_policy["max_transport_retry"] = 0
    (config / "retry-policy.json").write_text(
        json.dumps(retry_policy, indent=2) + "\n",
        encoding="utf-8",
    )
    calls = 0

    def failing_provider(model, *_args):
        nonlocal calls
        calls += 1
        events = (
            ProviderNeutralAgentEvent(
                provider=model.provider,
                model_config_id=model.model_config_id,
                timestamp="unavailable",
                event_index=0,
                event_type=EventType.RUN_STARTED,
                raw_event_pointer="raw#0",
            ),
            ProviderNeutralAgentEvent(
                provider=model.provider,
                model_config_id=model.model_config_id,
                timestamp="unavailable",
                event_index=1,
                event_type=EventType.TRANSPORT_ERROR,
                raw_event_pointer="raw#1",
                message_text="quota-safe synthetic transport failure",
            ),
            ProviderNeutralAgentEvent(
                provider=model.provider,
                model_config_id=model.model_config_id,
                timestamp="unavailable",
                event_index=2,
                event_type=EventType.RUN_COMPLETED,
                raw_event_pointer="raw#2",
            ),
        )
        return InvocationEnvelope(
            events,
            {"fake.json": "{}\n"},
            "quota-safe synthetic transport failure",
            -1,
            1,
            "quota-safe synthetic transport failure",
        )

    result = run_phase(
        config_root=config,
        output_root=tmp_path / "pilot",
        phase="pilot",
        revision_root=ROOT.parents[1],
        implementation_python=implementation_python(),
        model_ids=("G1",),
        scenario_ids=("B1",),
        variant_ids=("V1",),
        provider_invoker=failing_provider,
    )

    assert calls == 1
    assert result["runtime_failures"] == 1


def test_complete_locked_final_emits_paper_reporting_bundle(tmp_path) -> None:
    config = tmp_path / "config"
    config.mkdir()
    pilot_models = json.loads((ROOT / "config/pilot.models.json").read_text(encoding="utf-8"))
    pilot_models["models"] = pilot_models["models"][:1]
    (config / "final.models.json").write_text(
        json.dumps(pilot_models, indent=2) + "\n",
        encoding="utf-8",
    )
    matrix = json.loads((ROOT / "config/pilot.matrix.json").read_text(encoding="utf-8"))
    matrix.update({"phase": "final", "prompt_variant_ids": ["V1"], "repetitions": 1})
    (config / "final.matrix.json").write_text(
        json.dumps(matrix, indent=2) + "\n",
        encoding="utf-8",
    )
    (config / "retry-policy.json").write_bytes((ROOT / "config/retry-policy.json").read_bytes())
    (config / "resource-policy.json").write_bytes(
        (ROOT / "config/resource-policy.json").read_bytes()
    )

    def text_only_provider(model, _prompt, _bridge, _prepared):
        events = (
            ProviderNeutralAgentEvent(
                provider=model.provider,
                model_config_id=model.model_config_id,
                timestamp="unavailable",
                event_index=0,
                event_type=EventType.RUN_STARTED,
                raw_event_pointer="raw#0",
            ),
            ProviderNeutralAgentEvent(
                provider=model.provider,
                model_config_id=model.model_config_id,
                timestamp="unavailable",
                event_index=1,
                event_type=EventType.ASSISTANT_MESSAGE,
                raw_event_pointer="raw#1",
                message_text="No tool call.",
            ),
            ProviderNeutralAgentEvent(
                provider=model.provider,
                model_config_id=model.model_config_id,
                timestamp="unavailable",
                event_index=2,
                event_type=EventType.RUN_COMPLETED,
                raw_event_pointer="raw#2",
            ),
        )
        return InvocationEnvelope(events, {"fake.json": "{}\n"}, "", 0, 1, None)

    output = tmp_path / "final"
    run_phase(
        config_root=config,
        output_root=output,
        phase="final",
        revision_root=ROOT.parents[1],
        implementation_python=implementation_python(),
        provider_invoker=text_only_provider,
    )

    reporting = output / "normalized/paper-reporting"
    assert (reporting / "agent_behavior_table.tex").is_file()
    assert (reporting / "admission_mechanism_table.tex").is_file()
    assert (reporting / "behavior_vs_authority.svg").is_file()
    assert (reporting / "behavior_vs_authority.pdf").is_file()
    assert (reporting / "behavior_vs_authority.png").is_file()


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
