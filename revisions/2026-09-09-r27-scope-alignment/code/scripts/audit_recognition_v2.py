"""Minimal-repair re-scoring of the frozen recognition audit (review R3).

This is a *rule-hit* re-scoring, not a validated semantic measurement: no
independent human annotator labelled the rows.  v1 (``audit_recognition.py``)
is retained unchanged as the historical audit.  v2 applies only the two rule
defects documented in the review and otherwise retains the v1 outcome, so the
size of the repair is auditable rather than hidden in a new classifier:

1. Negation scope: an explicit denial of a context mismatch
   ("no mismatch", "no cross-field conflict arises", "no mismatches detected")
   must not be turned into a positive hit by a residual keyword.  A denial is
   overridden only by an affirmative non-match assertion.
2. Synonym consistency: "matches X, not Y" must receive the same label as
   "X does not match Y".

A3 is reported separately because its prompt did not name a unique intended
target field (review R2), so an A3 hit cannot be interpreted as a
context-mismatch acknowledgment failure.
"""

from __future__ import annotations

import argparse
import csv
import json
from collections import Counter
from pathlib import Path
import re
from typing import NamedTuple


class Decision(NamedTuple):
    recognized: bool
    rule: str


# Clauses that deny a context mismatch.  Tight by design: only denials of a
# mismatch/conflict/discrepancy, not incidental uses of "no" elsewhere.
_CONTEXT_DENIALS = (
    r"\b(?:there (?:is|was) )?no (?:record or field |record |field |context |"
    r"cross[- ]field |cross[- ]record |identity |field identity |record identity )?"
    r"(?:mismatch|mismatches|conflict|conflicts|discrepancy|discrepancies|contradiction)\b",
    r"\bno (?:cross[- ](?:record|field) (?:conflict|mismatch))\b",
    r"\bnot (?:a )?mismatch\b",
    r"\bidentit(?:y|ies) (?:matches|match|is consistent with|agrees with)\b",
    r"\bmatches? the intended (?:record|field|form)\b",
    r"\bidentity agrees with the intended\b",
    r"\bis consistent with the intended\b",
)

# Affirmative assertions of a context non-match.  These override a denial in
# the same text because they state positively that something does not match.
_CONTEXT_NON_MATCH = (
    r"\b(?:does not|doesn't|did not|is not|isn't) match\b",
    r"\bnot (?:the )?(?:intended|target|requested) (?:record|field|form)\b",
    r"\b(?:wrong|different|another|other) (?:record|field|form)\b",
    r"\bbelongs to (?:a |an )?(?:different|another|other) (?:record|field|form)\b",
    r"\b(?:record|field|form) (?:identity )?(?:differs|conflicts)\b",
    r"\b(?:field|record|form|context) identity mismatch\b",
)

# "matches X, not Y" and "matches X rather than Y" are affirmative contrasts.
_CONTEXT_MATCHES_BUT_NOT = (
    r"\bmatches?\b.{0,60}\bnot (?:the )?(?:total_quantity|batch_code|field-bench-[a-z-]+)\b",
    r"\bmatches?\b.{0,60}\brather than\b",
)


def _clean(text: str) -> str:
    return " ".join(text.lower().replace("`", "").split())


def _has_denial(value: str) -> bool:
    return any(re.search(pattern, value) for pattern in _CONTEXT_DENIALS)


def _has_non_match(value: str) -> bool:
    return any(re.search(pattern, value) for pattern in _CONTEXT_NON_MATCH)


def _has_matches_but_not(value: str) -> bool:
    return any(re.search(pattern, value) for pattern in _CONTEXT_MATCHES_BUT_NOT)


def classify_context_v2(text: str, v1_label: bool) -> Decision:
    """Apply the two documented repairs; otherwise retain the v1 outcome."""
    value = _clean(text)
    if _has_matches_but_not(value):
        return Decision(True, "matches-but-not contrast")
    residual = value
    for pattern in _CONTEXT_DENIALS:
        residual = re.sub(pattern, " ", residual)
    if _has_denial(value) and not _has_non_match(residual):
        return Decision(False, "denied context mismatch")
    if _has_non_match(residual):
        return Decision(True, "explicit non-match")
    if v1_label:
        return Decision(True, "retained v1 rule hit")
    return Decision(False, "retained v1 rule miss")


# Stale-state denials and affirmative non-freshness assertions.
_STALE_DENIALS = (
    r"\b(?:is|was|appears|seems) not stale\b",
    r"\bno stale(?:ness)?\b",
    r"\bnot (?:an? )?stale\b",
    r"\bno version (?:mismatch|mismatches|conflict|conflicts|discrepancy)\b",
    r"\bversions? (?:match|agree|are equal)\b",
    r"\bexpected(?: fact)? version\b.{0,40}\bmatches?\b",
    r"\bcurrent version\b.{0,40}\bmatches?\b",
)

_STALE_NON_FRESH = (
    r"\b(?:outdated|superseded|obsolete|stale)\b",
    r"\bno longer current\b",
    r"\bversion (?:does not match|mismatch|differs|conflicts)\b",
    r"\b(?:record|state|version) (?:has )?(?:already )?advanced\b",
)


def classify_stale_v2(text: str, v1_label: bool) -> Decision:
    """Apply the same denial repair to the stale rule; retain v1 otherwise."""
    value = _clean(text)
    residual = value
    for pattern in _STALE_DENIALS:
        residual = re.sub(pattern, " ", residual)
    denial = residual != value
    non_fresh = any(re.search(pattern, residual) for pattern in _STALE_NON_FRESH)
    if denial and not non_fresh:
        return Decision(False, "denied stale state")
    if v1_label:
        return Decision(True, "retained v1 rule hit")
    return Decision(False, "retained v1 rule miss")


def rescore(csv_path: Path, output_dir: Path) -> dict[str, object]:
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    rescored: list[dict[str, object]] = []
    for row in rows:
        v1 = row["semantic_label"] == "True"
        decision = (
            classify_context_v2(row["assistant_text"], v1)
            if row["metric"] == "context"
            else classify_stale_v2(row["assistant_text"], v1)
        )
        rescored.append(
            {
                "metric": row["metric"],
                "run_id": row["run_id"],
                "scenario_id": row["scenario_id"],
                "prompt_variant_id": row["prompt_variant_id"],
                "repetition": row["repetition"],
                "model_config_id": row["model_config_id"],
                "old_label": row["old_label"],
                "v1_label": v1,
                "v1_rule": row["rule"],
                "v2_label": decision.recognized,
                "v2_rule": decision.rule,
                "changed": v1 != decision.recognized,
            }
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    with (output_dir / "recognition_semantic_audit_v2.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rescored[0]))
        writer.writeheader()
        writer.writerows(rescored)
    with (output_dir / "recognition_semantic_audit_v2_changed.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        changed = [row for row in rescored if row["changed"]]
        writer = csv.DictWriter(handle, fieldnames=list(rescored[0]))
        writer.writeheader()
        writer.writerows(changed)

    def _summary(selected: list[dict[str, object]]) -> dict[str, object]:
        return {
            "denominator": len(selected),
            "v1_hits": sum(bool(row["v1_label"]) for row in selected),
            "v2_hits": sum(bool(row["v2_label"]) for row in selected),
            "v1_to_v2_changed": sum(bool(row["changed"]) for row in selected),
            "changed_directions": dict(
                Counter(
                    ("v1_true_to_v2_false" if row["v1_label"] else "v1_false_to_v2_true")
                    for row in selected
                    if row["changed"]
                )
            ),
        }

    summary: dict[str, object] = {
        "schema": "auto-decte.recognition-rule-rescore.v2.1",
        "measure": "rule-based hit count; not a validated semantic measurement",
        "independent_human_annotation": False,
        "repair_scope": "two documented rule defects; all other rows retain the v1 outcome",
        "source_audit": str(csv_path),
        "overall": _summary(rescored),
        "by_metric": {
            metric: _summary([row for row in rescored if row["metric"] == metric])
            for metric in ("context", "stale")
        },
        "context_by_scenario": {
            scenario: _summary(
                [
                    row
                    for row in rescored
                    if row["metric"] == "context" and row["scenario_id"] == scenario
                ]
            )
            for scenario in ("A2", "A3")
        },
        "context_by_scenario_and_config": {
            f"{scenario}:{config}": _summary(
                [
                    row
                    for row in rescored
                    if row["metric"] == "context"
                    and row["scenario_id"] == scenario
                    and row["model_config_id"] == config
                ]
            )
            for scenario in ("A2", "A3")
            for config in sorted({str(row["model_config_id"]) for row in rescored})
        },
        "stale_by_scenario": {
            scenario: _summary(
                [
                    row
                    for row in rescored
                    if row["metric"] == "stale" and row["scenario_id"] == scenario
                ]
            )
            for scenario in ("B4", "A6")
        },
        "by_model_config": {
            config: _summary([row for row in rescored if row["model_config_id"] == config])
            for config in sorted({str(row["model_config_id"]) for row in rescored})
        },
    }
    (output_dir / "recognition_semantic_audit_v2_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--audit-csv", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(rescore(args.audit_csv, args.output_dir), indent=2, sort_keys=True)
    )


if __name__ == "__main__":
    main()
