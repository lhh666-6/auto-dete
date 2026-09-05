"""Executable witnesses for Proposition 1's observation-level construction.

Observations and outcomes are DERIVED from raw histories, never stored.
``observe`` applies the manuscript Table 2 observation functions;
``normative_outcome`` applies the contract checks.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field
import json
from pathlib import Path
from typing import Any, Sequence

CLASSES = ("D_C", "D_V", "D_F", "D_B", "D_S")


@dataclass(frozen=True)
class Candidate:
    candidate_id: str
    record_id: str
    field_id: str
    evidence_id: str
    producer_id: str
    proposal_value: Any


@dataclass(frozen=True)
class Authorization:
    authorization_id: str
    candidate_id: str
    authorized_value: Any
    role: str


@dataclass(frozen=True)
class BatchItem:
    candidate_id: str
    authorization_id: str


@dataclass(frozen=True)
class SourceAnchor:
    field_id: str
    source_id: str | None


@dataclass(frozen=True)
class FieldValue:
    field_id: str
    value: Any


@dataclass(frozen=True)
class History:
    name: str
    target_record_id: str
    expected_version: Any
    observed_version: Any
    declared_fields: frozenset[str]
    committed_fields: frozenset[str]
    successor_count: int
    predecessor_values: tuple[FieldValue, ...] = field(default_factory=tuple)
    successor_values: tuple[FieldValue, ...] = field(default_factory=tuple)
    candidates: tuple[Candidate, ...] = field(default_factory=tuple)
    authorizations: tuple[Authorization, ...] = field(default_factory=tuple)
    batch_items: tuple[BatchItem, ...] = field(default_factory=tuple)
    sources: tuple[SourceAnchor, ...] = field(default_factory=tuple)

def observe(history: History, class_name: str) -> Any:
    candidates = {c.candidate_id: c for c in history.candidates}
    authorizations = {a.authorization_id: a for a in history.authorizations}
    successor_values = {item.field_id: item.value for item in history.successor_values}
    if class_name == "D_C":
        return tuple(
            (
                candidates[item.candidate_id].candidate_id,
                candidates[item.candidate_id].record_id,
                candidates[item.candidate_id].field_id,
                candidates[item.candidate_id].evidence_id,
                candidates[item.candidate_id].producer_id,
            )
            for item in history.batch_items
        )
    if class_name == "D_V":
        return tuple(
            (
                candidates[item.candidate_id].proposal_value,
                authorizations[item.authorization_id].authorized_value,
                successor_values[candidates[item.candidate_id].field_id],
                authorizations[item.authorization_id].role,
            )
            for item in history.batch_items
        )
    if class_name == "D_F":
        return (history.expected_version, history.observed_version)
    if class_name == "D_B":
        return (
            frozenset(history.declared_fields),
            frozenset(history.committed_fields),
            history.successor_count,
        )
    if class_name == "D_S":
        return tuple(sorted((s.field_id, s.source_id) for s in history.sources))
    raise KeyError(class_name)


def project(history: History, classes: Sequence[str]) -> tuple[tuple[str, object], ...]:
    return tuple((name, observe(history, name)) for name in classes)

def validate_history_domain(history: History) -> tuple[str, ...]:
    errors: list[str] = []
    candidate_ids = {c.candidate_id for c in history.candidates}
    authorization_ids = {a.authorization_id for a in history.authorizations}
    if len(candidate_ids) != len(history.candidates):
        errors.append("duplicate candidate_id")
    if len(authorization_ids) != len(history.authorizations):
        errors.append("duplicate authorization_id")
    predecessor_fields = [item.field_id for item in history.predecessor_values]
    successor_fields = [item.field_id for item in history.successor_values]
    if len(predecessor_fields) != len(set(predecessor_fields)):
        errors.append("duplicate predecessor field value")
    if len(successor_fields) != len(set(successor_fields)):
        errors.append("duplicate successor field value")
    if set(predecessor_fields) != history.declared_fields:
        errors.append("predecessor values do not cover declared fields")
    if set(successor_fields) != history.declared_fields:
        errors.append("successor values do not cover declared fields")
    for auth in history.authorizations:
        if auth.candidate_id not in candidate_ids:
            errors.append(f"authorization {auth.authorization_id} has no candidate")
    for item in history.batch_items:
        if item.candidate_id not in candidate_ids:
            errors.append(f"batch item {item.candidate_id} has no candidate")
        if item.authorization_id not in authorization_ids:
            errors.append(f"batch item has no authorization {item.authorization_id}")
    if not history.declared_fields:
        errors.append("empty declared field domain")
    if not history.committed_fields <= history.declared_fields:
        errors.append("committed field outside declared domain")
    for candidate in history.candidates:
        if candidate.field_id not in history.declared_fields:
            errors.append(f"candidate {candidate.candidate_id} targets undeclared field")
    for source in history.sources:
        if source.field_id not in history.declared_fields:
            errors.append(f"source targets undeclared field {source.field_id}")
    return tuple(errors)

def _context_ok(h: History) -> bool:
    candidates = {c.candidate_id: c for c in h.candidates}
    authorizations = {a.authorization_id: a for a in h.authorizations}
    return all(
        candidates[item.candidate_id].record_id == h.target_record_id
        and authorizations[item.authorization_id].candidate_id == item.candidate_id
        for item in h.batch_items
    )


def _attribution_ok(h: History) -> bool:
    candidates = {c.candidate_id: c for c in h.candidates}
    authorizations = {a.authorization_id: a for a in h.authorizations}
    successor_values = {item.field_id: item.value for item in h.successor_values}
    return all(
        authorizations[item.authorization_id].role == "human-authorized"
        and successor_values[candidates[item.candidate_id].field_id]
        == authorizations[item.authorization_id].authorized_value
        for item in h.batch_items
    )


def _freshness_ok(h: History) -> bool:
    return h.expected_version == h.observed_version


def _batch_ok(h: History) -> bool:
    return h.committed_fields == h.declared_fields and h.successor_count == 1


def _source_ok(h: History) -> bool:
    counts = {
        field_id: sum(
            1
            for source in h.sources
            if source.field_id == field_id and source.source_id is not None
        )
        for field_id in h.declared_fields
    }
    return all(count == 1 for count in counts.values())


def normative_outcome(h: History) -> tuple[str, str, str]:
    status = (
        "admissible"
        if _context_ok(h) and _attribution_ok(h) and _freshness_ok(h) and _batch_ok(h) and _source_ok(h)
        else "inadmissible"
    )
    if h.successor_count != 1:
        successor = "fragmented-successor"
    elif h.committed_fields != h.declared_fields:
        successor = "partial-successor"
    else:
        successor = "complete-successor"
    trace = "complete-trace" if _source_ok(h) else "incomplete-trace"
    return (status, successor, trace)

def _candidate(candidate_id="candidate-1", record_id="record-A", field_id="score",
               evidence_id="evidence-1", proposal_value=100):
    return Candidate(candidate_id, record_id, field_id, evidence_id, "model-A", proposal_value)


def _auth(authorization_id="auth-1", candidate_id="candidate-1", role="human-authorized"):
    return Authorization(authorization_id, candidate_id, 101, role)

def paired_histories() -> dict[str, tuple[History, History]]:
    single = dict(
        target_record_id="record-A",
        expected_version=7,
        observed_version=7,
        declared_fields=frozenset({"score"}),
        committed_fields=frozenset({"score"}),
        successor_count=1,
        predecessor_values=(FieldValue("score", 90),),
        successor_values=(FieldValue("score", 101),),
        candidates=(_candidate(),),
        authorizations=(_auth(),),
        batch_items=(BatchItem("candidate-1", "auth-1"),),
        sources=(SourceAnchor("score", "transition-score"),),
    )
    pairs = {
        "D_C": (
            History(name="exact-candidate", **single),
            History(
                name="equal-value-cross-context-substitute",
                **{**single, "candidates": (_candidate(record_id="record-B"),)},
            ),
        ),
        "D_V": (
            History(name="retained-correction", **single),
            History(
                name="correction-role-erased",
                **{**single, "authorizations": (_auth(role="machine-attributed"),)},
            ),
        ),
        "D_F": (
            History(name="fresh-authorization", **single),
            History(name="same-bytes-after-supersession", **{**single, "observed_version": 8}),
        ),
    }

    def batch_pair():
        base = dict(
            target_record_id="record-A",
            expected_version=7,
            observed_version=7,
            declared_fields=frozenset({"score", "status"}),
            committed_fields=frozenset({"score", "status"}),
            predecessor_values=(
                FieldValue("score", 90),
                FieldValue("status", "open"),
            ),
            successor_values=(
                FieldValue("score", 101),
                FieldValue("status", 50),
            ),
            candidates=(
                _candidate(),
                _candidate("candidate-2", "record-A", "status", "evidence-2", 50),
            ),
            authorizations=(
                _auth(),
                Authorization("auth-2", "candidate-2", 50, "human-authorized"),
            ),
            batch_items=(
                BatchItem("candidate-1", "auth-1"),
                BatchItem("candidate-2", "auth-2"),
            ),
            sources=(
                SourceAnchor("score", "transition-score"),
                SourceAnchor("status", "transition-status"),
            ),
        )
        return (
            History(name="complete-declared-batch", successor_count=1, **base),
            History(
                name="partial-declared-batch",
                successor_count=1,
                **{**base, "committed_fields": frozenset({"score"})},
            ),
        )

    pairs["D_B"] = batch_pair()
    pairs["D_S"] = (
        History(name="total-field-source-map", **single),
        History(
            name="missing-field-source",
            **{**single, "sources": (SourceAnchor("score", None),)},
        ),
    )
    return pairs

def verify() -> None:
    pairs = paired_histories()
    assert set(pairs) == set(CLASSES)
    for omitted, (safe, unsafe) in pairs.items():
        assert validate_history_domain(safe) == ()
        assert validate_history_domain(unsafe) == ()
        remaining = tuple(item for item in CLASSES if item != omitted)
        assert normative_outcome(safe) != normative_outcome(unsafe)
        assert project(safe, remaining) == project(unsafe, remaining)
        assert project(safe, CLASSES) != project(unsafe, CLASSES)


def _json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (set, frozenset)):
        return [_json_safe(item) for item in sorted(value)]
    return value


def build_report() -> dict[str, Any]:
    """Expose raw histories and every value derived by the checker."""
    report_pairs: dict[str, Any] = {}
    for omitted, (safe, unsafe) in paired_histories().items():
        remaining = tuple(item for item in CLASSES if item != omitted)
        report_pairs[omitted] = {
            "safe": {
                "history": asdict(safe),
                "domain_errors": validate_history_domain(safe),
                "observations": {item: observe(safe, item) for item in CLASSES},
                "normative_outcome": normative_outcome(safe),
            },
            "unsafe": {
                "history": asdict(unsafe),
                "domain_errors": validate_history_domain(unsafe),
                "observations": {item: observe(unsafe, item) for item in CLASSES},
                "normative_outcome": normative_outcome(unsafe),
            },
            "changed_observation_classes": [
                item for item in CLASSES if observe(safe, item) != observe(unsafe, item)
            ],
            "reduced_projection_equal": project(safe, remaining)
            == project(unsafe, remaining),
            "normative_outcomes_differ": normative_outcome(safe)
            != normative_outcome(unsafe),
        }
    return _json_safe({
        "checker": "observation-witnesses-v2-derived",
        "observations_and_outcomes_are_derived": True,
        "information_classes": CLASSES,
        "pairs": report_pairs,
    })


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", type=Path, help="write an auditable witness report")
    args = parser.parse_args()
    verify()
    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(
            json.dumps(build_report(), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
    print("PASS: five domain-valid history pairs satisfy the derived projection condition")
