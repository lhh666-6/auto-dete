"""Construct application services from runtime settings."""

from dataclasses import dataclass

from sqlalchemy import create_engine

from app.adapters.ai.disabled import DisabledAIReview
from app.adapters.database.authority_facades import (
    AuthorityReadFacade,
    CandidateWriteFacade,
    FactAdmissionFacade,
)
from app.adapters.database.models import Base
from app.adapters.database.repositories import (
    SqlAlchemyFormRepository,
    install_sqlite_pragmas,
    stamp_schema_version,
)
from app.adapters.export.xlsx import XlsxExporter
from app.adapters.recognition.opencv import OpenCvImagePipeline
from app.adapters.storage.local import LocalEvidenceStorage
from app.adapters.vector.local import LocalVectorIndex
from app.application.ai_review_forms import AIReviewForms
from app.application.export_forms import ExportForms
from app.application.import_forms import ImportForms
from app.application.query_forms import QueryForms
from app.application.recognize_forms import RecognizeForms
from app.application.review_forms import ReviewForms
from app.domain.principal import prototype_principal_policy
from config.settings import Settings


@dataclass(frozen=True, slots=True)
class Services:
    settings: Settings
    repository: SqlAlchemyFormRepository
    imports: ImportForms
    reviews: ReviewForms
    queries: QueryForms
    exports: ExportForms
    recognition: RecognizeForms
    ai_reviews: AIReviewForms
    vector_index: LocalVectorIndex


def build_services(settings: Settings) -> Services:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    engine = create_engine(f"sqlite:///{settings.database_path}")
    install_sqlite_pragmas(engine)
    Base.metadata.create_all(engine)
    stamp_schema_version(engine)
    principal_policy = prototype_principal_policy(settings.authority_fact_admission_principals)
    repository = SqlAlchemyFormRepository(engine, principal_policy=principal_policy)
    authority_read = AuthorityReadFacade(repository)
    candidate_writer = CandidateWriteFacade(repository)
    fact_admission = FactAdmissionFacade(repository)
    storage = LocalEvidenceStorage(settings.evidence_root)
    queries = QueryForms(repository)
    pipeline = OpenCvImagePipeline()
    return Services(
        settings=settings,
        repository=repository,
        imports=ImportForms(repository, repository, repository, storage),
        reviews=ReviewForms(
            repository,
            repository,
            authority_read=authority_read,
            admission=fact_admission,
            known_producers=frozenset(settings.authority_known_producers),
            known_selection_artifacts=frozenset(settings.authority_selection_artifacts),
        ),
        queries=queries,
        exports=ExportForms(repository, XlsxExporter(), queries),
        recognition=RecognizeForms(
            repository,
            repository,
            repository,
            storage,
            pipeline,
            candidate_writer=candidate_writer,
        ),
        ai_reviews=AIReviewForms(repository, repository, DisabledAIReview()),
        vector_index=LocalVectorIndex(),
    )
