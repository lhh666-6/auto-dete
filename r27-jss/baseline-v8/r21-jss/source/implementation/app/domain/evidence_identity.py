"""Canonical persisted evidence identity for the certificate era."""

from __future__ import annotations

import json
import unicodedata
from dataclasses import dataclass
from urllib.parse import quote, unquote

from app.domain.models import EvidenceFile

LOCATOR_VERSION = 1


def canonicalize_storage_uri(uri: str) -> str:
    """Return one portable, storage-relative, normalized URI."""

    normalized = unicodedata.normalize("NFC", uri).replace("\\", "/")
    if not normalized or normalized.startswith("/"):
        raise ValueError("evidence URI must be a non-empty relative path")
    if len(normalized) >= 2 and normalized[1] == ":":
        raise ValueError("evidence URI must not contain a drive prefix")
    segments: list[str] = []
    for raw_segment in normalized.split("/"):
        segment = unicodedata.normalize("NFC", unquote(raw_segment))
        if segment in {"", ".", ".."}:
            raise ValueError("evidence URI contains an empty or traversal segment")
        segments.append(quote(segment, safe="-._~"))
    return "/".join(segments)


def canonical_evidence_locator(
    *,
    form_id: str,
    related_field_id: str | None,
    uri: str,
    crop: str | None = None,
) -> str:
    payload: dict[str, object] = {
        "form_id": unicodedata.normalize("NFC", form_id),
        "related_field_id": (
            unicodedata.normalize("NFC", related_field_id) if related_field_id is not None else None
        ),
        "uri": canonicalize_storage_uri(uri),
        "v": LOCATOR_VERSION,
    }
    if crop is not None:
        payload["crop"] = unicodedata.normalize("NFC", crop)
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def locator_from_evidence(evidence: EvidenceFile) -> str:
    return canonical_evidence_locator(
        form_id=evidence.form_id,
        related_field_id=evidence.related_field_id,
        uri=evidence.uri,
    )


@dataclass(frozen=True, slots=True)
class EvidenceIdentity:
    content_sha256: str
    locator: str

    @classmethod
    def from_evidence(cls, evidence: EvidenceFile) -> EvidenceIdentity:
        return cls(evidence.sha256, locator_from_evidence(evidence))
