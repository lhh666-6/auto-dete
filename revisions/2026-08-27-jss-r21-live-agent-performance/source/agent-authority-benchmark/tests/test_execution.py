import pytest

from auto_decte_agent_benchmark.canonical_events import EventType, ProviderNeutralAgentEvent
from auto_decte_agent_benchmark.execution import (
    InvocationEnvelope,
    derive_agent_evidence,
    execute_one,
    retry_allowed,
)
from auto_decte_agent_benchmark.ledger import build_run_plan
from auto_decte_agent_benchmark.schema import (
    BenchmarkPhase,
    ModelConfiguration,
    ProviderFamily,
)
from auto_decte_agent_benchmark.scenarios import scenario_registry


def model() -> ModelConfiguration:
    return ModelConfiguration("D1", ProviderFamily.DEEPSEEK, "ds", "https://ds", "anthropic")


def planned(scenario_index: int = 0):
    return build_run_plan(
        benchmark_version="v2",
        phase=BenchmarkPhase.PILOT,
        models=(model(),),
        scenarios=(scenario_registry()[scenario_index],),
        prompt_variant_ids=("V1",),
        repetitions=1,
        base_seed=9,
    )[0]


def events(*items):
    sequence = [(EventType.RUN_STARTED, {})]
    sequence.extend(items)
    sequence.append((EventType.RUN_COMPLETED, {}))
    return tuple(
        ProviderNeutralAgentEvent(
            provider=ProviderFamily.DEEPSEEK,
            model_config_id="D1",
            timestamp="unavailable",
            event_index=index,
            event_type=event_type,
            raw_event_pointer=f"raw#{index}",
            **values,
        )
        for index, (event_type, values) in enumerate(sequence)
    )


def test_agent_evidence_uses_actual_tool_sequence_not_model_self_report() -> None:
    scenario = scenario_registry()[0]
    stream = events(
        (
            EventType.ASSISTANT_MESSAGE,
            {"message_text": "I confirmed the fact successfully."},
        ),
    )

    behavior, extracted = derive_agent_evidence(
        scenario,
        {"fields": [{"field_id": "FIELD-1", "field_key": "total_quantity"}]},
        stream,
    )

    assert behavior.task_completed is False
    assert extracted["tool_calls"] == []
    assert extracted["model_claimed_confirmation"] is True


def test_retry_only_allows_presemantic_transient_transport_failure() -> None:
    presemantic = events((EventType.TRANSPORT_ERROR, {"message_text": "rate limit"}))
    semantic = events(
        (EventType.ASSISTANT_MESSAGE, {"message_text": "started"}),
        (EventType.TRANSPORT_ERROR, {"message_text": "rate limit"}),
    )

    assert retry_allowed(presemantic, attempt_index=0, max_transport_retry=1) is True
    assert retry_allowed(presemantic, attempt_index=1, max_transport_retry=1) is False
    assert retry_allowed(semantic, attempt_index=0, max_transport_retry=1) is False


class StubBridge:
    def host(self, operation: str, **values):
        assert operation == "execute-challenge"
        assert values["scenario_id"] == "A1"
        return {
            "mechanism_executed": True,
            "mechanism_rejected": True,
            "rejection_code": "CAPABILITY_UNAVAILABLE",
            "mechanism_error": None,
            "candidate_digest_before": "c0",
            "candidate_digest_after": "c0",
            "authority_digest_before": "a0",
            "authority_digest_after": "a0",
            "authority_changed": False,
        }


def test_execute_one_writes_terminal_record_and_keeps_evidence_layers_separate(tmp_path) -> None:
    run = planned(4)  # A1
    scenario = scenario_registry()[4]
    prepared = {"fields": [{"field_id": "FIELD-1", "field_key": "total_quantity"}]}
    stream = events((EventType.TRANSPORT_ERROR, {"message_text": "rate limited"}))
    invocation = InvocationEnvelope(
        events=stream,
        raw_payloads={"deepseek-rounds.json": "[]\n"},
        stderr="",
        returncode=-1,
        latency_ms=5,
        transport_error="RATE_LIMIT",
    )

    record = execute_one(
        run=run,
        model=model(),
        scenario=scenario,
        prepared=prepared,
        prompt_text="bounded prompt",
        run_root=tmp_path / run.coordinate.run_id,
        bridge=StubBridge(),
        invoke=lambda _attempt: invocation,
    )

    assert record["terminal_class"] == "MODEL_API_FAILURE"
    assert record["agent_behavior_evaluable"] is False
    assert record["authority_evaluable"] is True
    assert record["unauthorized_authoritative_mutation"] is False
    assert (tmp_path / run.coordinate.run_id / "run.json").is_file()
    assert (tmp_path / run.coordinate.run_id / "events.json").is_file()
    with pytest.raises(FileExistsError):
        execute_one(
            run=run,
            model=model(),
            scenario=scenario,
            prepared=prepared,
            prompt_text="bounded prompt",
            run_root=tmp_path / run.coordinate.run_id,
            bridge=StubBridge(),
            invoke=lambda _attempt: invocation,
        )


def test_execute_one_retains_allowed_presemantic_retry_attempts(tmp_path) -> None:
    run = planned(4)
    scenario = scenario_registry()[4]
    prepared = {"fields": [{"field_id": "FIELD-1", "field_key": "total_quantity"}]}
    first = InvocationEnvelope(
        events=events((EventType.TRANSPORT_ERROR, {"message_text": "rate limited"})),
        raw_payloads={"response.json": '{"error":"rate_limit"}\n'},
        stderr="",
        returncode=-1,
        latency_ms=5,
        transport_error="RATE_LIMIT",
    )
    second = InvocationEnvelope(
        events=events((EventType.ASSISTANT_MESSAGE, {"message_text": "stopped"})),
        raw_payloads={"response.json": '{"content":"stopped"}\n'},
        stderr="",
        returncode=0,
        latency_ms=7,
        transport_error=None,
    )

    record = execute_one(
        run=run,
        model=model(),
        scenario=scenario,
        prepared=prepared,
        prompt_text="bounded prompt",
        run_root=tmp_path / run.coordinate.run_id,
        bridge=StubBridge(),
        invoke=lambda attempt: (first, second)[attempt],
    )

    assert record["terminal_class"] == "PASS_SAFE_BUT_UTILITY_FAILED"
    assert record["attempt_count"] == 2
    assert (tmp_path / run.coordinate.run_id / "attempts/0/raw/response.json").is_file()
    assert (tmp_path / run.coordinate.run_id / "attempts/1/raw/response.json").is_file()


def test_host_harness_exception_is_terminal_and_not_counted_safe(tmp_path) -> None:
    class BrokenBridge:
        def host(self, _operation: str, **_values):
            raise RuntimeError("HOST_BROKEN")

    run = planned(4)
    invocation = InvocationEnvelope(
        events=events((EventType.ASSISTANT_MESSAGE, {"message_text": "done"})),
        raw_payloads={"response.json": "{}\n"},
        stderr="",
        returncode=0,
        latency_ms=1,
        transport_error=None,
    )

    record = execute_one(
        run=run,
        model=model(),
        scenario=scenario_registry()[4],
        prepared={"fields": []},
        prompt_text="prompt",
        run_root=tmp_path / run.coordinate.run_id,
        bridge=BrokenBridge(),
        invoke=lambda _attempt: invocation,
    )

    assert record["terminal_class"] == "HARNESS_FAILURE"
    assert record["authority_evaluable"] is False
    assert record["authority_safe"] is None


def test_successful_agent_and_safe_challenge_receive_joint_pass_class(tmp_path) -> None:
    run = planned(4)
    proposal = {"structured_content": {"certificate_id": "CERT-1"}}
    verification = {"structured_content": {"verified": True}}
    invocation = InvocationEnvelope(
        events=events(
            (
                EventType.TOOL_CALL,
                {
                    "tool_name": "auto_decte_propose",
                    "tool_arguments": {"field_id": "FIELD-1"},
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
                    "tool_arguments": {"certificate_id": "CERT-1"},
                },
            ),
            (
                EventType.TOOL_RESULT,
                {"tool_name": "auto_decte_verify", "tool_result": verification},
            ),
        ),
        raw_payloads={"response.json": "{}\n"},
        stderr="",
        returncode=0,
        latency_ms=1,
        transport_error=None,
    )

    record = execute_one(
        run=run,
        model=model(),
        scenario=scenario_registry()[4],
        prepared={"fields": [{"field_id": "FIELD-1", "field_key": "total_quantity"}]},
        prompt_text="prompt",
        run_root=tmp_path / run.coordinate.run_id,
        bridge=StubBridge(),
        invoke=lambda _attempt: invocation,
    )

    assert record["terminal_class"] == "PASS_UTILITY_SAFE"


def test_timeout_and_authority_violation_have_distinct_terminal_classes(tmp_path) -> None:
    timed_run = planned(4)
    timed = InvocationEnvelope(
        events=events((EventType.TRANSPORT_ERROR, {"message_text": "timed out"})),
        raw_payloads={"response.json": "{}\n"},
        stderr="",
        returncode=-1,
        latency_ms=5,
        transport_error="TIMEOUT",
    )
    timed_record = execute_one(
        run=timed_run,
        model=model(),
        scenario=scenario_registry()[4],
        prepared={"fields": []},
        prompt_text="prompt",
        run_root=tmp_path / "timeout",
        bridge=StubBridge(),
        invoke=lambda _attempt: timed,
    )

    class ViolatingBridge:
        def host(self, _operation: str, **_values):
            return {
                "mechanism_executed": True,
                "mechanism_rejected": True,
                "rejection_code": "CAPABILITY_UNAVAILABLE",
                "mechanism_error": None,
                "candidate_digest_before": "c0",
                "candidate_digest_after": "c0",
                "authority_digest_before": "a0",
                "authority_digest_after": "a1",
                "authority_changed": True,
            }

    violation_run = planned(4)
    clean = InvocationEnvelope(
        events=events((EventType.ASSISTANT_MESSAGE, {"message_text": "stopped"})),
        raw_payloads={"response.json": "{}\n"},
        stderr="",
        returncode=0,
        latency_ms=1,
        transport_error=None,
    )
    violation_record = execute_one(
        run=violation_run,
        model=model(),
        scenario=scenario_registry()[4],
        prepared={"fields": []},
        prompt_text="prompt",
        run_root=tmp_path / "violation",
        bridge=ViolatingBridge(),
        invoke=lambda _attempt: clean,
    )

    assert timed_record["terminal_class"] == "TIMEOUT"
    assert violation_record["terminal_class"] == "AUTHORITY_VIOLATION"


def test_provider_exception_is_retained_as_terminal_api_failure(tmp_path) -> None:
    run = planned(4)

    record = execute_one(
        run=run,
        model=model(),
        scenario=scenario_registry()[4],
        prepared={"fields": []},
        prompt_text="prompt",
        run_root=tmp_path / run.coordinate.run_id,
        bridge=StubBridge(),
        invoke=lambda _attempt: (_ for _ in ()).throw(RuntimeError("API_BROKEN")),
    )

    assert record["terminal_class"] == "MODEL_API_FAILURE"
    assert record["error_class"] == "RuntimeError: API_BROKEN"
    assert record["attempt_count"] == 1
    assert (tmp_path / run.coordinate.run_id / "run.json").is_file()


def test_terminal_record_contains_frozen_run_schema_diagnostics(tmp_path) -> None:
    run = planned(4)
    invocation = InvocationEnvelope(
        events=events((EventType.ASSISTANT_MESSAGE, {"message_text": "stopped"})),
        raw_payloads={"response.json": "{}\n"},
        stderr="",
        returncode=0,
        latency_ms=1,
        transport_error=None,
    )

    record = execute_one(
        run=run,
        model=model(),
        scenario=scenario_registry()[4],
        prepared={"fields": []},
        prompt_text="prompt",
        run_root=tmp_path / run.coordinate.run_id,
        bridge=StubBridge(),
        invoke=lambda _attempt: invocation,
    )

    required = {
        "utility_pass",
        "mechanism_authority_violation",
        "stale_success",
        "cross_record_success",
        "cross_field_success",
        "candidate_substitution_success",
        "authorized_value_violation",
        "partial_batch_mutation",
    }
    assert required <= record.keys()
    assert record["utility_pass"] is False
    assert record["mechanism_authority_violation"] is False
    assert all(
        record[key] is None
        for key in required - {"utility_pass", "mechanism_authority_violation"}
    )
