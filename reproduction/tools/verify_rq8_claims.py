"""Claim-by-claim verification of RQ8 against the frozen run records.

Tests each headline number the manuscript reports and prints PASS/FAIL.
Writes nothing.
"""

import collections
import io
import json
import sys

FAILURE_TERMINAL = {"HARNESS_FAILURE", "MODEL_API_FAILURE", "TIMEOUT", "INVALID_OUTPUT"}
NO_CALL_SCENARIOS = {"A1", "A10"}


def main(path):
    runs = json.load(io.open(path, encoding="utf-8"))
    benign = [r for r in runs if r["expected_outcome"] == "benign"]
    reject = [r for r in runs if r["expected_outcome"] == "reject"]
    results = []

    def check(name, got, want):
        ok = got == want
        results.append((ok, name, got, want))
        return ok

    # ---- matrix size
    check("1,260 planned executions", len(runs), 1260)
    check("360 planned benign runs", len(benign), 360)

    # ---- behaviour endpoint
    ev = [r for r in benign if r["agent_behavior_evaluable"]]
    check("335 behavior-evaluable benign runs", len(ev), 335)
    check("25 unscored benign runs", len(benign) - len(ev), 25)
    strict_all = sum(1 for r in benign if r["agent_task_completed"])
    check("320/360 strict-trajectory", strict_all, 320)
    strict_ev = sum(1 for r in ev if r["agent_task_completed"])
    check("320/335 strict (conditional)", strict_ev, 320)

    # ---- runtime failures, keyed on terminal_class
    rc = {k: sum(1 for r in runs if r["terminal_class"] == k) for k in FAILURE_TERMINAL}
    total_fail = sum(rc.values())
    check("93 runtime failures (terminal_class)", total_fail, 93)
    for cfg in ("D1", "G1", "G2"):
        got = sum(1 for r in runs
                  if r["model_config_id"] == cfg and r["terminal_class"] in FAILURE_TERMINAL)
        check("%s runtime failures /420" % cfg, got, {"D1": 76, "G1": 4, "G2": 13}[cfg])

    for name in ("SETUP_FAILURE", "TOOL_RUNTIME_FAILURE"):
        check("no %s" % name,
              sum(1 for r in runs if r.get("error_class") == name or r.get("terminal_class") == name),
              0)

    failed = [r for r in runs if r["terminal_class"] in FAILURE_TERMINAL]
    check("64 of 93 failures retain an authority verdict",
          sum(1 for r in failed if r.get("authority_evaluable")), 64)

    # ---- authority endpoint
    ae = [r for r in reject if r.get("authority_evaluable")]
    check("899 authority-evaluable challenges", len(ae), 899)
    adm = [r for r in ae if r["scenario_id"] not in NO_CALL_SCENARIOS]
    noc = [r for r in ae if r["scenario_id"] in NO_CALL_SCENARIOS]
    check("720 admission-call challenges", len(adm), 720)
    check("179 capability-unavailable challenges", len(noc), 179)
    check("179 = scenarios A1+A10",
          sum(1 for r in ae if r["scenario_id"] in NO_CALL_SCENARIOS), 179)

    def unauth(r):
        v = r.get("unauthorized_authoritative_mutation")
        if v is None:
            v = r.get("unauthorized_mutation")
        return bool(v)

    check("0/720 unauthorized mutations (admission call)",
          sum(1 for r in adm if unauth(r)), 0)
    check("0/179 unauthorized mutations (no call)",
          sum(1 for r in noc if unauth(r)), 0)
    check("0/899 combined", sum(1 for r in ae if unauth(r)), 0)

    for cfg in ("D1", "G1", "G2"):
        g = [r for r in ae if r["model_config_id"] == cfg]
        check("authority-evaluable count %s" % cfg, len(g), {"D1": 299, "G1": 300, "G2": 300}[cfg])

    # ---- report
    print("=" * 78)
    print("RQ8 CLAIM VERIFICATION against the frozen normalized run records")
    print("=" * 78)
    npass = sum(1 for ok, *_ in results if ok)
    for ok, name, got, want in results:
        print("  %-4s %-48s got=%-6s want=%s"
              % ("PASS" if ok else "FAIL", name, got, want))
    print("\n  %d/%d claims reproduced exactly" % (npass, len(results)))

    print("\n  terminal_class distribution:")
    for k, v in sorted(collections.Counter(r["terminal_class"] for r in runs).items()):
        print("    %-34s %4d" % (k, v))

    print("\n  authority-evaluable challenges by scenario (reject runs):")
    for s in sorted({r["scenario_id"] for r in ae}):
        g = [r for r in ae if r["scenario_id"] == s]
        ex = sum(1 for r in g if r.get("mechanism_challenge_executed"))
        print("    %-4s n=%3d  admission-call=%3d  no-call=%3d"
              % (s, len(g), ex, len(g) - ex))

    return 0 if npass == len(results) else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
