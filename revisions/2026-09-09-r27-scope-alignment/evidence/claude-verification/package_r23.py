"""Build and verify MANIFEST-r23.json and the r23 ZIP package.

Usage (from anywhere):

    python evidence/claude-verification/package_r23.py --build
    python evidence/claude-verification/package_r23.py --check

The manifest binds every packaged file except itself; the ZIP contains the
whole package (including the manifest) under a single top-level directory.
Build intermediates (``paper/out``), ``__pycache__`` and ``.pytest_cache`` are
excluded, matching the r22-concise packaging convention.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT.parent / "2026-09-08-r22-concise"
MANIFEST = ROOT / "MANIFEST-r23.json"
ZIP_PATH = ROOT.parent / "r23-executable-checklist-verified-2026-09-09.zip"
SCHEMA = "auto-decte.r23-executable-checklist-manifest.v2"

EXCLUDE_PARTS = {"out", "__pycache__", ".pytest_cache", ".hypothesis"}
EXCLUDE_RELS = {"MANIFEST-r23.json"}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def packaged_files(root):
    out = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel = path.relative_to(root).as_posix()
        if rel in EXCLUDE_RELS or any(part in EXCLUDE_PARTS for part in path.parts):
            continue
        out.append(rel)
    return out


def page_count(pdf):
    import fitz  # local import: only needed when building the manifest

    return fitz.open(pdf).page_count


def log_stats(log_path):
    if not log_path.exists():
        return {"present": False}
    text = log_path.read_text(encoding="utf-8", errors="replace")
    return {
        "present": True,
        "latex_warnings": len(re.findall(r"LaTeX Warning", text)),
        "overfull": len(re.findall(r"Overfull", text)),
        "underfull": len(re.findall(r"Underfull", text)),
        "undefined": len(re.findall(r"(?i)undefined", text)),
    }


def protected_comparison():
    base = {rel: sha256(BASELINE / rel) for rel in packaged_files(BASELINE)}
    new = {rel: sha256(ROOT / rel) for rel in packaged_files(ROOT)}
    added = sorted(set(new) - set(base))
    removed = sorted(set(base) - set(new))
    changed = sorted(rel for rel in set(base) & set(new) if base[rel] != new[rel])
    protected_prefixes = ("code/", "evidence/", "fixtures/", "baseline-v8/")
    protected_changed = [rel for rel in changed if rel.startswith(protected_prefixes)]
    paper_changed = [rel for rel in changed if rel.startswith("paper/")]
    other_changed = [rel for rel in changed
                     if not rel.startswith(protected_prefixes) and not rel.startswith("paper/")]
    common = set(base) & set(new)
    protected_common = sorted(rel for rel in common if rel.startswith(protected_prefixes))
    protected_unchanged = [rel for rel in protected_common if rel not in changed]
    return {
        "baseline_packaged_files": len(base),
        "new_packaged_files": len(new),
        "added": added,
        "removed": removed,
        "changed": changed,
        "protected_changed": protected_changed,
        "paper_changed": paper_changed,
        "other_changed": other_changed,
        "protected_files_compared": len(protected_common),
        "protected_files_unchanged": len(protected_unchanged),
    }


def build():
    files = packaged_files(ROOT)
    comparison = protected_comparison()
    summary = json.loads((ROOT / "evidence/checklist-runs-reviewed-2026-09-09/summary.json").read_text(encoding="utf-8"))
    handoff = {}
    for line in (ROOT / "evidence/codex-handoff/SHA256SUMS.txt").read_text(encoding="utf-8").splitlines():
        digest, name = line.split(" *", 1)
        handoff[name] = digest
    manifest = {
        "schema": SCHEMA,
        "created_utc": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "package": "revisions/2026-09-08-r23-executable-checklist",
        "baseline": {
            "package": "revisions/2026-09-08-r22-concise",
            "main_pages": page_count(BASELINE / "paper/main.pdf"),
            "supplement_pages": page_count(BASELINE / "paper/supplement.pdf"),
        },
        "verification": {
            "main_pages": page_count(ROOT / "paper/main.pdf"),
            "supplement_pages": page_count(ROOT / "paper/supplement.pdf"),
            "main_sha256": sha256(ROOT / "paper/main.pdf"),
            "supplement_sha256": sha256(ROOT / "paper/supplement.pdf"),
            "main_log": log_stats(ROOT / "paper/out/main.log"),
            "supplement_log": log_stats(ROOT / "paper/out/supplement.log"),
            "protected_comparison": {
                "baseline_packaged_files": comparison["baseline_packaged_files"],
                "new_packaged_files": comparison["new_packaged_files"],
                "added_count": len(comparison["added"]),
                "removed_count": len(comparison["removed"]),
                "changed_count": len(comparison["changed"]),
                "protected_changed": comparison["protected_changed"],
                "paper_changed": comparison["paper_changed"],
                "other_changed": comparison["other_changed"],
                "protected_files_compared": comparison["protected_files_compared"],
                "protected_files_unchanged": comparison["protected_files_unchanged"],
                "removed": comparison["removed"],
                "removed_note": ("MANIFEST-r22.json was the stale r22-concise manifest copied into the r23 "
                                 "directory; the r23 package uses MANIFEST-r23.json and the r22 manifest "
                                 "remains in revisions/2026-09-08-r22-concise/."),
            },
            "tests": {
                "codex_behavior_tests": 12,
                "runner_tests_after_codex_review": 15,
                "total_passed": 27,
                "evidence": "evidence/checklist-verification-green-2026-09-09.txt",
                "protected_suite_rerun": {
                    "passed": 377,
                    "evidence": "evidence/pytest-full-claude.txt",
                    "note": ("sources are byte-identical to the r22-concise baseline; "
                             "the run is a reproducibility check, not a new experiment"),
                },
            },
            "fixed_cases": summary["cases"],
            "case_policy_records": summary["runs"],
            "database_executions": summary["database_executions"],
            "outcome_divergent_cases": summary["outcome_divergent_cases"],
            "paired_history_states_equal": summary["paired_history_states_equal"],
            "codex_handoff_sha256": handoff,
            "claude_test_harness_fix": "evidence/claude-test-harness-fix.diff",
        },
        "files": {rel: {"bytes": (ROOT / rel).stat().st_size, "sha256": sha256(ROOT / rel)}
                  for rel in files},
    }
    MANIFEST.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    with zipfile.ZipFile(ZIP_PATH, "w", zipfile.ZIP_DEFLATED) as zf:
        for rel in files:
            zf.write(ROOT / rel, f"r23-executable-checklist/{rel}")
        zf.write(MANIFEST, "r23-executable-checklist/MANIFEST-r23.json")
    return manifest


def check():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    problems = []
    for rel, meta in manifest["files"].items():
        path = ROOT / rel
        if not path.exists():
            problems.append(f"missing: {rel}")
        elif sha256(path) != meta["sha256"]:
            problems.append(f"hash mismatch: {rel}")
    listed = set(manifest["files"]) | {"MANIFEST-r23.json"}
    on_disk = set(packaged_files(ROOT)) | {"MANIFEST-r23.json"}
    for rel in sorted(on_disk - listed):
        problems.append(f"not in manifest: {rel}")
    for rel in sorted(listed - on_disk):
        problems.append(f"manifest entry not on disk: {rel}")
    if not ZIP_PATH.exists():
        problems.append("zip missing")
    else:
        with zipfile.ZipFile(ZIP_PATH) as zf:
            names = {n.split("/", 1)[1] for n in zf.namelist() if "/" in n}
            for rel in sorted(listed - names):
                problems.append(f"zip missing: {rel}")
            for rel in sorted(names - listed):
                problems.append(f"zip extra: {rel}")
            for rel in sorted(listed & names):
                if hashlib.sha256(zf.read(f"r23-executable-checklist/{rel}")).hexdigest() != manifest["files"].get(rel, {}).get("sha256", sha256(MANIFEST)):
                    problems.append(f"zip hash mismatch: {rel}")
    return manifest, problems


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.build:
        manifest = build()
        print(f"manifest: {MANIFEST} ({len(manifest['files'])} files)")
        print(f"zip: {ZIP_PATH}")
    if args.check:
        manifest, problems = check()
        print(json.dumps({
            "schema": manifest["schema"],
            "main_pages": manifest["verification"]["main_pages"],
            "supplement_pages": manifest["verification"]["supplement_pages"],
            "files": len(manifest["files"]),
            "problems": problems,
        }, indent=2))
        return 1 if problems else 0
    if not args.build and not args.check:
        parser.error("pass --build and/or --check")
    return 0


if __name__ == "__main__":
    sys.exit(main())
