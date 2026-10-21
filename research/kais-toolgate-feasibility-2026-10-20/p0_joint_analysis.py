"""Read-only retrospective N/E/C analysis; stdlib, no runner/model/gate calls.

Run: python research/kais-toolgate-feasibility-2026-10-20/p0_joint_analysis.py
Reuses the frozen stdlib scorer's score() on saved SQLite/JSON evidence, checks
the saved scores, and adds paired eligibility checks. Only p0_* outputs change.
"""
from pathlib import Path
from collections import Counter, defaultdict
import argparse
import csv
import hashlib
import json
import runpy


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def require(condition, message):
    if not condition:
        raise ValueError(message)


def main():
    here = Path(__file__).resolve().parent
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=here.parent / "kais-external-baseline-sprint-2026-10-15")
    parser.add_argument("--out-dir", type=Path, default=here)
    args = parser.parse_args()
    source, out = args.source.resolve(), args.out_dir.resolve()
    require(out != source and source not in out.parents, "Outputs must be outside saved source package")
    hashes = {}

    def remember(path):
        path = Path(path).resolve()
        key = path.relative_to(source).as_posix()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        require(key not in hashes or hashes[key] == digest, f"Input changed during reading: {key}")
        hashes[key] = digest
        return path

    def read(path):
        return json.loads(remember(path).read_text(encoding="utf-8"))

    freeze = read(source / "OFFLINE-FREEZE.json")
    for name, digest in freeze["files"].items():
        remember(source / name)
        require(hashes[name] == digest, f"Frozen input hash mismatch: {name}")
    # Read the frozen independent scorer only, never the experiment implementation.
    scorer_path = remember(source / "score_offline.py")
    scorer = runpy.run_path(str(scorer_path), run_name="p0_saved_evidence_scorer")
    score = scorer["score"]
    original_dump = scorer["dump_sql"]

    def tracked_dump(path):
        return original_dump(remember(path))  # Original opens SQLite mode=ro.

    score.__globals__.update(read=read, dump_sql=tracked_dump)
    output = source / "output"
    completion, collection = read(output / "completion.json"), read(output / "collection.json")
    require(collection["freeze_master"] == freeze["master_sha256"], "Freeze identity mismatch")
    folders = sorted(path.parent for path in output.glob("*/record.json"))
    require(set(completion["records"]) == {p.name for p in folders}, "Completion membership mismatch")
    expected = {(x["task_id"], x["scenario"], x["route"]) for x in collection["assignment"]}
    scores = [score(folder) for folder in folders]
    key = lambda r: (r["task_id"], r["scenario"], r["route"])
    require(len(scores) == len(expected) == completion["terminal"] == 99, "Record denominator mismatch")
    require({key(r) for r in scores} == expected, "Assignment mismatch")
    require(all(not r["errors"] for r in scores), "Frozen scorer evidence verification failed")
    saved = read(output / "analysis" / "scores.json")
    require(sorted(scores, key=key) == sorted(saved, key=key), "Recomputed score differs from saved score")
    triples = defaultdict(dict)
    records = {}
    attempts = {}
    for folder, s in zip(folders, scores):
        r = read(folder / "record.json")
        k = key(r)
        records[k] = r
        triples[(r["task_id"], r["scenario"])][r["route"]] = s
        details = []
        for e in r["events"]:
            a, b = read(folder / e["sql_before_path"]), read(folder / e["sql_after_path"])
            pre, post = scorer["state"](a, r["route"]), scorer["state"](b, r["route"])
            require(pre == e["pre_snapshot"] and post == e["post_snapshot"],
                    f"Raw event SQL/snapshot mismatch: {folder.name}/{e['seq']}")
            if e["type"] != "transaction_attempt":
                continue
            preview = e["authorization"]["preview"]
            originals, used = e["original_packets"], e["observed_used_packets"]
            context = lambda p: {k: v for k, v in p.items() if k not in {"id", "candidate_id"}}
            same_context = bool(originals and used) and set(originals) == set(used) and all(
                context(originals[f]) == context(used[f]) for f in originals)
            details.append({
                "seq": e["seq"], "phase": e["phase"],
                "pre_version": pre["version"], "post_version": post["version"],
                "expected_version": preview["expected_version"],
                "fresh": pre["version"] == preview["expected_version"],
                "identity_observability": e["identity_observability"],
                "reviewed_candidate_ids": preview["candidate_ids"],
                "used_candidate_ids": e["observed_used_candidate_ids"],
                "candidate_ids_equal": preview["candidate_ids"] == e["observed_used_candidate_ids"],
                "retained_context_equal_excluding_id_and_candidate_id": same_context,
                "authorized_arguments_equal": {
                    k: v for k, v in e["actual_args"].items() if k != "order_id"
                } == preview["authorized"]["address"],
                "state_unchanged": pre == post,
                "all_tables_unchanged": a == b,
                "changed_tables": sorted(t for t in set(a) | set(b) if a.get(t) != b.get(t)),
                "version_delta": post["version"] - pre["version"],
                "status": e["outcome"]["status"],
                "reason": e["outcome"].get("reason"),
                "sql_before_path": (folder / e["sql_before_path"]).relative_to(source).as_posix(),
                "sql_after_path": (folder / e["sql_after_path"]).relative_to(source).as_posix(),
                "record_path": (folder / "record.json").relative_to(source).as_posix(),
            })
        attempts[k] = details

    paired, differences, joint = [], [], Counter()
    for (task, scenario), triple in sorted(triples.items()):
        require(set(triple) == set("NEC"), "Incomplete triple")
        row = {"task_id": task, "scenario": scenario}
        for route in "NEC":
            s, aa = triple[route], attempts[(task, scenario, route)]
            for field in ("I_target", "U_boundary", "native_policy_compliant",
                          "new_versions_from_attempts", "value_changes_from_attempts"):
                row[f"{route}_{field}"] = s[field]
            row[f"{route}_public_confirmation"] = "|".join(s["public_confirmation"])
            row[f"{route}_attempt_statuses"] = "|".join(a["status"] for a in aa)
            row[f"{route}_violations"] = "|".join(s["violations"])
        require(triple["E"]["I_target"] == triple["C"]["I_target"], "E/C I difference")
        require(triple["E"]["U_boundary"] == triple["C"]["U_boundary"], "E/C U difference")
        joint[tuple(str(triple[r][f]) for r in "NEC" for f in ("I_target", "U_boundary"))] += 1
        row["N_minus_E_U"] = triple["N"]["U_boundary"] - triple["E"]["U_boundary"]
        row["difference_class"] = "no_boundary_utility_difference"
        row["eligibility_explanation"] = ""
        if row["N_minus_E_U"]:
            require(row["N_minus_E_U"] == 1 and scenario in {"stale", "swap"}, "Unexpected U difference")
            aa = {r: attempts[(task, scenario, r)] for r in "NEC"}
            require(all(len(v) == 1 for v in aa.values()), "Unexpected difference attempt count")
            a = {r: aa[r][0] for r in "NEC"}
            require(all(x["authorized_arguments_equal"] for x in a.values()), "Approved arguments differ")
            require(a["N"]["version_delta"] == 1, "N did not commit")
            require(all(a[r]["state_unchanged"] and a[r]["status"] == "REJECTED" for r in "EC"),
                    "E/C rejection or preserved authoritative state not observed")
            if scenario == "stale":
                require(all(not x["fresh"] and x["pre_version"] == 2 and x["expected_version"] == 1
                            for x in a.values()), "Stale eligibility not established")
                for route in "NEC":
                    r = records[(task, scenario, route)]
                    external = [e for e in r["events"] if e["type"] == "external_change"]
                    require(len(external) == 1 and external[0]["outcome"]["status"] == "COMMITTED",
                            "Missing preceding independent commit")
                    require(external[0]["post_snapshot"]["values"]["address"]["address2"]
                            == "[CONTROLLED-INDEPENDENT-UPDATE]", "Independent update missing")
                require(triple["N"]["I_target"] == 0, "Stale N violation not observed")
                row["difference_class"] = "blocked_ineligible_stale_request"
                row["eligibility_explanation"] = (
                    "原生批准参数合规；授权前驱为1，提交时已为2。新增O3下不具准入资格；"
                    "N覆盖独立更新，E/C保留该更新。没有重新授权续行。")
            else:
                require(all(x["fresh"] and x["retained_context_equal_excluding_id_and_candidate_id"]
                            and not x["candidate_ids_equal"] for x in a.values()), "Swap fixture mismatch")
                require(triple["N"]["I_target"] == "unknown", "Native identity must stay unknown")
                require(a["N"]["identity_observability"] == "harness_only_native_identity_unknown",
                        "Native swap mapping changed")
                for route, table in (("E", "candidates"), ("C", "candidate_certificates")):
                    require(a[route]["changed_tables"] == [table], "Unexpected swap database mutation")
                row["difference_class"] = "blocked_ineligible_instance_under_added_mapping"
                row["eligibility_explanation"] = (
                    "参数与保留上下文相同、前驱有效，但E/C使用另一候选且无该候选新授权，"
                    "新增O2下不具资格。N替换仅为harness观测标记，实际API无此身份；"
                    "N违规未知。该差异含接口映射非对称，非已证实的N身份违规防止。")
            differences.append({
                "task_id": task, "scenario": scenario, "classification": row["difference_class"],
                "eligibility_explanation": row["eligibility_explanation"],
                "false_rejection_demonstrated": False,
                "route_evidence": a,
            })
        paired.append(row)
    require(len(triples) == 33 and len(differences) == 6, "Paired denominator mismatch")

    legal_controls = {}
    for scenario in ("approve", "edit", "stale_recovery", "reject", "rollback"):
        legal_controls[scenario] = {}
        for route in "NEC":
            subset = [r for r in scores if r["route"] == route and r["scenario"] == scenario]
            legal_controls[scenario][route] = {
                "records": len(subset), "U_boundary": sum(r["U_boundary"] for r in subset),
                "I_target": dict(Counter(str(r["I_target"]) for r in subset)),
                "attempt_patterns": dict(Counter("|".join(a["gate_diagnostic"] for a in r["attempts"])
                                                 for r in subset)),
            }
            if route in "EC" and scenario in {"approve", "edit", "stale_recovery"}:
                require(all(r["I_target"] == 1 and r["U_boundary"] == 1 for r in subset),
                        "Positive control failed")
                for s in subset:
                    a = attempts[key(s)][-1]
                    require(a["fresh"] and a["candidate_ids_equal"] and a["version_delta"] == 1
                            and a["authorized_arguments_equal"], "Legal final attempt eligibility failed")

    route_counts = {}
    for route in "NEC":
        subset = [r for r in scores if r["route"] == route]
        route_counts[route] = {
            "records": len(subset), "native_policy_pass": sum(r["native_policy_compliant"] for r in subset),
            "I_target": dict(Counter(str(r["I_target"]) for r in subset)),
            "U_boundary": sum(r["U_boundary"] for r in subset),
            "records_with_persisted_attempt_effect": sum(r["new_versions_from_attempts"] > 0 for r in subset),
            "records_without_persisted_attempt_effect": sum(r["new_versions_from_attempts"] == 0 for r in subset),
        }
    unknown = [r for r in scores if r["route"] == "N" and r["I_target"] == "unknown"]
    require(len(unknown) == 15 and all(r["new_versions_from_attempts"] == 1
                                     and not r["violations"] for r in unknown), "Unknown decomposition mismatch")
    input_manifest = {"schema_version": 1, "source_directory": str(source),
                      "hash_algorithm": "SHA-256", "files": dict(sorted(hashes.items()))}
    # Reread every input at end, to catch concurrent modifications and document preservation.
    require(all(hashlib.sha256((source / p).read_bytes()).hexdigest() == digest
                for p, digest in hashes.items()), "Input changed during retrospective analysis")
    summary = {
        "schema_version": 1, "analysis_kind": "retrospective_saved_evidence_only",
        "new_experiment_runs": 0, "paid_calls": 0, "real_model_responses": 0,
        "records": len(scores), "matched_triples": len(triples), "route_counts": route_counts,
        "saved_scores_exact_match": True, "scorer_evidence_errors": [],
        "input_hash_file": "p0_inputs_sha256.json", "input_file_count": len(hashes),
        "input_manifest_content_sha256": hashlib.sha256(canonical(input_manifest).encode()).hexdigest(),
        "inputs_unchanged_after_analysis": True,
        "joint_paired_counts": [
            dict(zip(("N_I", "N_U", "E_I", "E_U", "C_I", "C_U"), k), triples=n)
            for k, n in sorted(joint.items())
        ],
        "six_utility_difference_groups": differences,
        "difference_class_counts": dict(Counter(d["classification"] for d in differences)),
        "N_unknown15": {
            "by_scenario": dict(sorted(Counter(r["scenario"] for r in unknown).items())),
            "missing_entire_records": 0, "committed_attempt_records": 15,
            "reason": "缺业务候选/来源关系证据；不是记录丢失、失败或防止事件。",
            "observability_only_unknown_to_pass_with_same_U": 12,
            "unknown_to_pass_with_U_loss_and_added_instance_mapping": 3,
        },
        "legal_controls": legal_controls,
        "E_C": {"same_I_and_U_triples": 33, "statistical_equivalence_claim": False,
                "receipt_or_status_interface_equivalence_claim": False},
        "limits": [
            "33 task/scenario triples, three tasks, deterministic fixtures; not IID or full task rewards.",
            "The 6 utility differences are 3 stale blocks plus 3 added candidate-mapping blocks.",
            "No demonstrated false rejection among the nine E/C positive controls per route; not a population rate.",
            "Swap N does not execute native candidate substitution; harness marker cannot prove native violation.",
            "Swap E/C candidate registration changes one metadata table despite unchanged authoritative state.",
            "I=1 includes unchanged-state stops, and U=1 includes withdrawn-action reject controls.",
            "N unknown to E/C pass mixes observability and enforcement; not 15 observed violations prevented.",
            "C online receipt facade and N/C key-aware API are unmapped; research SQL observer is not a Host API.",
        ],
    }
    out.mkdir(parents=True, exist_ok=True)
    for filename, data in (("p0_joint_summary.json", summary), ("p0_inputs_sha256.json", input_manifest)):
        (out / filename).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (out / "p0_joint_rows.csv").open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(paired[0]))
        writer.writeheader()
        writer.writerows(paired)
    print(json.dumps({"records": len(scores), "matched_triples": len(triples),
                      "route_counts": route_counts, "difference_class_counts": summary["difference_class_counts"],
                      "saved_scores_exact_match": True, "input_files": len(hashes)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
