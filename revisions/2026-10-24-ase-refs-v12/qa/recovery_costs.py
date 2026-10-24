"""Read-only audit of saved G episodes; writes only this review's outputs.

No model calls and no experimental reruns. The route minima (reuse=1,
reauthorization=2) are conditional on the manuscript's tool interface.
"""
import csv
import hashlib
import json
import statistics
import zipfile
from collections import Counter
from pathlib import Path, PurePosixPath

LIVE = Path(__file__).resolve().parent.parent
ROOT = LIVE.parent.parent
OUT = LIVE / "tables"
DATA = LIVE / "scripts/figures/figure-data.json"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def sha(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def main():
    import argparse
    global ROOT, OUT
    parser = argparse.ArgumentParser(description='Recompute recovery costs from the two frozen archives.')
    parser.add_argument('--repository-root', type=Path, default=ROOT, help='Full repository containing the original and supplementary archives')
    parser.add_argument('--output', type=Path, default=OUT, help='Output directory for derived tables and audit records')
    args = parser.parse_args()
    ROOT = args.repository_root.resolve()
    OUT = args.output.resolve()
    OUT.mkdir(parents=True, exist_ok=True)
    data = read_json(DATA)
    source_checks = []
    sources = {source["path"]: source for source in data["sources"]}
    required_archives = sorted({pair["source_archive"] for pair in data["g_pairs"]})
    for archive in required_archives:
        if archive not in sources:
            raise ValueError(f"Archive has no frozen hash: {archive}")
        path = ROOT / archive
        if not path.is_file():
            raise FileNotFoundError(f"Required archive missing: {path}. See REPRODUCE-RECOVERY.md.")
        source_checks.append({"path": archive,
                              "matches": sha(path) == sources[archive]["sha256"]})
    if not all(x["matches"] for x in source_checks):
        raise ValueError("A recovery archive differs from its frozen hash")

    archives, rows = {}, []
    state_hash_checks = 0
    try:
        for pair in data["g_pairs"]:
            archive = pair["source_archive"]
            if archive not in archives:
                archives[archive] = zipfile.ZipFile(ROOT / archive)
            z = archives[archive]
            member = pair["archive_members"]["bound"]["events"]
            events = [json.loads(s) for s in z.read(member).decode("utf-8-sig").splitlines() if s.strip()]
            assert [e["sequence"] for e in events] == sorted(e["sequence"] for e in events)
            by_id = {e["event_id"]: e for e in events}
            feedback = by_id[pair["bound_episode"]["feedback_event_id"]]
            assert feedback["event_type"] == "feedback_delivered"
            assert feedback["payload"]["delivered"] is True
            trigger = by_id[feedback["payload"]["decision_event_id"]]
            tp = trigger["payload"]
            assert (tp.get("reason_code") or tp.get("result", {}).get("error_code")) == "INSTANCE_MISMATCH"
            results = {e["payload"]["tool_call_id"]: e for e in events if e["event_type"] == "tool_result"}
            agent_calls = [e for e in events if e["event_type"] == "tool_call" and e["origin"] == "agent"]
            later = [e for e in agent_calls if e["sequence"] > feedback["sequence"]]
            endpoint = None
            for call in later:
                result_event = results.get(call["payload"]["tool_call_id"])
                if not result_event:
                    continue
                rp = result_event["payload"]
                if call["payload"]["tool_name"] != "commit" or rp["result"].get("status") != "ok":
                    continue
                states = []
                for key in ("state_before_ref", "state_after_ref"):
                    ref = rp[key]
                    state_member = str(PurePosixPath(member).parent / ref["relative_path"])
                    raw = z.read(state_member)
                    assert hashlib.sha256(raw).hexdigest() == ref["sha256"]
                    state_hash_checks += 1
                    states.append(json.loads(raw.decode("utf-8-sig")))
                if len(states[1]["transitions"]) > len(states[0]["transitions"]):
                    assert result_event["sequence"] > call["sequence"]
                    endpoint = call
                    break
            assert endpoint is not None, f"No durable recovery: {pair['id']}"
            episode = [e for e in later if e["sequence"] <= endpoint["sequence"]]
            post = [e for e in later if e["sequence"] > endpoint["sequence"]]
            names = [e["payload"]["tool_name"] for e in episode]
            minimum = {"reuse-reviewed": 1, "reauthorization": 2}[pair["recovery_path"]]
            expected = ["commit"] if minimum == 1 else ["request_authorization", "commit"]
            assert names == expected, (pair["id"], names)
            assert len(episode) == pair["bound_episode"]["additional_tool_calls"]
            assert len(agent_calls) == pair["bound_calls"]
            assert len(episode) + len(post) == len(agent_calls), "Unaccounted pre-feedback calls"
            assert all(results[e["payload"]["tool_call_id"]]["payload"]["result"].get("status") == "ok" for e in episode)

            c_member = pair["archive_members"]["context"]["events"]
            c_events = [json.loads(s) for s in z.read(c_member).decode("utf-8-sig").splitlines() if s.strip()]
            c_calls = [e for e in c_events if e["event_type"] == "tool_call" and e["origin"] == "agent"]
            assert len(c_calls) == pair["context_calls"]
            assert len(agent_calls) - len(c_calls) == pair["calls_delta"]
            rows.append({
                "cohort": pair["cohort"], "id": pair["id"], "case_id": pair["case_id"],
                "route": pair["recovery_path"], "route_minimum_calls": minimum,
                "actual_calls_to_durable_commit": len(episode), "excess_calls_for_selected_route": len(episode) - minimum,
                "post_commit_calls": len(post), "post_commit_tools": ";".join(e["payload"]["tool_name"] for e in post),
                "bound_suffix_calls": len(agent_calls), "context_suffix_calls": len(c_calls),
                "suffix_call_difference": pair["calls_delta"], "suffix_seconds_difference": pair["seconds_delta"],
                "recovery_tools": ";".join(names), "context_tools": ";".join(e["payload"]["tool_name"] for e in c_calls),
                "context_completion": pair["contextU"], "bound_completion": pair["boundU"],
                "feedback_event": feedback["event_id"], "durable_commit_call": endpoint["event_id"],
                "archive": archive, "bound_events_member": member, "context_events_member": c_member,
            })
    finally:
        for z in archives.values():
            z.close()

    summaries = []
    for cohort in ("original_A", "original_B", "supplementary_A"):
        rs = [r for r in rows if r["cohort"] == cohort]
        item = {"cohort": cohort, "n": len(rs), "routes": dict(Counter(r["route"] for r in rs))}
        for key in ("route_minimum_calls", "actual_calls_to_durable_commit", "excess_calls_for_selected_route", "post_commit_calls", "bound_suffix_calls", "context_suffix_calls", "suffix_call_difference"):
            vals = [r[key] for r in rs]
            item[key] = {"mean": statistics.mean(vals), "min": min(vals), "max": max(vals)}
        item["suffix_seconds_difference"] = {"median": statistics.median(r["suffix_seconds_difference"] for r in rs), "min": min(r["suffix_seconds_difference"] for r in rs), "max": max(r["suffix_seconds_difference"] for r in rs)}
        summaries.append(item)
    result = {
        "scope": "Read-only audit of archived G events and state hashes, not a rerun or complete research-package audit.",
        "metric_boundary": "Calls after delivered mismatch feedback through first successful commit that adds a persisted transition. Minimum is route-specific tool calls, not optimal route choice, human cost, model turns, or elapsed time.",
        "source_checks": source_checks,
        "figure_data_sha256": sha(DATA), "state_hash_checks": state_hash_checks,
        "g_episodes": len(rows), "task_definitions": len({r["case_id"] for r in rows}),
        "routes": dict(Counter(r["route"] for r in rows)),
        "route_minimum_met": sum(r["excess_calls_for_selected_route"] == 0 for r in rows),
        "cohorts": summaries,
        "arithmetic_checks": {"original_completion_context": 9 + 117, "original_completion_bound": 9 + 119, "original_difference_percentage_points": 100 * 2 / 256, "supplementary_difference_percentage_points": 100 * 2 / 117},
    }
    with (OUT / "recovery-cost-episodes.csv").open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (OUT / "recovery-cost-source.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    table = [r"\begin{table}[tbp]", r"\caption{Agent tool calls at delivered G handoffs. All entries except $n$ are cohort means; post-commit calls occur after the first successful persistent recovery commit.}\label{tab:recovery-decomposition}", r"\centering\small", r"\setlength{\tabcolsep}{3pt}", r"\begin{tabular*}{\textwidth}{@{\extracolsep{\fill}}lrrrrrr@{}}", r"\toprule", r"Collection & $n$ & \shortstack{To recovery\\commit} & \shortstack{After\\commit} & \shortstack{Bound\\suffix} & \shortstack{Context\\suffix} & $\Delta$ \\", r"\midrule"]
    labels = {"original_A":"Original A", "original_B":"Original B", "supplementary_A":"Supplementary A"}
    for c in summaries:
        keys = ["actual_calls_to_durable_commit", "post_commit_calls", "bound_suffix_calls", "context_suffix_calls", "suffix_call_difference"]
        table.append(labels[c["cohort"]] + " & " + str(c["n"]) + " & " + " & ".join(f"{c[k]['mean']:.3f}" for k in keys) + r" \\")
    table += [r"\bottomrule", r"\end{tabular*}", r"\par\smallskip\begin{minipage}{\textwidth}\small Recovery comprises one commit in each of 24 reuse episodes and an authorization request followed by a commit in each of eight fresh-authorization episodes. The last column is bound minus context over complete suffixes, not calls beyond a route minimum. Values are recomputed from the archived event order and persistent transitions; no new runs are added.\end{minipage}", r"\end{table}"]
    (OUT / "recovery-decomposition.tex").write_text("\n".join(table)+"\n",encoding="utf-8")
    print(json.dumps({"episodes":len(rows),"state_hash_checks":state_hash_checks,"route_minimum_met":result["route_minimum_met"],"output":str(OUT / "recovery-decomposition.tex")}))



if __name__ == "__main__":
    main()
