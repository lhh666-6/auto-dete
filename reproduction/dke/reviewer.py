"""Reviewer entry point for the DKE deposit; frozen scientific sources stay intact."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import shutil
import statistics
import subprocess
import sys

REPO = Path(__file__).resolve().parents[2]
DEPOSIT = "2645e5e18c900ea91c9c980e44195dc71e410432"
SOURCE = "c6d512843c905cab6d8521dd8c914f7fb26d85ae"
ARCHIVE = "r21-jss/evidence/agent-authority-benchmark-v2/final/2026-09-01-three-config-10x"
CORE_PACKAGES = ["sqlalchemy==2.0.51", "pytest==9.1.1"]
# The original deposit did not record a Playwright package version. This is the
# reviewer driver's version, not a retroactive claim about the original run.
BROWSER_PACKAGE = "playwright==1.58.0"


def git(*args: str) -> bytes:
    return subprocess.check_output(["git", "-C", str(REPO), *args])


def read(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def rows(path: Path) -> list:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def prepare(work: Path) -> None:
    require(not work.exists(), f"Workspace exists: {work}. Choose a new --workspace; nothing overwritten.")
    # Resolve pins before creating a directory. A normal clone has these objects;
    # a filtered clone can retrieve them on demand without materializing databases.
    for pin in (DEPOSIT, SOURCE):
        git("cat-file", "-e", pin + "^{commit}")
    work.mkdir(parents=True)
    files = {}

    def extract(pin: str, path: str, relative: str) -> None:
        target = work / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        # cat-file reads the blob directly; show may first stat commit:path as
        # a worktree filename and exceed Windows path limits in a deep checkout.
        data = git("cat-file", "blob", f"{pin}:{path}")
        require(not data.startswith(b"version https://git-lfs.github.com/spec/v1"),
                f"LFS pointer instead of data: {path}; obtain this object's LFS content.")
        target.write_bytes(data)
        files[relative] = {"commit": pin, "path": path, "sha256": digest(target)}

    paths = git("ls-tree", "-r", "--name-only", DEPOSIT, "DKE-supplement").decode().splitlines()
    for path in paths:
        relative = path.removeprefix("DKE-supplement/")
        root_file = "/" not in relative
        small_evidence = relative.startswith(("results/e1/", "results/e2/", "results/e3/", "tables/"))
        if root_file or (small_evidence and Path(relative).suffix in (".json", ".jsonl", ".csv")
                         and "/databases/" not in relative and "/pilot" not in relative):
            extract(DEPOSIT, path, path)
    impl = "latest/code/implementation-fixed/"
    for path in git("ls-tree", "-r", "--name-only", SOURCE, impl, "latest/code/formal-fixed").decode().splitlines():
        part = path.removeprefix(impl)
        if (path.startswith("latest/code/formal-fixed/") and path.endswith(".py")) or (
            path.startswith(impl) and (part.startswith(("app/", "benchmarks/", "config/"))
                                      or part in ("pyproject.toml", "uv.lock"))):
            extract(SOURCE, path, "dke-experiments/" + path)
    old = "r21-jss/source/performance-experiment/benchmarks/r21_feature_baseline.py"
    extract(SOURCE, old, "dke-experiments/" + old)
    # The integrity manifest also covers the preserved strengthened-control
    # source. Include every listed source rather than silently verifying a subset.
    for name in read(work / "DKE-supplement/source-integrity.json")["files"]:
        path = name.replace("\\", "/")
        relative = "dke-experiments/" + path
        if relative not in files:
            extract(SOURCE, path, relative)
    extract(SOURCE, ARCHIVE + "/normalized/runs.json", "dke-experiments/" + ARCHIVE + "/normalized/runs.json")
    for item in read(work / "DKE-supplement/results/e1/inputs.json"):
        if "events_file" in item:
            path = item["events_file"].replace("\\", "/")
            extract(SOURCE, path, "dke-experiments/" + path)
            require(digest(work / "dke-experiments" / path) == item["events_sha256"],
                    "Selected archive input hash mismatch: " + path)
    write(work / "snapshot.json", {"deposit_commit": DEPOSIT, "source_commit": SOURCE, "files": files})
    check_sources(work)
    print(f"Prepared {len(files)} pinned files in {work}; no archived databases downloaded.")


def check_sources(work: Path) -> None:
    snapshot = read(work / "snapshot.json")
    require(snapshot["deposit_commit"] == DEPOSIT and snapshot["source_commit"] == SOURCE, "Wrong snapshot pins")
    for path, entry in snapshot["files"].items():
        require(digest(work / path) == entry["sha256"], "Prepared file changed: " + path)
    root = work / "DKE-supplement"
    manifest = read(root / "artifact-manifest.json")["files"]
    for path in snapshot["files"]:
        if path.startswith("DKE-supplement/"):
            relative = path.removeprefix("DKE-supplement/")
            expected = manifest.get(relative.replace("/", "\\"), manifest.get(relative))
            if expected:
                require(digest(work / path) == expected, "Deposit manifest mismatch: " + relative)
    for path, expected in read(root / "source-integrity.json")["files"].items():
        relative = path.replace("\\", "/")
        require(digest(work / "dke-experiments" / relative) == expected, "Source-integrity mismatch: " + relative)
    for path, expected in read(root / "results/e3/pre-run-manifest-all.json").items():
        relative = path.replace("\\", "/")
        target = work / "dke-experiments" / relative if relative.startswith("latest/") else root / relative
        require(digest(target) == expected, "Timing source hash mismatch: " + relative)


def e1_checks(output: Path, expected: Path) -> dict:
    records, summary = rows(output / "receipts.jsonl"), read(output / "summary.json")
    require(len(records) == 495, "E1 requires 495 receipts")
    require(all(not r["harness_error"] for r in records), "E1 contains harness errors")
    calculated = []
    for arm in ("journal_context", "journal_exact", "reference"):
        group = [r for r in records if r["arm"] == arm]
        counts = Counter(q["status"] for r in group for q in r["queries"])
        calculated.append({"arm": arm, "planned": len(group), "scored": len(group), "harness_errors": 0,
                           "accepted": sum(r["accepted"] for r in group),
                           **{key: sum(r[flag] for r in group) for key, flag in (
                               ("instance_policy_violations", "instance_policy_violation"),
                               ("value_policy_violations", "value_policy_violation"),
                               ("instance_false_rejections", "instance_false_rejection"),
                               ("value_false_rejections", "value_false_rejection"))},
                           "rejections_with_writes": sum(not r["accepted"] and not r["zero_write_on_reject"] for r in group),
                           "query_counts": dict(counts)})
    require(calculated == summary["arms"] == read(expected / "summary.json")["arms"], "E1 aggregate mismatch")
    indexed = {(r["sample"], r["case"], r["arm"]): r for r in records}
    require(len(indexed) == 495, "Duplicate E1 receipt keys")
    pairs = {(r["sample"], r["case"]) for r in records}
    for sample, case in pairs:
        exact, ref = [indexed[(sample, case, a)] for a in ("journal_exact", "reference")]
        require(exact["accepted"] == ref["accepted"] and exact["queries"] == ref["queries"], "Exact/reference pair mismatch")
    separators = sum(indexed[(s, c, "journal_context")]["accepted"] and not indexed[(s, c, "journal_exact")]["accepted"]
                     for s, c in pairs if c == "same_value_substitution")
    require(len(pairs) == 165 and separators == 15, "E1 pair/separator count mismatch")
    require(all(r["accepted"] or (r["zero_write_on_reject"] and r["before_digest"] == r["after_digest"])
                for r in records), "E1 rejected case wrote state")
    return {"executions": len(records), "exact_reference_agreement": len(pairs), "equal_value_separators": separators}


def e2_checks(output: Path, expected: Path) -> dict:
    records = rows(output / "browser-observations.jsonl")
    require(len(records) == 60 and len({(r["label"], r["mode"], r["case"]) for r in records}) == 60,
            "E2 requires 60 distinct browser observations")
    require(all(not r["harness_error"] for r in records), "E2 contains harness errors")
    calculated = []
    for mode in ("original_confirm", "session_gate"):
        group = [r for r in records if r["mode"] == mode]
        calculated.append({"mode": mode, "planned": len(group), "scored": len(group), "harness_errors": 0,
                           "accepted": sum(r["response"]["accepted"] for r in group),
                           "review_mismatch_cases": sum(bool(r["review_mismatches"]) for r in group),
                           "rejections_with_writes": sum(not r["response"]["accepted"] and not r["response"]["zero_write_on_reject"] for r in group),
                           "cases": [{k: r[k] for k in ("label", "case", "review_mismatches")} |
                                     {"accepted": r["response"]["accepted"]} for r in group]})
    require(calculated == read(output / "summary.json") == read(expected / "summary.json"), "E2 summary mismatch")
    require(all(r["response"]["accepted"] or r["response"]["before_digest"] == r["response"]["after_digest"]
                for r in records), "E2 rejected case wrote state")
    return {"browser_cases": 60, "accepted_by_mode": {s["mode"]: s["accepted"] for s in calculated}}


def verify(work: Path) -> None:
    check_sources(work)
    results = work / "DKE-supplement/results"
    report = {"deposit_commit": DEPOSIT, "source_commit": SOURCE,
              "e1": e1_checks(results / "e1", results / "e1"),
              "e2": e2_checks(results / "e2", results / "e2"), "e3": {}}
    for section, keys, count in (("mechanism", ["fields", "changed", "arm"], 4000),
                                  ("ablation", ["fields", "changed", "arm"], 4000),
                                  ("trace", ["fields", "versions", "records", "arm"], 14400)):
        raw = rows(results / "e3" / section / "raw.jsonl")
        require(len(raw) == count, "E3 observation count mismatch: " + section)
        groups = {}
        for row in raw:
            groups.setdefault(tuple(row[k] for k in keys), []).append(row)
        calculated = []
        for key in sorted(groups):
            group = groups[key]
            ms = sorted(r["latency_ns"] / 1e6 for r in group)
            require(len(group) == 200, "E3 cell does not contain 200 observations")
            calculated.append(dict(zip(keys, key)) | {"n": len(group), "p50_ms": statistics.median(ms),
                "p95_ms": ms[int((len(ms) - 1) * .95)], "min_ms": ms[0], "max_ms": ms[-1],
                "sql_min": min(r.get("sql_statements", 0) for r in group),
                "sql_max": max(r.get("sql_statements", 0) for r in group)})
        require(calculated == read(results / "e3" / section / "summary.json"), "E3 raw-to-summary mismatch: " + section)
        report["e3"][section] = {"observations": len(raw), "arm_cells": len(groups), "summary_matches": True}
    report["scope"] = "Pinned source/input integrity and raw-to-summary checks; no new execution or database restoration."
    write(work / "verification.json", report)
    print(json.dumps(report, indent=2))


def uv_python(script: Path, *args: str, browser: bool = False, cwd: Path | None = None) -> None:
    packages = CORE_PACKAGES + ([BROWSER_PACKAGE] if browser else [])
    command = ["uv", "run", "--no-project", "--python", "3.11"]
    for package in packages:
        command += ["--with", package]
    subprocess.run(command + ["python", "-B", str(script), *args], cwd=cwd, check=True)


def execute(work: Path, action: str, section: str) -> None:
    check_sources(work)
    root = work / "DKE-supplement"
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    output = work / "runs" / (action + "-" + stamp)
    require(not output.exists(), "Output exists; wait a second before starting another run")
    output.parent.mkdir(exist_ok=True)
    print("New output: " + str(output), flush=True)
    if action == "test":
        # pytest runs as a module to avoid depending on a particular interpreter path.
        packages = [arg for p in CORE_PACKAGES for arg in ("--with", p)]
        subprocess.run(["uv", "run", "--no-project", "--python", "3.11", *packages, "python", "-B", "-m", "pytest",
                        "-q", "-p", "no:cacheprovider", "--basetemp", str(output), str(root / "test_supplement.py")],
                       cwd=root, check=True)
    elif action == "formal":
        formal = work / "dke-experiments/latest/code/formal-fixed"
        output.mkdir()
        subprocess.run([sys.executable, "-B", "-m", "unittest", "discover", "-s", "tests", "-v"], cwd=formal, check=True)
    elif action == "e1":
        uv_python(root / "experiment1.py", "--output", str(output), cwd=root)
        write(output / "comparison-to-deposit.json", e1_checks(output, root / "results/e1"))
    elif action == "e2":
        # Only the driver launch path is adapted in a disposable sibling directory.
        # The archived driver stays intact; scientific case logic is unchanged.
        runtime = work / ("browser-runtime-" + stamp)
        runtime.mkdir()
        for source in root.glob("*.py"):
            shutil.copyfile(source, runtime / source.name)
        driver = runtime / "browser_driver.py"
        original = driver.read_text(encoding="utf-8")
        old = "executable_path=r'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'"
        require(original.count(old) == 1, "Unexpected browser launch expression")
        driver.write_text("import os\n" + original.replace(old, 'executable_path=os.environ.get("DKE_CHROME")'), encoding="utf-8")
        write(runtime / "browser-adapter.json", {"original_sha256": digest(root / "browser_driver.py"),
              "adapted_sha256": digest(driver), "change": "Browser executable from DKE_CHROME or Playwright Chromium; case logic unchanged",
              "reviewer_driver_package": BROWSER_PACKAGE, "original_driver_package_version": "not recorded",
              "browser_executable": os.environ.get("DKE_CHROME", "Playwright-installed Chromium")})
        # experiment2 needs the actual uv interpreter for its driver subprocess.
        launch = runtime / "launch_reviewer_e2.py"
        launch.write_text("import sys\nfrom pathlib import Path\nfrom experiment2 import run\nrun(Path(sys.argv[1]), sys.executable)\n", encoding="utf-8")
        uv_python(launch, str(output), browser=True, cwd=runtime)
        shutil.copyfile(runtime / "browser-adapter.json", output / "browser-adapter.json")
        write(output / "comparison-to-deposit.json", e2_checks(output, root / "results/e2"))
    elif action == "e3":
        uv_python(root / "experiment3.py", "--section", section, "--output", str(output), cwd=root)
    print("Completed. Results: " + str(output))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("prepare", "verify", "test", "formal", "e1", "e2", "e3"))
    parser.add_argument("--workspace", type=Path, default=REPO / ".reviewer-work")
    parser.add_argument("--section", choices=("all", "mechanism", "ablation", "trace", "storage"), default="all",
                        help="For e3 only. Uses the full frozen workload, never a pilot.")
    args = parser.parse_args()
    work = args.workspace.resolve()
    require(work != REPO and not work.is_relative_to(REPO / "DKE-supplement")
            and not work.is_relative_to(REPO / "revisions") and not work.is_relative_to(REPO / "latest"),
            "Use a separate workspace, outside deposited evidence and manuscript directories")
    if args.action == "prepare":
        prepare(work)
    elif args.action == "verify":
        verify(work)
    else:
        execute(work, args.action, args.section)


if __name__ == "__main__":
    try:
        main()
    except (ValueError, FileNotFoundError, subprocess.CalledProcessError) as exc:
        print("STOP: " + str(exc), file=sys.stderr)
        sys.exit(1)
