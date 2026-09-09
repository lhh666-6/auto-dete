"""Build the non-self-referential manifest for the Git deposit subtree."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tracked_files(root: Path) -> list[Path]:
    repo = Path(
        subprocess.check_output(
            ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
            text=True,
        ).strip()
    )
    package_rel = root.relative_to(repo).as_posix()
    output = subprocess.check_output(
        ["git", "-C", str(repo), "ls-files", "--cached", "--others", "--exclude-standard", "--", package_rel],
        text=True,
    )
    paths = []
    for line in output.splitlines():
        path = repo / line
        if path.is_file() and path.resolve() != (root / "PACKAGE_MANIFEST.json").resolve():
            paths.append(path)
    return sorted(paths, key=lambda path: path.relative_to(root).as_posix())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    root = args.root.resolve()
    entries = []
    total_bytes = 0
    for path in tracked_files(root):
        size = path.stat().st_size
        total_bytes += size
        entries.append(
            {
                "path": path.relative_to(root).as_posix(),
                "bytes": size,
                "sha256": sha256(path),
            }
        )
    manifest = {
        "schema": "auto-decte-r21-package-manifest-v1",
        "created_utc": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "algorithm": "sha256",
        "scope": "Every Git-tracked file below r21-jss except this non-self-referential manifest",
        "exclusions": [
            "local virtual environments, generated package metadata, property-test state, static-analysis state, and caches",
            "duplicate source snapshots and dependency runtimes",
            "superseded pilot, diagnostic, and aborted hosted-model runs",
            "credentials and provider authentication material",
        ],
        "file_count": len(entries),
        "total_bytes": total_bytes,
        "files": entries,
    }
    (root / "PACKAGE_MANIFEST.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
