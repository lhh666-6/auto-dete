"""Portable offline scientific readback from frozen archives and distributed tables.

No experiment execution, model calls, or network access. Both --repository-root
and --output are explicit. The completion bootstrap preserves the archived seed
and percentile convention; the G bootstrap remains labelled exploratory.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import random
import re
import statistics
import sys
import zipfile
from collections import Counter, defaultdict
from pathlib import Path, PurePosixPath

BASE = Path(__file__).resolve().parent.parent
ORIGINAL = "revisions/2026-10-07-kais-continuity/replication-package.zip"
SUPPLEMENT = "research/phase2-results-snapshots/2026-10-07-complete/quota-recovery-complete.zip"
EXPECTED = {
    ORIGINAL: "1bc17338d18f198811e0e58eca9b64bded29f9b01cd61558862455e7e0d469d8",
    SUPPLEMENT: "536f8b7d784d1af118145affd90c3d613b67ad44d9c5b3607b463bcebeacbec1",
}
LEDGERS = {
    ORIGINAL: "research/agent-policy-phase2-formal-2026-10-07/formal-results/collection-status.json",
    SUPPLEMENT: "research/agent-policy-phase2-quota-recovery-2026-10-07/results/collection-status.json",
}
SOURCE_FILES = {}
SOURCE_MEMBERS = {}


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def read_file(path):
    raw = path.read_bytes()
    SOURCE_FILES[str(path)] = digest(raw)
    return raw


def read_json(path):
    return json.loads(read_file(path).decode("utf-8-sig"))


class Archive:
    def __init__(self, root, relative):
        self.relative = relative
        self.path = root / relative
        assert digest(read_file(self.path)) == EXPECTED[relative], relative
        self.z = zipfile.ZipFile(self.path)
        self.names = self.z.namelist()

    def raw(self, member):
        raw = self.z.read(member)
        SOURCE_MEMBERS[self.relative + "::" + member] = digest(raw)
        return raw

    def json(self, member):
        return json.loads(self.raw(member).decode("utf-8-sig"))

    def events(self, member):
        return [json.loads(s) for s in self.raw(member).decode("utf-8-sig").splitlines() if s.strip()]


def percentile_interval(values):
    values = sorted(values)
    n = len(values)
    return [values[int(.025 * (n - 1))], values[int(.975 * (n - 1))]]


def completion(archive):
    status = archive.json(LEDGERS[ORIGINAL])
    # Read and hash the frozen algorithm, but do not execute archived source.
    archive.raw("research/agent-policy-phase2-formal-2026-10-07/src/phase2/analysis.py")
    grouped, counts = defaultdict(dict), defaultdict(Counter)
    all_family_b = []
    for pair in status["pairs"].values():
        a = pair["assignment"]
        r = pair["result"]
        c, t = a["config_id"], a["case_id"]
        d = int(r["bound"]["task_completion"]) - int(r["context"]["task_completion"])
        grouped[t][c] = d
        grouped[t]["scenario"] = a["scenario"]
        for policy in ("context", "bound"):
            counts[c][policy] += int(r[policy]["task_completion"])
        counts[c]["pairs"] += 1
        counts[c]["context_only"] += int(d == -1)
        counts[c]["bound_only"] += int(d == 1)
        if c == "B" and all("elapsed_ms" in r[p] for p in ("context", "bound")):
            all_family_b.append({"pair_id": a["pair_id"],
                                 "calls": r["bound"]["agent_tool_calls"] - r["context"]["agent_tool_calls"],
                                 "seconds": (r["bound"]["elapsed_ms"] - r["context"]["elapsed_ms"]) / 1000})
    tasks = sorted(grouped)
    assert len(tasks) == 128 and all(v["A"] == 0 for v in grouped.values())
    strata = [[t for t in tasks if grouped[t]["scenario"] == s]
              for s in sorted({v["scenario"] for v in grouped.values()})]
    rng = random.Random(20261007)
    draws_b, draws_pooled = [], []
    for _ in range(10000):
        sampled = [rng.choice(block) for block in strata for _ in block]
        b = sum(grouped[t]["B"] for t in sampled) / len(sampled)
        pooled = sum((grouped[t]["A"] + grouped[t]["B"]) / 2 for t in sampled) / len(sampled)
        assert pooled == b / 2
        draws_b.append(b)
        draws_pooled.append(pooled)
    b = sum(v["B"] for v in grouped.values()) / 128
    pooled = sum((v["A"] + v["B"]) / 2 for v in grouped.values()) / 128
    ib, ip = percentile_interval(draws_b), percentile_interval(draws_pooled)
    assert (b, ib) == (0.015625, [-0.0390625, 0.0703125])
    assert (pooled, ip) == (0.0078125, [-0.01953125, 0.03515625])
    return {
        "unit": "128 task clusters; each retains 2 configuration-specific policy pairs; 256 planned arms per policy, 512 arms overall",
        "planned_policy_pairs": 256, "task_clusters": 128,
        "counts_by_config": dict(counts),
        "original_B": {"estimate": b, "percentile_95_interval": ib},
        "pooled": {"estimate": pooled, "percentile_95_interval": ip},
        "bootstrap_iterations": 10000, "seed": 20261007,
        "stratum_sizes": {s: sum(v["scenario"] == s for v in grouped.values())
                          for s in sorted({v["scenario"] for v in grouped.values()})},
        "all_10000_pooled_draws_equal_half_B": True,
        "all_family_B_recorded_suffix_pairs": {
            "pairs": len(all_family_b),
            "mean_call_difference": statistics.mean(r["calls"] for r in all_family_b),
            "mean_seconds_difference": statistics.mean(r["seconds"] for r in all_family_b),
            "median_seconds_difference": statistics.median(r["seconds"] for r in all_family_b),
            "excluded_pair": "FORMAL-N-020-B (bound suffix not started, no suffix cost record)",
        },
        "interpretation": "The pooled contrast and interval rescale the same B discordance by exactly one half; they provide no independent precision gain. Planned-ledger denominators retain pre-review failures.",
    }


def durable_increment(archive, events_member, result):
    states = []
    for name in ("state_before_ref", "state_after_ref"):
        ref = result["payload"][name]
        member = str(PurePosixPath(events_member).parent / ref["relative_path"])
        raw = archive.raw(member)
        assert digest(raw) == ref["sha256"], member
        states.append(json.loads(raw))
    return len(states[1]["transitions"]) > len(states[0]["transitions"])


def recovery(archives):
    data = read_json(BASE / "scripts/figures/figure-data.json")
    rows = list(csv.DictReader(io.StringIO(read_file(BASE / "tables/recovery-cost-episodes.csv").decode("utf-8-sig"))))
    figures = {(p["cohort"], p["id"]): p for p in data["g_pairs"]}
    audited = []
    for r in rows:
        p = figures[(r["cohort"], r["id"])]
        z = archives[r["archive"]]
        be = z.events(r["bound_events_member"])
        ce = z.events(r["context_events_member"])
        by_id = {e["event_id"]: e for e in be}
        feedback, endpoint = by_id[r["feedback_event"]], by_id[r["durable_commit_call"]]
        assert feedback["event_type"] == "feedback_delivered" and feedback["payload"]["delivered"]
        calls = [e for e in be if e["event_type"] == "tool_call" and e["origin"] == "agent"]
        recovery_calls = [e for e in calls if feedback["sequence"] < e["sequence"] <= endpoint["sequence"]]
        post = [e for e in calls if e["sequence"] > endpoint["sequence"]]
        ccalls = [e for e in ce if e["event_type"] == "tool_call" and e["origin"] == "agent"]
        names = [e["payload"]["tool_name"] for e in recovery_calls]
        expected = ["commit"] if r["route"] == "reuse-reviewed" else ["request_authorization", "commit"]
        assert names == expected
        assert len(recovery_calls) == int(r["route_minimum_calls"]) == int(r["actual_calls_to_durable_commit"])
        assert len(calls) == len(recovery_calls) + len(post) == int(r["bound_suffix_calls"])
        assert len(ccalls) == int(r["context_suffix_calls"])
        assert len(calls) - len(ccalls) == int(r["suffix_call_difference"]) == p["calls_delta"]
        assert float(r["suffix_seconds_difference"]) == p["seconds_delta"]
        endpoint_result = next(e for e in be if e["event_type"] == "tool_result"
                               and e["payload"]["tool_call_id"] == endpoint["payload"]["tool_call_id"])
        assert endpoint_result["payload"]["result"]["status"] == "ok"
        assert durable_increment(z, r["bound_events_member"], endpoint_result)
        handoff = [e for e in ce if e["origin"] == "harness_handoff"
                   and e["payload"].get("tool_name") == "commit" and "tool_call_id" in e["payload"]]
        assert len(handoff) == 1
        handoff_result = next(e for e in ce if e["event_type"] == "tool_result"
                              and e["payload"]["tool_call_id"] == handoff[0]["payload"]["tool_call_id"])
        assert handoff_result["payload"]["result"]["status"] == "ok"
        assert durable_increment(z, r["context_events_member"], handoff_result)
        audited.append({**r, "harness_commit_event": handoff[0]["event_id"],
                        "harness_commit_result": handoff_result["event_id"],
                        "harness_commit_persisted": True})
    cohorts = []
    for cohort in ("original_B", "original_A", "supplementary_A"):
        rr = sorted([r for r in rows if r["cohort"] == cohort], key=lambda r: r["case_id"])
        values = [int(r["suffix_call_difference"]) for r in rr]
        times = [float(r["suffix_seconds_difference"]) for r in rr]
        interval = None
        if len(rr) > 1:
            rng = random.Random(20261023)
            draws = [statistics.mean(rng.choice(values) for _ in values) for _ in range(10000)]
            interval = percentile_interval(draws)
        cohorts.append({
            "cohort": cohort, "task_pairs": len(rr), "task_definitions": len({r["case_id"] for r in rr}),
            "call_difference_mean": statistics.mean(values), "call_difference_range": [min(values), max(values)],
            "call_difference_distribution": dict(sorted(Counter(values).items())),
            "exploratory_paired_bootstrap_95_interval": interval,
            "seconds_difference_median": statistics.median(times), "seconds_difference_range": [min(times), max(times)],
            "zero_agent_call_context_suffixes": sum(int(r["context_suffix_calls"]) == 0 for r in rr),
            "zero_agent_call_context_suffixes_with_completion": sum(int(r["context_suffix_calls"]) == 0 and int(r["context_completion"]) == 1 for r in rr),
            "routes": dict(Counter(r["route"] for r in rr)),
            "decomposition_means": {k: statistics.mean(int(r[k]) for r in rr) for k in (
                "actual_calls_to_durable_commit", "post_commit_calls", "bound_suffix_calls", "context_suffix_calls")},
        })
    return {
        "pairs": len(rows), "task_definitions": len({r["case_id"] for r in rows}),
        "route_minimum_recovery_calls_met": len(audited), "harness_context_commits_verified": len(audited),
        "persistent_state_hash_checks": 4 * len(audited), "cohorts": cohorts,
        "bootstrap": {"new_exploratory_analysis": True, "iterations": 10000, "seed": 20261023,
                      "unit": "task pair within each cohort, retaining both policy suffixes; never pool the repeated A/B task definitions",
                      "interval": "percentile using floor(.025*(B-1)), floor(.975*(B-1)); absent for original A n=1",
                      "scope": "Conditional sensitivity to resampling these constructed tasks, not a population or deployment-performance guarantee."},
        "interpretation": "All 32 recovery sequences reach the selected-route tool-call minimum. This concerns calls through the first persistent recovery commit, not the full-suffix bound-minus-context difference. The latter includes recovery, later confirmation and context-side calls; the harness already commits on the context side. It is not a count of unnecessary or useless actions, and route minimality does not establish optimal route choice or time.",
    }, audited


def contains(obj, wanted):
    if isinstance(obj, str):
        return obj in wanted
    if isinstance(obj, dict):
        return any(contains(v, wanted) for v in obj.values())
    if isinstance(obj, list):
        return any(contains(v, wanted) for v in obj)
    return False


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def n_exposure(archives, root):
    # Same bounded exposure definition as the prior n_exposure.py, independently
    # regrouped by explicit (collection, pair id), never inferred by dividing arms.
    rows, planned = [], []
    for relative, z in archives.items():
        collection = "original" if relative == ORIGINAL else "suppA"
        ledger = z.json(LEDGERS[relative])
        for pid, p in ledger["pairs"].items():
            if p["assignment"]["scenario"] == "N":
                planned.append((collection, pid))
        finals, afters = {}, {}
        for member in z.names:
            match = re.search(r"/(FORMAL-N-\d+-[AB])/(?:attempt-\d+/)?(context|bound)/state/(final|\d+-after)\.json$", member)
            if not match:
                continue
            task, policy, state = match.groups()
            key = (task, policy)
            if state == "final":
                finals[key] = member
            else:
                number = int(state.split("-")[0])
                if key not in afters or number > afters[key][0]:
                    afters[key] = (number, member)
        for key in sorted(set(finals) | set(afters)):
            state_member = finals.get(key) or afters[key][1]
            state = z.json(state_member)
            directory = state_member.split("/state/")[0]
            grants, candidates = state.get("grants") or {}, state.get("candidates") or {}
            ordered = sorted(grants.values(), key=lambda g: (str(g.get("issued_at", "")), str(g.get("authorization_id", ""))))
            initial = ordered[0].get("reviewed_candidate_id") if ordered else None
            context = candidates.get(initial, {}).get("context")
            wanted = {p for p in state.get("preview_ids", []) if p != initial
                      and isinstance(context, dict) and isinstance(candidates.get(p, {}).get("context"), dict)
                      and canonical(candidates[p]["context"]) == canonical(context)}
            presented = responded = False
            if wanted:
                for member in z.names:
                    if member.startswith(directory + "/model-inputs/") and member.endswith(".json"):
                        if contains(z.json(member), wanted):
                            presented = True
                            break
                events = z.events(directory + "/events.jsonl")
                created = next((i for i, e in enumerate(events) if e["event_type"] == "candidate_created"
                                and e["payload"].get("candidate_id") in wanted), None)
                if created is not None:
                    responded = any(e["event_type"] == "model_response" and not e["payload"].get("error_code")
                                    for e in events[created + 1:])
            reused = reauthorized = False
            unauthorized = 0
            for transition in state.get("transitions") or []:
                args = transition.get("arguments") or {}
                candidate = args.get("candidate_id")
                reviewed = grants.get(args.get("authorization_id"), {}).get("reviewed_candidate_id")
                unauthorized += int(reviewed is not None and candidate != reviewed)
                reused |= candidate is not None and candidate == initial
                reauthorized |= candidate in wanted and reviewed == candidate
            rows.append({"collection": collection, "task": key[0], "policy": key[1],
                         "state_record": state_member, "partial_history": key not in finals,
                         "reviewed": bool(grants), "preview_delivered": bool(state.get("preview_ids")),
                         "exposed_equivalent": bool(wanted), "presented_and_responded": presented and responded,
                         "commit_initial": reused, "reauthorised_preview": reauthorized,
                         "unauthorised_substitution": unauthorized})
    old_path = BASE / "tables/integrated-n-arms.csv"
    old = list(csv.DictReader(io.StringIO(read_file(old_path).decode("utf-8-sig"))))
    by_id = lambda rr: {(r["collection"], r["task"], r["policy"]): r for r in rr}
    previous = by_id(old)
    assert len(previous) == len(rows) == 185
    for r in rows:
        assert {k: str(v) for k, v in r.items()} == previous[(r["collection"], r["task"], r["policy"])]
    summary = {"planned_arms": len(planned) * 2, "planned_pairs": len(planned),
               "planned_task_definitions": len({p.rsplit("-", 1)[0] for _, p in planned}),
               "old_per_arm_csv_exactly_reproduced": True, "populations": {}}
    pair_rows = []
    for label, predicate in (("state_retained", lambda r: True), ("reviewed", lambda r: r["reviewed"]),
                             ("presented_and_responded", lambda r: r["presented_and_responded"])):
        selected = [r for r in rows if predicate(r)]
        groups = defaultdict(list)
        for r in selected:
            groups[(r["collection"], r["task"])].append(r)
        summary["populations"][label] = {
            "arms": len(selected), "cohort_configuration_pairs": len(groups),
            "task_definitions": len({r["task"].rsplit("-", 1)[0] for r in selected}),
            "pairs_with_both_arms": sum(len(v) == 2 for v in groups.values()),
            "pairs_with_one_arm": sum(len(v) == 1 for v in groups.values()),
            "single_arm_pairs": [{"collection": k[0], "pair_id": k[1], "policy": v[0]["policy"]}
                                 for k, v in groups.items() if len(v) == 1],
        }
        if label == "presented_and_responded":
            for (collection, pid), rr in sorted(groups.items()):
                pair_rows.append({"collection": collection, "pair_id": pid,
                                  "task_definition": pid.rsplit("-", 1)[0],
                                  "exposed_arms": len(rr), "policies": ";".join(sorted(r["policy"] for r in rr)),
                                  "reused_arms": sum(r["commit_initial"] for r in rr),
                                  "reauthorized_arms": sum(r["reauthorised_preview"] for r in rr),
                                  "partial_state_arms": sum(r["partial_history"] for r in rr)})
    summary["legal_paths"] = {"reused": sum(r["commit_initial"] for r in rows if r["presented_and_responded"]),
                              "reauthorized": sum(r["reauthorised_preview"] for r in rows if r["presented_and_responded"]),
                              "unauthorized_substitutions": sum(r["unauthorised_substitution"] for r in rows)}
    assert summary["populations"]["presented_and_responded"]["cohort_configuration_pairs"] == 64
    return summary, rows, pair_rows


def feedback():
    analysis = read_json(BASE / "tables/feedback-sensitivity/analysis.json")
    pairs = list(csv.DictReader(io.StringIO(read_file(BASE / "tables/feedback-sensitivity/pairs.csv").decode("utf-8-sig"))))
    cells = [c for c in analysis["cells"] if c["controller"] == "model"]
    pairs = [p for p in pairs if p["controller"] == "model"]
    assert len(cells) == 24 and len(pairs) == 12
    metrics = ["all_tool_calls", "elapsed_seconds", "output_tokens", "input_tokens", "cache_read_input_tokens",
               "cache_creation_input_tokens", "authorization_calls", "get_state_reads", "other_tool_calls",
               "rejected_calls", "retry_attempts", "transport_failures"]
    output = []
    for state in ("valid", "revoked", "unavailable", "all"):
        pp = [p for p in pairs if state == "all" or p["authorization_state"] == state]
        row = {"state": state, "pairs": len(pp), "task_definitions": len({p["task_instance_id"] for p in pp})}
        for metric in metrics:
            totals = {}
            for condition in ("facts", "facts_plus_options"):
                rr = [c for c in cells if c["feedback"] == condition and (state == "all" or c["authorization_state"] == state)]
                totals[condition] = sum(c["costs"][metric] for c in rr)
                row[condition + "_" + metric] = totals[condition]
            delta = totals["facts_plus_options"] - totals["facts"]
            paired_delta = sum(float(p["delta_" + metric]) for p in pp)
            assert abs(delta - paired_delta) < 1e-8, (state, metric)
            row["delta_" + metric] = delta
        output.append(row)
    return {
        "pairs": 12, "task_definitions": 4, "arms_per_condition": 12,
        "unit": "one labels-versus-facts pair within each of four reused tasks and three permission states; 12 pairs are not 12 independent task definitions",
        "direction": "facts_plus_options (labels) minus facts",
        "states_and_total": output,
        "call_difference_distribution": dict(sorted(Counter(int(p["delta_all_tool_calls"]) for p in pairs).items())),
        "scope": "Exploratory descriptive totals, no interaction, significance, equivalence or production-latency inference. Output tokens, uncached input and cache fields remain separate; they are not total billed tokens or monetary cost.",
    }, output


def write_csv(path, rows):
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def checkpoints(archive):
    """Count recorded reached events only after independently hashing saved state."""
    status = archive.json(LEDGERS[ORIGINAL])
    b_pairs = {pid: value for pid, value in status["pairs"].items()
               if value["assignment"]["config_id"] == "B"}
    event_rows = []
    for member in sorted(archive.names):
        match = re.search(r"/(FORMAL-[A-Z]-\d+-B)/prefix/events\.jsonl$", member)
        if not match:
            continue
        pair_id = match.group(1)
        assert pair_id in b_pairs, pair_id
        reached = [event for event in archive.events(member)
                   if event["event_type"] == "checkpoint" and event["payload"].get("reached") is True]
        assert len(reached) <= 1, pair_id
        for event in reached:
            ref = event["payload"]["state_ref"]
            state_member = str(PurePosixPath(member).parent / ref["relative_path"])
            observed = digest(archive.raw(state_member))
            assert observed == ref["sha256"] == event["payload"]["checkpoint_state_sha256"], pair_id
            event_rows.append({"pair_id": pair_id, "event_id": event["event_id"],
                               "events_member": member, "state_member": state_member,
                               "state_sha256": observed})
    event_ids = {r["pair_id"] for r in event_rows}
    summary_ids = {pid for pid, value in b_pairs.items()
                   if value["result"].get("checkpoint_reached") is True}
    assert len(event_ids) == len(event_rows)
    assert summary_ids <= event_ids
    return {"event_verified": len(event_rows), "summary_flags": len(summary_ids),
            "planned_B_pairs": len(b_pairs), "event_verified_without_summary_flag": sorted(event_ids - summary_ids),
            "event_rows": event_rows,
            "scope": "Reached shared-prefix events with matching saved state hashes; no implication that both suffixes started or completed."}


def portable_sources(input_root):
    output = {}
    for absolute, expected in SOURCE_FILES.items():
        path = Path(absolute).resolve()
        if path.is_relative_to(BASE):
            key = "source-root/" + path.relative_to(BASE).as_posix()
        elif path.is_relative_to(input_root):
            key = "input-root/" + path.relative_to(input_root).as_posix()
        else:
            raise ValueError("Unexpected source outside the declared input/source roots")
        output[key] = expected
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository-root", type=Path, required=True,
                        help="INPUT_ROOT with the two frozen ZIP paths in EXTERNAL-INPUTS.json")
    parser.add_argument("--output", type=Path, required=True,
                        help="Directory for scientific-statistics.json and four derived CSVs")
    args = parser.parse_args()
    root, output = args.repository_root.resolve(), args.output.resolve()
    missing = [relative for relative in EXPECTED if not (root / relative).is_file()]
    if missing:
        parser.error("Missing frozen input(s): " + ", ".join(missing))
    archives = {relative: Archive(root, relative) for relative in EXPECTED}
    try:
        result = {"scope": "Read-only reconstruction; exploratory G intervals labelled separately; no experimental reruns.",
                  "python_version": sys.version, "script_sha256": digest(Path(__file__).read_bytes())}
        result["completion"] = completion(archives[ORIGINAL])
        result["recovery"], recovery_rows = recovery(archives)
        result["N"], n_rows, n_pairs = n_exposure(archives, root)
        result["feedback"], feedback_rows = feedback()
        result["checkpoint"] = checkpoints(archives[ORIGINAL])
        assert all(digest(Path(path).read_bytes()) == expected for path, expected in SOURCE_FILES.items())
        result["source_files_sha256"] = portable_sources(root)
        result["source_archive_members_sha256"] = SOURCE_MEMBERS
        result["all_external_input_hashes_unchanged"] = True
        output.mkdir(parents=True, exist_ok=True)
        for name, rows in (("recovery-pairs", recovery_rows), ("n-arms", n_rows),
                           ("n-exposed-pairs", n_pairs), ("feedback-secondary", feedback_rows)):
            write_csv(output / ("integrated-" + name + ".csv"), rows)
        (output / "scientific-statistics.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(json.dumps({"completion_bootstrap_reproduced": True, "recovery_pairs": result["recovery"]["pairs"],
                          "N_exposed_pairs": result["N"]["populations"]["presented_and_responded"]["cohort_configuration_pairs"],
                          "checkpoint_events": result["checkpoint"]["event_verified"],
                          "checkpoint_summary_flags": result["checkpoint"]["summary_flags"],
                          "inputs_unchanged": True}))
    finally:
        for archive in archives.values():
            archive.z.close()


if __name__ == "__main__":
    main()

