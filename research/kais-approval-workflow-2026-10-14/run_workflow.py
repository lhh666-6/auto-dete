"""Execute the locked, local-only saved-plan workflow protocol.

This is workflow glue around an unchanged OpenTofu binary, not a native approval API
or an implementation of the paper's full contract. All recoveries are scripted.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
import traceback
from datetime import datetime, timezone


ROOT = Path(__file__).resolve().parent
ROUTES = ("saved_plan_binding", "binding_plus_correction_receipt")
RELATIONS = ("Accept", "Correction")
SCENARIOS = ("normal", "configuration_changed", "regenerated_equivalent",
             "different_plan", "stale_state", "relocated_same_artifact")
NOTE = "retain-reviewed-reference"
TIMEOUT = 120


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def save(path, obj):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def local(path, base=ROOT):
    result = (base / path).resolve() if not Path(path).is_absolute() else Path(path).resolve()
    if not result.is_relative_to(base.resolve()):
        raise ValueError(f"Path must stay inside {base}: {result}")
    return result


def verify_freeze(path):
    frozen = json.loads(path.read_text(encoding="utf-8-sig"))
    if not frozen.get("locked_at_utc") or not frozen.get("inputs"):
        raise ValueError("Freeze requires locked_at_utc and nonempty inputs")
    seen = set()
    for item in frozen["inputs"]:
        source = local(item["path"])
        if sha(source) != item["sha256"]:
            raise ValueError(f"Frozen input changed: {item['path']}")
        seen.add(source.relative_to(ROOT).as_posix())
    required = {"run_workflow.py", "WORKFLOW_PROTOCOL.md", "software_sources.json"}
    if not required.issubset(seen):
        raise ValueError(f"Freeze missing required inputs: {sorted(required - seen)}")
    return frozen


class NativeFailure(RuntimeError):
    pass


class Fixture:
    def __init__(self, path, binary, relation, route):
        self.path, self.binary, self.relation, self.route = path, binary, relation, route
        self.work = path / "workspace"
        self.work.mkdir(parents=True)
        for name in ("commands", "artifacts", "configurations", "approvals", "receipts", "states"):
            (path / name).mkdir()
        self.commands, self.artifacts, self.approvals, self.receipts = [], [], [], []
        self.snapshots = []
        self.config_number = 0
        self.expected_quantity = 20 if relation == "Accept" else 21
        self.env = {k: v for k, v in os.environ.items()
                    if not k.upper().startswith(("TF_", "TOFU_"))}
        cli_config = path / "empty-cli.tfrc"
        cli_config.write_text("", encoding="utf-8")
        self.env.update(CHECKPOINT_DISABLE="1", TF_IN_AUTOMATION="1",
                        TF_CLI_CONFIG_FILE=str(cli_config))

    def relative(self, path):
        return Path(path).relative_to(self.path).as_posix()

    def call(self, args, label, required=True):
        number = len(self.commands) + 1
        folder = self.path / "commands" / f"{number:03d}-{label}"
        folder.mkdir()
        start = time.monotonic()
        timed_out = False
        launch_error = None
        try:
            process = subprocess.run([str(self.binary), *args], cwd=self.work, env=self.env,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                     timeout=TIMEOUT, check=False)
            stdout, stderr, code = process.stdout, process.stderr, process.returncode
        except subprocess.TimeoutExpired as exc:
            stdout, stderr, code = exc.stdout or b"", exc.stderr or b"", None
            timed_out = True
        except OSError as exc:
            launch_error = repr(exc)
            stdout, stderr, code = b"", str(exc).encode("utf-8"), None
        (folder / "stdout.txt").write_bytes(stdout)
        (folder / "stderr.txt").write_bytes(stderr)
        record = {"number": number, "label": label, "argv": [str(self.binary), *args],
                  "cwd": str(self.work), "exit_code": code, "timed_out": timed_out,
                  "launch_error": launch_error,
                  "timeout_seconds": TIMEOUT, "elapsed_seconds": time.monotonic() - start,
                  "stdout": self.relative(folder / "stdout.txt"),
                  "stderr": self.relative(folder / "stderr.txt")}
        self.commands.append(record)
        save(folder / "command.json", record)
        if required and (timed_out or code != 0):
            raise NativeFailure(f"Native command failed or timed out: {label}; see {folder}")
        return record, stdout

    def configure(self, value):
        config = {"terraform": {"required_version": "= 1.13.1"},
                  "resource": {"terraform_data": {"change": {
                      "input": {"quantity": value, "reference_note": NOTE}}}}}
        self.config_number += 1
        save(self.work / "main.tf.json", config)
        save(self.path / "configurations" / f"{self.config_number:03d}.json", config)

    def plan(self, value, name):
        self.configure(value)
        plan_path = self.path / "artifacts" / f"{name}.tfplan"
        self.call(["plan", "-input=false", "-no-color", f"-out={plan_path}"], f"plan-{name}")
        _, stdout = self.call(["show", "-json", str(plan_path)], f"show-{name}")
        plan_json = json.loads(stdout)
        resources = plan_json["planned_values"]["root_module"]["resources"]
        planned = next(r for r in resources if r["address"] == "terraform_data.change")
        inputs = planned["values"]["input"]
        if inputs != {"quantity": value, "reference_note": NOTE}:
            raise ValueError(f"Unexpected planned inputs for {name}: {inputs}")
        json_path = plan_path.with_suffix(".json")
        save(json_path, plan_json)
        artifact = {"artifact_id": name, "path": self.relative(plan_path),
                    "sha256": sha(plan_path), "plan_json": self.relative(json_path),
                    "quantity": inputs["quantity"], "reference_note": inputs["reference_note"]}
        self.artifacts.append(artifact)
        save(self.path / "artifacts" / f"{name}.artifact.json", artifact)
        return artifact

    def snapshot(self, label):
        state_path = self.work / "terraform.tfstate"
        state = {"label": label, "exists": state_path.exists(), "quantity": None,
                 "reference_note": None, "serial": None, "lineage": None, "sha256": None}
        if state_path.exists():
            copy = self.path / "states" / f"{len(self.snapshots):03d}-{label}.tfstate"
            shutil.copyfile(state_path, copy)
            raw = json.loads(copy.read_text(encoding="utf-8-sig"))
            state.update(serial=raw.get("serial"), lineage=raw.get("lineage"), sha256=sha(copy),
                         path=self.relative(copy))
            resource = next((r for r in raw.get("resources", [])
                             if r.get("type") == "terraform_data" and r.get("name") == "change"), None)
            if resource and resource.get("instances"):
                value = resource["instances"][0]["attributes"]["input"]
                if "value" in value and "type" in value:
                    value = value["value"]
                state.update(quantity=value.get("quantity"), reference_note=value.get("reference_note"))
        self.snapshots.append(state)
        save(self.path / "states" / f"{len(self.snapshots)-1:03d}-{label}.json", state)
        return state

    def initialize(self):
        self.configure(7)
        self.call(["init", "-input=false", "-no-color"], "init")
        seed = self.plan(7, "seed")
        seed_observation = self.native_apply(seed, "seed")
        save(self.path / "seed-observation.json", seed_observation)
        if (seed_observation["native_exit_code"] != 0 or seed_observation["native_timed_out"]
                or seed_observation["native_launch_error"]):
            raise NativeFailure("Seed native transition failed or has unknown completion")
        initial = self.snapshot("seed-verified")
        if initial["quantity"] != 7 or initial["reference_note"] != NOTE:
            raise ValueError("Seed state did not contain expected native resource inputs")
        self.proposal = self.plan(20, "proposal")
        self.reviewed = self.proposal if self.relation == "Accept" else self.plan(21, "corrected")
        self.approval = self.approve(self.reviewed, "initial")
        save(self.path / "workflow.json", {"relation": self.relation, "route": self.route,
             "original_proposal_artifact": self.proposal, "reviewed_artifact": self.reviewed,
             "authorized_quantity": self.expected_quantity,
             "reviewer": "deterministic scripted approval, not a human participant"})

    def approve(self, artifact, label):
        approval = {"approval_id": f"approval-{label}", "artifact_id": artifact["artifact_id"],
                    "sha256": artifact["sha256"], "approved_quantity": artifact["quantity"],
                    "approved_reference_note": artifact["reference_note"],
                    "reviewed_path": artifact["path"], "reviewer": "scripted-trusted-reviewer"}
        self.approvals.append(approval)
        save(self.path / "approvals" / f"{label}.json", approval)
        return approval

    def native_apply(self, artifact, label):
        before = self.snapshot(f"{label}-before")
        command, _ = self.call(["apply", "-input=false", "-no-color",
                                str(local(artifact["path"], self.path))], f"apply-{label}", required=False)
        after = self.snapshot(f"{label}-after")
        diagnostic = "\n".join((self.path / command[key]).read_text(encoding="utf-8", errors="replace")
                               for key in ("stdout", "stderr")).lower()
        error_kind = None
        if command["exit_code"] not in (0, None):
            error_kind = "stale_plan" if "saved plan is stale" in diagnostic else "unclassified_native_error"
        return {"native_command_number": command["number"], "native_exit_code": command["exit_code"],
                "native_timed_out": command["timed_out"], "native_launch_error": command["launch_error"],
                "native_error_kind": error_kind,
                "before": before, "after": after,
                "state_changed": before["sha256"] != after["sha256"]}

    def receipt(self, artifact, approval):
        return {"original_proposal_id": self.proposal["artifact_id"],
                "original_proposal_sha256": self.proposal["sha256"],
                "original_proposal_quantity": self.proposal["quantity"],
                "authorized_quantity": approval["approved_quantity"],
                "reviewed_artifact_id": approval["artifact_id"],
                "reviewed_artifact_sha256": approval["sha256"],
                "attempted_artifact_id": artifact["artifact_id"],
                "attempted_artifact_sha256": artifact["sha256"],
                "executed_artifact_id": None, "executed_artifact_sha256": None,
                "executed_quantity": None}

    def attempt(self, artifact, approval, label, corrupt=None):
        # Selection is explicit: this function never substitutes the approved artifact for its caller.
        result = {"label": label, "caller_requested_artifact_id": artifact["artifact_id"],
                  "selected_artifact_id": artifact["artifact_id"], "selected_path": artifact["path"],
                  "approved_artifact_id": approval["artifact_id"], "gate_decision": "allow",
                  "gate_reason": "artifact identity and digest match", "native_command_number": None,
                  "native_exit_code": None, "native_timed_out": False, "native_launch_error": None,
                  "native_error_kind": None}
        actual_digest = sha(local(artifact["path"], self.path))
        gate_checks = {"logical_artifact_matches": artifact["artifact_id"] == approval["artifact_id"],
                       "actual_digest_matches_approval": actual_digest == approval["sha256"],
                       "artifact_metadata_matches_bytes": actual_digest == artifact["sha256"]}
        result["binding_checks"] = gate_checks
        receipt = None
        if self.route == ROUTES[1]:
            receipt = self.receipt(artifact, approval)
            if corrupt:
                receipt.update(corrupt)
            result["receipt_checks"] = {
                "original_value_matches_plan": receipt["original_proposal_quantity"] == self.proposal["quantity"],
                "original_bytes_preserved": sha(local(self.proposal["path"], self.path)) == receipt["original_proposal_sha256"],
                "authorized_value_matches_plan": receipt["authorized_quantity"] == artifact["quantity"],
                "reviewed_matches_attempt": receipt["reviewed_artifact_id"] == receipt["attempted_artifact_id"]
                    and receipt["reviewed_artifact_sha256"] == receipt["attempted_artifact_sha256"]}
            receipt_path = self.path / "receipts" / f"{label}.pre.json"
            save(receipt_path, receipt)
            self.receipts.append(self.relative(receipt_path))
        if not all(gate_checks.values()):
            result.update(gate_decision="reject", gate_reason="artifact binding mismatch")
        elif receipt is not None and not all(result["receipt_checks"].values()):
            result.update(gate_decision="reject", gate_reason="correction receipt inconsistent")
        if result["gate_decision"] == "allow":
            result.update(self.native_apply(artifact, label))
        else:
            state = self.snapshot(f"{label}-gate-rejected")
            result.update(before=state, after=state, state_changed=False)
        if receipt is not None:
            native_succeeded = result["native_command_number"] is not None and result["native_exit_code"] == 0 and not result["native_timed_out"]
            receipt.update(executed_quantity=result["after"]["quantity"] if native_succeeded else None,
                           executed_artifact_id=artifact["artifact_id"] if native_succeeded else None,
                           executed_artifact_sha256=actual_digest if native_succeeded else None,
                           observed_state_quantity=result["after"]["quantity"],
                           native_invoked=result["native_command_number"] is not None,
                           native_exit_code=result["native_exit_code"],
                           native_timed_out=result["native_timed_out"],
                           commit_observed=result["state_changed"])
            path = self.path / "receipts" / f"{label}.post.json"
            save(path, receipt)
            self.receipts.append(self.relative(path))
        save(self.path / f"attempt-{label}.json", result)
        return result

    def metrics(self):
        return {"native_cli_calls": len(self.commands), "approval_records": len(self.approvals),
                "additional_correction_receipt_records": len(self.receipts),
                "additional_correction_receipt_bytes": sum((self.path / p).stat().st_size for p in self.receipts)}


def success(attempt):
    return attempt["gate_decision"] == "allow" and attempt["native_exit_code"] == 0 and not attempt["native_timed_out"]


def outcome_status(checks, observations):
    if any(o and (o.get("native_timed_out") or o.get("native_launch_error")
                  or o.get("native_error_kind") == "unclassified_native_error") for o in observations):
        return "unknown"
    return "pass" if all(checks.values()) else "fail"


def run_main(fixture, scenario):
    fixture.initialize()
    selected, approval = fixture.reviewed, fixture.approval
    advance = None
    if scenario == "configuration_changed":
        fixture.configure(99)
    elif scenario == "regenerated_equivalent":
        selected = fixture.plan(fixture.expected_quantity, "regenerated")
    elif scenario == "different_plan":
        selected = fixture.plan(42, "different")
    elif scenario == "stale_state":
        intervening = fixture.plan(99, "intervening")
        intervening_approval = fixture.approve(intervening, "intervening")
        # This independent valid native transition is setup, not the evaluated correction continuation.
        advance = fixture.native_apply(intervening, "intervening")
        save(fixture.path / "intervening-authorization.json", intervening_approval)
        if advance["native_exit_code"] != 0 or advance["native_timed_out"] or advance["after"]["quantity"] != 99:
            raise NativeFailure("Intervening native transition failed")
    elif scenario == "relocated_same_artifact":
        destination = fixture.path / "artifacts" / "relocated.tfplan"
        shutil.copyfile(local(fixture.reviewed["path"], fixture.path), destination)
        selected = dict(fixture.reviewed, path=fixture.relative(destination))
        save(fixture.path / "artifacts" / "relocated.artifact.json", selected)
    initial = fixture.attempt(selected, approval, "initial")
    recovery = None
    recovery_steps = []
    if scenario in ("regenerated_equivalent", "different_plan"):
        selected = fixture.reviewed
        recovery_steps = ["explicitly select previously reviewed artifact", "execute with original approval"]
        recovery = fixture.attempt(selected, approval, "recovery")
    elif scenario == "stale_state":
        selected = fixture.plan(fixture.expected_quantity, "recovery")
        approval = fixture.approve(selected, "recovery")
        recovery_steps = ["plan against current state", "review and approve new plan", "execute newly approved plan"]
        recovery = fixture.attempt(selected, approval, "recovery")
    final = recovery or initial
    replay = fixture.attempt(selected, approval, "replay")
    expected_block = scenario in ("regenerated_equivalent", "different_plan")
    checks = {
        "initial_gate_matches_protocol": initial["gate_decision"] == ("reject" if expected_block else "allow"),
        "initial_native_behavior_matches_protocol": (
            initial["native_command_number"] is None if expected_block else
            initial["native_error_kind"] == "stale_plan" and not initial["native_timed_out"] if scenario == "stale_state" else success(initial)),
        "rejected_attempt_preserves_state": not initial["state_changed"] if expected_block or scenario == "stale_state" else True,
        "final_native_commit_succeeded": success(final),
        "final_authorized_value": final["after"]["quantity"] == fixture.expected_quantity,
        "unchanged_reference_preserved": final["after"]["reference_note"] == NOTE,
        "replay_native_observation_known": replay["native_command_number"] is not None
            and (replay["native_exit_code"] == 0 or replay["native_error_kind"] == "stale_plan")
            and not replay["native_timed_out"],
        "replay_no_second_state_change": not replay["state_changed"],
        "replay_value_preserved": replay["after"]["quantity"] == fixture.expected_quantity,
    }
    return {"relation": fixture.relation, "route": fixture.route, "scenario": scenario,
            "initial": initial, "recovery": recovery, "recovery_steps": recovery_steps,
            "replay": replay, "intervening_transition": advance, "checks": checks,
            "status": outcome_status(checks, (initial, recovery, replay)), **fixture.metrics()}


def run_control(fixture, kind):
    fixture.initialize()
    if kind == "direct_native_regenerated":
        artifact = fixture.plan(fixture.expected_quantity, "regenerated")
        observation = fixture.native_apply(artifact, "direct-native-regenerated")
        checks = {"explicit_native_application_succeeded": observation["native_exit_code"] == 0 and not observation["native_timed_out"],
                  "authorized_business_value": observation["after"]["quantity"] == fixture.expected_quantity,
                  "unchanged_reference_preserved": observation["after"]["reference_note"] == NOTE}
    elif kind == "fresh_approval":
        artifact = fixture.plan(fixture.expected_quantity, "regenerated")
        approval = fixture.approve(artifact, "fresh")
        observation = fixture.attempt(artifact, approval, "fresh-approval")
        checks = {"new_approval_allows_new_artifact": success(observation),
                  "authorized_business_value": observation["after"]["quantity"] == fixture.expected_quantity,
                  "unchanged_reference_preserved": observation["after"]["reference_note"] == NOTE}
    else:
        field = "original_proposal_quantity" if kind == "corrupt_proposal_receipt" else "authorized_quantity"
        observation = fixture.attempt(fixture.reviewed, fixture.approval, kind, corrupt={field: 12345})
        checks = {"inconsistent_receipt_rejected": observation["gate_decision"] == "reject",
                  "native_not_invoked": observation["native_command_number"] is None,
                  "state_unchanged": not observation["state_changed"] and observation["after"]["quantity"] == 7}
    return {"relation": fixture.relation, "route": fixture.route, "control": kind,
            "observation": observation, "checks": checks,
            "status": outcome_status(checks, (observation,)), **fixture.metrics()}


def normalize_observation(obs):
    if obs is None:
        return None
    return {key: obs.get(key) for key in ("gate_decision", "gate_reason", "native_exit_code", "native_timed_out", "native_error_kind", "state_changed")} | {
        "native_invoked": obs.get("native_command_number") is not None,
        "native_launch_failed": bool(obs.get("native_launch_error")),
        "before_quantity": obs["before"]["quantity"], "after_quantity": obs["after"]["quantity"],
        "before_reference_note": obs["before"]["reference_note"], "after_reference_note": obs["after"]["reference_note"],
        "serial_delta": (obs["after"]["serial"] - obs["before"]["serial"])
            if obs["after"]["serial"] is not None and obs["before"]["serial"] is not None else None}


def normalize(row):
    stable = {key: row[key] for key in ("relation", "route", "scenario", "control", "status", "checks",
              "native_cli_calls", "approval_records", "additional_correction_receipt_records", "recovery_steps") if key in row}
    # Bytes/digests/resource IDs/lineage/timing/absolute paths are retained in raw records, not compared across rebuilds.
    for key in ("initial", "recovery", "replay", "observation", "intervening_transition"):
        if key in row:
            stable[key] = normalize_observation(row[key])
    if row["status"] == "unknown":
        stable["error_type"] = row.get("error_type")
    return stable


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", action="store_true", help="Execute the locked protocol")
    parser.add_argument("--out-dir", required=True, help="New output directory below this experiment's runs/")
    parser.add_argument("--freeze", default="PROTOCOL_FREEZE.json")
    args = parser.parse_args()
    if not args.run:
        parser.error("Native execution requires --run and a matching freeze")
    freeze_path = local(args.freeze)
    frozen = verify_freeze(freeze_path)
    software = json.loads((ROOT / "software_sources.json").read_text(encoding="utf-8-sig"))
    binary = local(software["binary_path"])
    if sha(binary) != software["binary_sha256"] or software["version"] != "1.13.1":
        raise ValueError("Native binary does not match verified software manifest")
    output = local(args.out_dir)
    runs = ROOT / "runs"
    if output == runs or not output.is_relative_to(runs) or output.exists():
        raise ValueError("Output must be a new directory strictly beneath experiment/runs/")
    output.mkdir(parents=True)
    save(output / "frozen-inputs.json", frozen)
    save(output / "software.json", software)
    version_fixture = Fixture(output / "environment", binary, "Accept", ROUTES[0])
    _, version_bytes = version_fixture.call(["version", "-json"], "version")
    version = json.loads(version_bytes)
    version_values = [version.get(k) for k in ("terraform_version", "tofu_version", "opentofu_version")]
    if software["version"] not in version_values:
        raise ValueError(f"Unexpected native version: {version}")
    save(output / "environment.json", {"started_at_utc": datetime.now(timezone.utc).isoformat(),
          "python": sys.version, "platform": sys.platform, "native_version": version,
          "cli_timeout_seconds": TIMEOUT, "external_provider_or_cloud_resources": False,
          "native_approval_api": False, "deterministic_scripted_recovery": True})
    rows, controls = [], []
    jobs = [("main", relation, route, scenario) for relation in RELATIONS
            for scenario in SCENARIOS for route in ROUTES]
    jobs += [("control", relation, ROUTES[0], "direct_native_regenerated") for relation in RELATIONS]
    jobs += [("control", relation, route, "fresh_approval") for relation in RELATIONS for route in ROUTES]
    jobs += [("control", "Correction", ROUTES[1], kind)
             for kind in ("corrupt_proposal_receipt", "corrupt_authorized_receipt")]
    for group, relation, route, scenario in jobs:
        identifier = f"{relation.lower()}--{scenario}--{route}"
        fixture = Fixture(output / group / identifier, binary, relation, route)
        try:
            row = run_main(fixture, scenario) if group == "main" else run_control(fixture, scenario)
        except Exception as exc:
            row = {"relation": relation, "route": route,
                   "scenario" if group == "main" else "control": scenario,
                   "status": "unknown", "error_type": type(exc).__name__, "error": str(exc),
                   "checks": {}, **fixture.metrics()}
            (fixture.path / "error.txt").write_text(traceback.format_exc(), encoding="utf-8")
        row["record_directory"] = fixture.path.relative_to(output).as_posix()
        save(fixture.path / "result.json", row)
        (rows if group == "main" else controls).append(row)
        save(output / "results.json", {"main": rows, "controls": controls})
        print(f"{group}: {identifier}: {row['status']}", flush=True)
    save(output / "normalized_summary.json", {"main": [normalize(r) for r in rows],
                                             "controls": [normalize(r) for r in controls]})
    all_rows = rows + controls
    report = {"completed_at_utc": datetime.now(timezone.utc).isoformat(),
              "main_records": len(rows), "control_records": len(controls),
              "statuses": {status: sum(r["status"] == status for r in all_rows)
                           for status in ("pass", "fail", "unknown")},
              "checks_evaluated": sum(len(r["checks"]) for r in all_rows),
              "checks_passed": sum(sum(r["checks"].values()) for r in all_rows),
              "native_cli_calls": sum(r["native_cli_calls"] for r in all_rows) + len(version_fixture.commands),
              "full_paper_contract_implemented": False, "agent_or_human_recovery_measured": False}
    save(output / "run_summary.json", report)
    print(json.dumps(report, indent=2), flush=True)
    return 0 if report["statuses"]["fail"] == 0 and report["statuses"]["unknown"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
