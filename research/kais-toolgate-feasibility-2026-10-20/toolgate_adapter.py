"""Offline T-configured feasibility through unmodified ToolGate callbacks.

The business relation, fixture records, pure draft tool, and SQLite persistence
bridge are local configuration/adaptation. They are not ToolGate-native policy
or persistence features. This single-thread exercise makes no concurrency claim.
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import importlib
import io
import json
from pathlib import Path
import sqlite3
import sys


UPSTREAM_COMMIT = "976ad3f5528f89e248cbdf55840347b445934155"
VENDOR = Path(__file__).resolve().parent / "vendor" / "ToolGate"
TOOL_NAME = "draft_authorized_address"


def _json(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def _unpack(state):
    return {name: deepcopy(field["value"]) for name, field in state.items()}


def _snapshot(connection):
    row = connection.execute(
        "SELECT version, values_json, sources_json, transition_id "
        "FROM versions ORDER BY version DESC LIMIT 1"
    ).fetchone()
    return {
        "version": row[0],
        "values": json.loads(row[1]),
        "sources": json.loads(row[2]),
        "transition_id": row[3],
    }


def _save_version(connection, snapshot):
    connection.execute(
        "INSERT INTO versions VALUES (?, ?, ?, ?)",
        (
            snapshot["version"],
            _json(snapshot["values"]),
            _json(snapshot["sources"]),
            snapshot["transition_id"],
        ),
    )


def run_case(case: dict, outdir: Path) -> dict:
    """Execute one supplied control; return original trace and durable evidence."""
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    db_path = outdir / f"{case['id']}.sqlite"
    if db_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing evidence: {db_path}")

    stdout, stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(stdout), redirect_stderr(stderr):
        vendor_path = str(VENDOR)
        if vendor_path not in sys.path:
            sys.path.insert(0, vendor_path)
        pipeline_module = importlib.import_module("toolgate.pipeline.pipeline")
        if Path(pipeline_module.__file__).resolve().parent.parent.parent != VENDOR:
            raise ImportError("ToolGate import does not resolve to the pinned vendor")
        from toolgate.contracts.contract import Postcondition, Precondition, ToolContract
        from toolgate.core.tool_executor import ToolExecutor

    target, field = "record-1", "address"
    context = {
        "target": target,
        "predecessor_version": 1,
        "field": field,
        "proposal": deepcopy(case["proposal"]),
    }
    candidates = [{"candidate_id": "c1", **deepcopy(context)}]
    if case["kind"] in {"reused_after_preview", "reauthorized", "instance_mismatch"}:
        candidates.append({"candidate_id": "c2", **deepcopy(context)})
    approvals = [{
        "approval_id": "approval-1",
        "reviewed_candidate_id": "c1",
        **deepcopy(context),
        "authorized": deepcopy(case["authorized"]),
    }]
    if case["kind"] == "reauthorized":
        approvals.append({
            **deepcopy(approvals[0]),
            "approval_id": "approval-2",
            "reviewed_candidate_id": "c2",
        })
    approval = approvals[-1]
    used_id = "c2" if case["kind"] in {"reauthorized", "instance_mismatch"} else "c1"
    candidate = next(item for item in candidates if item["candidate_id"] == used_id)
    transition_id = "address-commit"
    callback_counts = {"pre": 0, "post": 0}
    callback_log, executor_log, bridge_log = [], [], []
    symbolic_before = None
    reasoner_calls = 0

    connection = sqlite3.connect(db_path)
    try:
        connection.executescript(
            """
            CREATE TABLE versions (
                version INTEGER PRIMARY KEY, values_json TEXT NOT NULL,
                sources_json TEXT NOT NULL, transition_id TEXT
            );
            CREATE TABLE candidates (
                candidate_id TEXT PRIMARY KEY, context_json TEXT NOT NULL
            );
            CREATE TABLE approvals (
                approval_id TEXT PRIMARY KEY, reviewed_candidate_id TEXT NOT NULL,
                authorization_json TEXT NOT NULL
            );
            CREATE TABLE transitions (
                transition_id TEXT PRIMARY KEY, record_json TEXT NOT NULL
            );
            """
        )
        seed = {
            "version": 1,
            "values": deepcopy(case["initial"]),
            "sources": {"address": "seed-address", "batch": "seed-batch"},
            "transition_id": None,
        }
        _save_version(connection, seed)
        for item in candidates:
            connection.execute(
                "INSERT INTO candidates VALUES (?, ?)",
                (item["candidate_id"], _json(item)),
            )
        for item in approvals:
            connection.execute(
                "INSERT INTO approvals VALUES (?, ?, ?)",
                (item["approval_id"], item["reviewed_candidate_id"], _json(item)),
            )
        connection.commit()

        # An explicit earlier transaction advances the persisted predecessor.
        # This is sequential fixture setup, not a simultaneous-writer test.
        if case["kind"] == "stale":
            connection.execute("BEGIN IMMEDIATE")
            advanced = deepcopy(seed)
            advanced["version"] = 2
            advanced["values"]["batch"] = "concurrent"
            advanced["sources"]["batch"] = "independent-update"
            advanced["transition_id"] = "independent-update"
            external = {
                "transition_id": "independent-update",
                "external": True,
                "target": target,
                "field": "batch",
                "from_version": 1,
                "to_version": 2,
                "version": 2,
                "previous_source": seed["sources"]["batch"],
                "final": "concurrent",
            }
            connection.execute(
                "INSERT INTO transitions VALUES (?, ?)",
                (external["transition_id"], _json(external)),
            )
            _save_version(connection, advanced)
            connection.commit()

        # Author-written bridge: snapshot -> original pipeline -> durable commit.
        connection.execute("BEGIN IMMEDIATE")
        before = _snapshot(connection)
        bridge_log.append({"event": "begin_immediate", "version": before["version"]})
        initial_entities = {
            "target": (target, "str"),
            "version": (before["version"], "int"),
            "values": (deepcopy(before["values"]), "dict"),
            "sources": (deepcopy(before["sources"]), "dict"),
            "candidate": (deepcopy(candidate), "dict"),
            "approval": (deepcopy(approval), "dict"),
            "transition_id": (transition_id, "str"),
            "transition": ({}, "dict"),
        }

        def pre(state_dict):
            callback_counts["pre"] += 1
            state = _unpack(state_dict)
            selected, grant = state["candidate"], state["approval"]
            persisted_candidate = connection.execute(
                "SELECT context_json FROM candidates WHERE candidate_id = ?",
                (selected["candidate_id"],),
            ).fetchone()
            persisted_approval = connection.execute(
                "SELECT authorization_json FROM approvals WHERE approval_id = ?",
                (grant["approval_id"],),
            ).fetchone()
            current = _snapshot(connection)
            checks = {
                "target_and_field": (
                    state["target"] == selected["target"] == grant["target"] == target
                    and selected["field"] == grant["field"] == field
                ),
                "current_predecessor": (
                    state["version"] == current["version"]
                    == selected["predecessor_version"] == grant["predecessor_version"]
                    and state["values"] == current["values"]
                    and state["sources"] == current["sources"]
                ),
                "persisted_candidate": (
                    persisted_candidate is not None
                    and json.loads(persisted_candidate[0]) == selected
                ),
                "persisted_approval": (
                    persisted_approval is not None
                    and json.loads(persisted_approval[0]) == grant
                ),
                "same_context": all(selected[key] == grant[key] for key in context),
                "reviewed_instance": selected["candidate_id"] == grant["reviewed_candidate_id"],
            }
            passed = all(checks.values())
            callback_log.append({"callback": "pre", "checks": checks, "passed": passed})
            return passed

        def draft(tool_name, params, config):
            # Pure draft: no SQL or external write happens in this executor.
            executor_log.append({"tool_name": tool_name, "params": deepcopy(params)})
            values, sources = deepcopy(params["values"]), deepcopy(params["sources"])
            values[field] = deepcopy(params["approval"]["authorized"])
            if case["kind"] == "wrong_value":
                values[field] = deepcopy(params["candidate"]["proposal"])
            if case["kind"] == "unchanged_field_changed":
                values["batch"] = "unreviewed"
            sources[field] = params["transition_id"]
            transition = {
                "transition_id": params["transition_id"],
                "external": False,
                "target": params["target"],
                "field": field,
                "from_version": params["version"],
                "to_version": params["version"] + 1,
                "version": params["version"] + 1,
                "approval_id": params["approval"]["approval_id"],
                "used_candidate_id": params["candidate"]["candidate_id"],
                "reviewed_candidate_id": params["approval"]["reviewed_candidate_id"],
                "proposal": deepcopy(params["candidate"]["proposal"]),
                "authorized": deepcopy(params["approval"]["authorized"]),
                "final": deepcopy(values[field]),
                "previous_source": params["sources"][field],
            }
            return {
                "error": "",
                "response": {
                    "version": params["version"] + 1,
                    "values": values,
                    "sources": sources,
                    "transition": transition,
                },
            }

        def post(old_dict, new_dict, result):
            callback_counts["post"] += 1
            old, new = _unpack(old_dict), _unpack(new_dict)
            response = result.get("response", {})
            values, sources = response.get("values", {}), response.get("sources", {})
            record = response.get("transition", {})
            expected_record = {
                "transition_id": old["transition_id"],
                "external": False,
                "target": old["target"],
                "field": field,
                "from_version": old["version"],
                "to_version": old["version"] + 1,
                "version": old["version"] + 1,
                "approval_id": old["approval"]["approval_id"],
                "used_candidate_id": old["candidate"]["candidate_id"],
                "reviewed_candidate_id": old["approval"]["reviewed_candidate_id"],
                "proposal": old["candidate"]["proposal"],
                "authorized": old["approval"]["authorized"],
                "final": old["approval"]["authorized"],
                "previous_source": old["sources"][field],
            }
            successor_fields = {"version", "values", "sources", "transition"}
            checks = {
                "no_error": result.get("error") == "",
                "complete_successor": (
                    set(response) == successor_fields
                    and set(values) == set(old["values"])
                    and set(sources) == set(old["sources"])
                    and set(new) == set(old)
                ),
                "authorized_value": values.get(field) == old["approval"]["authorized"],
                "unchanged_values": all(
                    values.get(key) == value
                    for key, value in old["values"].items() if key != field
                ),
                "unchanged_sources": all(
                    sources.get(key) == value
                    for key, value in old["sources"].items() if key != field
                ),
                "changed_source": sources.get(field) == old["transition_id"],
                "transition_relation": record == expected_record,
                "successor_version": response.get("version") == old["version"] + 1,
                "native_update_matches_draft": all(
                    new.get(key) == response.get(key) for key in successor_fields
                ),
                "other_symbolic_fields_preserved": all(
                    new.get(key) == value
                    for key, value in old.items() if key not in successor_fields
                ),
            }
            passed = all(checks.values())
            callback_log.append({"callback": "post", "checks": checks, "passed": passed})
            return passed

        class FixedRetriever:
            def retrieve(self, query, state_summary="", top_k=25):
                return [TOOL_NAME]

        def reasoner(query, history, state):
            nonlocal reasoner_calls, symbolic_before
            reasoner_calls += 1
            if reasoner_calls == 1:
                symbolic_before = deepcopy(state.to_dict())
                return pipeline_module.Action(
                    type="start_call_tool", content="Draft the reviewed address change"
                )
            return pipeline_module.Action(type="answer", content="Single offline attempt complete")

        contract = ToolContract(
            tool_name=TOOL_NAME,
            tool_description="Construct a complete candidate successor without external effects",
            precondition=Precondition(check_function=pre),
            postcondition=Postcondition(
                state_update_rules={
                    key: f"result.response.{key}"
                    for key in ("version", "values", "sources", "transition")
                },
                verify_function=post,
            ),
            input_schema={
                "type": "object",
                "properties": {key: {} for key in initial_entities},
                "required": list(initial_entities),
            },
        )
        pipeline = pipeline_module.ToolGatePipeline(
            tool_contracts={TOOL_NAME: contract},
            llm_client=None,
            llm_reasoner=reasoner,
            tool_executor=ToolExecutor(tool_executor_func=draft),
            retriever=FixedRetriever(),
            max_steps=2,
            use_llm_verifier=False,
        )
        with redirect_stdout(stdout), redirect_stderr(stderr):
            native_result = pipeline.run(
                query="Apply the reviewed address change", initial_entities=initial_entities
            )
        accepted = any(entry["state_updated"] for entry in native_result["trace"])
        if accepted:
            final = _unpack(native_result["final_state"])
            connection.execute(
                "INSERT INTO transitions VALUES (?, ?)",
                (final["transition"]["transition_id"], _json(final["transition"])),
            )
            _save_version(connection, {
                "version": final["version"],
                "values": final["values"],
                "sources": final["sources"],
                "transition_id": final["transition"]["transition_id"],
            })
            connection.commit()
            bridge_log.append({"event": "commit_after_post", "version": final["version"]})
        else:
            connection.rollback()
            bridge_log.append({"event": "rollback_no_business_write"})
        after = _snapshot(connection)
    finally:
        connection.close()

    return {
        "method": "T-configured",
        "method_alias": "T+relation",
        "case_id": case["id"],
        "kind": case["kind"],
        "accepted": accepted,
        "committed": accepted,
        "db_path": str(db_path.resolve()),
        "initial": seed,
        "before": before,
        "after": after,
        "candidates": candidates,
        "approvals": approvals,
        "used_candidate_id": used_id,
        "reviewed_candidate_id": approval["reviewed_candidate_id"],
        "approval_id": approval["approval_id"],
        "callback_counts": callback_counts,
        "callback_log": callback_log,
        "executor_called": bool(executor_log),
        "executor_calls": len(executor_log),
        "executor_log": executor_log,
        "reasoner_calls": reasoner_calls,
        "symbolic_before": symbolic_before,
        "symbolic_after": native_result["final_state"],
        "trace": native_result["trace"],
        "native_result": native_result,
        "failed_tools": sorted(pipeline.failed_tools),
        "bridge_log": bridge_log,
        "stdout": stdout.getvalue(),
        "stderr": stderr.getvalue(),
        "source_provenance": {
            "native_pipeline": {
                "commit": UPSTREAM_COMMIT,
                "source": str(Path(pipeline_module.__file__).resolve()),
                "modified": False,
            },
            "callback_configuration": {
                "source": str(Path(__file__).resolve()),
                "interfaces": ["Precondition.check_function", "Postcondition.verify_function"],
                "role": "Author-supplied business relation through ordinary native callbacks",
                "imports_C_verifier": False,
            },
            "persistence_bridge": {
                "source": str(Path(__file__).resolve()),
                "role": "Author-written SQLite snapshot and post-acceptance commit bridge",
                "native_ToolGate_feature": False,
                "transaction": "BEGIN IMMEDIATE; snapshot; original pipeline; commit on acceptance",
            },
            "offline_drivers": {
                "retriever": "Fixed single-tool retriever",
                "reasoner": "Scripted llm_reasoner",
                "llm_client": None,
                "model_calls": 0,
                "network_calls": 0,
                "executor": "Pure candidate successor construction",
            },
            "scope": "Sequential development controls; no concurrent-writer guarantee tested",
        },
    }
