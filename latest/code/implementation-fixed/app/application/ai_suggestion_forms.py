"""Candidate-only AI suggestion use case for external harness integrations."""

from __future__ import annotations

import math
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from uuid import uuid4

from app.application.ports import (
    AuthorityReadPort,
    CandidateWritePort,
    FormRepository,
    ImmutableObjectStorage,
)
from app.domain.authority import (
    CandidateCertificate,
    SelectionState,
    SourceKind,
    canonical_json,
)
from app.domain.evidence_identity import locator_from_evidence
from app.domain.models import AuditEvent, EvidenceFile, EvidenceType, utc_now


@dataclass(frozen=True, slots=True)
class AISuggestionResult:
    candidate_id: str
    certificate_id: str
    evidence_file_id: str
    evidence_uri: str
    expected_fact_version: int


class AISuggestionForms:
    """Persist a parent-linked AI output without a fact-admission capability."""

    def __init__(
        self,
        *,
        forms: FormRepository,
        authority: AuthorityReadPort,
        candidate_writer: CandidateWritePort,
        storage: ImmutableObjectStorage,
        clock: Callable[[], datetime] = utc_now,
    ) -> None:
        self._forms = forms
        self._authority = authority
        self._candidate_writer = candidate_writer
        self._storage = storage
        self._clock = clock

    def propose(
        self,
        *,
        form_id: str,
        field_id: str,
        parent_certificate_id: str,
        value: Any,
        confidence: float,
        producer_id: str,
        producer_version: str,
        selection_artifact_id: str,
        session_id: str,
        execution_id: str,
    ) -> AISuggestionResult:
        form = self._forms.get_form(form_id)
        if form is None:
            raise ValueError(f"unknown form: {form_id}")
        field = self._forms.get_form_field(field_id)
        if field is None:
            raise ValueError(f"unknown field: {field_id}")
        if field.form_id != form_id:
            raise ValueError(f"field {field_id} does not belong to form {form_id}")

        parent = self._authority.get_certificate(parent_certificate_id)
        if parent is None:
            raise ValueError(f"unknown parent certificate: {parent_certificate_id}")
        if not parent.verify_content_address():
            raise ValueError("parent certificate content address is invalid")
        if parent.target_record_id != form_id or parent.field_key != field.field_name:
            raise ValueError("parent certificate does not match the requested form and field")
        if parent.expected_fact_version != form.current_record_version:
            raise ValueError("parent certificate is stale for the current fact version")
        parent_evidence_id = self._authority.get_certificate_evidence_file_id(
            parent_certificate_id
        )
        parent_evidence = (
            self._authority.get_evidence(parent_evidence_id) if parent_evidence_id else None
        )
        if parent_evidence is None or parent_evidence.sha256 != parent.evidence_hash:
            raise ValueError("parent evidence binding is missing or invalid")

        if not producer_id or not producer_version or not selection_artifact_id:
            raise ValueError("producer and selection artifact identities must be non-empty")
        if not session_id or not execution_id:
            raise ValueError("DSH session and execution identities must be non-empty")
        if not isinstance(confidence, (int, float)) or not math.isfinite(confidence):
            raise ValueError("confidence must be finite")
        if confidence < 0.0 or confidence > 1.0:
            raise ValueError("confidence must be between 0 and 1")

        created_at = self._clock()
        candidate_id = f"AI-{uuid4().hex}"
        payload = {
            "schema_version": "auto-decte.ai-output.v1",
            "form_id": form_id,
            "field_id": field_id,
            "field_key": field.field_name,
            "candidate_id": candidate_id,
            "value": value,
            "confidence": confidence,
            "parent_certificate_id": parent_certificate_id,
            "producer_id": producer_id,
            "producer_version": producer_version,
            "selection_artifact_id": selection_artifact_id,
            "session_id": session_id,
            "execution_id": execution_id,
            "expected_fact_version": form.current_record_version,
            "created_at": created_at.isoformat(),
        }
        stored = self._storage.store_bytes(
            canonical_json(payload).encode("utf-8"), ".json", "ai-outputs"
        )
        evidence = EvidenceFile(
            file_id=stored.file_id,
            form_id=form_id,
            type=EvidenceType.AI_OUTPUT,
            uri=stored.uri,
            sha256=stored.sha256,
            related_field_id=field_id,
            created_at=created_at,
        )
        certificate = CandidateCertificate.from_value(
            candidate_id=candidate_id,
            field_key=field.field_name,
            value=value,
            evidence_hash=stored.sha256,
            evidence_locator=locator_from_evidence(evidence),
            template_id=form.template_id,
            template_version=form.template_version,
            source_kind=SourceKind.AI_SUGGESTION,
            producer_id=producer_id,
            producer_version=producer_version,
            selection_artifact_id=selection_artifact_id,
            confidence=float(confidence),
            selection_state=SelectionState.SELECTED,
            lineage_parent_ids=(parent_certificate_id,),
            target_record_id=form_id,
            expected_fact_version=form.current_record_version,
            created_at=created_at,
        )
        audit = AuditEvent(
            event_id=f"EVENT-{uuid4().hex}",
            form_id=form_id,
            event_type="AI_SUGGESTION_PROPOSED",
            actor_id=producer_id,
            after={
                "candidate_id": candidate_id,
                "certificate_id": certificate.certificate_id,
                "parent_certificate_id": parent_certificate_id,
                "selection_artifact_id": selection_artifact_id,
            },
            evidence_ids=(stored.file_id,),
            timestamp=created_at,
        )
        try:
            self._candidate_writer.append_candidate_certificate(
                evidence=evidence,
                certificate=certificate,
                audit=audit,
                field_id=field_id,
            )
        except Exception:
            self._storage.discard(stored.uri)
            raise

        return AISuggestionResult(
            candidate_id=candidate_id,
            certificate_id=certificate.certificate_id,
            evidence_file_id=stored.file_id,
            evidence_uri=stored.uri,
            expected_fact_version=form.current_record_version,
        )
