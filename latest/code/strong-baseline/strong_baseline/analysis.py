"""Semantic projections, fairness checks and the section 46 self-audit.

Prompt v3.2 sections 22-27 and 37:
  * a baseline must be compared through a projection it actually declares
    (never raw byte equality alone, never a projection that smuggles in a
    relation the baseline does not have);
  * the raw database digest is only for zero-write/rollback/stutter checks;
  * SAFE and substitution histories must be checked automatically for every
    quantity except the exact candidate selected.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .core import canonical, columns_of, digest, foreign_keys_into

#: Harness surrogates that carry no authority content (section 23).
SURROGATE_COLUMNS = {
    "tx_id", "audit_seq", "attempt_seq", "binding_seq", "row_digest",
    "prev_row_digest", "created_at", "requested_at", "recorded_at", "opened_at",
    "settled_at", "consumed_at", "read_at", "before_digest", "after_digest",
}

#: Columns that whose name contains any of these tokens are candidate identity.
CANDIDATE_IDENTITY_TOKENS = ("candidate_id", "certificate_id", "used_candidate")


def project(state: Mapping[str, Any], *, declared: bool) -> dict:
    """Project an externally read state.

    ``declared=False`` keeps *every* column (the strongest possible comparison).
    ``declared=True`` drops harness surrogates, which is what the wall-clock
    robustness run needs (section 23).
    """
    out: dict[str, Any] = {}
    for table, spec in sorted(state["tables"].items()):
        keep = [i for i, column in enumerate(spec["columns"])
                if not (declared and column in SURROGATE_COLUMNS)]
        out[table] = {
            "columns": [spec["columns"][i] for i in keep],
            "rows": sorted(canonical([row[i] for i in keep]) for row in spec["rows"]),
        }
    return out


def projection_digest(state: Mapping[str, Any], *, declared: bool = True) -> str:
    return digest(project(state, declared=declared))


def candidate_identity_relations(db_path: Any) -> dict:
    """Every persisted path from an authority relation to an exact candidate.

    Section 46 asks whether the strengthened baseline *already* implements the
    obligation.  If any authority table names a candidate, the answer is yes and
    the experiment must stop and the baseline be reclassified.
    """
    fks = foreign_keys_into(db_path, "candidates", "candidate_id")
    columns: dict[str, list[str]] = {}
    tables = sorted({fk["from_table"] for fk in fks})
    for table in tables:
        columns[table] = columns_of(db_path, table)
    return {
        "foreign_keys_into_candidates": fks,
        "tables_referencing_candidates": tables,
        "implements_exact_candidate_relation": bool(fks),
    }


def infer_review_origin(state: Mapping[str, Any], handle: str) -> dict:
    """Test-side diagnostic (section 26): which candidates are *compatible* with
    the recorded authorization?

    ``UNIQUE_BY_RECORDED_CONSTRAINTS`` must never be reported as proof that a
    human reviewed that candidate (section 27); only Full's explicit
    authorization binding may be reported as ``EXPLICITLY_BOUND``.
    """
    tables = state["tables"]
    if "authorization_bindings" in tables:
        rows = [dict(zip(tables["authorization_bindings"]["columns"], row))
                for row in tables["authorization_bindings"]["rows"]]
        bound = sorted({row["certificate_id"] for row in rows if row["decision_id"] == handle})
        return {"status": "EXPLICITLY_BOUND" if bound else "NO_MATCH", "candidates": bound,
                "basis": "immutable authorization binding names the exact certificate"}
    if "approvals" not in tables:
        return {"status": "NOT_APPLICABLE", "candidates": [], "basis": "no authorization table"}
    approvals = [dict(zip(tables["approvals"]["columns"], row))
                 for row in tables["approvals"]["rows"]]
    approval = next((row for row in approvals if row["approval_id"] == handle), None)
    if approval is None:
        return {"status": "NO_MATCH", "candidates": [], "basis": "unknown authorization handle"}
    authorized = __import__("json").loads(approval["approved_values_json"])
    candidates = [dict(zip(tables["candidates"]["columns"], row))
                  for row in tables["candidates"]["rows"]]
    # The join a conventional audit log can actually make: record + field only.
    compatible = sorted(row["candidate_id"] for row in candidates
                        if row["record_id"] == approval["record_id"] and row["field"] in authorized)
    if not compatible:
        return {"status": "NO_MATCH", "candidates": [], "basis": "no candidate for record/field"}
    if len(compatible) == 1:
        return {"status": "UNIQUE_BY_RECORDED_CONSTRAINTS", "candidates": compatible,
                "basis": "record+field join is unique"}
    return {"status": "AMBIGUOUS", "candidates": compatible,
            "basis": "record+field join admits more than one candidate"}


def fairness_checks(*, safe_inputs: Mapping[str, Any], unsafe_inputs: Mapping[str, Any]) -> dict:
    """Automatic section 37 checks: only the selected candidate may differ."""
    invariants = [
        "candidate_registry_content", "target_record", "target_field", "authorized_value",
        "expected_predecessor_version", "observed_predecessor_version", "reviewer_principal",
        "baseline_visible_evidence", "baseline_visible_producer", "batch_semantics",
        "intended_authoritative_value",
    ]
    checks = []
    for name in invariants:
        left, right = safe_inputs.get(name), unsafe_inputs.get(name)
        checks.append({"invariant": name, "safe": left, "unsafe": right, "equal": left == right})
    selected_differs = safe_inputs.get("selected_candidate") != unsafe_inputs.get("selected_candidate")
    checks.append({"invariant": "selected_exact_candidate", "safe": safe_inputs.get("selected_candidate"),
                   "unsafe": unsafe_inputs.get("selected_candidate"), "equal": not selected_differs})
    return {
        "all_invariants_equal": all(check["equal"] for check in checks if check["invariant"] != "selected_exact_candidate"),
        "selected_candidate_differs": selected_differs,
        "checks": checks,
    }
