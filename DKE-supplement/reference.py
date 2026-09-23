"""Adapter to the unmodified published implementation, not a reimplementation."""
from __future__ import annotations

import copy
import json
import sqlite3
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path

from common import canonical, digest
from sqlalchemy import create_engine, event
from app.adapters.database.models import Base
from app.adapters.database.migrations import migrate_schema
from app.adapters.database.repositories import SqlAlchemyFormRepository, install_sqlite_pragmas
from app.application.review_forms import ReviewForms
from app.application.query_forms import QueryForms
from app.domain.authority import CandidateCertificate, SourceKind, SelectionState
from app.domain.evidence_identity import canonical_evidence_locator
from app.domain.models import Form, FormField, EvidenceFile, EvidenceType
from app.domain.principal import prototype_principal_policy


def packet(field, value, version, nonce, *, evidence='archived-replay', now=None):
    now = now or datetime.now(timezone.utc)
    evidence_id = 'E-' + digest([field, evidence])[:24]
    locator = canonical_evidence_locator(form_id='FORM-1', related_field_id='FIELD-'+field,
                                        uri='evidence/'+evidence_id+'.json')
    cert = CandidateCertificate.from_value(candidate_id=nonce, field_key=field, value=value,
        evidence_hash=digest(evidence), evidence_locator=locator, template_id='T1',
        template_version='1', source_kind=SourceKind.RECOGNITION,
        producer_id='archived-output-replay', producer_version='dke-replay-v1',
        selection_artifact_id='recognition-threshold-v1', confidence=0.0,
        selection_state=SelectionState.SELECTED, lineage_parent_ids=(),
        target_record_id='FORM-1', expected_fact_version=version, created_at=now)
    p = {'id': cert.certificate_id, 'candidate_id': nonce, 'field': field,
         'proposed': value, 'expected_version': version, 'record_id': 'FORM-1',
         'evidence_id': evidence_id, 'evidence_hash': cert.evidence_hash,
         'evidence_locator': locator, 'producer': cert.producer_id,
         'producer_version': cert.producer_version, 'created_at': now.isoformat()}
    return p


def certificate(p):
    return CandidateCertificate.from_value(candidate_id=p['candidate_id'], field_key=p['field'],
        value=p['proposed'], evidence_hash=p['evidence_hash'], evidence_locator=p['evidence_locator'],
        template_id='T1', template_version='1', source_kind=SourceKind.RECOGNITION,
        producer_id=p['producer'], producer_version=p['producer_version'],
        selection_artifact_id='recognition-threshold-v1', confidence=0.0,
        selection_state=SelectionState.SELECTED, lineage_parent_ids=(),
        target_record_id=p['record_id'], expected_fact_version=p['expected_version'],
        created_at=datetime.fromisoformat(p['created_at']))


class Capture:
    def append_fact_transition(self, **kwargs):
        self.bundle = copy.deepcopy(kwargs)
        return True


class Reference:
    def __init__(self, path, fields):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.engine = create_engine('sqlite:///'+self.path.as_posix())
        install_sqlite_pragmas(self.engine)
        @event.listens_for(self.engine, 'connect')
        def pragmas(connection, record):
            connection.execute('PRAGMA synchronous=FULL')
        Base.metadata.create_all(self.engine)
        migrate_schema(self.engine)
        self.repo = SqlAlchemyFormRepository(self.engine,
            principal_policy=prototype_principal_policy(('reviewer', 'reviewer-2')))
        self.repo.add_form(Form(form_id='FORM-1', template_id='T1', template_version='1'))
        for f in fields:
            self.repo.add_form_field(FormField('FIELD-'+f, 'FORM-1', f, {}))
        self.packets = {}

    def service(self, admission=None):
        return ReviewForms(self.repo, self.repo, authority_read=self.repo,
            admission=self.repo if admission is None else admission,
            known_producers=frozenset({('archived-output-replay', 'dke-replay-v1')}),
            known_selection_artifacts=frozenset({'recognition-threshold-v1'}))

    def add(self, p):
        c = certificate(p)
        assert c.certificate_id == p['id']
        if self.repo.get_evidence(p['evidence_id']) is None:
            locator = json.loads(p['evidence_locator'])
            self.repo.add_evidence(EvidenceFile(p['evidence_id'], 'FORM-1', EvidenceType.AI_OUTPUT,
                locator['uri'], p['evidence_hash'], 'FIELD-'+p['field']))
        self.repo.add_certificate(c, field_id='FIELD-'+p['field'],
            evidence_file_id=p['evidence_id'], recognition_attempt_id=None)
        self.packets[p['id']] = p

    def confirm(self, version, values, ids, actor='reviewer'):
        return self.service().confirm('FORM-1', version, {f: values[f] for f in ids}, actor, 'scripted review',
            certificate_ids_by_field=ids, manual_evidence_ids_by_field={})

    def prepare(self, version, values, ids, actor='reviewer'):
        capture = Capture()
        self.service(capture).confirm('FORM-1', version, {f: values[f] for f in ids}, actor, 'scripted review',
            certificate_ids_by_field=ids, manual_evidence_ids_by_field={})
        return capture.bundle

    def admit(self, approval, ids, values=None, failpoint=None):
        bundle = copy.deepcopy(approval)
        # Deliberately change the candidate USED by admission while preserving the
        # independently recorded authorization. This tests the transactional boundary.
        ts = []
        for t in bundle['transitions']:
            if t.field_key in ids:
                p = self.packets[ids[t.field_key]]
                t = replace(t, certificate_id=p['id'], evidence_sha256=p['evidence_hash'],
                    evidence_locator=p['evidence_locator'], producer_id=p['producer'],
                    producer_version=p['producer_version'])
            if values is not None and t.field_key in values:
                t = replace(t, value_payload=canonical(values[t.field_key]))
            ts.append(t)
        bundle['transitions'] = ts
        if values is not None:
            bundle['record'].values.update(values)
        def fail(name):
            if name == failpoint:
                raise RuntimeError('INJECTED:'+name)
        self.repo._admission_failpoint = fail if failpoint else None
        try:
            ok = self.repo.append_fact_transition(**bundle)
            if not ok:
                raise ValueError('STALE_OR_CONFLICT')
        finally:
            self.repo._admission_failpoint = None

    def query(self):
        # Fresh sqlite3 reads; no QueryForms trace, planner, or ORM result is used.
        with sqlite3.connect(self.path) as con:
            con.row_factory = sqlite3.Row
            vr = con.execute('SELECT * FROM record_versions WHERE form_id=? ORDER BY version DESC LIMIT 1', ('FORM-1',)).fetchone()
            if vr is None:
                return {}
            values, sources = json.loads(vr['values']), json.loads(vr['fact_sources'])
            out = {}
            for f, tid in sources.items():
                r = con.execute('''SELECT t.created_version, t.value_payload, c.value_payload proposal,
                    c.certificate_id, d.reviewer_id, b.authorized_value_payload
                    FROM fact_transitions t JOIN candidate_certificates c ON c.certificate_id=t.certificate_id
                    JOIN human_decisions d ON d.decision_id=t.decision_id
                    JOIN authorization_bindings b ON b.decision_id=d.decision_id
                    WHERE t.transition_id=?''', (tid,)).fetchone()
                out[f] = {'proposal': json.loads(r['proposal']),
                    'authorized': json.loads(r['authorized_value_payload']), 'reviewer': r['reviewer_id'],
                    'reviewed_candidates': [r['certificate_id']], 'committed': values[f],
                    'source_version': r['created_version']}
            return out

    def close(self):
        self.engine.dispose()
