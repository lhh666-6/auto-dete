"""Public-order boundary controls using the preserved C admission engine.

The supplied callback invokes the native Retail tool on an isolated clone and
returns its complete proposed order. This module passes that order to the
original C implementation and retains each attempt, including a rejected first
attempt. It implements no replacement admission verifier.
"""
from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
import importlib.util
import json
from pathlib import Path
import re


HERE = Path(__file__).resolve().parent
PREVIOUS_ADAPTER = (
    HERE.parent / "kais-toolgate-feasibility-2026-10-20" / "contract_adapter.py"
)
SUPPORTED_KINDS = {
    "corrected",
    "reauthorized",
    "instance_mismatch",
    "wrong_value",
}


def _load_helpers():
    """Reuse input construction from the frozen development adapter."""
    spec = importlib.util.spec_from_file_location(
        "_kais_preserved_c_development_adapter", PREVIOUS_ADAPTER
    )
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load preserved adapter: {PREVIOUS_ADAPTER}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run_case(case, outdir, draft_callback):
    """Run an input-only control against a fresh, non-overwritable authority.

    ``draft_callback(address)`` must return a complete JSON-serializable public
    order from the original native tool operating on a clone. A scripted second
    attempt is permitted only after an actual rejection with unchanged business
    state; no error or unexpected successful first attempt triggers recovery.
    """
    case_id = case["id"]
    kind = case["kind"]
    if not isinstance(case_id, str) or not re.fullmatch(r"[A-Za-z0-9_-]+", case_id):
        raise ValueError("Case ID must be a safe filename component")
    if kind not in SUPPORTED_KINDS:
        raise ValueError(f"Unsupported public boundary control: {kind}")
    initial_order = deepcopy(case["initial"])
    proposal = deepcopy(case["proposal"])
    authorized = deepcopy(case["authorized"])
    if not isinstance(initial_order, dict) or "address" not in initial_order:
        raise ValueError("A complete public order with address is required")
    if not callable(draft_callback):
        raise TypeError("draft_callback must be callable")

    helpers = _load_helpers()
    stores = helpers._load_store()
    source_check = stores.verify_sources()
    outdir = Path(outdir).resolve()
    outdir.mkdir(parents=True, exist_ok=True)
    db_path = outdir / f"{case_id}.sqlite"
    if db_path.exists():
        raise FileExistsError(f"Refuse to overwrite case authority: {db_path}")
    timestamp = datetime.now(timezone.utc)
    store = stores.Store("full", db_path, initial_order, timestamp=timestamp)
    attempts = []
    events = []
    try:
        initial = store.snapshot()
        events.append({"stage": "seed", "state": deepcopy(initial)})
        handle = store.prepare(
            proposal,
            authorized,
            f"{case_id}:review",
            "public-reference-correction-evidence",
        )
        first_reviewed = deepcopy(handle["ids"])
        events.append({
            "stage": "prepare",
            "preview": deepcopy(handle["preview"]),
            "reviewed_candidate_ids": deepcopy(first_reviewed),
        })

        if kind == "reauthorized":
            packets = helpers._register_second_candidate(store, handle)
            events.append({
                "stage": "register_context_identical_preview",
                "candidate_packets": deepcopy(packets),
                "original_candidate_ids": deepcopy(first_reviewed),
                "changes": ["candidate_id", "derived certificate id"],
            })
            handle = helpers._reauthorize_registered(
                store, handle, packets, authorized
            )
            events.append({
                "stage": "reauthorize_registered_preview",
                "preview": deepcopy(handle["preview"]),
                "reviewed_candidate_ids": deepcopy(handle["ids"]),
            })

        def attempt(address, *, candidate_swap, phase):
            before = store.snapshot()
            sql_before = store.dump()
            actual = None
            outcome = None
            callback_completed = False
            try:
                draft = draft_callback(deepcopy(address))
                callback_completed = True
                if not isinstance(draft, dict):
                    raise TypeError("Native draft callback must return a complete order dict")
                actual = json.loads(
                    json.dumps(draft, ensure_ascii=False, allow_nan=False)
                )
                # All unchanged fields come from the original native-tool
                # result. C's original repository checks the complete record.
                outcome = store.commit(
                    handle, actual, candidate_swap=candidate_swap
                )
            except Exception as exc:
                # Adapter/callback errors are retained but never interpreted as
                # policy rejections or used to initiate a second attempt.
                outcome = {
                    "status": "ENGINEERING_ERROR",
                    "reason": str(exc),
                    "error_type": type(exc).__name__,
                    "reviewed_candidate_ids": deepcopy(handle["ids"]),
                    "used_candidate_ids": None,
                }
            after = store.snapshot()
            sql_after = store.dump()
            request = {
                "address": deepcopy(address),
                "preview": deepcopy(handle["preview"]),
                "complete_successor": deepcopy(actual),
                "candidate_swap": candidate_swap,
                "first_reviewed_candidate_ids": deepcopy(first_reviewed),
                "reviewed_candidate_ids": deepcopy(handle["ids"]),
            }
            record = {
                "attempt": len(attempts) + 1,
                "phase": phase,
                "accepted": outcome["status"] == "COMMITTED",
                "committed": after["version"] > before["version"],
                "business_state_unchanged": before == after,
                "before": before,
                "after": after,
                "sql_before": sql_before,
                "sql_after": sql_after,
                "request": request,
                "preview": deepcopy(handle["preview"]),
                "reviewed_candidate_ids": deepcopy(outcome["reviewed_candidate_ids"]),
                "used_candidate_ids": deepcopy(outcome["used_candidate_ids"]),
                "outcome": outcome,
                "native_draft_callback_completed": callback_completed,
            }
            attempts.append(record)
            events.append({
                "stage": "attempt",
                "attempt": record["attempt"],
                "phase": phase,
                "outcome": deepcopy(outcome),
                "state": deepcopy(after),
            })
            return record

        first = attempt(
            proposal if kind == "wrong_value" else authorized,
            candidate_swap=kind == "instance_mismatch",
            phase="initial",
        )
        recovery_eligible = (
            kind in {"instance_mismatch", "wrong_value"}
            and first["outcome"]["status"] == "REJECTED"
            and first["business_state_unchanged"]
            and not first["committed"]
        )
        if recovery_eligible:
            events.append({
                "stage": "scripted_recovery",
                "trigger": "actual rejection with unchanged business state",
                "action": "reuse reviewed candidate with authorized address",
                "reviewed_candidate_ids": deepcopy(handle["ids"]),
            })
            attempt(authorized, candidate_swap=False, phase="scripted_recovery")
        elif kind in {"instance_mismatch", "wrong_value"}:
            events.append({
                "stage": "scripted_recovery_not_started",
                "first_status": first["outcome"]["status"],
                "business_state_unchanged": first["business_state_unchanged"],
                "reason": "requires actual rejection with unchanged business state",
            })

        result = {
            "method": "C",
            "case_id": case_id,
            "kind": kind,
            "db_path": str(db_path),
            "timestamp_utc": timestamp.isoformat(),
            "initial_order": initial_order,
            "initial": initial,
            "final": store.snapshot(),
            "attempts": attempts,
            "events": events,
            "source_provenance": {
                "route": "stores.Store(full)",
                "admission": "original ReviewForms / SqlAlchemyFormRepository",
                "stores_path": str(helpers.SPRINT / "stores.py"),
                "stores_sha256": helpers._sha256(helpers.SPRINT / "stores.py"),
                "reference_path": str(stores.SUPPLEMENT / "reference.py"),
                "reference_sha256": helpers._sha256(stores.SUPPLEMENT / "reference.py"),
                "source_manifest_path": str(helpers.SPRINT / "contract-source-manifest.json"),
                "source_manifest_sha256": helpers._sha256(
                    helpers.SPRINT / "contract-source-manifest.json"
                ),
                "helper_adapter_path": str(PREVIOUS_ADAPTER),
                "helper_adapter_sha256": helpers._sha256(PREVIOUS_ADAPTER),
                "pinned_source_check": source_check,
                "admission_verifier_modified": False,
                "draft_source": "caller-supplied original native Retail tool on a clone",
                "recovery": "fixed script after observed rejection; not model behavior",
                "hosted_model_calls": 0,
            },
        }
        json.dumps(result, ensure_ascii=False, allow_nan=False)
        return result
    finally:
        store.close()
