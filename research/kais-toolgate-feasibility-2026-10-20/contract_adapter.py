"""Eight development controls against the preserved C implementation.

This adapter constructs inputs and records the original implementation's
behavior. Admission remains in ReviewForms / SqlAlchemyFormRepository.
The caller must freeze the inputs and sources before executing cases.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import sys


HERE = Path(__file__).resolve().parent
SPRINT = HERE.parent / "kais-external-baseline-sprint-2026-10-15"
SUPPORTED_KINDS = {
    "accepted",
    "corrected",
    "reused_after_preview",
    "reauthorized",
    "instance_mismatch",
    "stale",
    "wrong_value",
    "unchanged_field_changed",
}


def _sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def _load_store():
    # stores verifies its 19 pinned original implementation sources on import.
    sys.path.insert(0, str(SPRINT))
    import stores

    if Path(stores.__file__).resolve() != (SPRINT / "stores.py").resolve():
        raise RuntimeError("An unrelated stores module is already loaded")
    return stores


def _register_second_candidate(store, handle):
    """Register a new identity with all original context fields preserved."""
    from reference import certificate

    packets = {}
    for field, original in handle["packets"].items():
        p = deepcopy(original)
        p["candidate_id"] = original["candidate_id"] + ":preview"
        p["id"] = certificate(p).certificate_id
        store._add(p)
        packets[field] = p
    return packets


def _reauthorize_registered(store, handle, packets, authorized):
    """Use original prepare to approve the already registered second instance."""
    ids = {field: p["id"] for field, p in packets.items()}
    approval = store.engine.prepare(
        handle["version"], {"address": deepcopy(authorized)}, deepcopy(ids)
    )
    updated = deepcopy(handle)
    updated["approval"] = approval
    updated["ids"] = deepcopy(ids)
    updated["candidate_ids"] = deepcopy(ids)
    updated["packets"] = deepcopy(packets)
    updated["preview"]["nonce"] = handle["preview"]["nonce"] + ":reauthorized"
    updated["preview"]["candidate_ids"] = deepcopy(ids)
    updated["preview"]["candidate_packets"] = deepcopy(packets)
    return updated


def run_case(case, outdir):
    """Run one input-only case and return JSON-serializable raw observations.

    No expected outcome is read. Each case gets a fresh, non-overwritable
    SQLite authority. Original grants, certificates and transitions are retained
    in the database as well as the before/after SQL dumps.
    """
    case_id = case["id"]
    kind = case["kind"]
    if not isinstance(case_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", case_id):
        raise ValueError("Case ID must be a safe filename component")
    if kind not in SUPPORTED_KINDS:
        raise ValueError(f"Unsupported development control: {kind}")
    initial = deepcopy(case["initial"])
    proposed = deepcopy(case["proposal"])
    authorized = deepcopy(case["authorized"])
    if set(initial) != {"address", "batch"}:
        raise ValueError("These controls require exactly address and batch")

    stores = _load_store()
    source_check = stores.verify_sources()
    outdir = Path(outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    db_path = outdir / f"{case_id}.sqlite"
    if db_path.exists():
        raise FileExistsError(f"Refuse to overwrite case authority: {db_path}")
    timestamp = datetime.now(timezone.utc)
    store = stores.Store("full", db_path, initial, timestamp=timestamp)
    events = []
    try:
        seed = store.snapshot()
        events.append({"stage": "seed", "state": deepcopy(seed)})
        handle = store.prepare(
            proposed, authorized, f"{case_id}:review", "development-correction-evidence"
        )
        first_reviewed = deepcopy(handle["ids"])
        first_preview = deepcopy(handle["preview"])
        events.append({
            "stage": "prepare",
            "reviewed_candidate_ids": deepcopy(first_reviewed),
            "preview": deepcopy(first_preview),
        })

        registered_preview = None
        if kind in {"reused_after_preview", "reauthorized"}:
            packets = _register_second_candidate(store, handle)
            registered_preview = deepcopy(packets)
            events.append({
                "stage": "register_context_identical_preview",
                "candidate_packets": deepcopy(packets),
                "original_candidate_ids": deepcopy(first_reviewed),
                "changes": ["candidate_id", "derived certificate id"],
            })
            if kind == "reauthorized":
                handle = _reauthorize_registered(store, handle, packets, authorized)
                events.append({
                    "stage": "reauthorize_registered_preview",
                    "reviewed_candidate_ids": deepcopy(handle["ids"]),
                    "preview": deepcopy(handle["preview"]),
                })

        if kind == "stale":
            concurrent = deepcopy(store.snapshot()["values"])
            concurrent["batch"] = "concurrent"
            external_outcome = store.external_change(concurrent)
            events.append({
                "stage": "independent_committed_update",
                "outcome": deepcopy(external_outcome),
                "state": store.snapshot(),
            })

        # For stale input, use the CURRENT complete values. Only the original
        # grant's predecessor is stale; batch is not accidentally overwritten.
        before = store.snapshot()
        sql_before = store.dump()
        actual = deepcopy(before["values"])
        actual["address"] = deepcopy(authorized)
        if kind == "wrong_value":
            actual["address"] = deepcopy(proposed)
        elif kind == "unchanged_field_changed":
            actual["batch"] = "unreviewed"

        candidate_swap = kind == "instance_mismatch"
        request = {
            "preview": deepcopy(handle["preview"]),
            "complete_successor": deepcopy(actual),
            "candidate_swap": candidate_swap,
            "first_reviewed_candidate_ids": deepcopy(first_reviewed),
            "reviewed_candidate_ids": deepcopy(handle["ids"]),
        }
        outcome = store.commit(handle, actual, candidate_swap=candidate_swap)
        after = store.snapshot()
        sql_after = store.dump()
        events.append({
            "stage": "attempt",
            "outcome": deepcopy(outcome),
            "state": deepcopy(after),
        })
        result = {
            "method": "C",
            "case_id": case_id,
            "kind": kind,
            "accepted": outcome["status"] == "COMMITTED",
            # Actual authority observation is distinct from the returned status.
            "committed": after["version"] > before["version"],
            "db_path": str(db_path),
            "timestamp_utc": timestamp.isoformat(),
            "before": before,
            "after": after,
            "sql_before": sql_before,
            "sql_after": sql_after,
            "reviewed_candidate_ids": deepcopy(outcome["reviewed_candidate_ids"]),
            "used_candidate_ids": deepcopy(outcome["used_candidate_ids"]),
            "first_reviewed_candidate_ids": first_reviewed,
            "registered_preview_packets": registered_preview,
            "request": request,
            "outcome": outcome,
            "events": events,
            "source_provenance": {
                "route": "stores.Store(full)",
                "admission": "original ReviewForms / SqlAlchemyFormRepository",
                "stores_path": str(SPRINT / "stores.py"),
                "stores_sha256": _sha256(SPRINT / "stores.py"),
                "reference_path": str(stores.SUPPLEMENT / "reference.py"),
                "reference_sha256": _sha256(stores.SUPPLEMENT / "reference.py"),
                "source_manifest_path": str(SPRINT / "contract-source-manifest.json"),
                "source_manifest_sha256": _sha256(SPRINT / "contract-source-manifest.json"),
                "pinned_source_check": source_check,
                "admission_verifier_modified": False,
                "hosted_model_calls": 0,
            },
        }
        # Fail loudly for an accidental ORM/domain object in the raw export.
        json.dumps(result, ensure_ascii=False, allow_nan=False)
        return result
    finally:
        store.close()
