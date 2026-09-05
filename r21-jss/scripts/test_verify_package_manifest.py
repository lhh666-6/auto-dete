import hashlib
import json
import subprocess
import sys
from pathlib import Path


SCRIPT = Path(__file__).with_name("verify_package_manifest.py")


def _write_manifest(root: Path, content: bytes) -> None:
    payload = root / "payload.txt"
    payload.write_bytes(content)
    manifest = {
        "algorithm": "sha256",
        "file_count": 1,
        "total_bytes": len(content),
        "files": [
            {
                "path": "payload.txt",
                "bytes": len(content),
                "sha256": hashlib.sha256(content).hexdigest(),
            }
        ],
    }
    (root / "PACKAGE_MANIFEST.json").write_text(
        json.dumps(manifest), encoding="utf-8"
    )


def test_verifier_accepts_matching_package_and_rejects_tamper(tmp_path: Path) -> None:
    _write_manifest(tmp_path, b"frozen evidence\n")

    clean = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert clean.returncode == 0
    assert '"verified": true' in clean.stdout.lower()

    (tmp_path / "payload.txt").write_bytes(b"tampered\n")
    tampered = subprocess.run(
        [sys.executable, str(SCRIPT), "--root", str(tmp_path)],
        capture_output=True,
        text=True,
    )
    assert tampered.returncode == 1
    assert "sha256:payload.txt" in tampered.stdout
