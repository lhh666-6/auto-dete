"""The declared nine-case executable control, re-driven for the new policies.

The case *semantics* are the frozen ones: ``evidence/r27-standard-practice-baseline/
run_baseline.py`` (B0) and ``code/checklist-example/value_audit_demo.py`` (E0)
declare the same nine cases.  Nothing here is rewritten; the new policies are
driven through an equivalent action script so that outcomes stay comparable
with the frozen ``CANDIDATE_BOUND_REFERENCE`` (prompt v3.2 sections 12, 28, 53).
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping

from . import b0_bridge
from .core import Counter, DeterministicClock, canonical, digest, raw_state, rows_as_dicts, sha256_text
from .policies import (CANDIDATE_COLUMNS, POLICY_B1, POLICY_FULL, make_candidate,
                       open_policy, publish)

_B0 = b0_bridge.load_b0()

#: Reference outcomes of the candidate-bound policy, taken from the *frozen* B0
#: module (which in turn cites evidence/checklist-runs-verified-2026-09-09).
CANDIDATE_BOUND_REFERENCE = _B0.CANDIDATE_BOUND_REFERENCE
CASE_SPECS = _B0.CASE_SPECS

RECORD_ID = "R1"
INITIAL_VALUES = {"quantity": 90, "batch": "A"}

#: One shared crop/model invocation for the two equal-valued candidates: the
#: evidence *content* is byte-identical and only the storage locator differs
#: (the favourable case for a content-snapshot baseline; see the O1 note in the
#: Phase 1 report -- whether production PNG encoding is deterministic is
#: UNVERIFIED, which is why E1 is run in both variants).
SHARED_EVIDENCE_HASH = sha256_text("crop-bytes/R1/quantity/<pinned-crop>")


def build_registry(clock: Callable[[], str], *, distinct_evidence_hash: bool = False) -> list[dict]:
    """The declared candidate pool.

    ``candidate_id`` is *content-addressed*, exactly as production does
    (``app/domain/authority.py:251-273``): the address covers ``created_at`` and
    the evidence locator, so two independently generated candidates can never be
    byte-identical-yet-distinct.  ``handle`` is the human-facing name used by the
    paper's supplement (``q100a``/``q100b``) and is a *test-side* label only.
    """
    second_hash = sha256_text("crop-bytes/R1/quantity/<pinned-crop>#re-encode") \
        if distinct_evidence_hash else SHARED_EVIDENCE_HASH
    specs = [
        dict(handle="q100a", record_id=RECORD_ID, field="quantity", proposed_json="100",
             producer_id="detector-v1", producer_version="1.0.0",
             selection_artifact_id="SEL-1", expected_fact_version=0,
             evidence_hash=SHARED_EVIDENCE_HASH, evidence_locator="blob://evidence/q100a",
             created_at="2026-09-09T12:00:01.000000+00:00"),
        dict(handle="q100b", record_id=RECORD_ID, field="quantity", proposed_json="100",
             producer_id="detector-v1", producer_version="1.0.0",
             selection_artifact_id="SEL-1", expected_fact_version=0,
             evidence_hash=second_hash, evidence_locator="blob://evidence/q100b",
             created_at="2026-09-09T12:00:02.000000+00:00"),
        dict(handle="q101", record_id=RECORD_ID, field="quantity", proposed_json="101",
             producer_id="detector-v1", producer_version="1.0.0",
             selection_artifact_id="SEL-1", expected_fact_version=0,
             evidence_hash=sha256_text("crop-bytes/R1/quantity/101"),
             evidence_locator="blob://evidence/q101",
             created_at="2026-09-09T12:00:03.000000+00:00"),
        dict(handle="other100", record_id="R2", field="quantity", proposed_json="100",
             producer_id="detector-v1", producer_version="1.0.0",
             selection_artifact_id="SEL-2", expected_fact_version=0,
             evidence_hash=sha256_text("crop-bytes/R2/quantity/100"),
             evidence_locator="blob://evidence/other100",
             created_at="2026-09-09T12:00:04.000000+00:00"),
        dict(handle="batchB", record_id=RECORD_ID, field="batch", proposed_json='"B"',
             producer_id="detector-v1", producer_version="1.0.0",
             selection_artifact_id="SEL-3", expected_fact_version=0,
             evidence_hash=sha256_text("crop-bytes/R1/batch/B"),
             evidence_locator="blob://evidence/batchB",
             created_at="2026-09-09T12:00:05.000000+00:00"),
    ]
    return make_candidate(clock, specs)


def handle_map(specs: list[dict], rows: list[dict]) -> dict[str, str]:
    """test-side ``handle -> persisted candidate_id`` map (never inside a policy)."""
    return {spec["handle"]: row["candidate_id"] for spec, row in zip(specs, rows)}


def registry_with_handles(clock, **kwargs) -> tuple[list[dict], dict[str, str]]:
    specs, handles = [], {}
    rows = build_registry(clock, **kwargs)
    # ``build_registry`` keeps the declared order, so re-derive the handle order.
    from .policies import CANDIDATE_CONTENT_FIELDS
    order = ["q100a", "q100b", "q101", "other100", "batchB"]
    for name, row in zip(order, rows):
        handles[name] = row["candidate_id"]
    return rows, handles


def new_policy(policy: str, path: Path, *, clock, distinct_evidence_hash: bool = False,
               variant: str | None = None):
    rows, handles = registry_with_handles(clock, distinct_evidence_hash=distinct_evidence_hash)
    kwargs = dict(candidates=rows, initial_values=INITIAL_VALUES, clock=clock,
                  tx_ids=Counter("TX"), record_id=RECORD_ID)
    if variant is not None:
        from .policies import TransactionalValueAuditBaseline
        obj = TransactionalValueAuditBaseline(path, variant=variant, **kwargs)
    else:
        obj = open_policy(policy, path, **kwargs)
    return obj, handles


def observations_of(state: dict) -> dict:
    """The post-state observations both harnesses report (B0-compatible naming)."""
    return {
        "successor_values": json.loads(rows_as_dicts(state, "records")[0]["values_json"]),
        "audit_rows": len(rows_as_dicts(state, "audits")),
        "stored_sources": _stored_sources(state),
        "reconstructed_sources": _B0.reconstruct_sources(state),
        "proposal_attribution": _B0.proposal_attribution(state)
        if "approvals" in state["tables"] else None,
    }


def _stored_sources(state: dict) -> dict | None:
    if "fact_sources" not in state["tables"]:
        return None
    rows = rows_as_dicts(state, "fact_sources")
    return {row["field"]: f"v{row['source_version']}:{row['field']}" for row in rows}


# --------------------------------------------------------------------------
# the nine declared cases
# --------------------------------------------------------------------------

def run_all_cases(policy: str, out_dir: Path, *, variant: str | None = None,
                  distinct_evidence_hash: bool = False) -> tuple[list[dict], list[dict]]:
    """Run the nine declared cases for one policy, writing one database per case."""
    out_dir = Path(out_dir)
    if out_dir.exists():
        raise FileExistsError(f"Refusing to replace prior evidence: {out_dir}")
    (out_dir / "db").mkdir(parents=True)
    policy_tag = variant or policy
    runs: list[dict] = []
    dbs: list[dict] = []

    def fresh(case_id, suffix=""):
        clock = DeterministicClock()
        db = out_dir / "db" / f"{case_id}__{policy_tag}{suffix}.db"
        if db.exists():
            raise FileExistsError(f"Refusing to replace prior evidence: {db}")
        obj, cand = new_policy(policy, db, clock=clock,
                               distinct_evidence_hash=distinct_evidence_hash, variant=variant)
        return obj, cand, db, clock

    # 1. legal correction
    obj, cand, db, clock = fresh("legal-correction")
    publish(obj, "review-1", {"quantity": cand["q100a"]}, {"quantity": 101})
    pre = raw_state(db)
    result = obj.submit("review-1", {"quantity": cand["q100a"]}, {"quantity": 101})
    post = raw_state(db)
    obj.close()
    runs.append(_record("legal-correction", policy_tag,
                        [{"action": "approve", "candidate": {"quantity": "q100a"}, "values": {"quantity": 101}},
                         {"action": "submit", "candidate": {"quantity": "q100a"}, "values": {"quantity": 101}}],
                        result, pre, post, db, observations_of(post)))
    dbs.append(_db_record(case_id="legal-correction", policy=policy_tag, db=db, pre=pre, post=post))

    # 2. equal-valued substitution
    obj, cand, db, clock = fresh("equal-value-substitution")
    publish(obj, "review-1", {"quantity": cand["q100a"]}, {"quantity": 101})
    pre = raw_state(db)
    result = obj.submit("review-1", {"quantity": cand["q100b"]}, {"quantity": 101})
    post = raw_state(db)
    obj.close()
    runs.append(_record("equal-value-substitution", policy_tag,
                        [{"action": "approve", "candidate": {"quantity": "q100a"}, "values": {"quantity": 101}},
                         {"action": "submit", "candidate": {"quantity": "q100b"}, "values": {"quantity": 101}}],
                        result, pre, post, db,
                        {**observations_of(post),
                         "reviewed_candidate": "q100a", "submitted_candidate": "q100b",
                         "reviewed_candidate_persisted": False,
                         "accepted_substitute": bool(result["accepted"])}))
    dbs.append(_db_record(case_id="equal-value-substitution", policy=policy_tag, db=db, pre=pre, post=post))

    # 3. cross-record candidate
    obj, cand, db, clock = fresh("cross-record-candidate")
    publish(obj, "review-1", {"quantity": cand["q100a"]}, {"quantity": 101})
    pre = raw_state(db)
    result = obj.submit("review-1", {"quantity": cand["other100"]}, {"quantity": 101})
    post = raw_state(db)
    obj.close()
    runs.append(_record("cross-record-candidate", policy_tag,
                        [{"action": "approve", "candidate": {"quantity": "q100a"}, "values": {"quantity": 101}},
                         {"action": "submit", "candidate": {"quantity": "other100"}, "values": {"quantity": 101}}],
                        result, pre, post, db,
                        {"reviewed_candidate": "q100a", "submitted_candidate": "other100",
                         "submitted_record": "R2"}))
    dbs.append(_db_record(case_id="cross-record-candidate", policy=policy_tag, db=db, pre=pre, post=post))

    # 4. stale version
    obj, cand, db, clock = fresh("stale-version")
    publish(obj, "review-1", {"quantity": cand["q100a"]}, {"quantity": 101})
    publish(obj, "intervening", {"batch": cand["batchB"]}, {"batch": "B"})
    first = obj.submit("intervening", {"batch": cand["batchB"]}, {"batch": "B"})
    pre = raw_state(db)
    result = obj.submit("review-1", {"quantity": cand["q100a"]}, {"quantity": 101})
    post = raw_state(db)
    obj.close()
    runs.append(_record("stale-version", policy_tag,
                        [{"action": "approve", "candidate": {"quantity": "q100a"}, "values": {"quantity": 101}},
                         {"action": "intervening commit", "candidate": {"batch": "batchB"}, "values": {"batch": "B"}},
                         {"action": "submit", "candidate": {"quantity": "q100a"},
                          "values": {"quantity": 101}, "note": "approved at version 0"}],
                        result, pre, post, db,
                        {"intervening_commit_accepted": bool(first["accepted"]),
                         "expected_version": 0,
                         "version_after_intervening": rows_as_dicts(post, "records")[0]["version"]}))
    dbs.append(_db_record(case_id="stale-version", policy=policy_tag, db=db, pre=pre, post=post))

    # 5. wrong value
    obj, cand, db, clock = fresh("wrong-value")
    publish(obj, "review-1", {"quantity": cand["q100a"]}, {"quantity": 101})
    pre = raw_state(db)
    result = obj.submit("review-1", {"quantity": cand["q100a"]}, {"quantity": 102})
    post = raw_state(db)
    obj.close()
    runs.append(_record("wrong-value", policy_tag,
                        [{"action": "approve", "candidate": {"quantity": "q100a"}, "values": {"quantity": 101}},
                         {"action": "submit", "candidate": {"quantity": "q100a"}, "values": {"quantity": 102}}],
                        result, pre, post, db, {"approved_value": 101, "submitted_value": 102}))
    dbs.append(_db_record(case_id="wrong-value", policy=policy_tag, db=db, pre=pre, post=post))

    # 6. partial batch
    obj, cand, db, clock = fresh("partial-batch")
    publish(obj, "review-1", {"quantity": cand["q100a"], "batch": cand["batchB"]},
            {"quantity": 101, "batch": "B"})
    pre = raw_state(db)
    result = obj.submit("review-1", {"quantity": cand["q100a"]}, {"quantity": 101})
    post = raw_state(db)
    obj.close()
    runs.append(_record("partial-batch", policy_tag,
                        [{"action": "approve", "candidate": {"quantity": "q100a", "batch": "batchB"},
                          "values": {"quantity": 101, "batch": "B"}},
                         {"action": "submit", "candidate": {"quantity": "q100a"}, "values": {"quantity": 101}}],
                        result, pre, post, db,
                        {"approved_fields": ["quantity", "batch"], "submitted_fields": ["quantity"],
                         "omitted_field": "batch"}))
    dbs.append(_db_record(case_id="partial-batch", policy=policy_tag, db=db, pre=pre, post=post))

    # 7. injected failure
    obj, cand, db, clock = fresh("injected-failure")
    publish(obj, "review-1", {"quantity": cand["q100a"]}, {"quantity": 101})
    pre = raw_state(db)
    result = obj.submit("review-1", {"quantity": cand["q100a"]}, {"quantity": 101},
                        fail_after_writes=True)
    post = raw_state(db)
    obj.close()
    runs.append(_record("injected-failure", policy_tag,
                        [{"action": "approve", "candidate": {"quantity": "q100a"}, "values": {"quantity": 101}},
                         {"action": "submit", "candidate": {"quantity": "q100a"}, "values": {"quantity": 101},
                          "note": "injected failure after writes, before commit"}],
                        result, pre, post, db,
                        {"injected_after": "CAS update, version insert, audit insert, source map, "
                                           "consumption and attempt rows",
                         "tables_compared": sorted(pre["tables"])}))
    dbs.append(_db_record(case_id="injected-failure", policy=policy_tag, db=db, pre=pre, post=post))

    # 8. two-step copy-forward
    obj, cand, db, clock = fresh("two-step-copy-forward")
    publish(obj, "review-1", {"quantity": cand["q100a"]}, {"quantity": 101})
    first = obj.submit("review-1", {"quantity": cand["q100a"]}, {"quantity": 101})
    publish(obj, "review-2", {"batch": cand["batchB"]}, {"batch": "B"})
    pre = raw_state(db)
    second = obj.submit("review-2", {"batch": cand["batchB"]}, {"batch": "B"})
    post = raw_state(db)
    obj.close()
    recon = _B0.reconstruct_sources(post)
    stored = _stored_sources(post)
    runs.append(_record("two-step-copy-forward", policy_tag,
                        [{"action": "commit", "candidate": {"quantity": "q100a"}, "values": {"quantity": 101}},
                         {"action": "commit", "candidate": {"batch": "batchB"}, "values": {"batch": "B"},
                          "note": "quantity is unchanged and must copy forward"}],
                        second, pre, post, db,
                        {**observations_of(post),
                         "first_step_accepted": bool(first["accepted"]),
                         "second_step_accepted": bool(second["accepted"]),
                         "stored_matches_reconstruction": None if stored is None else stored == recon,
                         "successor_versions": [v["version"] for v in rows_as_dicts(post, "versions")]}))
    dbs.append(_db_record(case_id="two-step-copy-forward", policy=policy_tag, db=db, pre=pre, post=post))

    # 9. paired reviewed-candidate histories
    per_candidate = {}
    for name in ("q100a", "q101"):
        obj, cand, db, clock = fresh("paired-reviewed-candidate", suffix=f"-{name}")
        publish(obj, "review-1", {"quantity": cand[name]}, {"quantity": 101})
        result = obj.submit("review-1", {"quantity": cand[name]}, {"quantity": 101})
        per_candidate[name] = {"observed": {"accepted": bool(result["accepted"]),
                                            "reason": result.get("reason")},
                               "state": raw_state(db), "database_file": db.name}
        obj.close()
    left = per_candidate["q100a"]["state"]["tables"]
    right = per_candidate["q101"]["state"]["tables"]
    differing = [table for table in sorted(left) if left[table] != right[table]]
    runs.append({
        "case_id": "paired-reviewed-candidate", "policy": policy_tag,
        "requested_action": [
            {"action": "approve+submit", "candidate": "q100a", "values": {"quantity": 101}},
            {"action": "approve+submit", "candidate": "q101", "values": {"quantity": 101}},
            {"note": "identical candidate pools, values, actor, and expected version"}],
        "observed": {"states_equal": not differing, "differing_tables": differing},
        "state_unchanged": None,
        "observations": {"reviewed_candidates": ["q100a", "q101"],
                         "candidate_proposed_values": {"q100a": 100, "q101": 101},
                         "authorized_value": 101,
                         "reviewed_candidate_persisted": False,
                         "paired_histories_distinguishable": bool(differing)},
        "database_file": [per_candidate[c]["database_file"] for c in ("q100a", "q101")],
        "runs": per_candidate,
    })
    for name in ("q100a", "q101"):
        dbs.append(_db_record(case_id="paired-reviewed-candidate",
                              policy=policy_tag,
                              db=out_dir / "db" / per_candidate[name]["database_file"],
                              pre=None, post=per_candidate[name]["state"], suffix=f"-{name}"))
    return runs, dbs


def _record(case_id, policy, requested, result, pre, post, db, observations):
    return {
        "case_id": case_id, "policy": policy, "requested_action": requested,
        "observed": {"accepted": bool(result["accepted"]), "reason": result.get("reason")},
        "state_unchanged": pre["tables"] == post["tables"],
        "observations": observations,
        "database_file": Path(db).name,
    }


def _db_record(*, case_id, policy, db, pre, post, suffix=""):
    return {
        "case_id": case_id, "policy": policy, "database_file": Path(db).name,
        "suffix": suffix,
        "pre_state_digest": None if pre is None else digest(pre["tables"]),
        "post_state_digest": digest(post["tables"]),
        "post_state": post,
        "file_digest": None,
    }


def compare_with_reference(runs: list[dict]) -> dict:
    """Same comparison B0 performs against the frozen candidate-bound reference."""
    by_case = {r["case_id"]: r for r in runs}
    agreed, divergent = [], []
    for case_id, reference in CANDIDATE_BOUND_REFERENCE.items():
        record = by_case[case_id]
        if case_id == "paired-reviewed-candidate":
            observed = {"states_equal": record["observed"]["states_equal"]}
        else:
            observed = {"accepted": record["observed"]["accepted"],
                        "reason": record["observed"]["reason"]}
        (agreed if observed == reference else divergent).append(case_id)
    return {"agreement": agreed, "divergence": divergent,
            "reference": CANDIDATE_BOUND_REFERENCE,
            "observed": {cid: ({"states_equal": by_case[cid]["observed"]["states_equal"]}
                               if cid == "paired-reviewed-candidate"
                               else {"accepted": by_case[cid]["observed"]["accepted"],
                                     "reason": by_case[cid]["observed"]["reason"]})
                         for cid in CANDIDATE_BOUND_REFERENCE}}
