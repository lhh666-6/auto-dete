#!/usr/bin/env python3
"""Verify the integrated current package against its manifest.

Run this from the package directory it belongs to::

    cd latest
    python verify_latest.py

The package manifest (``MANIFEST-r27.json``, filename retained for
compatibility) is non-self-referential and records the SHA-256 digest and byte
size of every shipped file, plus the main/supplement page counts and the
citation count.  This entry point re-hashes the tree and reports any missing,
extra, modified, or page-count-divergent item.  It reads no network and writes
nothing, so it is safe to run on a sealed package.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
BUILDER = (
    HERE
    / "evidence"
    / "human-acknowledgment-annotation-2026-09-10"
    / "build_latest_manifest.py"
)


def main() -> int:
    if not BUILDER.is_file():
        print(f"manifest builder not found: {BUILDER}", file=sys.stderr)
        return 2
    return subprocess.call(
        [
            sys.executable,
            str(BUILDER),
            "--root", str(HERE),
            "--manifest", str(HERE / "MANIFEST-r27.json"),
            "--verify-only",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
