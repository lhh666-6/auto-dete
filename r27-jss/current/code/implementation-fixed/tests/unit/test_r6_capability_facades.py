"""R6: application services receive disjoint runtime capabilities."""

from pathlib import Path

from app.adapters.database.authority_facades import (
    AuthorityReadFacade,
    CandidateWriteFacade,
    FactAdmissionFacade,
)
from app.services.container import build_services
from config.settings import Settings


class _BroadRepositoryProbe:
    def append_candidate_unit(self, **kwargs):
        return ("candidate", kwargs)

    def append_candidate_certificate(self, **kwargs):
        return ("ai-candidate", kwargs)

    def append_fact_transition(self, **kwargs):
        return ("fact", kwargs)

    def add_transition(self, *args, **kwargs):
        return (args, kwargs)

    def add_decision(self, *args, **kwargs):
        return (args, kwargs)

    def get_certificate(self, certificate_id: str):
        return certificate_id

    def get_certificate_evidence_file_id(self, certificate_id: str):
        return certificate_id

    def get_evidence(self, file_id: str):
        return file_id


def test_runtime_facades_have_disjoint_public_write_surfaces() -> None:
    broad = _BroadRepositoryProbe()
    candidates = CandidateWriteFacade(broad)
    reads = AuthorityReadFacade(broad)
    admissions = FactAdmissionFacade(broad)

    assert callable(candidates.append_candidate_unit)
    assert callable(candidates.append_candidate_certificate)
    assert not hasattr(candidates, "append_fact_transition")
    assert not hasattr(candidates, "add_transition")
    assert not hasattr(candidates, "add_decision")

    assert reads.get_certificate("CERT-1") == "CERT-1"
    assert not hasattr(reads, "append_candidate_unit")
    assert not hasattr(reads, "append_candidate_certificate")
    assert not hasattr(reads, "append_fact_transition")

    assert callable(admissions.append_fact_transition)
    assert not hasattr(admissions, "append_candidate_unit")
    assert not hasattr(admissions, "append_candidate_certificate")
    assert not hasattr(admissions, "add_transition")
    assert not hasattr(admissions, "add_decision")


def test_production_container_keeps_candidate_and_fact_capabilities_apart(
    tmp_path: Path,
) -> None:
    services = build_services(Settings(data_root=tmp_path / "data"))

    assert not hasattr(services.recognition._candidate_writer, "append_fact_transition")
    assert not hasattr(services.recognition._candidate_writer, "add_transition")
    assert not hasattr(services.recognition, "_admission")
    assert hasattr(services.reviews._admission, "append_fact_transition")
    assert not hasattr(services.reviews._admission, "append_candidate_unit")
