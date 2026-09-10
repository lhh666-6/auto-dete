"""Independent projection of persisted authority rows into the batch Alloy model.

This module is test infrastructure, not an application adapter.  It reads the
repository's public query surface, emits a canonical relational record, and
then constrains an exact Alloy instance.  The generated model therefore does
not call the production admission validator or reimplement its accept/reject
decision.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from collections.abc import Iterable, Mapping, Sequence
from copy import deepcopy
from dataclasses import dataclass, replace
from enum import StrEnum
from pathlib import Path
from typing import Any

from app.domain.authority import canonical_json

SCHEMA_VERSION = "auto-decte-alloy-projection-v1"


class AlloyOutcome(StrEnum):
    SAT = "SAT"
    UNSAT = "UNSAT"


class RejectionProjectionError(ValueError):
    """The concrete rejection is not a zero-authority-write stutter."""


@dataclass(frozen=True, slots=True)
class AuthoritySnapshot:
    """Canonical raw database relations used to prove rejection stuttering."""

    payload: Mapping[str, Any]

    def canonical_text(self) -> str:
        return json.dumps(
            self.payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )

    def with_added_transition(self, transition_id: str) -> AuthoritySnapshot:
        payload = deepcopy(self.payload)
        payload["transition_ids"].append(transition_id)
        return replace(self, payload=payload)


@dataclass(frozen=True, slots=True)
class AdmissionProjection:
    """Canonical concrete relation plus an optional deliberate mapping mutant."""

    payload: Mapping[str, Any]
    mutation: str | None = None

    def with_mutation(self, mutation: str) -> AdmissionProjection:
        payload = deepcopy(self.payload)
        items = payload["items"]
        if not items:
            raise ValueError("mapping mutation requires at least one item")
        item = items[0]
        certificates = {row["certificate_id"]: row for row in payload["certificates"]}
        authorizations = {row["authorization_id"]: row for row in payload["authorizations"]}
        transitions = {row["transition_id"]: row for row in payload["transitions"]}
        certificate = certificates[item["certificate_id"]]
        authorization = authorizations[item["authorization_id"]]
        transition = transitions[item["transition_id"]]

        if mutation == "item_field_binding":
            alternatives = [
                field for field in payload["declared_fields"] if field != item["field_key"]
            ]
            certificate["field_key"] = alternatives[0] if alternatives else "__rogue_field__"
        elif mutation == "evidence_identity_binding":
            alternatives = [
                row["evidence_id"]
                for row in payload["evidence"]
                if row["evidence_id"] != item["evidence_id"]
            ]
            if not alternatives:
                raise ValueError("evidence mutation requires two evidence rows")
            item["evidence_id"] = alternatives[0]
        elif mutation == "version_binding":
            item["expected_version"] = payload["post"]["version"]
        elif mutation == "freshness_binding":
            wrong_version = payload["post"]["version"]
            item["expected_version"] = wrong_version
            certificate["expected_version"] = wrong_version
        elif mutation == "authorization_certificate_binding":
            alternatives = [
                cert_id for cert_id in certificates if cert_id != item["certificate_id"]
            ]
            if not alternatives:
                raise ValueError("authorization-certificate mutation requires two certificates")
            authorization["certificate_id"] = alternatives[0]
        elif mutation == "principal_binding":
            authorization["principal"] = "__unauthorized_principal__"
        elif mutation == "authorization_value_binding":
            item["authorized_value"] = canonical_json("__unauthorized_value__")
        elif mutation == "transition_bijection":
            payload["post"]["transition_ids"].remove(item["transition_id"])
        elif mutation == "certificate_preexists":
            payload["pre"]["certificate_ids"].remove(item["certificate_id"])
        elif mutation == "evidence_preexists":
            payload["pre"]["evidence_ids"].remove(item["evidence_id"])
        elif mutation == "committed_value_effect":
            payload["post"]["values"][item["field_key"]] = canonical_json(
                "__wrong_committed_value__"
            )
        elif mutation == "committed_source_effect":
            alternatives = [
                other["transition_id"]
                for other in items
                if other["transition_id"] != item["transition_id"]
            ]
            if not alternatives:
                raise ValueError("source mutation requires a multi-item batch")
            payload["post"]["fact_sources"][item["field_key"]] = alternatives[0]
        elif mutation == "transition_field_binding":
            alternatives = [
                field for field in payload["declared_fields"] if field != item["field_key"]
            ]
            transition["field_key"] = alternatives[0] if alternatives else "__rogue_field__"
        elif mutation == "transition_evidence_binding":
            alternatives = [
                row["evidence_id"]
                for row in payload["evidence"]
                if row["evidence_id"] != item["evidence_id"]
            ]
            if not alternatives:
                raise ValueError("evidence mutation requires two evidence rows")
            transition["evidence_id"] = alternatives[0]
        elif mutation == "transition_version_binding":
            transition["from_version"] = transition["to_version"]
        elif mutation == "transition_value_binding":
            transition["value"] = canonical_json("__wrong_transition_value__")
        elif mutation == "transition_producer_binding":
            transition["producer"] = ["__wrong_producer__", "0"]
        elif mutation == "transition_certificate_binding":
            alternatives = [
                cert_id for cert_id in certificates if cert_id != item["certificate_id"]
            ]
            if not alternatives:
                raise ValueError("certificate mutation requires two certificates")
            transition["certificate_id"] = alternatives[0]
        elif mutation == "transition_authorization_binding":
            alternatives = [
                auth_id for auth_id in authorizations if auth_id != item["authorization_id"]
            ]
            if not alternatives:
                raise ValueError("authorization mutation requires two bindings")
            transition["authorization_id"] = alternatives[0]
        elif mutation == "initial_snapshot_domain":
            if payload["pre"]["values"]:
                raise ValueError("initial snapshot mutation requires an initial event")
            payload["items"] = payload["items"][:-1]
        else:
            raise ValueError(f"unknown mapping mutation: {mutation}")
        return replace(self, payload=payload, mutation=mutation)

    def canonical_text(self) -> str:
        return json.dumps(
            self.payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=False,
        )


def capture_authority_snapshot(repository: Any, *, form_id: str) -> AuthoritySnapshot:
    """Capture every application/authority identity relevant to a rejection."""

    form = repository.get_form(form_id)
    if form is None:
        raise ValueError(f"unknown form {form_id}")
    versions = sorted(repository.list_record_versions(form_id), key=lambda row: row.version)
    certificates = sorted(
        repository.list_certificates_for_form(form_id),
        key=lambda row: row.certificate_id,
    )
    decisions = sorted(
        repository.list_decisions_for_form(form_id),
        key=lambda row: row.decision_id,
    )
    bindings = sorted(
        repository.list_authorization_bindings_for_form(form_id),
        key=lambda row: row.binding_id,
    )
    transitions = sorted(
        (
            transition
            for version in range(1, form.current_record_version + 1)
            for transition in repository.list_transitions_for_version(form_id, version)
        ),
        key=lambda row: row.transition_id,
    )
    evidence = sorted(repository.list_evidence(form_id), key=lambda row: row.file_id)
    payload = {
        "schema": SCHEMA_VERSION,
        "form_id": form_id,
        "current_version": form.current_record_version,
        "review_status": str(form.review_status),
        "versions": [
            {
                "record_id": row.record_id,
                "version": row.version,
                "values": {key: canonical_json(value) for key, value in sorted(row.values.items())},
                "fact_sources": dict(sorted(row.fact_sources.items())),
            }
            for row in versions
        ],
        "certificate_ids": [row.certificate_id for row in certificates],
        "decision_ids": [row.decision_id for row in decisions],
        "authorization_ids": [row.binding_id for row in bindings],
        "transition_ids": [row.transition_id for row in transitions],
        "evidence_ids": [row.file_id for row in evidence],
    }
    return AuthoritySnapshot(payload=payload)


def project_rejected_admission(
    repository: Any,
    *,
    form_id: str,
    declared_fields: Sequence[str],
    expected_version: int,
    attempted_values: Mapping[str, Any],
    certificate_ids_by_field: Mapping[str, str],
    principal: str,
    before: AuthoritySnapshot,
    after: AuthoritySnapshot,
) -> AdmissionProjection:
    """Prove a rejected call stuttered and serialize its invalid attempt.

    Attempted authorization/transition atoms are not persisted authority
    objects.  The projection records why the attempted item relation cannot
    satisfy the Full contract.
    """

    if before.canonical_text() != after.canonical_text():
        raise RejectionProjectionError(
            "rejected admission changed authoritative database relations"
        )
    if set(attempted_values) != set(certificate_ids_by_field):
        raise RejectionProjectionError("attempted value and certificate field domains differ")

    certificates = sorted(
        repository.list_certificates_for_form(form_id),
        key=lambda row: row.certificate_id,
    )
    certificate_by_id = {certificate.certificate_id: certificate for certificate in certificates}
    evidence_rows: dict[str, Any] = {}
    certificate_evidence: dict[str, str] = {}
    for certificate in certificates:
        evidence_id = repository.get_certificate_evidence_file_id(certificate.certificate_id)
        if evidence_id is None:
            raise RejectionProjectionError(
                f"certificate {certificate.certificate_id} lacks evidence"
            )
        evidence = repository.get_evidence(evidence_id)
        if evidence is None:
            raise RejectionProjectionError(f"missing evidence {evidence_id}")
        certificate_evidence[certificate.certificate_id] = evidence_id
        evidence_rows[evidence_id] = evidence

    persisted_decisions = sorted(
        repository.list_decisions_for_form(form_id),
        key=lambda row: row.decision_id,
    )
    decision_by_id = {decision.decision_id: decision for decision in persisted_decisions}
    persisted_bindings = sorted(
        repository.list_authorization_bindings_for_form(form_id),
        key=lambda row: row.binding_id,
    )
    binding_by_decision = {binding.decision_id: binding for binding in persisted_bindings}
    persisted_transitions = sorted(
        (
            transition
            for version in range(1, before.payload["current_version"] + 1)
            for transition in repository.list_transitions_for_version(form_id, version)
        ),
        key=lambda row: row.transition_id,
    )

    violations: list[str] = []
    if expected_version != before.payload["current_version"]:
        violations.append("freshness_binding")
    items: list[dict[str, Any]] = []
    attempt_authorizations: list[dict[str, Any]] = []
    attempt_transitions: list[dict[str, Any]] = []
    for field_key in sorted(attempted_values):
        certificate_id = certificate_ids_by_field[field_key]
        certificate = certificate_by_id.get(certificate_id)
        if certificate is None:
            violations.append(f"missing_certificate:{field_key}")
            continue
        if certificate.target_record_id != form_id:
            violations.append(f"record_binding:{field_key}")
        if certificate.field_key != field_key:
            violations.append(f"field_binding:{field_key}")
        if certificate.expected_fact_version != expected_version:
            violations.append(f"version_binding:{field_key}")
        authorization_id = f"ATTEMPT-AUTH:{field_key}"
        transition_id = f"ATTEMPT-TRANSITION:{field_key}"
        authorized_value = canonical_json(attempted_values[field_key])
        evidence_id = certificate_evidence[certificate_id]
        items.append(
            {
                "field_key": field_key,
                "certificate_id": certificate_id,
                "authorization_id": authorization_id,
                "evidence_id": evidence_id,
                "expected_version": expected_version,
                "authorized_value": authorized_value,
                "transition_id": transition_id,
            }
        )
        attempt_authorizations.append(
            {
                "authorization_id": authorization_id,
                "decision_id": f"ATTEMPT-DECISION:{field_key}",
                "certificate_id": certificate_id,
                "authorized_value": authorized_value,
                "principal": principal,
            }
        )
        attempt_transitions.append(
            {
                "transition_id": transition_id,
                "record_id": form_id,
                "field_key": field_key,
                "evidence_id": evidence_id,
                "from_version": expected_version,
                "to_version": expected_version + 1,
                "value": authorized_value,
                "producer": [
                    certificate.producer_id,
                    certificate.producer_version,
                ],
                "certificate_id": certificate_id,
                "authorization_id": authorization_id,
            }
        )
    if not violations:
        raise RejectionProjectionError("rejected attempt has no mapped Full-contract violation")

    versions = repository.list_record_versions(form_id)
    current_record = versions[-1] if versions else None
    state_payload = _record_payload(current_record)
    state_payload.update(
        {
            "transition_ids": [transition.transition_id for transition in persisted_transitions],
            "certificate_ids": [certificate.certificate_id for certificate in certificates],
            "authorization_ids": [binding.binding_id for binding in persisted_bindings],
            "evidence_ids": sorted(evidence_rows),
        }
    )
    persisted_authorizations = [
        {
            "authorization_id": binding.binding_id,
            "decision_id": binding.decision_id,
            "certificate_id": binding.certificate_id,
            "authorized_value": binding.authorized_value_payload,
            "principal": decision_by_id[binding.decision_id].reviewer_id,
        }
        for binding in persisted_bindings
    ]
    transition_rows = [
        {
            "transition_id": transition.transition_id,
            "record_id": transition.record_id,
            "field_key": transition.field_key,
            "evidence_id": certificate_evidence[transition.certificate_id],
            "from_version": transition.created_version - 1,
            "to_version": transition.created_version,
            "value": transition.value_payload,
            "producer": [
                transition.producer_id,
                transition.producer_version,
            ],
            "certificate_id": transition.certificate_id,
            "authorization_id": binding_by_decision[transition.decision_id].binding_id,
        }
        for transition in persisted_transitions
    ]
    payload = {
        "schema": SCHEMA_VERSION,
        "outcome": "rejected",
        "record_id": form_id,
        "declared_fields": sorted(set(declared_fields)),
        "principal": principal,
        "expected_version": expected_version,
        "current_version": before.payload["current_version"],
        "formal_max_version": max(
            before.payload["current_version"] + 1,
            expected_version + 1,
        ),
        "violations": sorted(violations),
        "items": items,
        "pre": deepcopy(state_payload),
        "post": deepcopy(state_payload),
        "evidence": [
            {
                "evidence_id": evidence_id,
                "record_id": evidence.form_id,
                "content": evidence.sha256,
                "locator": next(
                    certificate.evidence_locator
                    for certificate in certificates
                    if certificate_evidence[certificate.certificate_id] == evidence_id
                ),
            }
            for evidence_id, evidence in sorted(evidence_rows.items())
        ],
        "certificates": [
            {
                "certificate_id": certificate.certificate_id,
                "candidate_id": certificate.candidate_id,
                "record_id": certificate.target_record_id,
                "field_key": certificate.field_key,
                "evidence_id": certificate_evidence[certificate.certificate_id],
                "expected_version": certificate.expected_fact_version,
                "value": certificate.value_payload,
                "producer": [
                    certificate.producer_id,
                    certificate.producer_version,
                ],
            }
            for certificate in certificates
        ],
        "decisions": [
            {
                "decision_id": decision.decision_id,
                "candidate_id": decision.candidate_id,
                "field_key": decision.field_key,
                "principal": decision.reviewer_id,
            }
            for decision in persisted_decisions
        ],
        "authorizations": persisted_authorizations + attempt_authorizations,
        "transitions": transition_rows + attempt_transitions,
        "rejection_snapshot": before.payload,
    }
    return AdmissionProjection(payload=payload)


def _record_payload(record: Any | None) -> dict[str, Any]:
    if record is None:
        return {"version": 0, "values": {}, "fact_sources": {}}
    return {
        "version": record.version,
        "values": {key: canonical_json(value) for key, value in sorted(record.values.items())},
        "fact_sources": dict(sorted(record.fact_sources.items())),
    }


def project_committed_admission(
    repository: Any,
    *,
    form_id: str,
    version: int,
    declared_fields: Sequence[str],
) -> AdmissionProjection:
    """Read one committed successor and its raw authority relations.

    Candidate certificates and evidence already exist before review.  Current
    decisions, bindings, and transitions are the objects appended by the
    selected atomic admission.
    """

    if version < 1:
        raise ValueError("a committed admission version must be positive")
    field_domain = tuple(sorted(set(declared_fields)))
    if not field_domain:
        raise ValueError("declared_fields must be non-empty")

    versions = {record.version: record for record in repository.list_record_versions(form_id)}
    post_record = versions.get(version)
    if post_record is None:
        raise ValueError(f"missing committed version {version} for {form_id}")
    pre_record = versions.get(version - 1)

    transitions = sorted(
        (
            transition
            for created in range(1, version + 1)
            for transition in repository.list_transitions_for_version(form_id, created)
        ),
        key=lambda transition: (
            transition.created_version,
            transition.field_key,
            transition.transition_id,
        ),
    )
    current_transitions = [
        transition for transition in transitions if transition.created_version == version
    ]
    if not current_transitions:
        raise ValueError("committed successor has no persisted transitions")

    certificates = sorted(
        repository.list_certificates_for_form(form_id),
        key=lambda certificate: certificate.certificate_id,
    )
    certificate_by_id = {certificate.certificate_id: certificate for certificate in certificates}
    decisions = sorted(
        repository.list_decisions_for_form(form_id),
        key=lambda decision: decision.decision_id,
    )
    decision_by_id = {decision.decision_id: decision for decision in decisions}
    bindings = sorted(
        repository.list_authorization_bindings_for_form(form_id),
        key=lambda binding: binding.binding_id,
    )
    binding_by_decision = {binding.decision_id: binding for binding in bindings}

    evidence_rows: dict[str, Any] = {}
    certificate_evidence: dict[str, str] = {}
    for certificate in certificates:
        evidence_id = repository.get_certificate_evidence_file_id(certificate.certificate_id)
        if evidence_id is None:
            raise ValueError(f"certificate {certificate.certificate_id} has no evidence row")
        evidence = repository.get_evidence(evidence_id)
        if evidence is None:
            raise ValueError(f"missing evidence row {evidence_id}")
        evidence_rows[evidence_id] = evidence
        certificate_evidence[certificate.certificate_id] = evidence_id

    principals = {
        decision_by_id[transition.decision_id].reviewer_id for transition in current_transitions
    }
    if len(principals) != 1:
        raise ValueError("one batch admission must have exactly one principal")

    items: list[dict[str, Any]] = []
    for transition in current_transitions:
        certificate = certificate_by_id.get(transition.certificate_id)
        decision = decision_by_id.get(transition.decision_id)
        binding = binding_by_decision.get(transition.decision_id)
        if certificate is None or decision is None or binding is None:
            raise ValueError(f"incomplete authority chain for {transition.transition_id}")
        items.append(
            {
                "field_key": transition.field_key,
                "certificate_id": certificate.certificate_id,
                "decision_id": decision.decision_id,
                "authorization_id": binding.binding_id,
                "evidence_id": certificate_evidence[certificate.certificate_id],
                "expected_version": certificate.expected_fact_version,
                "authorized_value": binding.authorized_value_payload,
                "transition_id": transition.transition_id,
            }
        )

    used_decisions = {transition.decision_id for transition in transitions}
    pre_payload = _record_payload(pre_record)
    pre_payload.update(
        {
            "transition_ids": sorted(
                transition.transition_id
                for transition in transitions
                if transition.created_version < version
            ),
            "certificate_ids": [certificate.certificate_id for certificate in certificates],
            "authorization_ids": sorted(
                binding.binding_id
                for binding in bindings
                if binding.decision_id
                in {
                    transition.decision_id
                    for transition in transitions
                    if transition.created_version < version
                }
            ),
            "evidence_ids": sorted(evidence_rows),
        }
    )
    post_payload = _record_payload(post_record)
    post_payload.update(
        {
            "transition_ids": [transition.transition_id for transition in transitions],
            "certificate_ids": [certificate.certificate_id for certificate in certificates],
            "authorization_ids": [
                binding.binding_id for binding in bindings if binding.decision_id in used_decisions
            ],
            "evidence_ids": sorted(evidence_rows),
        }
    )
    payload = {
        "schema": SCHEMA_VERSION,
        "outcome": "committed",
        "record_id": form_id,
        "declared_fields": list(field_domain),
        "principal": next(iter(principals)),
        "pre": pre_payload,
        "post": post_payload,
        "items": items,
        "evidence": [
            {
                "evidence_id": evidence_id,
                "record_id": evidence.form_id,
                "content": evidence.sha256,
                "locator": next(
                    certificate.evidence_locator
                    for certificate in certificates
                    if certificate_evidence[certificate.certificate_id] == evidence_id
                ),
            }
            for evidence_id, evidence in sorted(evidence_rows.items())
        ],
        "certificates": [
            {
                "certificate_id": certificate.certificate_id,
                "candidate_id": certificate.candidate_id,
                "record_id": certificate.target_record_id,
                "field_key": certificate.field_key,
                "evidence_id": certificate_evidence[certificate.certificate_id],
                "expected_version": certificate.expected_fact_version,
                "value": certificate.value_payload,
                "producer": [
                    certificate.producer_id,
                    certificate.producer_version,
                ],
            }
            for certificate in certificates
        ],
        "decisions": [
            {
                "decision_id": decision.decision_id,
                "candidate_id": decision.candidate_id,
                "field_key": decision.field_key,
                "principal": decision.reviewer_id,
            }
            for decision in decisions
            if decision.decision_id in used_decisions
        ],
        "authorizations": [
            {
                "authorization_id": binding.binding_id,
                "decision_id": binding.decision_id,
                "certificate_id": binding.certificate_id,
                "authorized_value": binding.authorized_value_payload,
                "principal": decision_by_id[binding.decision_id].reviewer_id,
            }
            for binding in bindings
            if binding.decision_id in used_decisions
        ],
        "transitions": [
            {
                "transition_id": transition.transition_id,
                "record_id": transition.record_id,
                "field_key": transition.field_key,
                "evidence_id": certificate_evidence[transition.certificate_id],
                "from_version": transition.created_version - 1,
                "to_version": transition.created_version,
                "value": transition.value_payload,
                "producer": [
                    transition.producer_id,
                    transition.producer_version,
                ],
                "certificate_id": transition.certificate_id,
                "authorization_id": binding_by_decision[transition.decision_id].binding_id,
            }
            for transition in transitions
        ],
    }
    return AdmissionProjection(payload=payload)


def _find_research_root() -> Path:
    for ancestor in Path(__file__).resolve().parents:
        if (ancestor / "formal" / "alloy" / "batch" / "auto_decte_batch.als").is_file():
            return ancestor
    raise FileNotFoundError("cannot locate the parent research repository")


def _atom_map(values: Iterable[Any], prefix: str) -> dict[Any, str]:
    return {value: f"{prefix}{index}" for index, value in enumerate(sorted(set(values), key=str))}


def _sum(atoms: Iterable[str]) -> str:
    values = tuple(atoms)
    return " + ".join(values) if values else "none"


def _one_sigs(atoms: Iterable[str], parent: str) -> str:
    values = tuple(atoms)
    return f"one sig {', '.join(values)} extends {parent} {{}}" if values else ""


def _relation(lines: list[str], owner: str, field: str, tuples: Iterable[str]) -> None:
    values = tuple(tuples)
    if values:
        lines.append(f"  {owner}.{field} = {_sum(values)}")
    else:
        lines.append(f"  no {owner}.{field}")


def render_alloy_wrapper(projection: AdmissionProjection) -> str:
    """Render an exact, independently inspectable Alloy instance."""

    p = projection.payload
    if p.get("outcome") not in {"committed", "rejected"}:
        raise ValueError("unknown projection outcome")

    all_field_keys = set(p["declared_fields"])
    all_field_keys.update(row["field_key"] for row in p["certificates"])
    all_field_keys.update(row["field_key"] for row in p["transitions"])
    all_field_keys.update(row["field_key"] for row in p["items"])
    fields = _atom_map(all_field_keys, "FieldAtom")
    field_atoms = list(fields.values())

    evidence = {row["evidence_id"]: row for row in p["evidence"]}
    evid_atoms = _atom_map(evidence, "EvidenceAtom")
    content_atoms = _atom_map((row["content"] for row in evidence.values()), "ContentAtom")
    locator_atoms = _atom_map((row["locator"] for row in evidence.values()), "LocatorAtom")

    certificates = {row["certificate_id"]: row for row in p["certificates"]}
    cert_atoms = _atom_map(certificates, "CertificateAtom")
    cand_atoms = _atom_map(certificates, "CandidateAtom")
    cert_id_atoms = _atom_map(certificates, "CertIdAtom")

    authorizations = {row["authorization_id"]: row for row in p["authorizations"]}
    auth_atoms = _atom_map(authorizations, "AuthorizationAtom")
    transitions = {row["transition_id"]: row for row in p["transitions"]}
    trans_atoms = _atom_map(transitions, "TransitionAtom")
    item_atoms = {
        row["transition_id"]: f"AdmissionItemAtom{index}" for index, row in enumerate(p["items"])
    }

    raw_values = set(p["pre"]["values"].values())
    raw_values.update(p["post"]["values"].values())
    raw_values.update(row["value"] for row in certificates.values())
    raw_values.update(row["authorized_value"] for row in authorizations.values())
    raw_values.update(row["value"] for row in transitions.values())
    raw_values.update(row["authorized_value"] for row in p["items"])
    value_atoms = _atom_map(raw_values, "ValueAtom")

    producers = _atom_map(
        (
            tuple(row["producer"])
            for row in tuple(certificates.values()) + tuple(transitions.values())
        ),
        "ProducerAtom",
    )
    principals = _atom_map(
        tuple(row["principal"] for row in authorizations.values()) + (p["principal"],),
        "PrincipalAtom",
    )
    principal = principals[p["principal"]]
    max_version = p.get("formal_max_version", p["post"]["version"])
    version_atoms = [f"VersionAtom{index}" for index in range(max_version + 1)]

    declarations = [
        "module concrete_projection",
        "open auto_decte_batch",
        "",
        "one sig ConcreteRecord extends Record {}",
        _one_sigs(field_atoms, "Field"),
        _one_sigs(value_atoms.values(), "Value"),
        _one_sigs(producers.values(), "Producer"),
        _one_sigs(principals.values(), "Principal"),
        _one_sigs(content_atoms.values(), "EvidenceContent"),
        _one_sigs(locator_atoms.values(), "EvidenceLocator"),
        _one_sigs(evid_atoms.values(), "Evidence"),
        _one_sigs(version_atoms, "Version"),
        _one_sigs(cand_atoms.values(), "Candidate"),
        _one_sigs(cert_id_atoms.values(), "CertId"),
        _one_sigs(cert_atoms.values(), "Certificate"),
        _one_sigs(auth_atoms.values(), "Authorization"),
        _one_sigs(trans_atoms.values(), "Transition"),
        "one sig ConcretePre, ConcretePost extends State {}",
        _one_sigs(item_atoms.values(), "AdmissionItem"),
        "one sig ConcreteAdmission extends BatchAdmissionEvent {}",
        "",
        "fact ConcreteRelations {",
        "  ConcreteRecord.authoritativeFields = "
        f"{_sum(fields[field] for field in p['declared_fields'])}",
        f"  PrincipalRegistry.authorized = {_sum(principals.values())}",
    ]

    lines = declarations
    for index, version_atom in enumerate(version_atoms):
        lines.append(f"  {version_atom}.record = ConcreteRecord")
        if index < len(version_atoms) - 1:
            lines.append(f"  {version_atom}.succ = {version_atoms[index + 1]}")
        else:
            lines.append(f"  no {version_atom}.succ")

    for evidence_id, row in evidence.items():
        atom = evid_atoms[evidence_id]
        lines.extend(
            (
                f"  {atom}.record = ConcreteRecord",
                f"  {atom}.content = {content_atoms[row['content']]}",
                f"  {atom}.locator = {locator_atoms[row['locator']]}",
            )
        )

    for certificate_id, row in certificates.items():
        candidate = cand_atoms[certificate_id]
        target_field = fields[row["field_key"]]
        producer = producers[tuple(row["producer"])]
        lines.extend(
            (
                f"  {candidate}.targetRecord = ConcreteRecord",
                f"  {candidate}.targetField = {target_field}",
                f"  {candidate}.evidence = {evid_atoms[row['evidence_id']]}",
                f"  {candidate}.expectedVersion = VersionAtom{row['expected_version']}",
                f"  {candidate}.value = {value_atoms[row['value']]}",
                f"  {candidate}.producer = {producer}",
                f"  {cert_atoms[certificate_id]}.candidate = {candidate}",
                f"  {cert_atoms[certificate_id]}.certId = {cert_id_atoms[certificate_id]}",
            )
        )

    for authorization_id, row in authorizations.items():
        atom = auth_atoms[authorization_id]
        lines.extend(
            (
                f"  {atom}.certificate = {cert_atoms[row['certificate_id']]}",
                f"  {atom}.authorizedValue = {value_atoms[row['authorized_value']]}",
                f"  {atom}.principal = {principals[row['principal']]}",
            )
        )

    for transition_id, row in transitions.items():
        atom = trans_atoms[transition_id]
        lines.extend(
            (
                f"  {atom}.targetRecord = ConcreteRecord",
                f"  {atom}.targetField = {fields[row['field_key']]}",
                f"  {atom}.evidence = {evid_atoms[row['evidence_id']]}",
                f"  {atom}.fromVersion = VersionAtom{row['from_version']}",
                f"  {atom}.toVersion = VersionAtom{row['to_version']}",
                f"  {atom}.value = {value_atoms[row['value']]}",
                f"  {atom}.producer = {producers[tuple(row['producer'])]}",
                f"  {atom}.certificate = {cert_atoms[row['certificate_id']]}",
                f"  {atom}.authorization = {auth_atoms[row['authorization_id']]}",
            )
        )

    for state_name, state in (
        ("ConcretePre", p["pre"]),
        ("ConcretePost", p["post"]),
    ):
        _relation(
            lines,
            state_name,
            "committedValue",
            (
                f"ConcreteRecord -> {fields[field]} -> {value_atoms[value]}"
                for field, value in state["values"].items()
            ),
        )
        _relation(
            lines,
            state_name,
            "committedSource",
            (
                f"ConcreteRecord -> {fields[field]} -> {trans_atoms[source]}"
                for field, source in state["fact_sources"].items()
            ),
        )
        lines.append(
            f"  {state_name}.currentVersion = ConcreteRecord -> VersionAtom{state['version']}"
        )
        _relation(
            lines,
            state_name,
            "transitions",
            (trans_atoms[value] for value in state["transition_ids"]),
        )
        lines.append(f"  no {state_name}.candidates")
        _relation(
            lines,
            state_name,
            "certificates",
            (cert_atoms[value] for value in state["certificate_ids"]),
        )
        _relation(
            lines,
            state_name,
            "authorizations",
            (auth_atoms[value] for value in state["authorization_ids"]),
        )
        _relation(
            lines,
            state_name,
            "evidence",
            (evid_atoms[value] for value in state["evidence_ids"]),
        )

    for item in p["items"]:
        atom = item_atoms[item["transition_id"]]
        lines.extend(
            (
                f"  {atom}.certificate = {cert_atoms[item['certificate_id']]}",
                f"  {atom}.authorization = {auth_atoms[item['authorization_id']]}",
                f"  {atom}.targetRecord = ConcreteRecord",
                f"  {atom}.targetField = {fields[item['field_key']]}",
                f"  {atom}.targetEvidence = {evid_atoms[item['evidence_id']]}",
                f"  {atom}.expectedVersion = VersionAtom{item['expected_version']}",
                f"  {atom}.value = {value_atoms[item['authorized_value']]}",
                f"  {atom}.transition = {trans_atoms[item['transition_id']]}",
            )
        )

    predicate_lines = (
        ("  legalAdmission[ConcreteAdmission, Full]",)
        if p["outcome"] == "committed"
        else (
            "  fullAdmissionStep[ConcreteAdmission]",
            "  rejectedAdmission[ConcreteAdmission]",
            "  not batchContract[ConcreteAdmission, Full]",
        )
    )
    lines.extend(
        (
            "  ConcreteAdmission.pre = ConcretePre",
            "  ConcreteAdmission.post = ConcretePost",
            f"  ConcreteAdmission.items = {_sum(item_atoms.values())}",
            "  ConcreteAdmission.targetRecord = ConcreteRecord",
            f"  ConcreteAdmission.principal = {principal}",
            "}",
            "",
            "pred ConcreteRefinement {",
            *predicate_lines,
            "}",
            "",
        )
    )

    scopes = {
        "Record": 1,
        "Field": len(field_atoms),
        "Value": len(value_atoms),
        "Producer": len(producers),
        "Principal": len(principals),
        "EvidenceContent": len(content_atoms),
        "EvidenceLocator": len(locator_atoms),
        "Evidence": len(evid_atoms),
        "Version": len(version_atoms),
        "Candidate": len(cand_atoms),
        "CertId": len(cert_id_atoms),
        "Certificate": len(cert_atoms),
        "Authorization": len(auth_atoms),
        "Transition": len(trans_atoms),
        "State": 2,
        "AdmissionItem": len(item_atoms),
        "BatchAdmissionEvent": 1,
        "MachineEvent": 0,
        "TamperEvent": 0,
    }
    scope_text = ", ".join(f"exactly {count} {signature}" for signature, count in scopes.items())
    lines.append(f"run ConcreteRefinement for {scope_text}")
    return "\n".join(line for line in lines if line != "") + "\n"


def run_projection(projection: AdmissionProjection, output_dir: Path) -> AlloyOutcome:
    """Write the canonical record/wrapper and execute Alloy headlessly."""

    research_root = _find_research_root()
    batch_root = research_root / "formal" / "alloy" / "batch"
    jar_path = research_root / "tools" / "alloy-6.2.0.jar"
    java_candidates = sorted((research_root / "tools" / "jre21").rglob("java.exe"))
    if not java_candidates:
        raise FileNotFoundError("portable Java runtime not found")
    if not jar_path.is_file():
        raise FileNotFoundError(f"Alloy jar not found: {jar_path}")

    output_dir.mkdir(parents=True, exist_ok=False)
    projection_path = output_dir / "projection.json"
    wrapper_path = output_dir / "concrete_projection.als"
    model_path = output_dir / "auto_decte_batch.als"
    projection_path.write_text(projection.canonical_text() + "\n", encoding="utf-8")
    wrapper_path.write_text(render_alloy_wrapper(projection), encoding="utf-8")
    shutil.copyfile(batch_root / "auto_decte_batch.als", model_path)

    result_root = output_dir / "alloy-result"
    completed = subprocess.run(
        [
            str(java_candidates[0]),
            "-jar",
            str(jar_path),
            "exec",
            "-q",
            "-c",
            "ConcreteRefinement",
            "-t",
            "none",
            "-o",
            str(result_root),
            str(wrapper_path),
        ],
        cwd=output_dir,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    (output_dir / "alloy.stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (output_dir / "alloy.stderr.txt").write_text(completed.stderr, encoding="utf-8")
    if completed.returncode != 0:
        raise RuntimeError(f"Alloy CLI failed ({completed.returncode}): {completed.stderr}")
    receipt_path = result_root / "receipt.json"
    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    command = receipt["commands"]["ConcreteRefinement"]
    return AlloyOutcome.SAT if command.get("solution") else AlloyOutcome.UNSAT
