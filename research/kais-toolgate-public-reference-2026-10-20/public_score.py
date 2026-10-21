"""Independent, stdlib-only evidence scorer. Never imports or executes a gate.

Reads SQLite in mode=ro and evaluates the frozen scripted reference protocol.
Writing is limited to new score artifacts; existing different scores are refused.
"""
from __future__ import annotations

import argparse
from collections import Counter
from contextlib import closing
from copy import deepcopy
import csv
import gzip
import hashlib
import io
import json
from pathlib import Path
import sqlite3


HERE = Path(__file__).resolve().parent
TASKS = ("59", "71", "78", "96", "101", "102")
KINDS = ("corrected", "reauthorized", "instance_mismatch", "wrong_value")
METHODS = ("T-configured", "C")
BAD_FIRST = {"instance_mismatch", "wrong_value"}
PRE_KEYS = {
    "target_and_field", "current_predecessor", "persisted_candidate",
    "persisted_approval", "same_context", "reviewed_instance",
}
POST_KEYS = {
    "no_error", "complete_successor", "authorized_value", "unchanged_values",
    "unchanged_sources", "changed_source", "transition_relation",
    "successor_version", "native_update_matches_draft",
    "other_symbolic_fields_preserved",
}


class UnknownEvidence(ValueError):
    """An outcome cannot be classified as acceptance or a relation rejection."""


def canon(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False)


def equal(left, right):
    return canon(left) == canon(right)


def read(path):
    path = Path(path)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if path.suffix == ".gz" else raw)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def evidence_path(folder, name):
    path = (folder / name).resolve()
    if not path.is_relative_to(folder.resolve()):
        raise ValueError(f"Evidence path leaves its run folder: {name}")
    return path


def sql_normalize(tables):
    return {name: sorted(rows, key=canon) for name, rows in tables.items()}


def dump_sql(path):
    with closing(sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)) as con:
        con.row_factory = sqlite3.Row
        names = [r[0] for r in con.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return sql_normalize({
            name: [dict(r) for r in con.execute(
                'SELECT * FROM "' + name.replace('"', '""') + '"')]
            for name in names
        })


def core(snapshot):
    return {key: snapshot[key] for key in ("version", "values", "sources")}


def history(tables, method):
    return tables["record_versions" if method == "C" else "versions"]


def state(row, method):
    return {
        "version": row["version"],
        "values": json.loads(row["values"] if method == "C" else row["values_json"]),
        "sources": json.loads(row["fact_sources"] if method == "C" else row["sources_json"]),
    }


def latest(tables, method):
    return state(max(history(tables, method), key=lambda row: row["version"]), method)


def require(condition, message, errors):
    if not condition:
        errors.append(message)


def subset_rows(before, after):
    return not (Counter(map(canon, before)) - Counter(map(canon, after)))


def expected_identity(case, number, method):
    alternate = case["kind"] == "reauthorized" or (
        number == 1 and case["kind"] == "instance_mismatch")
    reviewed_alternate = case["kind"] == "reauthorized"
    if method == "T-configured":
        return ("c2" if alternate else "c1",
                "c2" if reviewed_alternate else "c1")
    first = case["id"] + ":review:address"
    second = first + (":substitute" if case["kind"] == "instance_mismatch" else ":preview")
    return (second if alternate else first, second if reviewed_alternate else first)


def check_identity(tables, attempt, case, number, method, errors):
    used, reviewed = expected_identity(case, number, method)
    if method == "C":
        candidates = {r["candidate_id"]: r for r in tables["candidate_certificates"]}
        first_name = case["id"] + ":review:address"
        first = candidates[first_name]
        used_row, reviewed_row = candidates[used], candidates[reviewed]
        require(attempt["used_candidate_ids"] == {"address": used_row["certificate_id"]},
                "attempt used the wrong candidate identity", errors)
        require(attempt["reviewed_candidate_ids"] == {"address": reviewed_row["certificate_id"]},
                "attempt reviewed the wrong candidate identity", errors)
        for candidate in (used_row, reviewed_row):
            require(candidate["field_key"] == "address"
                    and candidate["target_record_id"] == "FORM-1"
                    and candidate["expected_fact_version"] == 1
                    and equal(json.loads(candidate["value_payload"]), case["proposal"]),
                    "persisted C candidate context differs from case", errors)
        preview = attempt["request"]["preview"]
        expected_successor = deepcopy(case["initial"])
        expected_successor["address"] = case["authorized"]
        require(preview["candidate_ids"] == attempt["reviewed_candidate_ids"]
                and preview["expected_version"] == 1
                and equal(preview["proposal"], {"address": case["proposal"]})
                and equal(preview["authorized"], {"address": case["authorized"]})
                and equal(preview["complete_successor"], expected_successor)
                and preview["public_order_id"] == case["initial"]["order_id"],
                "C prepared review context differs from case", errors)
        if case["kind"] in {"reauthorized", "instance_mismatch"}:
            second_name = first_name + (":preview" if case["kind"] == "reauthorized" else ":substitute")
            second = candidates[second_name]
            context = lambda row: {k: v for k, v in row.items()
                                   if k not in {"candidate_id", "certificate_id"}}
            require(first["certificate_id"] != second["certificate_id"]
                    and equal(context(first), context(second)),
                    "second C instance is not distinct with identical context", errors)
    else:
        candidates = {r["candidate_id"]: json.loads(r["context_json"])
                      for r in tables["candidates"]}
        approvals = {r["approval_id"]: json.loads(r["authorization_json"])
                     for r in tables["approvals"]}
        selected, grant = attempt["request"]["candidate"], attempt["request"]["approval"]
        require(selected["candidate_id"] == used
                and grant["reviewed_candidate_id"] == reviewed
                and equal(selected, candidates[used])
                and equal(grant, approvals[grant["approval_id"]]),
                "T attempted candidate/review differs from persisted identity", errors)
        expected_context = {
            "target": str(case["initial"]["order_id"]), "field": "address",
            "predecessor_version": 1, "proposal": case["proposal"],
        }
        require(all(equal(selected[k], v) and equal(grant[k], v)
                    for k, v in expected_context.items())
                and equal(grant["authorized"], case["authorized"]),
                "persisted T candidate/review context differs from case", errors)
        if case["kind"] in {"reauthorized", "instance_mismatch"}:
            context = lambda row: {k: v for k, v in row.items() if k != "candidate_id"}
            require(equal(context(candidates["c1"]), context(candidates["c2"])),
                    "second T instance changed context", errors)


def check_commit(tables, before, after, case, number, method, errors):
    used, _ = expected_identity(case, number, method)
    if method == "C":
        transitions = [r for r in tables["fact_transitions"]
                       if r["created_version"] == after["version"]]
        if len(transitions) != 1:
            errors.append("expected one persisted address transition")
            return
        t = transitions[0]
        c = next(r for r in tables["candidate_certificates"]
                 if r["certificate_id"] == t["certificate_id"])
        b = next(r for r in tables["authorization_bindings"]
                 if r["decision_id"] == t["decision_id"])
        h = next(r for r in tables["human_decisions"]
                 if r["decision_id"] == t["decision_id"])
        require(t["field_key"] == h["field_key"] == "address"
                and c["candidate_id"] == h["candidate_id"] == used
                and c["expected_fact_version"] == before["version"]
                and b["certificate_id"] == t["certificate_id"]
                and equal(json.loads(c["value_payload"]), case["proposal"])
                and equal(json.loads(b["authorized_value_payload"]), case["authorized"])
                and equal(json.loads(t["value_payload"]), case["authorized"])
                and after["sources"]["address"] == t["transition_id"],
                "persisted C candidate/authorization/transition join failed", errors)
    else:
        transitions = [json.loads(r["record_json"]) for r in tables["transitions"]]
        transitions = [t for t in transitions if t["version"] == after["version"]]
        if len(transitions) != 1:
            errors.append("expected one persisted address transition")
            return
        t = transitions[0]
        c = next(json.loads(r["context_json"]) for r in tables["candidates"]
                 if r["candidate_id"] == t["used_candidate_id"])
        a = next(json.loads(r["authorization_json"]) for r in tables["approvals"]
                 if r["approval_id"] == t["approval_id"])
        expected = {
            "transition_id": after["sources"]["address"], "external": False,
            "target": str(case["initial"]["order_id"]), "field": "address",
            "from_version": before["version"], "to_version": after["version"],
            "version": after["version"], "approval_id": a["approval_id"],
            "used_candidate_id": used, "reviewed_candidate_id": used,
            "proposal": case["proposal"], "authorized": case["authorized"],
            "final": case["authorized"], "previous_source": before["sources"]["address"],
        }
        require(equal(t, expected) and a["reviewed_candidate_id"] == used
                and c["predecessor_version"] == a["predecessor_version"] == before["version"]
                and equal(c["proposal"], case["proposal"])
                and equal(a["authorized"], case["authorized"]),
                "persisted T candidate/authorization/transition join failed", errors)


def check_callbacks(attempt, expected_commit, case, number, errors):
    if attempt.get("engineering_errors"):
        raise RuntimeError("T recorded an engineering exception")
    logs, counts = attempt["callback_log"], attempt["callback_counts"]
    called = not (case["kind"] == "instance_mismatch" and number == 1)
    expected_names = ["pre", "post"] if called else ["pre"]
    if [entry.get("callback") for entry in logs] != expected_names:
        raise RuntimeError("Missing or extra completed native callback log")
    for entry in logs:
        checks = entry.get("checks")
        expected_keys = PRE_KEYS if entry["callback"] == "pre" else POST_KEYS
        if (not isinstance(checks, dict) or set(checks) != expected_keys
                or not all(type(v) is bool for v in checks.values())
                or type(entry.get("passed")) is not bool
                or entry["passed"] != all(checks.values())):
            raise RuntimeError("Incomplete or inconsistent callback predicate evidence")
    require(counts == {"pre": 1, "post": int(called)}
            and attempt["executor_calls"] == int(called)
            and len(attempt["executor_log"]) == int(called),
            "unexpected callback or executor count", errors)
    failed = {key for entry in logs for key, value in entry["checks"].items() if not value}
    expected_failed = set() if expected_commit else (
        {"reviewed_instance"} if case["kind"] == "instance_mismatch"
        else {"authorized_value", "transition_relation"})
    require(failed == expected_failed, "rejection did not exercise the specified relation", errors)
    old = {k: v["value"] for k, v in attempt["symbolic_before"].items()}
    require(equal(core(old), core(attempt["before"])),
            "pipeline input does not match SQL predecessor", errors)
    if expected_commit:
        new = {k: v["value"] for k, v in attempt["symbolic_after"].items()}
        require(equal(core(new), core(attempt["after"])),
                "accepted symbolic state differs from durable successor", errors)
    else:
        require(equal(attempt["symbolic_before"], attempt["symbolic_after"]),
                "rejection changed symbolic state", errors)
    require(not attempt["stdout"] and not attempt["stderr"],
            "unexpected upstream diagnostic output", errors)
    return called


def check_attempt(attempt, case, number, method, durable, errors):
    expected_commit = not (number == 1 and case["kind"] in BAD_FIRST)
    status = attempt["outcome"] if method == "T-configured" else attempt["outcome"]["status"]
    known = {"accepted", "relation_rejected"} if method == "T-configured" else {"COMMITTED", "REJECTED"}
    if status not in known:
        if "error" in str(status).lower():
            raise RuntimeError(f"Attempt returned engineering outcome {status}")
        raise UnknownEvidence(f"Unclassified attempt outcome {status}")
    require(status == ("accepted" if expected_commit else "relation_rejected")
            if method == "T-configured"
            else status == ("COMMITTED" if expected_commit else "REJECTED"),
            "outcome differs from fixed scenario", errors)
    sql_before, sql_after = attempt["sql_before"], attempt["sql_after"]
    before, after = latest(sql_before, method), latest(sql_after, method)
    require(equal(before, core(attempt["before"])) and equal(after, core(attempt["after"])),
            "reported attempt states differ from SQL snapshots", errors)
    require(before["version"] == 1 and equal(before["values"], case["initial"]),
            "attempt does not start at the unchanged initial predecessor", errors)
    require(set(before["sources"]) == set(case["initial"]),
            "initial source map is incomplete", errors)
    delta = after["version"] - before["version"]
    require(delta == int(expected_commit), "unexpected durable version increment", errors)
    require(type(attempt["accepted"]) is bool and type(attempt["committed"]) is bool
            and attempt["accepted"] == expected_commit
            and attempt["committed"] == (delta > 0),
            "acceptance/commit report disagrees with SQL or scenario", errors)
    require(subset_rows(history(sql_before, method), history(sql_after, method))
            and subset_rows(history(sql_after, method), history(durable, method)),
            "historical business versions were removed or rewritten", errors)
    check_identity(sql_after, attempt, case, number, method, errors)
    if expected_commit:
        expected_values = deepcopy(case["initial"])
        expected_values["address"] = case["authorized"]
        require(equal(after["values"], expected_values),
                "committed successor is not the complete authorized order", errors)
        require(set(after["sources"]) == set(before["sources"])
                and all(after["sources"][key] == value
                        for key, value in before["sources"].items() if key != "address")
                and after["sources"]["address"] != before["sources"]["address"],
                "unchanged sources were not preserved or changed source was not renewed", errors)
        check_commit(sql_after, before, after, case, number, method, errors)
    else:
        require(equal(before, after), "rejected attempt changed business state", errors)
        transitions = (sql_after["fact_transitions"] if method == "C"
                       else [json.loads(r["record_json"]) for r in sql_after["transitions"]])
        require(not any(t["created_version" if method == "C" else "version"] > 1
                        for t in transitions),
                "rejected attempt left a business transition", errors)
    if method == "T-configured":
        called = check_callbacks(attempt, expected_commit, case, number, errors)
    else:
        called = True
        if attempt.get("native_draft_callback_completed") is not True:
            raise RuntimeError("C native draft callback did not complete")
        reason = str(attempt["outcome"].get("reason", ""))
        if not expected_commit:
            fragment = ("binding/transition certificate mismatch"
                        if case["kind"] == "instance_mismatch"
                        else "binding/transition authorized value mismatch")
            require(fragment in reason, "C rejected for an unexpected reason", errors)
    return expected_commit, called


def action_view(action):
    return {"action_id": action.get("action_id"), "name": action["name"],
            "arguments": action["arguments"]}


def check_public(record, case, folder, inputs, final, draft_attempts, errors):
    data = inputs / str(case["task_id"])
    task, target = read(data / "task.json"), read(data / "target.json")
    before, reference = read(data / "before.json.gz"), read(data / "reference-final.json.gz")
    actions = task["evaluation_criteria"]["actions"]
    index, target_action = target["target_index"], target["target"]
    require(equal(target_action, actions[index]), "target differs from original task action", errors)
    order_id = target_action["arguments"]["order_id"]
    require(equal(case["initial"], before["orders"][order_id]),
            "case initial order is only a partial or different public order", errors)
    authorized = {k: v for k, v in target_action["arguments"].items() if k != "order_id"}
    proposal = deepcopy(authorized)
    proposal["address2"] = str(proposal.get("address2", "")) + " [unreviewed-draft]"
    require(equal(case["authorized"], authorized) and equal(case["proposal"], proposal),
            "case proposal/authorization differs from frozen public construction", errors)
    public = record["public"]
    drafts = public["draft_calls"]
    require(len(drafts) == len(draft_attempts), "native draft count differs from gate evidence", errors)
    for call, (number, attempt) in zip(drafts, draft_attempts):
        expected_address = case["proposal"] if number == 1 and case["kind"] == "wrong_value" else case["authorized"]
        expected_arguments = {"order_id": order_id, **expected_address}
        require(call.get("name", call.get("tool_name")) == target_action["name"]
                and equal(call["arguments"], expected_arguments)
                and equal(call["address"], expected_address),
                "native draft did not receive the prescribed complete arguments", errors)
        world = read(evidence_path(folder, call["world_path"]))
        expected_world = deepcopy(before)
        expected_world["orders"][order_id]["address"] = expected_address
        require(equal(world, expected_world),
                "native draft changed world outside the target order address", errors)
        require(equal(call["result"], world["orders"][order_id]),
                "native tool result differs from its actual complete draft order", errors)
        if record["method"] == "C":
            actual_order = attempt["request"]["complete_successor"]
            require(equal(attempt["request"]["address"], expected_address),
                    "C request address differs from native call", errors)
        else:
            entry = attempt["executor_log"][0]
            actual_order = entry["native_draft_order"]
            require(equal(entry["native_address_argument"], expected_address),
                    "T executor address differs from native call", errors)
        require(equal(actual_order, world["orders"][order_id]),
                "admission input was not the complete native draft result", errors)
    suffix_before = read(evidence_path(folder, public["suffix_initial_path"]))
    projected = deepcopy(before)
    projected["orders"][order_id] = deepcopy(final["values"])
    require(equal(suffix_before, projected),
            "suffix initial world does not project the actual SQLite successor", errors)
    suffix = read(evidence_path(folder, public["suffix_records_path"]))
    require(equal([action_view(a) for a in suffix],
                  [action_view(a) for a in actions[index + 1:]]),
            "suffix omits, changes, or reorders original actions/action IDs", errors)
    require(all("result" in entry for entry in suffix),
            "suffix omitted native results", errors)
    require(not any(isinstance(entry.get("result"), str)
                    and entry["result"].lower().startswith("error") for entry in suffix),
            "suffix contains a native tool error", errors)
    world = read(evidence_path(folder, public["final_world_path"]))
    require({"products", "users", "orders"} <= set(world),
            "final public world is incomplete", errors)
    require(equal(world, reference), "complete public final world differs from reference", errors)
    return len(drafts), len(suffix)


def score_arm(case, method, folder, inputs):
    row = {
        "case_id": case["id"], "task_id": str(case["task_id"]), "kind": case["kind"],
        "method": method, "status": "UNKNOWN", "boundary_status": "UNKNOWN",
        "public_status": "UNKNOWN", "attempts": None, "commits": None,
        "first_rejected": None, "scripted_recovery_committed": None,
        "native_draft_calls": None, "suffix_calls": None, "errors": "",
    }
    errors = []
    try:
        record = read(folder / "record.json")
        if record.get("engineering_status") != "COMPLETE":
            raise RuntimeError(record.get("error", "run did not complete"))
        require(record["method"] == method and record["case_id"] == case["id"]
                and record["kind"] == case["kind"], "record identifies a different route", errors)
        durable = dump_sql(evidence_path(folder, record["db_path"]))
        require(equal(durable, sql_normalize(read(folder / "sql-final.json"))),
                "saved final SQL differs from actual SQLite", errors)
        attempts = record["attempts"]
        row["attempts"] = len(attempts)
        require(len(attempts) == (2 if case["kind"] in BAD_FIRST else 1),
                "attempt count differs from fixed recovery protocol", errors)
        if not attempts:
            raise UnknownEvidence("No boundary attempt")
        draft_attempts = []
        for number, attempt in enumerate(attempts, 1):
            require(attempt["attempt"] == number, "attempt sequence is not contiguous", errors)
            if number > 1:
                require(equal(sql_normalize(attempts[number - 2]["sql_after"]),
                              sql_normalize(attempt["sql_before"])),
                        "state or authority changed between fixed recovery attempts", errors)
            _, called = check_attempt(attempt, case, number, method, durable, errors)
            if called:
                draft_attempts.append((number, attempt))
        require(equal(durable, sql_normalize(attempts[-1]["sql_after"])),
                "actual SQLite differs from last attempt evidence", errors)
        initial, final = core(record["initial"]), latest(durable, method)
        require(equal(initial, latest(attempts[0]["sql_before"], method))
                and equal(core(record["final"]), final),
                "reported initial/final state differs from actual SQL evidence", errors)
        require(sorted(r["version"] for r in history(durable, method)) == [1, 2],
                "route did not create exactly one target successor", errors)
        row["commits"] = sum(
            latest(a["sql_after"], method)["version"] > latest(a["sql_before"], method)["version"]
            for a in attempts)
        row["first_rejected"] = not attempts[0]["committed"]
        row["scripted_recovery_committed"] = (
            len(attempts) == 2 and attempts[1]["committed"] is True
            if case["kind"] in BAD_FIRST else None)
        if method == "T-configured":
            require(not record.get("startup_stdout") and not record.get("startup_stderr"),
                    "unexpected upstream startup diagnostic", errors)
        row["boundary_status"] = "PASS" if not errors else "FAIL"
        public_errors = []
        row["native_draft_calls"], row["suffix_calls"] = check_public(
            record, case, folder, inputs, final, draft_attempts, public_errors)
        row["public_status"] = "PASS" if not public_errors else "FAIL"
        errors.extend(public_errors)
        row["status"] = "PASS" if not errors else "FAIL"
    except UnknownEvidence as exc:
        row["status"] = "UNKNOWN"
        errors.append(f"{type(exc).__name__}: {exc}")
    except Exception as exc:
        row["status"] = "ENGINEERING_ERROR"
        errors.append(f"{type(exc).__name__}: {exc}")
    row["errors"] = "; ".join(errors)
    return row


def verify_hash_manifest(folder, errors):
    manifest = read(folder / "MANIFEST.json")
    for relative, expected in manifest["files"].items():
        file = evidence_path(folder, relative)
        require(file.is_file() and sha(file) == expected,
                f"input hash mismatch: {relative}", errors)


def score_run(folder):
    folder = Path(folder).resolve()
    inputs = folder / "inputs"
    cases = read(inputs / "cases.json")
    integrity_errors = []
    expected_ids = {f"P{task}-{kind}" for task in TASKS for kind in KINDS}
    require(len(cases) == 24 and {case["id"] for case in cases} == expected_ids,
            "run does not contain the frozen 24 unique task/scenario cases", integrity_errors)
    require(all(case["id"] == f"P{case['task_id']}-{case['kind']}" for case in cases),
            "case identity disagrees with task/scenario", integrity_errors)
    verify_hash_manifest(inputs, integrity_errors)
    freeze = read(folder / "freeze.json")
    source_hashes = {}
    for category in ("files", "protected_files"):
        for item in freeze.get(category, []):
            path = Path(item["path"])
            actual = sha(path) if path.is_file() else None
            source_hashes[str(path)] = actual
            require(actual == item["sha256"], f"frozen source mismatch: {path}", integrity_errors)
    require(bool(source_hashes), "freeze contains no verifiable source files", integrity_errors)
    require(str(HERE / "public_score.py").replace("\\", "/")
            in {str(Path(path)).replace("\\", "/") for path in source_hashes},
            "independent scorer was not included in source freeze", integrity_errors)
    receipt = read(folder / "RUN.json")
    require(receipt.get("network_attempts") == [], "run had network attempts or lacks their log", integrity_errors)
    result_hashes = receipt["result_hashes"]
    require(bool(result_hashes), "run receipt has no result hashes", integrity_errors)
    for item in result_hashes:
        path = evidence_path(folder, item["path"])
        require(path.is_file() and sha(path) == item["sha256"],
                f"saved run artifact hash mismatch: {item['path']}", integrity_errors)
    preflight = read(inputs / "PREFLIGHT.json")
    require(preflight.get("network_attempts") == []
            and len(preflight["tasks"]) == 6
            and all(item["status"] == "COMPLETE" for item in preflight["tasks"]),
            "native reference preflight was incomplete or attempted network", integrity_errors)
    rows = [score_arm(case, method, folder / case["id"] / method, inputs)
            for case in cases for method in METHODS]
    hashes = {}
    for path in sorted(folder.rglob("*")):
        if path.is_file() and not path.name.startswith("SCORE") and path.suffix in {".json", ".gz", ".sqlite"}:
            hashes[path.relative_to(folder).as_posix()] = sha(path)
    by_method = {}
    for method in METHODS:
        group = [r for r in rows if r["method"] == method]
        by_method[method] = {
            "statuses": dict(Counter(r["status"] for r in group)),
            "boundary_statuses": dict(Counter(r["boundary_status"] for r in group)),
            "public_statuses": dict(Counter(r["public_status"] for r in group)),
            "legal_initial_pass": sum(r["status"] == "PASS" and r["kind"] not in BAD_FIRST for r in group),
            "invalid_then_scripted_recovery_pass": sum(
                r["status"] == "PASS" and r["kind"] in BAD_FIRST for r in group),
        }
    summary = {
        "scope": "6 public tasks x 4 controlled scenarios x 2 methods; scripted reference continuation",
        "interpretation": "Complete native reference-world consistency, not official reward, NL assertion evaluation, or agent success rate",
        "tasks": 6, "task_scenario_combinations": len(cases), "records": len(rows),
        "by_method": by_method, "integrity_errors": integrity_errors,
        "all_pass": not integrity_errors and len(rows) == 48 and all(r["status"] == "PASS" for r in rows),
        "all_pairs_pass": not integrity_errors and len(rows) == 48 and all(
            rows[i]["status"] == rows[i + 1]["status"] == "PASS" for i in range(0, len(rows), 2)),
        "network_attempts": receipt.get("network_attempts"),
        "scorer_sha256": sha(Path(__file__)), "source_sha256": source_hashes,
        "input_and_result_sha256": hashes,
    }
    return rows, summary


def save_or_verify(path, content, verify_only=False):
    if path.exists():
        if path.read_text(encoding="utf-8") != content:
            raise ValueError(f"Existing score differs; preserving it: {path}")
    elif verify_only:
        raise FileNotFoundError(f"No saved score to verify: {path}")
    else:
        with path.open("x", encoding="utf-8", newline="") as stream:
            stream.write(content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_folder", type=Path)
    parser.add_argument("--verify", action="store_true", help="Require and verify existing scores without writing")
    args = parser.parse_args()
    rows, summary = score_run(args.run_folder)
    csv_buffer = io.StringIO(newline="")
    writer = csv.DictWriter(csv_buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    outputs = {
        args.run_folder / "SCORE-rows.csv": csv_buffer.getvalue(),
        args.run_folder / "SCORE.json": json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
    }
    # Verify all existing artifacts before creating any absent score.
    for path, content in outputs.items():
        if path.exists() or args.verify:
            save_or_verify(path, content, verify_only=True)
    for path, content in outputs.items():
        save_or_verify(path, content, verify_only=args.verify)
    print(json.dumps({k: v for k, v in summary.items()
                      if k not in {"source_sha256", "input_and_result_sha256"}}, ensure_ascii=False))
    if not summary["all_pass"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
