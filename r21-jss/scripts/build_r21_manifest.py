"""Build or verify the non-self-referential R21 revision manifest."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "evidence" / "r21-revision-manifest.json"

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
    "PACKAGE_MANIFEST.json",
    "main.aux",
    "main.bbl",
    "main.blg",
    "main.fdb_latexmk",
    "main.fls",
    "main.log",
    "main.out",
    "main.spl",
    "main.synctex.gz",
    MANIFEST.name,
}
EXCLUDED_PREFIXES = (
    "evidence/reproduced/r21/live-agent-smoke/",
    "evidence/reproduced/r21/r21-manifest-tamper-probe-",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def selected_files(root: Path = ROOT) -> list[Path]:
    selected = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(root)
        portable = relative.as_posix()
        if EXCLUDED_PARTS.intersection(relative.parts):
            continue
        if any(part.endswith(".egg-info") for part in relative.parts):
            continue
        if any(relative.parts[i:i + 2] in {
            ("runner-state", "hypothesis"), ("runner-state", "mypy")
        } for i in range(len(relative.parts) - 1)):
            continue
        if path.name in EXCLUDED_NAMES or "visual-check-" in portable:
            continue
        if portable.startswith(EXCLUDED_PREFIXES):
            continue
        selected.append(path)
    return sorted(selected, key=lambda path: path.relative_to(root).as_posix())


def build(
    root: Path = ROOT,
    *,
    paper_pdf: Path | None = None,
    paper_pages: int | None = None,
) -> dict[str, Any]:
    entries = []
    total_bytes = 0
    for path in selected_files(root):
        size = path.stat().st_size
        total_bytes += size
        entries.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": size,
                "sha256": sha256(path),
            }
        )
    payload: dict[str, Any] = {
        "schema": "auto-decte.r21-revision-manifest.v1",
        "revision": "2026-08-27-jss-r21-live-agent-performance",
        "algorithm": "sha256",
        "non_self_referential": True,
        "file_count": len(entries),
        "total_bytes": total_bytes,
        "files": entries,
    }
    if paper_pdf is not None or paper_pages is not None:
        if paper_pdf is None or paper_pages is None or paper_pages < 1:
            raise ValueError("paper_pdf and a positive paper_pages value are required together")
        paper_path = root / paper_pdf
        payload["paper_pdf"] = {
            "path": paper_pdf.as_posix(),
            "pages": paper_pages,
            "bytes": paper_path.stat().st_size,
            "sha256": sha256(paper_path),
        }
    return payload


def verify(payload: dict[str, Any], root: Path = ROOT) -> list[str]:
    failures: list[str] = []
    items = payload.get("files", [])
    declared_paths = [item["path"] for item in items]
    if len(declared_paths) != len(set(declared_paths)):
        failures.append("manifest:duplicate-path")
    for item in items:
        path = root / item["path"]
        if not path.is_file():
            failures.append(f"missing:{item['path']}")
        elif path.stat().st_size != item["bytes"]:
            failures.append(f"size:{item['path']}")
        elif sha256(path) != item["sha256"]:
            failures.append(f"sha256:{item['path']}")
    current_paths = {
        path.relative_to(root).as_posix() for path in selected_files(root)
    }
    for path in sorted(current_paths - set(declared_paths)):
        failures.append(f"extra:{path}")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("operation", choices=("build", "verify"))
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--paper-pdf", type=Path)
    parser.add_argument("--paper-pages", type=int)
    args = parser.parse_args()
    root = args.root.resolve()
    manifest_path = (
        args.manifest.resolve()
        if args.manifest is not None
        else root / "evidence" / MANIFEST.name
    )
    if args.operation == "build":
        manifest_path.parent.mkdir(parents=True, exist_ok=True)
        manifest_path.write_text(
            json.dumps(
                build(root, paper_pdf=args.paper_pdf, paper_pages=args.paper_pages),
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
    payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    failures = verify(payload, root)
    print(json.dumps({"verified": not failures, "failures": failures}, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
