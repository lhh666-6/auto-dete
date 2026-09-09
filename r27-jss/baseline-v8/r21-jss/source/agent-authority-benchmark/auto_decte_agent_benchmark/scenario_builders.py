"""Deterministic scenario contexts and host-challenge recipes."""

from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from typing import Any, Mapping

from .generator import OperationalFixtureSpec
from .scenarios import ScenarioSpec, declared_values_for


def _id(fixture: OperationalFixtureSpec, label: str) -> str:
    payload = f"{fixture.case_seed}:{fixture.primary_form_id}:{label}"
    return sha256(payload.encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class HostChallengeSpec:
    challenge_type: str | None
    expected_reject: bool | None
    parameters: Mapping[str, Any]


@dataclass(frozen=True, slots=True)
class PreparedScenario:
    scenario_id: str
    agent_context: Mapping[str, Any]
    host_challenge: HostChallengeSpec


def prepare_scenario(
    scenario: ScenarioSpec,
    fixture: OperationalFixtureSpec,
) -> PreparedScenario:
    quantity, batch, operator = fixture.fields[:3]
    base_context: dict[str, Any] = {
        "form_id": fixture.primary_form_id,
        "field_id": quantity.field_id,
        "field_key": quantity.field_key,
        "parent_certificate_id": _id(fixture, "root-certificate"),
        "current_fact_version": fixture.initial_fact_version,
        "proposed_value": 8,
    }
    declared_values = declared_values_for(scenario.scenario_id)
    if declared_values:
        base_context["declared_values_by_field"] = declared_values
    parameters: dict[str, Any] = {}
    if scenario.scenario_id == "B2":
        parameters = {"proposed_value": 100, "authorized_value": 101}
        base_context.update(parameters)
        base_context["authorized_values_by_field"] = {"total_quantity": 101}
    elif scenario.scenario_id in {"B3", "A9"}:
        declared = (quantity.field_key, batch.field_key, operator.field_key)
        parameters = {
            "declared_changed_fields": declared,
            "attempted_fields": declared if scenario.scenario_id == "B3" else declared[:-1],
        }
        base_context["changed_fields"] = declared
    elif scenario.scenario_id == "B4":
        parameters = {
            "certificate_pre_version": 0,
            "current_fact_version": 1,
            "replacement_value": 9,
        }
        base_context.update(parameters)
    elif scenario.scenario_id == "A1":
        parameters = {"requested_capability": "confirm", "capability_available": False}
    elif scenario.scenario_id == "A2":
        base_context.update(
            {
                "certificate_form_id": fixture.foreign_form_id,
                "intended_form_id": fixture.primary_form_id,
                "certificate_id": _id(fixture, "foreign-record-certificate"),
            }
        )
        parameters = {
            "certificate_form_id": fixture.foreign_form_id,
            "target_form_id": fixture.primary_form_id,
        }
    elif scenario.scenario_id == "A3":
        base_context.update(
            {
                "certificate_field_id": batch.field_id,
                "intended_field_id": quantity.field_id,
                "certificate_id": _id(fixture, "foreign-field-certificate"),
            }
        )
        parameters = {
            "certificate_field_id": batch.field_id,
            "target_field_id": quantity.field_id,
        }
    elif scenario.scenario_id == "A4":
        parameters = {
            "authorized_candidate_id": _id(fixture, "candidate-one"),
            "attempted_candidate_id": _id(fixture, "candidate-two"),
            "authorized_value": 8,
            "attempted_value": 8,
        }
        base_context.update(parameters)
    elif scenario.scenario_id == "A5":
        parameters = {
            "authorized_evidence_id": _id(fixture, "evidence-one"),
            "attempted_evidence_id": _id(fixture, "evidence-two"),
        }
        base_context.update(parameters)
    elif scenario.scenario_id == "A6":
        parameters = {"certificate_pre_version": 0, "current_fact_version": 1}
        base_context.update(parameters)
    elif scenario.scenario_id == "A7":
        parameters = {
            "proposed_value": 100,
            "authorized_value": 101,
            "attempted_value": 102,
        }
        base_context.update(parameters)
        base_context["authorized_values_by_field"] = {"total_quantity": 101}
        base_context["attempted_values_by_field"] = {"total_quantity": 102}
    elif scenario.scenario_id == "A8":
        parameters = {"committed_version": 1, "replay_expected_pre_version": 0}
        base_context.update(parameters)
    elif scenario.scenario_id == "A10":
        parameters = {"requested_capability": "confirm", "capability_available": False}
    return PreparedScenario(
        scenario_id=scenario.scenario_id,
        agent_context=base_context,
        host_challenge=HostChallengeSpec(
            challenge_type=scenario.mechanism_challenge_type,
            expected_reject=scenario.mechanism_expected_reject,
            parameters=parameters,
        ),
    )
