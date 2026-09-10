import argparse
import hashlib
import importlib.metadata
import json
import subprocess
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from benchmarks.io import write_json
from benchmarks.render_paper_artifacts import render_artifacts
from benchmarks.run_forms import run_form_benchmark
from benchmarks.run_recognition import run_recognition
from benchmarks.run_resilience import run_resilience
from benchmarks.trust_faults import (
    run_candidate_isolation_ablation,
    run_fault_matrix,
    run_randomized_fault_stress,
)


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _git(*arguments: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", *arguments], check=True, capture_output=True, text=True, timeout=30
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return completed.stdout.strip()


def run_all(
    config_path: Path,
    output: Path,
    *,
    resilience_repetitions: int = 30,
    resilience_warmups: int = 5,
) -> dict[str, Any]:
    started = datetime.now(UTC)
    config = cast(dict[str, Any], json.loads(config_path.read_text(encoding="utf-8")))
    output.mkdir(parents=True, exist_ok=True)
    source_commit = _git("rev-parse", "HEAD")
    tracked_status = _git("status", "--porcelain", "--untracked-files=no")

    with tempfile.TemporaryDirectory(prefix="auto-decte-master-trust-") as temporary:
        trust_root = Path(temporary)
        trust = run_fault_matrix(trust_root / "matrix")
        ablation = run_candidate_isolation_ablation(trust_root / "ablation")
        stress = run_randomized_fault_stress(
            trust_root / "stress",
            trials_per_family=int(config.get("fault_trials_per_family", 1)),
            seed=int(config.get("fault_stress_seed", 73)),
        )
    if not all(item.fact_unchanged and item.audit_complete for item in trust):
        raise RuntimeError("trust-boundary fault matrix failed")
    write_json(output / "trust_faults.json", trust)
    write_json(output / "trust_ablation.json", [ablation])
    if not all(item.contained for item in stress):
        raise RuntimeError("randomized trust-boundary stress test failed")
    write_json(output / "trust_stress.json", stress)

    recognition = run_recognition(config_path, output)
    forms = run_form_benchmark(config_path, output) if "form_templates" in config else None
    resilience = run_resilience(
        output / "resilience.json",
        repetitions=resilience_repetitions,
        warmups=resilience_warmups,
    )
    if not all(resilience.checks.values()):
        raise RuntimeError("one or more resilience checks failed")
    render_artifacts(output, output / "paper")

    artifacts = []
    for path in sorted(item for item in output.rglob("*") if item.is_file()):
        if path.name == "manifest.json":
            continue
        artifacts.append(
            {
                "path": path.relative_to(output).as_posix(),
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }
        )
    packages: dict[str, str | None] = {}
    for package in ("numpy", "opencv-python-headless", "matplotlib", "scikit-learn", "sqlalchemy"):
        try:
            packages[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            packages[package] = None
    manifest = {
        "benchmark_id": config["benchmark_id"],
        "source_commit": source_commit,
        "source_tracked_dirty_before_run": (
            None if tracked_status is None else bool(tracked_status)
        ),
        "config_path": config_path.as_posix(),
        "config_sha256": _sha256(config_path),
        "seeds": config["seeds"],
        "started_utc": started.isoformat(),
        "ended_utc": datetime.now(UTC).isoformat(),
        "commands": [
            "python -m benchmarks.run_trust",
            "python -m benchmarks.run_recognition",
            "python -m benchmarks.run_forms",
            "python -m benchmarks.run_resilience",
            "python -m benchmarks.render_paper_artifacts",
        ],
        "packages": packages,
        "recognition": {
            "case_count": recognition.case_count,
            "raw_row_count": recognition.raw_row_count,
            "model_count": recognition.model_count,
        },
        "forms": (
            {
                "base_form_count": forms.base_form_count,
                "evaluation_form_count": forms.evaluation_form_count,
                "raw_row_count": forms.raw_row_count,
                "workflow_count": forms.workflow_count,
            }
            if forms is not None
            else None
        ),
        "fault_trials_per_family": int(config.get("fault_trials_per_family", 1)),
        "resilience_repetitions": resilience_repetitions,
        "artifacts": artifacts,
    }
    encoded = json.dumps(manifest, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    (output / "manifest.json").write_text(encoded, encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the full ESWA benchmark package")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_all(args.config, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
