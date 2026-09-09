"""Unit tests for canonical persisted EvidenceIdentity."""

import pytest

from app.domain.evidence_identity import (
    EvidenceIdentity,
    canonical_evidence_locator,
    canonicalize_storage_uri,
)


def test_canonical_locator_is_versioned_semantic_json_without_row_id() -> None:
    locator = canonical_evidence_locator(
        form_id="FORM-1",
        related_field_id="FIELD-1",
        uri=r"field-crops\ab\image name.png",
    )
    assert locator == (
        '{"form_id":"FORM-1","related_field_id":"FIELD-1",'
        '"uri":"field-crops/ab/image%20name.png","v":1}'
    )
    assert "file_id" not in locator


def test_uri_normalizes_unicode_and_percent_encoding() -> None:
    assert canonicalize_storage_uri("é/%7e.txt") == "%C3%A9/~.txt"
    assert canonicalize_storage_uri("e\u0301/~.txt") == "%C3%A9/~.txt"


def test_identity_equivalence_and_semantic_distinctions() -> None:
    base = EvidenceIdentity(
        "ab" * 32,
        canonical_evidence_locator(form_id="FORM-1", related_field_id="FIELD-1", uri=r"crop\a.png"),
    )
    equivalent = EvidenceIdentity(
        "ab" * 32,
        canonical_evidence_locator(form_id="FORM-1", related_field_id="FIELD-1", uri="crop/a.png"),
    )
    assert equivalent == base

    variants = (
        EvidenceIdentity(
            "cd" * 32,
            canonical_evidence_locator(
                form_id="FORM-1", related_field_id="FIELD-1", uri="crop/a.png"
            ),
        ),
        EvidenceIdentity(
            "ab" * 32,
            canonical_evidence_locator(
                form_id="FORM-2", related_field_id="FIELD-1", uri="crop/a.png"
            ),
        ),
        EvidenceIdentity(
            "ab" * 32,
            canonical_evidence_locator(
                form_id="FORM-1", related_field_id="FIELD-2", uri="crop/a.png"
            ),
        ),
        EvidenceIdentity(
            "ab" * 32,
            canonical_evidence_locator(
                form_id="FORM-1", related_field_id="FIELD-1", uri="crop/b.png"
            ),
        ),
    )
    assert all(variant != base for variant in variants)


@pytest.mark.parametrize(
    "uri",
    ("", "/absolute/file", "C:/absolute/file", "a//b", "a/./b", "a/../b", "a/%2e%2e/b"),
)
def test_uri_rejects_absolute_empty_and_traversal_paths(uri: str) -> None:
    with pytest.raises(ValueError):
        canonicalize_storage_uri(uri)
