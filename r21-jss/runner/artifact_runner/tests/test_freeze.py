from __future__ import annotations

import json
from pathlib import Path

import pytest

from artifact_runner.freeze import build_source_freeze
from artifact_runner.integrity import verify_manifest


def test_freeze_allowlist_excludes_cache_and_refuses_overwrite(tmp_path: Path) -> None:
    parent = tmp_path / "parent"
    implementation = tmp_path / "implementation"
    (parent / "formal").mkdir(parents=True)
    (parent / "formal" / "model.als").write_text("sig A {}", encoding="utf-8")
    (implementation / "app").mkdir(parents=True)
    (implementation / "app" / "main.py").write_text("VALUE = 1", encoding="utf-8")
    (implementation / ".pytest_cache").mkdir()
    (implementation / ".pytest_cache" / "bad").write_text("cache", encoding="utf-8")
    config = {
        "schema_version": 1,
        "paper_repo": [{"path": "formal", "kind": "tree"}],
        "implementation": [{"path": "app", "kind": "tree"}],
        "runner": [],
        "excluded_names": [".pytest_cache"],
    }
    config_path = tmp_path / "freeze.json"
    config_path.write_text(json.dumps(config), encoding="utf-8")
    output = tmp_path / "freeze"
    build_source_freeze(parent, implementation, config_path, output)
    assert (output / "source" / "paper-repo" / "formal" / "model.als").exists()
    assert not any(path.name == ".pytest_cache" for path in output.rglob("*"))
    assert verify_manifest(output, output / "source_manifest.json") == []
    with pytest.raises(FileExistsError):
        build_source_freeze(parent, implementation, config_path, output)
