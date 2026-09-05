"""Executable witnesses for Proposition 1's observation-level construction.

These witnesses validate the projection argument, not the Alloy model.  Each
history exposes five logically factored observation coordinates even when a
concrete representation stores several coordinates in one object.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Sequence


CLASSES = ("D_C", "D_V", "D_F", "D_B", "D_S")


@dataclass(frozen=True)
class History:
    name: str
    raw: Mapping[str, object]
    observations: Mapping[str, object]
    outcome: tuple[str, str, str]


def project(history: History, classes: Sequence[str]) -> tuple[tuple[str, object], ...]:
    """Return the declared information projection in a stable order."""
    return tuple((name, history.observations[name]) for name in classes)


def _base() -> dict[str, object]:
    return {
        "D_C": ("candidate-1", "record-A", "score", "evidence-1", "model-A"),
        "D_V": (100, 101, 101, "proposal/human-authorized/committed"),
        "D_F": (7, 7, "current"),
        "D_B": (("score", "status"), ("score", "status"), "one-successor"),
        "D_S": (("score", "transition-score"), ("status", "transition-status")),
    }


def _history(
    name: str,
    changed_class: str,
    changed_observation: object,
    outcome: tuple[str, str, str],
    **raw: object,
) -> History:
    observations = _base()
    observations[changed_class] = changed_observation
    common_raw: dict[str, object] = {
        "candidate_id": "candidate-1",
        "candidate_value": 100,
        "authorized_value": 101,
        "committed_value": 101,
    }
    common_raw.update(raw)
    return History(name, common_raw, observations, outcome)


def paired_histories() -> dict[str, tuple[History, History]]:
    safe_outcome = ("admissible", "complete-successor", "complete-trace")
    return {
        "D_C": (
            _history("exact-candidate", "D_C", _base()["D_C"], safe_outcome),
            _history(
                "equal-value-cross-context-substitute",
                "D_C",
                ("candidate-2", "record-B", "score", "evidence-2", "model-A"),
                ("inadmissible", "candidate-substitution", "misbound-trace"),
                candidate_id="candidate-2",
            ),
        ),
        "D_V": (
            _history("retained-correction", "D_V", _base()["D_V"], safe_outcome),
            _history(
                "correction-role-erased",
                "D_V",
                (100, 101, 101, "committed-falsely-attributed-to-proposal"),
                ("inadmissible", "value-identical-successor", "false-origin"),
            ),
        ),
        "D_F": (
            _history("fresh-authorization", "D_F", _base()["D_F"], safe_outcome),
            _history(
                "same-bytes-after-supersession",
                "D_F",
                (7, 8, "stale"),
                ("inadmissible", "stale-successor", "historical-trace"),
            ),
        ),
        "D_B": (
            _history("complete-declared-batch", "D_B", _base()["D_B"], safe_outcome),
            _history(
                "partial-declared-batch",
                "D_B",
                (("score", "status"), ("score",), "partial-successor"),
                ("inadmissible", "partial-successor", "complete-trace"),
            ),
        ),
        "D_S": (
            _history("total-field-source-map", "D_S", _base()["D_S"], safe_outcome),
            _history(
                "missing-field-source",
                "D_S",
                (("score", "transition-score"),),
                ("inadmissible", "value-identical-successor", "incomplete-trace"),
            ),
        ),
    }


def verify() -> None:
    """Raise AssertionError unless every witness satisfies Equation (13)."""
    pairs = paired_histories()
    assert set(pairs) == set(CLASSES)
    for omitted, (safe, unsafe) in pairs.items():
        remaining = tuple(item for item in CLASSES if item != omitted)
        assert safe.outcome != unsafe.outcome
        assert project(safe, remaining) == project(unsafe, remaining)
        assert project(safe, CLASSES) != project(unsafe, CLASSES)


if __name__ == "__main__":
    verify()
    print("PASS: five paired histories satisfy the declared projection condition")
