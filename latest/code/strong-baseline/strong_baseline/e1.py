"""E1: the identity-isolation control.

The concrete analogue of the formal witness ``candidate_identity_pair``
(``code/formal-witness/observation-witnesses.py`` /
``evidence/r27-witness/observation-witness-report-v5.json``):

* one candidate registry holding two equal-valued, same-context candidates
  ``A`` (``q100a``) and ``B`` (``q100b``);
* SAFE history: the human reviews A and admission selects A;
* UNSAFE history: the human reviews A and admission selects B.

The only thing that may differ between the two histories is *which exact
candidate the admission step selected*.  The review oracle is test-side only
(section 19) and is never written into any policy database.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from . import policies
from .analysis import (candidate_identity_relations, infer_review_origin,
                       project, projection_digest)
from .core import (Counter, DeterministicClock, WallClock, canonical, columns_of,
                   diff_tables, digest, raw_state, rows_as_dicts)
from .policies import REVIEW_CONTEXT_FIELDS, candidate_content_hash
from .cases import INITIAL_VALUES, RECORD_ID, new_policy

CASE_ID = "identity-isolation-substitution"
FAMILY = "E1_IDENTITY_ISOLATION"
REVIEW_HANDLE = "review-1"
REVIEWED_HANDLE = "q100a"
SUBSTITUTE_HANDLE = "q100b"
AUTHORIZED_VALUE = {"quantity": 101}
AUTHORIZED_JSON = canonical(AUTHORIZED_VALUE)


def _pair_rows(state: Mapping[str, Any]) -> dict[str, dict]:
    return {row["candidate_id"]: row
            for row in (dict(zip(state["tables"]["candidates"]["columns"], r))
                        for r in state["tables"]["candidates"]["rows"])}


def pair_difference_table(state: Mapping[str, Any], id_a: str, id_b: str) -> dict:
    """Section 16 step 2/3: per-field physical difference of the two candidates."""
    rows = _pair_rows(state)
    a, b = rows[id_a], rows[id_b]
    table: dict[str, dict] = {}
    for field in sorted(a):
        table[field] = {"A": a[field], "B": b[field], "equal": a[field] == b[field]}
    return table


def field_visibility(state_safe: Mapping[str, Any], state_unsafe: Mapping[str, Any],
                     table: Mapping[str, Mapping[str, Any]]) -> dict:
    """Section 16 step 3: for each differing field, does the policy see it, and
    does it discriminate the two histories?"""
    proj_safe = project(state_safe, declared=True)
    proj_unsafe = project(state_unsafe, declared=True)
    tables = sorted(state_safe["tables"])
    owned = {t: columns_of_names(state_safe, t) for t in tables}
    out: dict[str, dict] = {}
    for field, spec in table.items():
        if spec["equal"]:
            out[field] = {"differs_in_pair": False, "stored_by_policy": None,
                          "owner_tables": [], "discriminates_histories": False,
                          "verdict": "identical in both candidates"}
            continue
        owners = [t for t in tables if field in owned[t]]
        discriminates = any(proj_safe[t] != proj_unsafe[t] for t in owners)
        out[field] = {
            "differs_in_pair": True,
            "stored_by_policy": bool(owners),
            "owner_tables": owners,
            "discriminates_histories": discriminates,
            "verdict": ("side channel: the field differs between SAFE and UNSAFE"
                        if discriminates else
                        "no candidate-level discriminating power: the field is stored "
                        "only inside a registry that is identical in both histories"),
        }
    return out


def columns_of_names(state: Mapping[str, Any], table: str) -> list[str]:
    return list(state["tables"][table]["columns"])


def _content_signature(row: Mapping[str, Any]) -> dict:
    return {key: row[key] for key in REVIEW_CONTEXT_FIELDS}


def _run_history(policy: str, variant: str | None, db: Path, *, admission_handle: str,
                 clock_kind: str, distinct_evidence_hash: bool) -> dict:
    clock = DeterministicClock() if clock_kind == "deterministic" else WallClock()
    obj, handles = new_policy(policy, db, clock=clock,
                              distinct_evidence_hash=distinct_evidence_hash, variant=variant)
    reviewed = handles[REVIEWED_HANDLE]
    admitted = handles[admission_handle]
    policies.publish(obj, REVIEW_HANDLE, {"quantity": reviewed}, AUTHORIZED_VALUE)
    pre = raw_state(db)
    expected_version = rows_as_dicts(pre, "records")[0]["version"]
    result = obj.submit(REVIEW_HANDLE, {"quantity": admitted}, AUTHORIZED_VALUE)
    post = raw_state(db)
    obj.close()
    return {
        "reviewed_candidate": reviewed,
        "admission_selected_candidate": admitted,
        "reviewed_handle": REVIEWED_HANDLE,
        "admission_selected_handle": admission_handle,
        "expected_predecessor_version": expected_version,
        "observed_predecessor_version": expected_version,
        "observed": {"accepted": bool(result["accepted"]), "reason": result.get("reason")},
        "state_unchanged": pre["tables"] == post["tables"],
        "pre_state": pre,
        "post_state": post,
        "database_file": db.name,
        "different_evidence_hash": distinct_evidence_hash,
    }


def run(case_dir: Path, *, policy: str, variant: str | None = None,
        clock_kind: str = "deterministic", distinct_evidence_hash: bool = False,
        admission_handle: str = SUBSTITUTE_HANDLE) -> dict:
    case_dir = Path(case_dir)
    case_dir.mkdir(parents=True, exist_ok=True)
    tag = variant or policy
    safe_db = case_dir / f"{CASE_ID}__{tag}__safe.db"
    unsafe_db = case_dir / f"{CASE_ID}__{tag}__unsafe.db"
    for path in (safe_db, unsafe_db):
        if path.exists():
            raise FileExistsError(f"Refusing to replace prior evidence: {path}")

    safe = _run_history(policy, variant, safe_db, admission_handle=REVIEWED_HANDLE,
                        clock_kind=clock_kind, distinct_evidence_hash=distinct_evidence_hash)
    unsafe = _run_history(policy, variant, unsafe_db, admission_handle=admission_handle,
                          clock_kind=clock_kind, distinct_evidence_hash=distinct_evidence_hash)

    raw_diff = diff_tables(safe["post_state"], unsafe["post_state"])
    proj_safe = project(safe["post_state"], declared=True)
    proj_unsafe = project(unsafe["post_state"], declared=True)
    proj_diff = {table: "differs" for table in sorted(proj_safe)
                 if proj_safe[table] != proj_unsafe[table]}

    pair = pair_difference_table(safe["pre_state"], safe["reviewed_candidate"],
                                 unsafe["admission_selected_candidate"])
    visibility = field_visibility(safe["post_state"], unsafe["post_state"], pair)
    relation = candidate_identity_relations(safe_db)

    origin = {name: infer_review_origin(history["post_state"], REVIEW_HANDLE)
              for name, history in (("safe", safe), ("unsafe", unsafe))}

    record = {
        "experiment_family": FAMILY,
        "case_id": CASE_ID,
        "policy": tag,
        "variant": variant,
        "clock": clock_kind,
        "expected_outcome": {"safe": "accept", "unsafe": "dependent on the exact binding"},
        "actual_outcome": {"safe": safe["observed"], "unsafe": unsafe["observed"]},
        "authoritative_state_changed": {
            "safe": not safe["state_unchanged"] and safe["observed"]["accepted"],
            "unsafe": not unsafe["state_unchanged"] and unsafe["observed"]["accepted"],
        },
        "before_version": {"safe": safe["expected_predecessor_version"],
                           "unsafe": unsafe["expected_predecessor_version"]},
        "after_version": {
            "safe": rows_as_dicts(safe["post_state"], "records")[0]["version"],
            "unsafe": rows_as_dicts(unsafe["post_state"], "records")[0]["version"]},
        "authorized_value": AUTHORIZED_VALUE,
        "committed_value": {
            "safe": json.loads(rows_as_dicts(safe["post_state"], "records")[0]["values_json"]),
            "unsafe": json.loads(rows_as_dicts(unsafe["post_state"], "records")[0]["values_json"])},
        "candidate_pool": sorted(pair),
        "selected_candidate_if_recorded": {
            "safe": _recorded_selection(safe["post_state"]),
            "unsafe": _recorded_selection(unsafe["post_state"])},
        "review_origin_status": origin,
        "source_reconstruction_status": {
            "safe": _sources(safe["post_state"]), "unsafe": _sources(unsafe["post_state"])},
        "trace_status": {"safe": "complete" if safe["observed"]["accepted"] else "none",
                         "unsafe": "complete" if unsafe["observed"]["accepted"] else "none"},
        "database_digest_before": {"safe": digest(safe["pre_state"]["tables"]),
                                   "unsafe": digest(unsafe["pre_state"]["tables"])},
        "database_digest_after": {"safe": digest(safe["post_state"]["tables"]),
                                  "unsafe": digest(unsafe["post_state"]["tables"])},
        "semantic_projection_hash": {
            "declared": {"safe": projection_digest(safe["post_state"], declared=True),
                         "unsafe": projection_digest(unsafe["post_state"], declared=True)},
            "full": {"safe": projection_digest(safe["post_state"], declared=False),
                     "unsafe": projection_digest(unsafe["post_state"], declared=False)}},
        "histories": {"safe": safe, "unsafe": unsafe},
        "comparison": {
            "raw_differing_tables": sorted(raw_diff),
            "declared_projection_differing_tables": sorted(proj_diff),
            "histories_indistinguishable_under_declared_projection": not proj_diff,
            "candidate_identity_relations": relation,
        },
        "candidate_pair_difference_table": pair,
        "candidate_pair_field_visibility": visibility,
        "ground_truth_review_target": REVIEWED_HANDLE,          # test-side only
        "attempted_admission_candidate": admission_handle,      # test-side only
        "pass": None,
        "notes": [],
    }
    record["fairness"] = fairness(record, distinct_evidence_hash=distinct_evidence_hash)
    record["observation_equivalence"] = {
        "pair_content_equivalent": record["fairness"]["evidence_hash_shared_between_pair"],
        "pair_differs_only_in": record["fairness"]["pair_differs_only_in"],
        "declared_projection_indistinguishable": not proj_diff,
        "reading": (
            "The two candidates are indistinguishable in every baseline-visible respect "
            "except their content-addressed identity."
            if record["fairness"]["evidence_hash_shared_between_pair"] else
            "The two candidates additionally differ in evidence content, so a baseline "
            "that snapshots reviewed content (B2) can separate them.  This is the "
            "unfavourable variant and the conclusion is reported separately."),
    }
    record["pass"] = record["fairness"]["all_invariants_equal"] and \
        record["fairness"]["selected_candidate_differs"]
    return record


def _recorded_selection(state: Mapping[str, Any]) -> Any:
    """Whatever the policy persisted about the candidate admission actually used."""
    tables = state["tables"]
    if "admission_attempts" not in tables:
        return None
    columns = tables["admission_attempts"]["columns"]
    if "used_candidate_json" not in columns:
        return "NOT_RECORDED"
    idx = columns.index("used_candidate_json")
    return [row[idx] for row in tables["admission_attempts"]["rows"]]


def _sources(state: Mapping[str, Any]) -> Any:
    if "fact_sources" not in state["tables"]:
        return None
    return {row["field"]: f"v{row['source_version']}:{row['field']}"
            for row in rows_as_dicts(state, "fact_sources")}


def fairness(record: Mapping[str, Any], *, distinct_evidence_hash: bool) -> dict:
    """Section 37 automatic checks."""
    safe, unsafe = record["histories"]["safe"], record["histories"]["unsafe"]
    pool = _pair_rows(safe["pre_state"])
    a = pool[safe["reviewed_candidate"]]
    b = pool[unsafe["admission_selected_candidate"]]
    signature = sorted(canonical(_content_signature(row)) for row in pool.values())

    def invariants(history):
        return {
            "candidate_registry_content": signature,
            "target_record": RECORD_ID,
            "target_field": "quantity",
            "authorized_value": AUTHORIZED_VALUE,
            "expected_predecessor_version": history["expected_predecessor_version"],
            "observed_predecessor_version": history["observed_predecessor_version"],
            "reviewer_principal": REVIEW_HANDLE,
            "baseline_visible_evidence": {
                "content_hash_shared": a["evidence_hash"] == b["evidence_hash"],
                "a": a["evidence_hash"], "b": b["evidence_hash"]},
            "baseline_visible_producer": {
                "producer_id": a["producer_id"], "producer_version": a["producer_version"],
                "selection_artifact_id": a["selection_artifact_id"]},
            "batch_semantics": "single-field batch {quantity: <candidate>}",
            "intended_authoritative_value": canonical({**INITIAL_VALUES, **AUTHORIZED_VALUE}),
            "selected_candidate": history["admission_selected_candidate"],
        }

    from .analysis import fairness_checks
    result = fairness_checks(safe_inputs=invariants(safe), unsafe_inputs=invariants(unsafe))
    result["evidence_hash_shared_between_pair"] = a["evidence_hash"] == b["evidence_hash"]
    result["evidence_hash_variant_requested_distinct"] = distinct_evidence_hash
    result["pair_differs_only_in"] = sorted(
        field for field, spec in record["candidate_pair_difference_table"].items()
        if not spec["equal"])
    result["note"] = (
        "SAFE and UNSAFE differ in exactly one input: the candidate handle passed to "
        "admission. Everything the baseline can observe about the two candidates "
        "(value, record, field, producer, producer version, selection artifact, expected "
        "version, and evidence content when the hashes coincide) is equal by construction."
    )
    return result
