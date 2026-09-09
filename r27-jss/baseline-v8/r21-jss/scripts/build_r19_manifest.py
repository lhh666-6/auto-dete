"""Build or verify the non-self-referential R19 revision manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence" / "r19-revision-manifest.json"

EXCLUDED_PARTS = {
    ".git",
    ".hypothesis",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "node_modules",
    "out",
}
EXCLUDED_NAMES = {
    "main.aux",
    "main.blg",
    "main.fdb_latexmk",
    "main.fls",
    "main.log",
    "main.out",
    "main.spl",
    "main.synctex.gz",
    MANIFEST.name,
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def selected_files() -> list[Path]:
    roots = [
        ROOT / "docs" / "literature-review",
        ROOT / "evidence" / "paper-inputs",
        ROOT / "evidence" / "reproduced" / "r19-dsh-2026-08-27-final",
        ROOT / "paper",
        ROOT / "source" / "dsh-plugin-auto-decte",
        ROOT / "source" / "implementation" / "app",
        ROOT / "source" / "implementation" / "tests",
    ]
    files: set[Path] = {
        ROOT / "FINAL_CODEX_HANDOFF.md",
        ROOT / "README.md",
        ROOT / "R19_BASELINE.md",
        ROOT / "findings.md",
        ROOT / "progress.md",
        ROOT / "task_plan.md",
        ROOT / "evidence" / "claim-evidence-ledger.json",
        ROOT / "evidence" / "r19-dsh-2026-08-27-final-clean-verification.json",
        ROOT / "evidence" / "r19-dsh-2026-08-27-final-tamper-verification.json",
        ROOT / "evidence" / "r19-verification-summary.json",
        ROOT / "source" / "external" / "downloads" / "deepseek-harness-dsh-v0.1.1-rc.2.zip",
        ROOT / "source" / "implementation" / "pyproject.toml",
        ROOT / "source" / "implementation" / "uv.lock",
        ROOT / "research_audit" / "08_FINAL_RESEARCH_LOCK.md",
        ROOT / "reviews" / "artifact-coherence" / "2026-08-27-r19.md",
        ROOT / "reviews" / "code-paper-audit" / "2026-08-27-r19.md",
        ROOT / "reviews" / "pre-submission-report" / "2026-08-27-r19.md",
        ROOT / "reviews" / "reproducibility" / "2026-08-27-r19.md",
        ROOT / "scripts" / "build_r19_manifest.py",
    }
    for base in roots:
        files.update(path for path in base.rglob("*") if path.is_file())
    return sorted(
        (
            path
            for path in files
            if path.exists()
            and not EXCLUDED_PARTS.intersection(path.relative_to(ROOT).parts)
            and path.name not in EXCLUDED_NAMES
            and "visual-check-" not in path.as_posix()
        ),
        key=lambda path: path.relative_to(ROOT).as_posix(),
    )


def build() -> dict[str, object]:
    entries = []
    total_bytes = 0
    for path in selected_files():
        size = path.stat().st_size
        total_bytes += size
        entries.append(
            {
                "path": path.relative_to(ROOT).as_posix(),
                "bytes": size,
                "sha256": sha256(path),
            }
        )
    return {
        "schema_version": "auto-decte.r19-revision-manifest.v1",
        "revision": "2026-08-27-jss-r19-dsh",
        "algorithm": "sha256",
        "non_self_referential": True,
        "file_count": len(entries),
        "total_bytes": total_bytes,
        "files": entries,
    }


def verify(payload: dict[str, object]) -> list[str]:
    failures: list[str] = []
    for entry in payload["files"]:  # type: ignore[index]
        item = entry  # type: ignore[assignment]
        path = ROOT / item["path"]  # type: ignore[index]
        if not path.is_file():
            failures.append(f"missing:{item['path']}")  # type: ignore[index]
        elif path.stat().st_size != item["bytes"]:  # type: ignore[index]
            failures.append(f"size:{item['path']}")  # type: ignore[index]
        elif sha256(path) != item["sha256"]:  # type: ignore[index]
            failures.append(f"sha256:{item['path']}")  # type: ignore[index]
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("build", "verify"))
    args = parser.parse_args()
    if args.operation == "build":
        MANIFEST.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    failures = verify(payload)
    print(json.dumps({"verified": not failures, "failures": failures}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
