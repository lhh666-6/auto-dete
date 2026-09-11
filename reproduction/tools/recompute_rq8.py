"""Independent recomputation of the paper's RQ8 headline numbers.

Reads ONLY the frozen normalized run records and recomputes the counts the
manuscript reports.  Writes nothing; prints a comparison table.

Usage:  python recompute_rq8.py <path-to-agent_authority_benchmark_runs.json>
"""

import collections
import io
import json
import sys


def main(path):
    runs = json.load(io.open(path, encoding="utf-8"))
    print("frozen records: %d" % len(runs))
    print("schema_version : %s" % sorted({r["schema_version"] for r in runs}))
    print("benchmark      : %s" % sorted({r["benchmark_version"] for r in runs}))
    print("phases         : %s" % dict(collections.Counter(r["phase"] for r in runs)))
    print()

    by_outcome = collections.Counter(r["expected_outcome"] for r in runs)
    print("expected_outcome: %s" % dict(by_outcome))

    by_cfg = collections.Counter(r["model_config_id"] for r in runs)
    print("by config       : %s" % dict(sorted(by_cfg.items())))
    by_scen = collections.Counter(r["scenario_id"] for r in runs)
    print("by scenario     : %s" % dict(sorted(by_scen.items())))
    by_var = collections.Counter(r["prompt_variant_id"] for r in runs)
    print("by variant      : %s" % dict(sorted(by_var.items())))
    by_rep = collections.Counter(r["repetition"] for r in runs)
    print("by repetition   : %s" % dict(sorted(by_rep.items())))
    print()

    benign = [r for r in runs if r["expected_outcome"] == "benign"]
    challenge = [r for r in runs if r["expected_outcome"] == "challenge"]
    print("=== BENIGN ===")
    print("planned benign runs                 : %d" % len(benign))
    ev = [r for r in benign if r["agent_behavior_evaluable"]]
    unev = [r for r in benign if not r["agent_behavior_evaluable"]]
    print("behavior-evaluable                  : %d" % len(ev))
    print("NOT behavior-evaluable (unscored)   : %d" % len(unev))
    strict_all = [r for r in benign if r["agent_task_completed"]]
    strict_ev = [r for r in ev if r["agent_task_completed"]]
    print("agent_task_completed / all planned  : %d / %d = %.2f%%"
          % (len(strict_all), len(benign), 100.0 * len(strict_all) / len(benign)))
    print("agent_task_completed / evaluable    : %d / %d = %.2f%%"
          % (len(strict_ev), len(ev), 100.0 * len(strict_ev) / len(ev)))
    btc = [r for r in benign if r.get("benign_task_completion")]
    print("benign_task_completion flag         : %d" % len(btc))
    print("  (benign_task_completion != agent_task_completed: %d)"
          % sum(1 for r in benign
                if bool(r.get("benign_task_completion")) != bool(r["agent_task_completed"])))
    print()

    print("=== RUNTIME FAILURES ===")
    fails = [r for r in runs if r.get("error_class") or r.get("returncode") not in (0, None)]
    print("records with error_class/returncode : %d" % len(fails))
    ec = collections.Counter(r.get("error_class") for r in runs if r.get("error_class"))
    print("error_class distribution            : %s" % dict(ec))
    for cfg in sorted(by_cfg):
        tot = by_cfg[cfg]
        f = sum(1 for r in runs if r["model_config_id"] == cfg and r.get("error_class"))
        print("  %s: %d/%d" % (cfg, f, tot))
    tc = collections.Counter(r.get("terminal_class") for r in runs)
    print("terminal_class distribution         : %s" % dict(tc))
    print()

    print("=== CHALLENGE / AUTHORITY ===")
    print("planned challenge runs              : %d" % len(challenge))
    ae = [r for r in challenge if r.get("authority_evaluable")]
    print("authority-evaluable                 : %d" % len(ae))
    adm = [r for r in ae if r.get("mechanism_challenge_executed")]
    noadm = [r for r in ae if not r.get("mechanism_challenge_executed")]
    print("  admission call executed           : %d" % len(adm))
    print("  no admission call                 : %d" % len(noadm))

    def unauth(r):
        v = r.get("unauthorized_authoritative_mutation")
        if v is None:
            v = r.get("unauthorized_mutation")
        return bool(v)

    print("  unauthorized mutation (executed)  : %d / %d"
          % (sum(1 for r in adm if unauth(r)), len(adm)))
    print("  unauthorized mutation (no call)   : %d / %d"
          % (sum(1 for r in noadm if unauth(r)), len(noadm)))
    print()

    print("=== admission-call vs no-call, by scenario ===")
    for scen in sorted({r["scenario_id"] for r in ae}):
        g = [r for r in ae if r["scenario_id"] == scen]
        ex = sum(1 for r in g if r.get("mechanism_challenge_executed"))
        print("  %-4s n=%3d  executed=%3d  no-call=%3d  unauth=%d"
              % (scen, len(g), ex, len(g) - ex, sum(1 for r in g if unauth(r))))
    print()

    print("=== failure classes named in the paper ===")
    for name in ("SETUP_FAILURE", "TOOL_RUNTIME_FAILURE"):
        print("  %-24s : %d" % (name, sum(1 for r in runs if r.get("error_class") == name)))
    print()

    print("=== cross-tab: error_class x agent_behavior_evaluable (challenge) ===")
    for ec_name in sorted({r.get("error_class") for r in runs if r.get("error_class")}):
        g = [r for r in challenge if r.get("error_class") == ec_name]
        print("  %-26s n=%3d  behavior_evaluable=%3d  authority_evaluable=%3d"
              % (ec_name, len(g),
                 sum(1 for r in g if r["agent_behavior_evaluable"]),
                 sum(1 for r in g if r.get("authority_evaluable"))))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
