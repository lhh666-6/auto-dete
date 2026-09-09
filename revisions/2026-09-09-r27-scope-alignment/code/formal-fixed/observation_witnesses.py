"""Executable witnesses for Proposition 1's observation-level construction.

Observations and outcomes are DERIVED from raw histories, never stored.
``observe`` applies the manuscript Table 2 observation functions;
``normative_outcome`` applies the contract checks.

Scope (review R5): the domain predicate separates the *schema* field domain
(the record's authoritative field set, over which value and source maps must
be total) from the *declared item* field domain (the fields named by the batch
items, over which the committed effect domain is checked).  An ordinary
single-field update with another field copied forward is therefore a complete
successor.  The script validates the five declared constructions and the
copy-forward control; it is not a general admission oracle.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, field, replace
import json
from pathlib import Path
from typing import Any, Sequence

CLASSES = ("D_C", "D_V", "D_F", "D_B", "D_S")


def _canonical_value(value: Any) -> str:
    """Canonical JSON form used for every value-equality decision here.

    Python equality treats ``2 == 2.0`` and ``1 == True`` as true; the
    contract, trace, and formal projection compare canonical JSON payloads.
    """
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def _canonical_equal(left: Any, right: Any) -> bool:
    return _canonical_value(left) == _canonical_value(right)


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
class SourceTransition:
    source_id: str
    field_id: str
    value: Any


@dataclass(frozen=True)
class CommitStep:
    successor_id: str
    before: tuple[FieldValue, ...]
    after: tuple[FieldValue, ...]

    @property
    def changed_fields(self) -> frozenset[str]:
        before = {v.field_id: v.value for v in self.before}
        after = {v.field_id: v.value for v in self.after}
        return frozenset(f for f in before if not _canonical_equal(before[f], after[f]))


@dataclass(frozen=True)
class History:
    name: str
    target_record_id: str
    expected_version: Any
    observed_version: Any
    declared_fields: frozenset[str]
    commits: tuple[CommitStep, ...]
    predecessor_values: tuple[FieldValue, ...] = field(default_factory=tuple)
    successor_values: tuple[FieldValue, ...] = field(default_factory=tuple)
    candidates: tuple[Candidate, ...] = field(default_factory=tuple)
    authorizations: tuple[Authorization, ...] = field(default_factory=tuple)
    batch_items: tuple[BatchItem, ...] = field(default_factory=tuple)
    sources: tuple[SourceAnchor, ...] = field(default_factory=tuple)
    predecessor_sources: tuple[SourceAnchor, ...] = field(default_factory=tuple)
    source_transitions: tuple[SourceTransition, ...] = field(default_factory=tuple)
    schema_fields: frozenset[str] | None = None

    @property
    def schema_field_domain(self) -> frozenset[str]:
        """Authoritative field set over which value and source maps are total.

        Defaults to ``declared_fields`` so the five all-field constructions
        are unchanged; a copy-forward witness sets it explicitly when the
        submitted item domain is narrower than the schema.
        """
        return self.schema_fields if self.schema_fields is not None else self.declared_fields

    @property
    def declared_item_fields(self) -> frozenset[str]:
        """Field domain named by the batch items (the declared effect domain)."""
        candidates = {c.candidate_id: c for c in self.candidates}
        derived = frozenset(
            candidates[item.candidate_id].field_id
            for item in self.batch_items
            if item.candidate_id in candidates
        )
        return derived if derived else frozenset(self.declared_fields)

    @property
    def committed_fields(self) -> frozenset[str]:
        return frozenset(f for step in self.commits for f in step.changed_fields)

    @property
    def successor_count(self) -> int:
        return len(self.commits)

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
                history.target_record_id,
                authorizations[item.authorization_id].candidate_id,
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
            frozenset(history.declared_item_fields),
            frozenset(history.committed_fields),
            history.successor_count,
            tuple(step.changed_fields for step in history.commits),
        )
    if class_name == "D_S":
        return (
            tuple(sorted(((s.field_id, s.source_id) for s in history.sources),
                         key=lambda item: (item[0], item[1] or ""))),
            _source_resolution(history),
        )
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
    if set(predecessor_fields) != history.schema_field_domain:
        errors.append("predecessor values do not cover schema fields")
    if set(successor_fields) != history.schema_field_domain:
        errors.append("successor values do not cover schema fields")
    current = {v.field_id: v.value for v in history.predecessor_values}
    successor_ids: set[str] = set()
    if not history.commits:
        errors.append("empty commit sequence")
    for step in history.commits:
        before = {v.field_id: v.value for v in step.before}
        after = {v.field_id: v.value for v in step.after}
        if (len(before) != len(step.before) or len(after) != len(step.after)
                or set(before) != history.schema_field_domain
                or set(after) != history.schema_field_domain):
            errors.append("commit snapshots do not cover schema exactly once")
        if before != current:
            errors.append("disconnected commit sequence")
        if step.successor_id in successor_ids:
            errors.append("duplicate successor identity")
        successor_ids.add(step.successor_id)
        current = after
    if current != {v.field_id: v.value for v in history.successor_values}:
        errors.append("commit sequence does not reach successor values")
    for auth in history.authorizations:
        if auth.candidate_id not in candidate_ids:
            errors.append(f"authorization {auth.authorization_id} has no candidate")
    for item in history.batch_items:
        if item.candidate_id not in candidate_ids:
            errors.append(f"batch item {item.candidate_id} has no candidate")
        if item.authorization_id not in authorization_ids:
            errors.append(f"batch item has no authorization {item.authorization_id}")
    if not history.schema_field_domain:
        errors.append("empty schema field domain")
    if not history.declared_item_fields <= history.schema_field_domain:
        errors.append("declared item fields are not a subset of the schema field domain")
    for candidate in history.candidates:
        if candidate.field_id not in history.schema_field_domain:
            errors.append(f"candidate {candidate.candidate_id} targets undeclared field")
    for source in (*history.sources, *history.predecessor_sources,
                   *history.source_transitions):
        if source.field_id not in history.schema_field_domain:
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
        and _canonical_equal(
            successor_values[candidates[item.candidate_id].field_id],
            authorizations[item.authorization_id].authorized_value,
        )
        for item in h.batch_items
    )


def _freshness_ok(h: History) -> bool:
    return h.expected_version == h.observed_version


def _batch_ok(h: History) -> bool:
    return h.committed_fields == h.declared_item_fields and h.successor_count == 1


def _source_resolution(h: History) -> tuple[tuple[object, ...], ...]:
    """Local source resolution; full candidate/authorization lineage is P6.

    Do not expose intermediate commit groups here: those belong to D_B.
    Resolution includes cardinality, field/value consistency, and exact
    source copy-forward for fields unchanged between endpoint snapshots.
    """
    before = {v.field_id: v.value for v in h.predecessor_values}
    after = {v.field_id: v.value for v in h.successor_values}
    results = []
    for field_id in sorted(after):
        anchors = [s for s in h.sources if s.field_id == field_id]
        matches = [t for s in anchors if s.source_id is not None
                   for t in h.source_transitions if t.source_id == s.source_id]
        consistent = (len(anchors) == 1 and len(matches) == 1
                      and matches[0].field_id == field_id
                      and _canonical_equal(matches[0].value, after[field_id]))
        prior = [s for s in h.predecessor_sources if s.field_id == field_id]
        copy_ok = (not _canonical_equal(before[field_id], after[field_id])
                   or (len(prior) == 1 and anchors == prior))
        results.append((field_id, len(anchors), len(matches), consistent, copy_ok))
    return tuple(results)


def _source_ok(h: History) -> bool:
    return all(anchors == 1 and matches == 1 and consistent and copy_ok
               for _, anchors, matches, consistent, copy_ok in _source_resolution(h))


def normative_outcome(h: History) -> tuple[str, str, str]:
    status = (
        "admissible"
        if _context_ok(h) and _attribution_ok(h) and _freshness_ok(h) and _batch_ok(h) and _source_ok(h)
        else "inadmissible"
    )
    if h.successor_count != 1:
        successor = "fragmented-successor"
    elif h.committed_fields != h.declared_item_fields:
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
        commits=(CommitStep("successor-1", (FieldValue("score", 90),),
                            (FieldValue("score", 101),)),),
        predecessor_values=(FieldValue("score", 90),),
        successor_values=(FieldValue("score", 101),),
        candidates=(_candidate(),),
        authorizations=(_auth(),),
        batch_items=(BatchItem("candidate-1", "auth-1"),),
        sources=(SourceAnchor("score", "transition-score"),),
        predecessor_sources=(SourceAnchor("score", "prior-score"),),
        source_transitions=(SourceTransition("prior-score", "score", 90),
                            SourceTransition("transition-score", "score", 101)),
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
            predecessor_sources=(SourceAnchor("score", "prior-score"),
                                 SourceAnchor("status", "prior-status")),
            source_transitions=(SourceTransition("prior-score", "score", 90),
                                SourceTransition("prior-status", "status", "open"),
                                SourceTransition("transition-score", "score", 101),
                                SourceTransition("transition-status", "status", 50)),
        )
        before, after = base["predecessor_values"], base["successor_values"]
        intermediate = (FieldValue("score", 101), FieldValue("status", "open"))
        return (
            History(name="atomic-declared-batch",
                    commits=(CommitStep("successor-1", before, after),), **base),
            History(
                name="fragmented-declared-batch",
                commits=(CommitStep("successor-1", before, intermediate),
                         CommitStep("successor-2", intermediate, after)),
                **base,
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


def candidate_identity_pair() -> tuple[History, History]:
    """Isolate reviewed-candidate linkage with the same pool, context and values."""
    base, _ = paired_histories()["D_C"]
    pool = (_candidate(), _candidate(candidate_id="candidate-2"))
    safe = replace(base, name="reviewed-candidate-selected", candidates=pool)
    unsafe = replace(
        safe, name="same-context-equal-value-unreviewed-candidate",
        batch_items=(BatchItem("candidate-2", "auth-1"),),
    )
    return safe, unsafe


def copy_forward_control() -> History:
    """Ordinary single-field update with another field copied forward.

    Review R5 control: the submitted item domain is {score}, the schema domain
    is {score, status}, and status keeps its prior value and exact prior
    source.  This must be a complete successor, not a partial one.
    """
    base = dict(
        target_record_id="record-A",
        expected_version=7,
        observed_version=7,
        declared_fields=frozenset({"score", "status"}),
        schema_fields=frozenset({"score", "status"}),
        predecessor_values=(
            FieldValue("score", 90),
            FieldValue("status", "open"),
        ),
        successor_values=(
            FieldValue("score", 101),
            FieldValue("status", "open"),
        ),
        candidates=(_candidate(),),
        authorizations=(_auth(),),
        batch_items=(BatchItem("candidate-1", "auth-1"),),
        sources=(
            SourceAnchor("score", "transition-score"),
            SourceAnchor("status", "prior-status"),
        ),
        predecessor_sources=(
            SourceAnchor("score", "prior-score"),
            SourceAnchor("status", "prior-status"),
        ),
        source_transitions=(
            SourceTransition("prior-score", "score", 90),
            SourceTransition("prior-status", "status", "open"),
            SourceTransition("transition-score", "score", 101),
        ),
    )
    return History(
        name="single-field-update-with-copy-forward",
        commits=(
            CommitStep(
                "successor-1", base["predecessor_values"], base["successor_values"]
            ),
        ),
        **base,
    )


def verify() -> None:
    pairs = paired_histories()
    assert set(pairs) == set(CLASSES)
    for omitted, (safe, unsafe) in [*pairs.items(), ("D_C", candidate_identity_pair())]:
        assert validate_history_domain(safe) == ()
        assert validate_history_domain(unsafe) == ()
        assert normative_outcome(safe) == ("admissible", "complete-successor", "complete-trace")
        assert normative_outcome(unsafe)[0] == "inadmissible"
        remaining = tuple(item for item in CLASSES if item != omitted)
        assert normative_outcome(safe) != normative_outcome(unsafe)
        assert project(safe, remaining) == project(unsafe, remaining)
        assert project(safe, CLASSES) != project(unsafe, CLASSES)

    control = copy_forward_control()
    assert validate_history_domain(control) == ()
    assert control.declared_item_fields == frozenset({"score"})
    assert control.schema_field_domain == frozenset({"score", "status"})
    assert normative_outcome(control) == ("admissible", "complete-successor", "complete-trace")


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
    all_pairs = {**paired_histories(), "D_C_identity": candidate_identity_pair()}
    for pair_name, (safe, unsafe) in all_pairs.items():
        omitted = "D_C" if pair_name == "D_C_identity" else pair_name
        remaining = tuple(item for item in CLASSES if item != omitted)
        report_pairs[pair_name] = {
            "safe": {
                "history": asdict(safe),
                "derived_commit_effects": safe.committed_fields,
                "derived_successor_count": safe.successor_count,
                "domain_errors": validate_history_domain(safe),
                "observations": {item: observe(safe, item) for item in CLASSES},
                "normative_outcome": normative_outcome(safe),
            },
            "unsafe": {
                "history": asdict(unsafe),
                "derived_commit_effects": unsafe.committed_fields,
                "derived_successor_count": unsafe.successor_count,
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
    control = copy_forward_control()
    return _json_safe({
        "checker": "observation-witnesses-v5-candidate-identity",
        "observations_and_outcomes_are_derived": True,
        "source_scope": "local resolution cardinality, field/value consistency, exact unchanged-source retention; full P6 lineage is checked separately",
        "domain_scope": (
            "schema field domain governs total value/source maps; declared item "
            "field domain governs committed effects and batch references"
        ),
        "validated_scope": (
            "five declared constructions, a separate D_C identity pair, plus one single-field "
            "copy-forward control; not a general admission oracle"
        ),
        "information_classes": CLASSES,
        "candidate_identity_pair": report_pairs.pop("D_C_identity"),
        "pairs": report_pairs,
        "copy_forward_control": {
            "history": asdict(control),
            "derived_declared_item_fields": control.declared_item_fields,
            "derived_schema_field_domain": control.schema_field_domain,
            "derived_commit_effects": control.committed_fields,
            "derived_successor_count": control.successor_count,
            "domain_errors": validate_history_domain(control),
            "normative_outcome": normative_outcome(control),
        },
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
    print("PASS: five class pairs and one additional candidate-identity pair satisfy the derived projection condition")
