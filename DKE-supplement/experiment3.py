"""Current-source sequential cost measurements with retained raw observations."""
from __future__ import annotations
import argparse
import importlib.util
import json
import random
import shutil
import sqlite3
import statistics
import time
from pathlib import Path
from common import ROOT, REPO, IMPL, canonical, environment, sha, summarize, write_json
from reference import Reference, packet
from journal import Journal
from sqlalchemy import create_engine, event, select
from app.adapters.database.models import Base, CandidateCertificateRow, FactTransitionRow
from app.adapters.database.repositories import SqlAlchemyFormRepository, install_sqlite_pragmas
from app.application.query_forms import QueryForms
from app.domain.principal import prototype_principal_policy
from benchmarks import authority_cost as cost

SPEC=importlib.util.spec_from_file_location('published_materialization',REPO/'r21-jss/source/performance-experiment/benchmarks/r21_feature_baseline.py')
material=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(material)

CONFIG={'seed':20260923,'warmups':5,'trials':200,'admission_fields':[1,8,32,128],
        'admission_changed':[1,4,'all'],'trace_fields':[1,8,32,128],
        'trace_versions':[1,10,100],'trace_records':[1,100,1000],
        'storage_transitions':[1000,10000,100000]}

def append(path,row):
    with path.open('a',encoding='utf-8') as f:f.write(json.dumps(row,default=str)+'\n')

def paired(rows,keys,arms):
    result=[];rng=random.Random(CONFIG['seed'])
    for key in sorted({tuple(r[k] for k in keys) for r in rows}):
        rs=[r for r in rows if tuple(r[k] for k in keys)==key]
        groups={a:sorted([r for r in rs if r['arm']==a],key=lambda r:r['pair']) for a in arms}
        a,b=([r['latency_ns']/1e6 for r in groups[arm]] for arm in arms)
        deltas=[x-y for x,y in zip(a,b,strict=True)]
        draws=sorted(statistics.fmean(rng.choices(deltas,k=len(deltas))) for _ in range(2000))
        result.append(dict(zip(keys,key))|{'arms':arms,'pairs':len(deltas),
            'mean_paired_delta_ms':statistics.fmean(deltas),'bootstrap_95ci_ms':[draws[49],draws[1949]],
            'p50_ratio_first_over_second':statistics.median(a)/statistics.median(b)})
    return result

def load_reference(path,packets):
    obj=Reference.__new__(Reference);obj.path=path;obj.packets=packets
    obj.engine=create_engine('sqlite:///'+path.as_posix());install_sqlite_pragmas(obj.engine)
    @event.listens_for(obj.engine,'connect')
    def settings(con,record):con.execute('PRAGMA synchronous=FULL')
    obj.repo=SqlAlchemyFormRepository(obj.engine,principal_policy=prototype_principal_policy(('reviewer','reviewer-2')))
    return obj

def load_journal(path,fields):
    obj=Journal.__new__(Journal);obj.path=path;obj.exact=True;obj.fields=set(fields)
    obj.con=sqlite3.connect(path,isolation_level=None);obj.con.row_factory=sqlite3.Row
    obj.con.executescript('PRAGMA foreign_keys=ON; PRAGMA synchronous=FULL; PRAGMA busy_timeout=5000;')
    return obj

def mechanism(config,out):
    out.mkdir();rng=random.Random(config['seed']);rows=[];cells=material._cells(config);rng.shuffle(cells)
    for fields,changed in cells:
        cell=out/f'{fields}-{changed}';cell.mkdir()
        initial={f'f{i:03d}':0 for i in range(fields)}
        values={f'f{i:03d}':1 for i in range(changed)}
        seeds=[packet(f,v,0,'seed-'+f,evidence='cost initial '+f) for f,v in initial.items()]
        changes=[packet(f,v,1,'review-'+f,evidence='cost update '+f) for f,v in values.items()]
        packets={p['id']:p for p in seeds+changes};ids={p['field']:p['id'] for p in changes}
        templates={}
        for arm in ['journal_exact','reference']:
            path=cell/(arm+'-template.db');s=Reference(path,initial) if arm=='reference' else Journal(path,initial,True)
            for p in packets.values():s.add(p)
            s.confirm(0,initial,{p['field']:p['id'] for p in seeds});s.close();templates[arm]=path
        for trial in range(config['warmups']+config['trials']):
            arms=['journal_exact','reference'];rng.shuffle(arms);answers={}
            for arm in arms:
                path=cell/(arm+'-working.db');shutil.copy2(templates[arm],path)
                s=load_reference(path,packets) if arm=='reference' else load_journal(path,initial)
                count=[0]
                def countsql(*args):count[0]+=1
                if arm=='reference':event.listen(s.engine,'before_cursor_execute',countsql)
                else:s.con.set_trace_callback(countsql)
                start=time.perf_counter_ns();s.confirm(1,values,ids);elapsed=time.perf_counter_ns()-start
                if arm=='reference':event.remove(s.engine,'before_cursor_execute',countsql)
                else:s.con.set_trace_callback(None)
                answers[arm]=s.query()
                for f,q in answers[arm].items():
                    assert canonical(q['committed'])==canonical(values.get(f,0))
                    assert q['source_version']==(2 if f in values else 1)
                with sqlite3.connect(path) as con:assert not con.execute('PRAGMA foreign_key_check').fetchall()
                s.close()
                if trial>=config['warmups']:
                    row={'fields':fields,'changed':changed,'pair':trial-config['warmups'],'arm':arm,'order':arms,
                         'latency_ns':elapsed,'sql_statements':count[0]}
                    rows.append(row);append(out/'raw.jsonl',row)
            assert canonical(answers['journal_exact'])==canonical(answers['reference'])
        print('E3 complete-mechanism cell',fields,changed,'complete',flush=True)
    write_json(out/'summary.json',summarize(rows,['fields','changed','arm']))
    write_json(out/'paired.json',paired(rows,['fields','changed'],['reference','journal_exact']))
    return {'cells':len(cells),'observations':len(rows),'query_equality_verified_every_pair':True,
            'sql_count_note':'SQLAlchemy counts cursor executions; sqlite3 trace also reports trigger activity. Cross-arm counts are not normalized.'}

def ablation(config,out):
    out.mkdir();rng=random.Random(config['seed']);rows=[];cells=material._cells(config);rng.shuffle(cells)
    for fields,changed in cells:
        cell=out/f'{fields}-{changed}';cell.mkdir();engine,eid=cost._seed_form(cell/'template',fields)
        cost._checkpoint(engine);engine.dispose();template=cell/'template/data.db'
        reference=cell/'reference.db';shutil.copy2(template,reference);cost._full_admission(reference,fields,changed,eid)
        delta=material.build_database_delta(template,reference);write_json(cell/'delta.json',delta)
        for trial in range(config['warmups']+config['trials']):
            arms=['full','materialization'];rng.shuffle(arms)
            for arm in arms:
                path=cell/(arm+'-working.db');shutil.copy2(template,path)
                result=cost._full_admission(path,fields,changed,eid) if arm=='full' else material.apply_database_delta(path,delta)
                if trial>=config['warmups']:
                    row={'fields':fields,'changed':changed,'pair':trial-config['warmups'],'arm':arm,'order':arms,**result}
                    rows.append(row);append(out/'raw.jsonl',row)
        print('E3 prevalidated-materialization cell',fields,changed,'complete',flush=True)
    write_json(out/'summary.json',summarize(rows,['fields','changed','arm']))
    write_json(out/'paired.json',paired(rows,['fields','changed'],['full','materialization']))
    return {'cells':len(cells),'observations':len(rows),'materialization_poststate_verified_every_trial':True,
            'interpretation':'Persistence ablation with precomputed valid database delta; NOT an alternative complete admission mechanism.'}


class PointLookupRepository:
    """Same verifier; three bulk reads become ID enumeration + actual point loads.

    This is a new controlled access-pattern ablation, not the historical verifier.
    Other repository operations delegate unchanged; no duplicate dummy SQL.
    """
    def __init__(self,repo):self.repo=repo;self.engine=repo._engine
    def __getattr__(self,name):return getattr(self.repo,name)
    def certificate_ids(self,form_id):
        with self.engine.connect() as con:
            return list(con.scalars(select(CandidateCertificateRow.certificate_id).where(CandidateCertificateRow.form_id==form_id).order_by(CandidateCertificateRow.created_at,CandidateCertificateRow.certificate_id)))
    def list_certificates_for_form(self,form_id):
        return [self.repo.get_certificate(cid) for cid in self.certificate_ids(form_id)]
    def list_certificate_evidence_bindings_for_form(self,form_id):
        return {cid:self.repo.get_certificate_evidence_file_id(cid) for cid in self.certificate_ids(form_id)}
    def list_transitions_for_form(self,form_id):
        with self.engine.connect() as con:
            ids=list(con.scalars(select(FactTransitionRow.transition_id).where(FactTransitionRow.form_id==form_id).order_by(FactTransitionRow.created_version,FactTransitionRow.field_key,FactTransitionRow.transition_id)))
        return [self.repo.get_fact_transition(tid) for tid in ids]

def seed_distractors(root,counts):
    """Seed valid unrelated forms once; backup snapshots outside timed regions."""
    root.mkdir();snapshots={}
    engine=cost._engine(root/'data.db');Base.metadata.create_all(engine);cost.migrate_schema(engine)
    repo=SqlAlchemyFormRepository(engine,principal_policy=prototype_principal_policy(('reviewer',)))
    review=cost._review_service(repo)
    for index in range(max(counts)):
        if index:
            fid=f'OTHER-{index}';image=root/(fid+'.png');image.write_bytes(f'distractor:{fid}'.encode())
            e=cost.ImportForms(repo,repo,repo,cost.LocalEvidenceStorage(root/'evidence')).import_image(image,fid,'T1','1','benchmark')
            repo.add_form_field(cost.FormField(fid+'-FIELD-0',fid,'f000',{}))
            review.confirm(fid,0,{'f000':index},'reviewer','trace distractor',certificate_ids_by_field={'f000':None},manual_evidence_ids_by_field={'f000':e.file_id})
        if index+1 in counts:
            path=root/f'background-{index+1}.db'
            with sqlite3.connect(root/'data.db') as src,sqlite3.connect(path) as dest:src.backup(dest)
            snapshots[index+1]=path
        if index and index%100==0:print('E3 background forms seeded:',index,flush=True)
    engine.dispose();return snapshots

def trace(config,out):
    out.mkdir();rng=random.Random(config['seed']);rows=[]
    snapshots=seed_distractors(out/'background',config['trace_records'])
    cells=[(f,v,r) for f in config['trace_fields'] for v in config['trace_versions'] for r in config['trace_records']];rng.shuffle(cells)
    for fields,versions,records in cells:
        cell=out/f'{fields}-{versions}-{records}';cell.mkdir();shutil.copy2(snapshots[records],cell/'data.db')
        engine,eid=cost._seed_form(cell,fields)
        repo=SqlAlchemyFormRepository(engine,principal_policy=prototype_principal_policy(('reviewer',)))
        review=cost._review_service(repo);values={f'f{i:03d}':0 for i in range(fields)}
        for version in range(2,versions+1):
            values['f000']=version
            review.confirm('FORM-1',version-1,values,'reviewer','trace history',certificate_ids_by_field={f:None for f in values},manual_evidence_ids_by_field={f:eid for f in values})
        queries={'batch':QueryForms(repo),'point_lookup':QueryForms(PointLookupRepository(repo))}
        expected=queries['batch'].trace('FORM-1');assert expected.status=='complete'
        with engine.connect() as con:assert con.exec_driver_sql('SELECT count(*) FROM forms').scalar()==records
        for trial in range(config['warmups']+config['trials']):
            arms=['batch','point_lookup'];rng.shuffle(arms)
            for arm in arms:
                captured=[]
                def action():captured.append(queries[arm].trace('FORM-1'))
                elapsed,sql=cost._measure(engine,action)
                assert captured[0]==expected,'Complete trace object changed'
                if trial>=config['warmups']:
                    row={'fields':fields,'versions':versions,'records':records,'pair':trial-config['warmups'],
                         'arm':arm,'order':arms,'latency_ns':elapsed,'sql_statements':sql}
                    rows.append(row);append(out/'raw.jsonl',row)
        cost._checkpoint(engine);engine.dispose()
        print('E3 trace cell',fields,versions,records,'complete',flush=True)
    write_json(out/'summary.json',summarize(rows,['fields','versions','records','arm']))
    write_json(out/'paired.json',paired(rows,['fields','versions','records'],['point_lookup','batch']))
    return {'cells':len(cells),'observations':len(rows),'full_trace_equality_verified_every_trial':True,
            'background_setup':'Shared valid distractor snapshots; original per-cell cardinality/history grid preserved; setup excluded from timing.'}

def run(output,section,pilot):
    output.mkdir(parents=True,exist_ok=True)
    config=dict(CONFIG)
    if pilot:config.update(warmups=1,trials=3,admission_fields=[1,8],trace_fields=[1,8],trace_versions=[1,3],trace_records=[1,3],storage_transitions=[10,100])
    write_json(output/'config.json',config)
    manifest={str(p.relative_to(ROOT)):sha(p) for p in ROOT.glob('*.py')}
    manifest.update({str(p.relative_to(REPO)):sha(p) for p in (IMPL/'app').rglob('*.py')})
    write_json(output/('pre-run-manifest-'+section+'.json'),manifest)
    write_json(output/'environment.json',environment()|{'durability':'Admission: SQLite DELETE journal, synchronous FULL (default or explicit). Storage fixture: WAL/NORMAL, checkpointed; not timing evidence.','source_root':str(IMPL)})
    sections=['mechanism','ablation','trace','storage'] if section=='all' else [section]
    receipts={}
    for name in sections:
        start=time.time()
        if name=='storage':
            root=output/'storage';root.mkdir();data=cost._storage_experiment(config,root);write_json(root/'raw.json',data)
            result={'cells':len(data['observations']),'scope':'Synthetic schema footprint; direct population, not validated real transitions or equal-function competitor.'}
        else:result=globals()[name](config,output/name)
        result.update(status='complete',elapsed_seconds=time.time()-start);receipts[name]=result
        write_json(output/(name+'-receipt.json'),result)
        print('E3 SECTION COMPLETE',name,result,flush=True)
    return receipts

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);p.add_argument('--section',choices=['all','mechanism','ablation','trace','storage'],default='all');p.add_argument('--pilot',action='store_true');a=p.parse_args();run(a.output,a.section,a.pilot)
