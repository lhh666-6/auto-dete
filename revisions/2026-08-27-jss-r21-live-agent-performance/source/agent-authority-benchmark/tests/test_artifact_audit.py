import hashlib
import json
from pathlib import Path

import pytest

from auto_decte_agent_benchmark.artifact_audit import audit_final_artifact
from auto_decte_agent_benchmark.manifest import build_manifest


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _complete_artifact(root: Path) -> Path:
    root.mkdir()
    (root / "raw").mkdir()
    (root / "raw" / "run.json").write_text('{"terminal":true}\n', encoding="utf-8")
    (root / "summary.json").write_text('{"complete":true}\n', encoding="utf-8")
    manifest_path = root / "manifest.json"
    manifest_path.write_text(
        json.dumps(build_manifest(root, manifest_path=manifest_path), sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return manifest_path


def test_audit_mutates_only_an_isolated_copy_and_writes_exact_detection_receipt(
    tmp_path: Path,
) -> None:
    final_root = tmp_path / "final"
    manifest_path = _complete_artifact(final_root)
    original_hashes = {
        path.relative_to(final_root).as_posix(): _sha256(path)
        for path in final_root.rglob("*")
        if path.is_file()
    }
    output = tmp_path / "audit"

    receipt_path = audit_final_artifact(final_root=final_root, output=output)

    receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
    assert receipt["schema_version"] == "agent-authority-tamper-probe.v2"
    assert receipt["status"] == "PASS"
    assert receipt["clean_verification_before"] == []
    assert receipt["tampered_verification"] == [
        f'HASH_OR_SIZE:{receipt["mutated_path"]}'
    ]
    assert receipt["clean_verification_after"] == []
    assert receipt["original_sha256"] != receipt["mutated_sha256"]
    assert receipt["original_bytes"] == receipt["mutated_bytes"]
    assert receipt["manifest_sha256"] == _sha256(manifest_path)
    assert not (output / "tampered-copy").exists()
    assert {
        path.relative_to(final_root).as_posix(): _sha256(path)
        for path in final_root.rglob("*")
        if path.is_file()
    } == original_hashes


def test_audit_rejects_dirty_final_without_creating_output(tmp_path: Path) -> None:
    final_root = tmp_path / "final"
    _complete_artifact(final_root)
    (final_root / "summary.json").write_text('{"complete":false}\n', encoding="utf-8")
    output = tmp_path / "audit"

    with pytest.raises(ValueError, match="clean Final manifest verification failed"):
        audit_final_artifact(final_root=final_root, output=output)

    assert not output.exists()


def test_audit_refuses_existing_or_nested_output(tmp_path: Path) -> None:
    final_root = tmp_path / "final"
    _complete_artifact(final_root)
    existing = tmp_path / "audit"
    existing.mkdir()

    with pytest.raises(FileExistsError):
        audit_final_artifact(final_root=final_root, output=existing)
    with pytest.raises(ValueError, match="outside the Final root"):
        audit_final_artifact(final_root=final_root, output=final_root / "audit")
