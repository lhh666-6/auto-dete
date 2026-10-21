"""Fetch the pinned upstream source, checking Git blob identity before use."""
from __future__ import annotations

import hashlib
import json
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INVENTORY = ROOT.parent / "kais-rejection-comparison-2026-10-20/toolgate-source-inventory.json"


def main() -> None:
    inventory = json.loads(INVENTORY.read_text(encoding="utf-8"))
    commit = inventory["sha"]
    destination = ROOT / "vendor" / "ToolGate"
    records = []
    for item in inventory["tree"]:
        name = item["path"]
        if item["type"] != "blob" or not (
            name.startswith("toolgate/") and name.endswith(".py")
            or name in {"setup.py", "requirements.txt"}
        ):
            continue
        target = destination / name
        url = f"https://raw.githubusercontent.com/Liam-magicbook/ToolGate/{commit}/{name}"
        if target.exists():
            data = target.read_bytes()
        else:
            for attempt in range(3):
                try:
                    request = urllib.request.Request(url, headers={"User-Agent": "research-reproducibility"})
                    with urllib.request.urlopen(request, timeout=30) as response:
                        data = response.read()
                    break
                except Exception:
                    if attempt == 2:
                        raise
                    time.sleep(attempt + 1)
        actual = hashlib.sha1(f"blob {len(data)}\0".encode() + data).hexdigest()
        if actual != item["sha"]:
            raise RuntimeError(f"Upstream blob mismatch: {name}")
        target.parent.mkdir(parents=True, exist_ok=True)
        if not target.exists():
            target.write_bytes(data)
        records.append({
            "path": target.relative_to(ROOT).as_posix(),
            "source_url": url,
            "git_blob_sha1": actual,
            "sha256": hashlib.sha256(data).hexdigest(),
        })
    receipt = {
        "source": inventory["source"],
        "commit": commit,
        "files": records,
        "source_modifications": False,
        "scope": "Pinned Python source and dependency metadata; no model call or package installation.",
    }
    (ROOT / "UPSTREAM-SOURCE.json").write_text(
        json.dumps(receipt, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps({"verified_upstream_files": len(records), "commit": commit}))


if __name__ == "__main__":
    main()
