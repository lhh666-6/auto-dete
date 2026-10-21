"""Pinned ToolGate plus configured relation and an author-written SQLite bridge.

The supplied draft callback executes the pinned retail tool on a clone and
returns the complete resulting order. Recovery is a fixed script, not autonomous
agent behavior. No C verifier is imported, and no network/model call is made here.
"""

from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
from copy import deepcopy
import importlib
import importlib.util
import io
import json
from pathlib import Path
import sqlite3
import sys
import traceback


FROZEN_ADAPTER = (
    Path(__file__).resolve().parent.parent
    / "kais-toolgate-feasibility-2026-10-20" / "toolgate_adapter.py"
)
_spec = importlib.util.spec_from_file_location("frozen_toolgate_helpers", FROZEN_ADAPTER)
_helpers = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_helpers)
_json, _unpack = _helpers._json, _helpers._unpack
_snapshot, _save_version = _helpers._snapshot, _helpers._save_version
TOOL_NAME = "draft_reviewed_retail_address"
STATE_KEYS = (
    "target", "version", "values", "sources", "candidate", "approval",
    "transition_id", "transition",
)


def _sql_snapshot(connection):
    result = {}
    for table, key in (
        ("versions", "version"), ("candidates", "candidate_id"),
        ("approvals", "approval_id"), ("transitions", "transition_id"),
    ):
        cursor = connection.execute(f"SELECT * FROM {table} ORDER BY {key}")
        columns = [column[0] for column in cursor.description]
        result[table] = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return result


def _transition(state, final_address):
    return {
        "transition_id": state["transition_id"],
        "external": False,
        "target": state["target"],
        "field": "address",
        "from_version": state["version"],
        "to_version": state["version"] + 1,
        "version": state["version"] + 1,
        "approval_id": state["approval"]["approval_id"],
        "used_candidate_id": state["candidate"]["candidate_id"],
        "reviewed_candidate_id": state["approval"]["reviewed_candidate_id"],
        "proposal": deepcopy(state["candidate"]["proposal"]),
        "authorized": deepcopy(state["approval"]["authorized"]),
        "final": deepcopy(final_address),
        "previous_source": state["sources"]["address"],
    }


def run_case(case: dict, outdir: Path, draft_callback) -> dict:
    """Run one frozen public workflow scenario and its specified recovery."""
    if case["kind"] not in {
        "corrected", "reauthorized", "instance_mismatch", "wrong_value",
    }:
        raise ValueError(f"Unsupported frozen scenario: {case['kind']}")
    if "address" not in case["initial"]:
        raise ValueError("The full initial order must contain its address")
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    db_path = outdir / f"{case['id']}.sqlite"
    if db_path.exists():
        raise FileExistsError(f"Refusing to overwrite existing evidence: {db_path}")

    startup_stdout, startup_stderr = io.StringIO(), io.StringIO()
    with redirect_stdout(startup_stdout), redirect_stderr(startup_stderr):
        if str(_helpers.VENDOR) not in sys.path:
            sys.path.insert(0, str(_helpers.VENDOR))
        pipeline_module = importlib.import_module("toolgate.pipeline.pipeline")
        if Path(pipeline_module.__file__).resolve().parent.parent.parent != _helpers.VENDOR:
            raise ImportError("ToolGate import does not resolve to the pinned vendor")
        from toolgate.contracts.contract import Postcondition, Precondition, ToolContract
        from toolgate.core.tool_executor import ToolExecutor

    target = str(case["initial"].get("order_id", "record-1"))
    context = {
        "target": target,
        "predecessor_version": 1,
        "field": "address",
        "proposal": deepcopy(case["proposal"]),
    }
    candidates = [{"candidate_id": "c1", **deepcopy(context)}]
    if case["kind"] in {"reauthorized", "instance_mismatch"}:
        candidates.append({"candidate_id": "c2", **deepcopy(context)})
    approvals = [{
        "approval_id": "approval-1", "reviewed_candidate_id": "c1",
        **deepcopy(context), "authorized": deepcopy(case["authorized"]),
    }]
    if case["kind"] == "reauthorized":
        approvals.append({
            **deepcopy(approvals[0]),
            "approval_id": "approval-2",
            "reviewed_candidate_id": "c2",
        })
    initial = {
        "version": 1,
        "values": deepcopy(case["initial"]),
        "sources": {name: f"seed-{name}" for name in case["initial"]},
        "transition_id": None,
    }
    attempts = []
    runtime = {}
    connection = sqlite3.connect(db_path)

    def engineering_error(stage, exc):
        runtime["engineering_errors"].append({
            "stage": stage,
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
        })

    def pre(state_dict):
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
        return {
            "target_and_field": (
                state["target"] == selected["target"] == grant["target"] == target
                and selected["field"] == grant["field"] == "address"
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

    def post(old_dict, new_dict, result):
        old, new = _unpack(old_dict), _unpack(new_dict)
        response = result.get("response", {})
        if not isinstance(response, dict):
            response = {}
        values, sources = response.get("values", {}), response.get("sources", {})
        successor_fields = {"version", "values", "sources", "transition"}
        return {
            "no_error": result.get("error") == "",
            "complete_successor": (
                set(response) == successor_fields
                and set(values) == set(old["values"])
                and set(sources) == set(old["sources"])
                and set(new) == set(old)
            ),
            "authorized_value": values.get("address") == old["approval"]["authorized"],
            "unchanged_values": all(
                values.get(key) == value
                for key, value in old["values"].items() if key != "address"
            ),
            "unchanged_sources": all(
                sources.get(key) == value
                for key, value in old["sources"].items() if key != "address"
            ),
            "changed_source": sources.get("address") == old["transition_id"],
            "transition_relation": (
                response.get("transition") == _transition(old, old["approval"]["authorized"])
            ),
            "successor_version": response.get("version") == old["version"] + 1,
            "native_update_matches_draft": all(
                new.get(key) == response.get(key) for key in successor_fields
            ),
            "other_symbolic_fields_preserved": all(
                new.get(key) == value
                for key, value in old.items() if key not in successor_fields
            ),
        }

    def checked_callback(name, callback, *args):
        runtime["callback_counts"][name] += 1
        try:
            checks = callback(*args)
        except Exception as exc:
            # Original ToolGate catches callback errors; preserve their identity
            # here so that an engineering exception cannot trigger recovery.
            engineering_error(name, exc)
            runtime["callback_log"].append({
                "callback": name, "passed": False,
                "engineering_error": runtime["engineering_errors"][-1],
            })
            raise
        passed = all(checks.values())
        runtime["callback_log"].append({
            "callback": name, "checks": checks, "passed": passed,
        })
        return passed

    def draft(tool_name, params, config):
        address = (
            params["candidate"]["proposal"] if runtime["use_wrong_value"]
            else params["approval"]["authorized"]
        )
        entry = {
            "tool_name": tool_name,
            "params": deepcopy(params),
            "native_address_argument": deepcopy(address),
        }
        runtime["executor_log"].append(entry)
        try:
            # The full result comes from the pinned retail tool on a clone.
            # This executor does not manually update the order's field values.
            values = deepcopy(draft_callback(deepcopy(address)))
            if not isinstance(values, dict):
                raise TypeError("The native draft callback must return a full order dictionary")
            entry["native_draft_order"] = deepcopy(values)
            sources = deepcopy(params["sources"])
            sources["address"] = params["transition_id"]
            return {
                "error": "",
                "response": {
                    "version": params["version"] + 1,
                    "values": values,
                    "sources": sources,
                    "transition": _transition(params, values.get("address")),
                },
            }
        except Exception as exc:
            engineering_error("draft_callback", exc)
            entry["engineering_error"] = runtime["engineering_errors"][-1]
            raise

    class FixedRetriever:
        def retrieve(self, query, state_summary="", top_k=25):
            return [TOOL_NAME]

    def reasoner(query, history, state):
        runtime["reasoner_calls"] += 1
        if runtime["reasoner_calls"] == 1:
            runtime["symbolic_before"] = deepcopy(state.to_dict())
            return pipeline_module.Action(
                type="start_call_tool", content="Draft the reviewed retail address change"
            )
        return pipeline_module.Action(type="answer", content="Scripted attempt complete")

    contract = ToolContract(
        tool_name=TOOL_NAME,
        tool_description="Run the native retail address tool on a clone to draft a full order",
        precondition=Precondition(
            check_function=lambda state: checked_callback("pre", pre, state)
        ),
        postcondition=Postcondition(
            state_update_rules={
                key: f"result.response.{key}"
                for key in ("version", "values", "sources", "transition")
            },
            verify_function=lambda old, new, result: checked_callback(
                "post", post, old, new, result
            ),
        ),
        input_schema={
            "type": "object",
            "properties": {key: {} for key in STATE_KEYS},
            "required": list(STATE_KEYS),
        },
    )
    # The same pipeline instance and SQLite connection serve both attempts.
    pipeline = pipeline_module.ToolGatePipeline(
        tool_contracts={TOOL_NAME: contract},
        llm_client=None,
        llm_reasoner=reasoner,
        tool_executor=ToolExecutor(tool_executor_func=draft),
        retriever=FixedRetriever(),
        max_steps=2,
        use_llm_verifier=False,
    )
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
        _save_version(connection, initial)
        for item in candidates:
            connection.execute(
                "INSERT INTO candidates VALUES (?, ?)", (item["candidate_id"], _json(item))
            )
        for item in approvals:
            connection.execute(
                "INSERT INTO approvals VALUES (?, ?, ?)",
                (item["approval_id"], item["reviewed_candidate_id"], _json(item)),
            )
        connection.commit()

        for number in (1, 2):
            used_id = (
                "c2" if number == 1 and case["kind"] in {"reauthorized", "instance_mismatch"}
                else "c1"
            )
            candidate = next(item for item in candidates if item["candidate_id"] == used_id)
            approval = approvals[-1] if case["kind"] == "reauthorized" else approvals[0]
            runtime = {
                "callback_counts": {"pre": 0, "post": 0},
                "callback_log": [], "executor_log": [], "engineering_errors": [],
                "reasoner_calls": 0, "symbolic_before": None,
                "use_wrong_value": number == 1 and case["kind"] == "wrong_value",
            }
            stdout, stderr = io.StringIO(), io.StringIO()
            connection.execute("BEGIN IMMEDIATE")
            before, sql_before = _snapshot(connection), _sql_snapshot(connection)
            transition_id = f"{case['id']}-address-attempt-{number}"
            entities = {
                "target": (target, "str"), "version": (before["version"], "int"),
                "values": (deepcopy(before["values"]), "dict"),
                "sources": (deepcopy(before["sources"]), "dict"),
                "candidate": (deepcopy(candidate), "dict"),
                "approval": (deepcopy(approval), "dict"),
                "transition_id": (transition_id, "str"), "transition": ({}, "dict"),
            }
            bridge_log = [{"event": "begin_immediate", "version": before["version"]}]
            native_result, accepted, committed = None, False, False
            try:
                with redirect_stdout(stdout), redirect_stderr(stderr):
                    native_result = pipeline.run(
                        query="Apply the reviewed retail address change",
                        initial_entities=entities,
                    )
                accepted = any(item["state_updated"] for item in native_result["trace"])
                if accepted and not runtime["engineering_errors"]:
                    final_state = _unpack(native_result["final_state"])
                    connection.execute(
                        "INSERT INTO transitions VALUES (?, ?)",
                        (transition_id, _json(final_state["transition"])),
                    )
                    _save_version(connection, {
                        "version": final_state["version"],
                        "values": final_state["values"],
                        "sources": final_state["sources"],
                        "transition_id": transition_id,
                    })
                    connection.commit()
                    committed = True
                    bridge_log.append({
                        "event": "commit_after_post", "version": final_state["version"],
                    })
                else:
                    connection.rollback()
                    bridge_log.append({"event": "rollback_no_business_write"})
            except Exception as exc:
                engineering_error("pipeline_or_bridge", exc)
                connection.rollback()
                bridge_log.append({"event": "rollback_engineering_error"})
            after, sql_after = _snapshot(connection), _sql_snapshot(connection)
            rejected = any(item["passed"] is False for item in runtime["callback_log"])
            outcome = (
                "engineering_error" if runtime["engineering_errors"]
                else "accepted" if committed
                else "relation_rejected" if rejected
                else "unclassified_failure"
            )
            attempts.append({
                "attempt": number,
                "before": before, "after": after,
                "sql_before": sql_before, "sql_after": sql_after,
                "accepted": accepted, "committed": committed, "outcome": outcome,
                "request": {"candidate": deepcopy(candidate), "approval": deepcopy(approval)},
                "used_candidate_id": used_id,
                "reviewed_candidate_id": approval["reviewed_candidate_id"],
                "approval_id": approval["approval_id"],
                "transition_id": transition_id,
                "callback_counts": runtime["callback_counts"],
                "callback_log": runtime["callback_log"],
                "executor_called": bool(runtime["executor_log"]),
                "executor_calls": len(runtime["executor_log"]),
                "executor_log": runtime["executor_log"],
                "reasoner_calls": runtime["reasoner_calls"],
                "symbolic_before": runtime["symbolic_before"],
                "symbolic_after": native_result["final_state"] if native_result else None,
                "trace": native_result["trace"] if native_result else pipeline._format_trace(),
                "native_result": native_result,
                "failed_tools": sorted(pipeline.failed_tools),
                "bridge_log": bridge_log,
                "engineering_errors": runtime["engineering_errors"],
                "stdout": stdout.getvalue(), "stderr": stderr.getvalue(),
            })
            recover = (
                number == 1
                and case["kind"] in {"instance_mismatch", "wrong_value"}
                and outcome == "relation_rejected"
                and before == after and sql_before == sql_after
            )
            if not recover:
                break
        final = _snapshot(connection)
    finally:
        connection.close()

    return {
        "method": "T-configured", "method_alias": "T+relation",
        "case_id": case["id"], "kind": case["kind"],
        "db_path": str(db_path.resolve()),
        "initial": initial, "final": final, "attempts": attempts,
        "candidates": candidates, "approvals": approvals,
        "startup_stdout": startup_stdout.getvalue(),
        "startup_stderr": startup_stderr.getvalue(),
        "source_provenance": {
            "native_pipeline": {
                "commit": _helpers.UPSTREAM_COMMIT,
                "source": str(Path(pipeline_module.__file__).resolve()), "modified": False,
            },
            "reused_helpers": {
                "source": str(FROZEN_ADAPTER),
                "functions": ["_json", "_unpack", "_snapshot", "_save_version"],
                "prior_adapter_modified": False,
            },
            "callback_configuration": {
                "source": str(Path(__file__).resolve()),
                "interfaces": ["Precondition.check_function", "Postcondition.verify_function"],
                "role": "Author-supplied relation using ordinary business predicate callbacks",
                "imports_C_verifier": False,
            },
            "persistence_bridge": {
                "source": str(Path(__file__).resolve()), "native_ToolGate_feature": False,
                "role": "Author-written SQLite records and post-acceptance commit bridge",
                "transaction": "BEGIN IMMEDIATE; snapshot; original pipeline; commit on acceptance",
            },
            "draft_tool": {
                "callback": getattr(draft_callback, "__qualname__", type(draft_callback).__name__),
                "role": "Caller-supplied pinned native retail tool on a cloned world",
                "returns": "Complete order; all non-address fields checked against predecessor",
            },
            "recovery": {
                "kind": "Fixed script on the same SQLite connection and ToolGatePipeline instance",
                "rule": "After a relation rejection with unchanged SQL, retry c1 and authorized address",
                "autonomous": False, "engineering_errors_recovered": False,
            },
            "offline_drivers": {
                "retriever": "Fixed single-tool retriever", "reasoner": "Scripted llm_reasoner",
                "llm_client": None, "model_calls": 0, "network_calls": 0,
            },
            "scope": "Sequential frozen public-workflow scenarios; no concurrency guarantee tested",
        },
    }
