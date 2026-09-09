from __future__ import annotations

import json
from pathlib import Path

import build_r21_manifest as manifest


def test_manifest_excludes_local_package_metadata(tmp_path: Path) -> None:
    metadata = tmp_path / "source" / "demo.egg-info" / "PKG-INFO"
    metadata.parent.mkdir(parents=True)
    metadata.write_text("local installation metadata", encoding="utf-8")
    assert manifest.build(tmp_path)["files"] == []


def test_manifest_excludes_runner_caches_but_keeps_evidence(tmp_path: Path) -> None:
    for relative in ["runner-state/hypothesis/constants/cache", "runner-state/mypy/cache.db",
                     "runner-state/receipts/result.json", "hypothesis/evidence.json"]:
        path = tmp_path / "evidence" / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("retained", encoding="utf-8")
    assert {item["path"] for item in manifest.build(tmp_path)["files"]} == {
        "evidence/runner-state/receipts/result.json", "evidence/hypothesis/evidence.json"}


def test_verify_rejects_exact_one_byte_change_and_extra_file(tmp_path: Path) -> None:
    (tmp_path / "payload.txt").write_bytes(b"locked\n")
    payload = manifest.build(tmp_path)

    assert manifest.verify(payload, tmp_path) == []

    (tmp_path / "payload.txt").write_bytes(b"LockeD\n")
    assert manifest.verify(payload, tmp_path) == ["sha256:payload.txt"]

    (tmp_path / "payload.txt").write_bytes(b"locked\n")
    (tmp_path / "extra.txt").write_bytes(b"extra\n")
    assert manifest.verify(payload, tmp_path) == ["extra:extra.txt"]


def test_manifest_is_non_self_referential(tmp_path: Path) -> None:
    (tmp_path / "payload.json").write_text(json.dumps({"value": 1}), encoding="utf-8")
    manifest_path = tmp_path / "evidence" / "r21-revision-manifest.json"
    manifest_path.parent.mkdir()
    manifest_path.write_text("{}\n", encoding="utf-8")

    payload = manifest.build(tmp_path)

    assert payload["non_self_referential"] is True
    assert [item["path"] for item in payload["files"]] == ["payload.json"]


def test_manifest_records_canonical_paper_identity_and_page_count(tmp_path: Path) -> None:
    paper_pdf = tmp_path / "paper" / "main-final.pdf"
    paper_pdf.parent.mkdir()
    paper_pdf.write_bytes(b"%PDF-1.7\nfinal-paper\n")

    payload = manifest.build(
        tmp_path,
        paper_pdf=Path("paper/main-final.pdf"),
        paper_pages=54,
    )

    assert payload["paper_pdf"] == {
        "path": "paper/main-final.pdf",
        "pages": 54,
        "bytes": paper_pdf.stat().st_size,
        "sha256": manifest.sha256(paper_pdf),
    }
