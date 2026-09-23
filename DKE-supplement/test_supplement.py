import copy
import json
from pathlib import Path
import pytest
from common import canonical, db_digest
from experiment1 import create_case, expected_query, score_queries
from reference import Reference
from journal import Journal

def test_query_scorer_rejects_same_value_wrong_identity():
    expected={'f':{'reviewed_candidates':['A'],'authorized':2}}
    actual={'f':{'reviewed_candidates':['B'],'authorized':2.0}}
    assert [r['status'] for r in score_queries(actual,expected)]==['wrong','wrong']
    actual['f']['reviewed_candidates']=['A','B']
    assert score_queries(actual,expected)[0]['status']=='ambiguous'

@pytest.mark.parametrize('arm',['journal_context','journal_exact','reference'])
@pytest.mark.parametrize('case',['accept','same_value_substitution','rollback_before_transition'])
def test_contract_controls(tmp_path,arm,case):
    initial,final,seed,reviewed,alternative,packets=create_case({'value':2.0,'initial_quantity':2},case)
    s=Reference(tmp_path/'db',initial) if arm=='reference' else Journal(tmp_path/'db',initial,arm=='journal_exact')
    try:
        for p in packets:s.add(p)
        s.confirm(0,initial,{f:p['id'] for f,p in seed.items()})
        ids={f:p['id'] for f,p in reviewed.items()};approval=s.prepare(1,final,ids)
        used=ids|({'quantity':alternative['id']} if case=='same_value_substitution' else {})
        before=db_digest(s.path)
        reject=case=='rollback_before_transition' or (case=='same_value_substitution' and arm!='journal_context')
        if reject:
            with pytest.raises(Exception):s.admit(approval,used,failpoint='before_transition' if case.startswith('rollback') else None)
            assert before==db_digest(s.path)
        else:
            s.admit(approval,used)
            q=s.query();assert canonical(q['quantity']['committed'])==canonical(final['quantity'])
            if arm=='journal_context':assert len(q['quantity']['reviewed_candidates'])==2
            else:assert q['quantity']['reviewed_candidates']==[ids['quantity']]
    finally:s.close()
