"""Independent stdlib read-only SQLite scorer; does not import either gate."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import sqlite3
from collections import Counter
from contextlib import closing
from pathlib import Path


def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def canon(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":"), allow_nan=False)


def equal(left, right):
    return canon(left) == canon(right)


def dump_sql(path):
    with closing(sqlite3.connect(Path(path).resolve().as_uri() + "?mode=ro", uri=True)) as con:
        con.row_factory = sqlite3.Row
        names = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
        return {name: sorted(
            [dict(r) for r in con.execute('SELECT * FROM "' + name.replace('"', '""') + '"')],
            key=lambda row: json.dumps(row, sort_keys=True),
        ) for name in names}


def state(row, method):
    return {
        "version": row["version"],
        "values": json.loads(row["values"] if method == "C" else row["values_json"]),
        "sources": json.loads(row["fact_sources"] if method == "C" else row["sources_json"]),
    }


def core(snapshot):
    return {key: snapshot[key] for key in ("version", "values", "sources")}


def check_committed_relation(tables, method, case, before, after):
    """Join persisted authority/transition/candidate records, not a gate's verdict."""
    errors = []
    if method == "C":
        transitions = [r for r in tables["fact_transitions"] if r["created_version"] == after["version"]]
        certs = {r["certificate_id"]: r for r in tables["candidate_certificates"]}
        decisions = {r["decision_id"]: r for r in tables["human_decisions"]}
        bindings = {r["decision_id"]: r for r in tables["authorization_bindings"]}
        if len(transitions) != 1:
            return ["expected exactly one changed-field transition"]
        t = transitions[0]
        c = certs.get(t["certificate_id"], {})
        b = bindings.get(t["decision_id"], {})
        h = decisions.get(t["decision_id"], {})
        checks = {
            "field": t["field_key"] == "address",
            "source_anchor": after["sources"]["address"] == t["transition_id"],
            "reviewed_instance": b.get("certificate_id") == t["certificate_id"],
            "expected_selected_candidate": c.get("candidate_id") == (
                case["id"] + ":review:address" + (":preview" if case["kind"] == "reauthorized" else "")
            ),
            "candidate_predecessor": c.get("expected_fact_version") == before["version"],
            "proposal": equal(json.loads(c.get("value_payload", "null")), case["proposal"]),
            "authorized": equal(json.loads(b.get("authorized_value_payload", "null")), case["authorized"]),
            "executed": equal(json.loads(t["value_payload"]), case["authorized"]),
            "decision_field": h.get("field_key") == "address",
        }
    else:
        transitions = [json.loads(r["record_json"]) for r in tables["transitions"]]
        transitions = [r for r in transitions if r["version"] == after["version"] and not r["external"]]
        candidates = {r["candidate_id"]: json.loads(r["context_json"]) for r in tables["candidates"]}
        approvals = {r["approval_id"]: json.loads(r["authorization_json"]) for r in tables["approvals"]}
        if len(transitions) != 1:
            return ["expected exactly one changed-field transition"]
        t = transitions[0]
        c = candidates.get(t["used_candidate_id"], {})
        a = approvals.get(t["approval_id"], {})
        checks = {
            "field": t["field"] == "address",
            "source_anchor": after["sources"]["address"] == t["transition_id"],
            "reviewed_instance": a.get("reviewed_candidate_id") == t["used_candidate_id"] == t["reviewed_candidate_id"],
            "expected_selected_candidate": t["used_candidate_id"] == ("c2" if case["kind"] == "reauthorized" else "c1"),
            "candidate_predecessor": c.get("predecessor_version") == before["version"] == a.get("predecessor_version"),
            "proposal": equal(c.get("proposal"), case["proposal"]) and equal(t["proposal"], case["proposal"]),
            "authorized": equal(a.get("authorized"), case["authorized"]) and equal(t["authorized"], case["authorized"]),
            "executed": equal(t["final"], case["authorized"]),
            "previous_source": t["previous_source"] == before["sources"]["address"],
        }
    errors += [name for name, valid in checks.items() if not valid]
    return errors


def check_identity_fixture(tables, record, case, method):
    """Check that preview/review/attempt actually used the specified identities."""
    kind = case["kind"]
    if kind not in {"reused_after_preview", "reauthorized", "instance_mismatch"}:
        return []
    errors = []
    if method == "C":
        candidates = {r["candidate_id"]: r for r in tables["candidate_certificates"]}
        first_name = case["id"] + ":review:address"
        second_name = first_name + (":substitute" if kind == "instance_mismatch" else ":preview")
        first, second = candidates.get(first_name), candidates.get(second_name)
        if not first or not second:
            return ["identity fixture missing original or second candidate in SQLite"]
        context = lambda row: {k: v for k, v in row.items() if k not in {"certificate_id", "candidate_id"}}
        expected_used = second if kind in {"reauthorized", "instance_mismatch"} else first
        expected_reviewed = second if kind == "reauthorized" else first
        if record["used_candidate_ids"].get("address") != expected_used["certificate_id"]:
            errors.append("attempt did not use expected candidate")
        if record["reviewed_candidate_ids"].get("address") != expected_reviewed["certificate_id"]:
            errors.append("review did not bind expected candidate")
    else:
        candidates = {r["candidate_id"]: json.loads(r["context_json"]) for r in tables["candidates"]}
        first, second = candidates.get("c1"), candidates.get("c2")
        if not first or not second:
            return ["identity fixture missing original or second candidate in SQLite"]
        context = lambda row: {k: v for k, v in row.items() if k != "candidate_id"}
        entered = {k: v["value"] for k, v in record["symbolic_before"].items()}
        if entered["candidate"]["candidate_id"] != ("c2" if kind in {"reauthorized", "instance_mismatch"} else "c1"):
            errors.append("pipeline did not receive expected candidate")
        if entered["approval"]["reviewed_candidate_id"] != ("c2" if kind == "reauthorized" else "c1"):
            errors.append("pipeline did not receive expected review")
    if not equal(context(first), context(second)):
        errors.append("preview/substitution changed context as well as identity")
    return errors


def score_arm(case, method, folder):
    record = read(folder / "record.json")
    row = {"case_id": case["id"], "kind": case["kind"], "method": method,
           "expected_write": case["expected_write"], "observed_write": None,
           "pre_calls": None, "post_calls": None, "executor_calls": None,
           "status": "UNKNOWN", "errors": ""}
    if record["engineering_status"] != "COMPLETE":
        row.update(status="ENGINEERING_ERROR", errors=record.get("error", "incomplete"))
        return row
    tables = dump_sql(folder / record["db_path"])
    errors = []
    if not equal(tables, read(folder / record["sql_after_path"])):
        errors.append("saved SQL differs from actual SQLite")
    errors += check_identity_fixture(tables, record, case, method)
    history = tables["record_versions" if method == "C" else "versions"]
    before_version = 2 if case["kind"] == "stale" else 1
    before_rows = [r for r in history if r["version"] == before_version]
    if len(before_rows) != 1:
        raise ValueError(f"Missing unique before version in {folder}")
    before = state(before_rows[0], method)
    after = state(max(history, key=lambda r: r["version"]), method)
    if not equal(before, core(record["before"])) or not equal(after, core(record["after"])):
        errors.append("reported state differs from independently read SQLite")
    initial_expected = json.loads(json.dumps(case["initial"]))
    if case["kind"] == "stale":
        initial_expected["batch"] = "concurrent"
    if not equal(before["values"], initial_expected):
        errors.append("before state does not implement frozen fixture")
    delta = after["version"] - before["version"]
    row["observed_write"] = delta > 0
    if method == "C" and record.get("outcome", {}).get("status") == "ERROR":
        row.update(status="ENGINEERING_ERROR", errors="C returned an engineering error")
        return row
    if delta != int(case["expected_write"]):
        errors.append(f"business version delta {delta} differs from expected")
    if bool(record.get("committed")) != (delta > 0):
        errors.append("commit report disagrees with durable effect")
    if case["expected_write"]:
        expected = json.loads(json.dumps(initial_expected))
        expected["address"] = case["authorized"]
        if not equal(after["values"], expected):
            errors.append("incorrect complete successor")
        if set(after["sources"]) != set(expected):
            errors.append("incomplete source map")
        if after["sources"].get("batch") != before["sources"]["batch"]:
            errors.append("unchanged field source was not preserved")
        errors += check_committed_relation(tables, method, case, before, after)
    else:
        if not equal(before, after):
            errors.append("rejected attempt changed business state")
        if method == "C":
            new_transitions = [r for r in tables["fact_transitions"] if r["created_version"] > before_version]
        else:
            new_transitions = [r for r in tables["transitions"] if json.loads(r["record_json"])["version"] > before_version]
        if new_transitions:
            errors.append("rejected attempt left a business transition")
    if method == "T-configured":
        counts = record["callback_counts"]
        logs = record["callback_log"]
        # Upstream callbacks turn raised exceptions into False. An exception
        # without a completed log is an execution error, not a valid rejection.
        logged = Counter(entry.get("callback") for entry in logs)
        log_complete = all(
            isinstance(entry.get("checks"), dict) and entry["checks"]
            and all(type(value) is bool for value in entry["checks"].values())
            and type(entry.get("passed")) is bool
            and entry["passed"] == all(entry["checks"].values())
            for entry in logs
        )
        if not log_complete or any(logged[name] != counts[name] for name in ("pre", "post")):
            row.update(status="ENGINEERING_ERROR", errors="callback did not finish with a complete predicate log")
            return row
        expected_called = case["kind"] not in {"instance_mismatch", "stale"}
        row.update(pre_calls=counts["pre"], post_calls=counts["post"], executor_calls=record["executor_calls"])
        if counts != {"pre": 1, "post": int(expected_called)} or record["executor_calls"] != int(expected_called):
            errors.append("unexpected native callback/executor count")
        if not case["expected_write"] and not equal(record["symbolic_before"], record["symbolic_after"]):
            errors.append("rejection changed symbolic state")
        if case["expected_write"]:
            symbolic = {k: v["value"] for k, v in record["symbolic_after"].items()}
            if not equal(core(symbolic), after):
                errors.append("accepted symbolic and durable state differ")
        if record["stdout"] or record["stderr"]:
            errors.append("unexpected captured upstream diagnostic; inspect raw output")
    row.update(status="PASS" if not errors else "FAIL", errors="; ".join(errors))
    return row


def score_run(folder):
    folder = Path(folder).resolve()
    cases = read(folder / "cases.json")
    rows = [score_arm(case, method, folder / case["id"] / method)
            for case in cases for method in ("T-configured", "C")]
    receipt = read(folder / "RUN.json")
    by_method = {}
    for method in ("T-configured", "C"):
        group = [r for r in rows if r["method"] == method]
        by_method[method] = {
            "statuses": dict(Counter(r["status"] for r in group)),
            "legal_controls_committed": sum(r["status"] == "PASS" and r["expected_write"]
                                            and r["observed_write"] is True for r in group),
            "invalid_controls_without_commit": sum(r["status"] == "PASS" and not r["expected_write"]
                                                  and r["observed_write"] is False for r in group),
        }
    artifacts = {}
    for file in sorted(folder.rglob("*")):
        if file.is_file() and file.suffix in {".sqlite", ".json"} and not file.name.startswith("SCORE"):
            artifacts[file.relative_to(folder).as_posix()] = hashlib.sha256(file.read_bytes()).hexdigest()
    summary = {
        "scope": "8 development controls, 2 conditions; not a heldout benchmark or statistical equivalence test",
        "records": len(rows), "by_method": by_method,
        "all_pass": all(r["status"] == "PASS" for r in rows),
        "all_pairs_same_observed_write": all(
            rows[i]["status"] in {"PASS", "FAIL"} and rows[i + 1]["status"] in {"PASS", "FAIL"}
            and type(rows[i]["observed_write"]) is bool and type(rows[i + 1]["observed_write"]) is bool
            and rows[i]["observed_write"] == rows[i + 1]["observed_write"]
            for i in range(0, len(rows), 2)),
        "network_attempts": receipt["network_attempts"],
        "input_sha256": artifacts,
    }
    return rows, summary


def save_or_verify(path, text):
    path = Path(path)
    if path.exists():
        if path.read_text(encoding="utf-8") != text:
            raise ValueError(f"Existing scores differ; preserving saved result: {path}")
    else:
        with path.open("x", encoding="utf-8", newline="") as output:
            output.write(text)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("run_folder", type=Path)
    args = parser.parse_args()
    rows, summary = score_run(args.run_folder)
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    save_or_verify(args.run_folder / "SCORE-rows.csv", buffer.getvalue())
    save_or_verify(args.run_folder / "SCORE.json", json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: v for k, v in summary.items() if k != "input_sha256"}))
    if not summary["all_pass"] or summary["network_attempts"]:
        raise SystemExit(1)
