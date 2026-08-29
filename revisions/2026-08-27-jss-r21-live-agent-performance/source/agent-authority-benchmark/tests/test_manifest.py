import json

from auto_decte_agent_benchmark.manifest import build_manifest, verify_manifest


def test_manifest_is_non_self_referential_and_detects_one_byte_change(tmp_path) -> None:
    root = tmp_path / "artifact"
    root.mkdir()
    (root / "raw.json").write_text('{"ok":true}\n', encoding="utf-8")
    (root / "nested").mkdir()
    (root / "nested/result.csv").write_text("run_id,ok\nR1,1\n", encoding="utf-8")
    manifest_path = root / "manifest.json"

    manifest = build_manifest(root, manifest_path=manifest_path)
    manifest_path.write_text(json.dumps(manifest, sort_keys=True) + "\n", encoding="utf-8")

    assert "manifest.json" not in {item["path"] for item in manifest["files"]}
    assert verify_manifest(root, manifest_path) == []
    (root / "raw.json").write_bytes(b'!{"ok":true}\n')
    failures = verify_manifest(root, manifest_path)
    assert failures == ["HASH_OR_SIZE:raw.json"]


def test_manifest_detects_missing_and_extra_files(tmp_path) -> None:
    root = tmp_path / "artifact"
    root.mkdir()
    (root / "one.txt").write_text("one", encoding="utf-8")
    manifest_path = root / "manifest.json"
    manifest_path.write_text(
        json.dumps(build_manifest(root, manifest_path=manifest_path)), encoding="utf-8"
    )
    (root / "one.txt").unlink()
    (root / "two.txt").write_text("two", encoding="utf-8")

    assert verify_manifest(root, manifest_path) == ["MISSING:one.txt", "EXTRA:two.txt"]
