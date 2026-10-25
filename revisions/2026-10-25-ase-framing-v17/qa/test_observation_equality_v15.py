"""Offline equality regressions; never invokes a model or recollects traces.

Run from any directory with standard-library Python. The byte-exact archived
source is bundled under qa/upstream and is loaded only in memory.
"""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import sys
import types

import observation_witnesses_v15 as fixed

UPSTREAM_SHA = "c6d512843c905cab6d8521dd8c914f7fb26d85ae"
UPSTREAM_PATH = "latest/code/formal-fixed/observation_witnesses.py"
UPSTREAM_HASH = "32bed3ae1aed344c3bf5c57c7f7e545e4e05836a154ae14d278be3aebd6b7832"
QA = Path(__file__).resolve().parent
REVISION = Path(__file__).resolve().parents[1]


def history(module, value):
    base = module.paired_histories()["D_V"][0]
    before = (module.FieldValue("score", 90),)
    after = (module.FieldValue("score", value),)
    return replace(
        base, authorizations=(replace(base.authorizations[0], authorized_value=value),),
        successor_values=after,
        commits=(module.CommitStep("successor-1", before, after),),
        source_transitions=(module.SourceTransition("prior-score", "score", 90),
                            module.SourceTransition("transition-score", "score", value)),
    )


def run(upstream, output):
    raw = upstream.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == UPSTREAM_HASH
    frozen = types.ModuleType("frozen_observation_checker_v15_audit")
    sys.modules[frozen.__name__] = frozen
    exec(compile(raw, f"{UPSTREAM_SHA}:{UPSTREAM_PATH}", "exec"), frozen.__dict__)
    frozen.verify()
    fixed.verify()
    results = []

    def check(name, condition):
        if not condition:
            raise AssertionError(name)
        results.append({"name": name, "status": "PASS"})

    # Nine checks per pair exercise consumers as well as the equality helper.
    cases = [
        ("integer-boolean", 1, True, False),
        ("integer-float", 2, 2.0, False),
        ("nested-type", {"x": [1, {"n": 2}]}, {"x": [True, {"n": 2.0}]}, False),
        ("dictionary-key-order", {"a": [1, 2.0], "b": {"c": True}},
         {"b": {"c": True}, "a": [1, 2.0]}, True),
    ]
    for label, left, right, equal in cases:
        h = history(fixed, left)
        changes = {
            "proposal": replace(h, candidates=(replace(h.candidates[0], proposal_value=right),)),
            "authorization": replace(h, authorizations=(replace(h.authorizations[0], authorized_value=right),)),
            "successor": replace(h, successor_values=(fixed.FieldValue("score", right),)),
        }
        # Start proposal at left too, so every comparison isolates one role.
        proposal_base = replace(h, candidates=(replace(h.candidates[0], proposal_value=left),))
        for role, changed in changes.items():
            base = proposal_base if role == "proposal" else h
            check(f"{label}/projection-{role}", (fixed.observe(base, "D_V") == fixed.observe(changed, "D_V")) == equal)
        check(f"{label}/attribution", fixed._attribution_ok(changes["authorization"]) == equal)
        step = fixed.CommitStep("s", (fixed.FieldValue("score", left),), (fixed.FieldValue("score", right),))
        check(f"{label}/changed-field", (not step.changed_fields) == equal)
        source = replace(h, source_transitions=(h.source_transitions[0], replace(h.source_transitions[1], value=right)))
        check(f"{label}/source-resolution", fixed._source_ok(source) == equal)
        check(f"{label}/endpoint", (not fixed.validate_history_domain(changes["successor"])) == equal)
        connection = replace(h, predecessor_values=(fixed.FieldValue("score", right),),
                             commits=(replace(h.commits[0], before=(fixed.FieldValue("score", left),)),))
        check(f"{label}/commit-connection", (not fixed.validate_history_domain(connection)) == equal)
        fresh = replace(h, expected_version=left, observed_version=right)
        fresh_control = replace(h, expected_version=left, observed_version=left)
        check(f"{label}/discriminator", fixed._freshness_ok(fresh) == equal
              and ((fixed.observe(fresh, "D_F") == fixed.observe(fresh_control, "D_F")) == equal))

    counterexamples = {}
    for module, label in [(frozen, "frozen"), (fixed, "v15")]:
        good = history(module, 1)
        bad = replace(good, authorizations=(replace(good.authorizations[0], authorized_value=True),))
        disconnected = replace(bad, successor_values=(module.FieldValue("score", True),),
                               source_transitions=(bad.source_transitions[0], replace(bad.source_transitions[1], value=True)))
        counterexamples[label] = {
            "authorization": {"domain_errors": [module.validate_history_domain(good), module.validate_history_domain(bad)],
                              "all_projections_equal": module.project(good, module.CLASSES) == module.project(bad, module.CLASSES),
                              "outcomes": [module.normative_outcome(good), module.normative_outcome(bad)]},
            "endpoint": {"domain_errors": module.validate_history_domain(disconnected),
                         "local_outcome": module.normative_outcome(disconnected)},
        }
    old, new = counterexamples["frozen"], counterexamples["v15"]
    check("actual-counterexample-1", old["authorization"]["all_projections_equal"]
          and not new["authorization"]["all_projections_equal"]
          and old["authorization"]["outcomes"][0] != old["authorization"]["outcomes"][1]
          and new["authorization"]["outcomes"][0] != new["authorization"]["outcomes"][1]
          and new["authorization"]["domain_errors"] == [(), ()])
    check("actual-counterexample-2", old["endpoint"]["domain_errors"] == ()
          and old["endpoint"]["local_outcome"][0] == "admissible"
          and "commit sequence does not reach successor values" in new["endpoint"]["domain_errors"])
    assert len(results) == 38
    checker = Path(fixed.__file__)
    report = {
        "status": "PASS", "upstream_commit": UPSTREAM_SHA, "upstream_path": UPSTREAM_PATH,
        "upstream_raw_sha256": UPSTREAM_HASH, "upstream_read_method": "Bundled byte-exact Git blob; hash verified before in-memory loading",
        "derived_checker": "qa/" + checker.name,
        "derived_checker_sha256": hashlib.sha256(checker.read_bytes()).hexdigest(),
        "regression_script_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "changes": ["Canonical JSON encoding of proposed, authorized and committed D_V payloads",
                    "Canonical JSON comparison of commit snapshot connections and declared endpoint",
                    "Canonical JSON encoding of D_F discriminators and matching freshness comparison"],
        "preserved_checks": {"class_pairs": 5, "candidate_identity_pairs": 1, "copy_forward_controls": 1,
                             "frozen_verify": "PASS", "v15_verify": "PASS"},
        "new_regressions": {"count": len(results), "matrix_checks": 36, "actual_counterexamples": 2, "results": results},
        "counterexamples": counterexamples, "derived_witness_report": fixed.build_report(),
        "scope": "Finite constructions and 38 equality regressions only; not a general admission oracle, exhaustive proof, JSON validator, new hosted experiment, or rerun of historical suites. Local outcome is meaningful only on the declared well-formed history domain.",
        "equality_scope": "Existing sorted-key whitespace-minimal JSON serialization retained. JSON payloads and Any-typed predecessor discriminators use canonical equality; opaque string identifiers retain identifier equality. No new input-normalization or non-JSON semantics.",
        "experiment_counts_changed": False, "model_calls": 0, "recollected_traces": 0,
    }
    target = output.resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_bytes((json.dumps(report, indent=2, sort_keys=True) + "\n").encode())
    print("PASS: 38 new equality regressions; preserved five class pairs, identity pair, and copy-forward control")
    print(target)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", type=Path, default=QA / "upstream" / "observation_witnesses.py",
                        help="byte-exact frozen source; verified against the fixed upstream SHA-256")
    parser.add_argument("--output", type=Path, default=REVISION / "audit" / "observation-equality-v15.json",
                        help="JSON receipt destination (default: ../audit/observation-equality-v15.json beside qa)")
    args = parser.parse_args()
    run(args.upstream, args.output)
