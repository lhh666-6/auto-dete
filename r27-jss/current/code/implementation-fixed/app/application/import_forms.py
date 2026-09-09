"""Form image and conditional audio import use cases."""

from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.adapters.storage.local import LocalEvidenceStorage
from app.application.ports import AuditRepository, EvidenceRepository, FormRepository
from app.domain.models import AuditEvent, EvidenceFile, EvidenceType, Form


class DuplicateEvidenceError(ValueError):
    pass


class InvalidAudioBindingError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class AudioTrigger:
    exception_code: str | None = None
    exception_note: str = ""
    correction_type: str | None = None
    dispute_flag: bool = False

    def permits_audio(self) -> bool:
        return (
            self.exception_code == "E99"
            or bool(self.exception_note.strip())
            or self.correction_type == "UNUSUAL"
            or self.dispute_flag
        )


class ImportForms:
    def __init__(
        self,
        forms: FormRepository,
        evidence: EvidenceRepository,
        audits: AuditRepository,
        storage: LocalEvidenceStorage,
    ) -> None:
        self._forms = forms
        self._evidence = evidence
        self._audits = audits
        self._storage = storage

    def import_image(
        self,
        source: Path,
        form_id: str,
        template_id: str,
        template_version: str,
        actor_id: str,
    ) -> EvidenceFile:
        digest = self._storage.hash_path(source)
        if self._evidence.find_by_sha256(digest) is not None:
            raise DuplicateEvidenceError(f"Evidence already imported: {digest}")
        if self._forms.get_form(form_id) is not None:
            raise DuplicateEvidenceError(f"Form already imported: {form_id}")
        stored = self._storage.store_path(source, "images")
        item = EvidenceFile(
            file_id=stored.file_id,
            form_id=form_id,
            type=EvidenceType.ORIGINAL_IMAGE,
            uri=stored.uri,
            sha256=stored.sha256,
        )
        self._forms.add_form(Form(form_id, template_id, template_version))
        self._evidence.add_evidence(item)
        self._audits.add_audit_event(
            AuditEvent(
                event_id=f"EVENT-{uuid4().hex}",
                form_id=form_id,
                event_type="IMPORT",
                actor_id=actor_id,
                after={"file_id": item.file_id, "sha256": item.sha256},
                evidence_ids=(item.file_id,),
            )
        )
        return item

    def import_audio(
        self,
        source: Path,
        form_id: str,
        actor_id: str,
        trigger: AudioTrigger,
        related_field_id: str | None = None,
    ) -> EvidenceFile:
        if not trigger.permits_audio():
            raise InvalidAudioBindingError(
                "Audio requires E99, a note, unusual correction, or dispute"
            )
        if self._forms.get_form(form_id) is None:
            raise KeyError(f"Unknown form: {form_id}")
        digest = self._storage.hash_path(source)
        if self._evidence.find_by_sha256(digest) is not None:
            raise DuplicateEvidenceError(f"Evidence already imported: {digest}")
        stored = self._storage.store_path(source, "audio")
        item = EvidenceFile(
            file_id=stored.file_id,
            form_id=form_id,
            related_field_id=related_field_id,
            type=EvidenceType.AUDIO,
            uri=stored.uri,
            sha256=stored.sha256,
        )
        self._evidence.add_evidence(item)
        self._audits.add_audit_event(
            AuditEvent(
                event_id=f"EVENT-{uuid4().hex}",
                form_id=form_id,
                event_type="AUDIO_IMPORT",
                actor_id=actor_id,
                after={"file_id": item.file_id},
                evidence_ids=(item.file_id,),
            )
        )
        return item
