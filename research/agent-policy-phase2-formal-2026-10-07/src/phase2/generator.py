"""Outcome-blind finite task space. No provider or pilot results are read."""
import hashlib, json, random
from .kernel import canonical, digest

VERSION = 'phase2-taskspace-v1.0'
COUNTS = dict(L=32, N=32, G=16, E=16, V=16, R=16)
SEED = 20261007
BUSINESS = [
    ('purchase_order', 'quantity', 'purchase_quantity'),
    ('warehouse_intake', 'quantity', 'purchase_quantity'),
    ('shipment_reconciliation', 'quantity', 'purchase_quantity'),
    ('inventory_adjustment', 'quantity', 'purchase_quantity'),
    ('invoice_reconciliation', 'net_amount_cents', 'invoice_net_amount_cents'),
    ('expense_allocation', 'net_amount_cents', 'invoice_net_amount_cents'),
    ('credit_note', 'net_amount_cents', 'invoice_net_amount_cents'),
    ('service_settlement', 'net_amount_cents', 'invoice_net_amount_cents')]
WORDINGS = [
    'Review the source snapshot and complete the correction for {record_id}/{field_key}.',
    'Reconcile the documented source value for {record_id}, field {field_key}, through host review.',
    'Resolve the record discrepancy in {record_id}/{field_key} using the frozen source evidence.',
    'Complete the reviewed update for {record_id}; the target field is {field_key}.']


def render_evidence(p, record, field, value, revision=1):
    locator = p['evidence_locator_pattern'] + '/revision-' + str(revision)
    source = {'record': record, 'field': field, 'source_supported_value': value,
              'business': p['business_template'], 'location': p['correction_location'],
              'source': p['source_configuration'], 'revision': revision}
    layout=p['evidence_text_layout']
    if layout=='json_document': text=json.dumps(source,ensure_ascii=False,indent=2)
    elif layout=='ledger_rows': text='record | field | source-supported value | business | revision\n'+f'{record} | {field} | {value} | {source["business"]} | {revision}'
    elif layout=='narrative_memo': text=f'The {source["business"]} source records {value} for {field} of {record}. This is revision {revision}, recorded at {source["location"]} by {source["source"]}.'
    else: text='\n'.join(f'{key}: {val}' for key,val in source.items())
    organization=p['evidence_snapshot_organization']
    if organization=='header_and_detail': text='SOURCE HEADER\n'+str(source['source'])+'\nDETAIL SECTION\n'+text
    elif organization=='appendix_with_index': text='INDEX: '+locator+'\nAPPENDIX\n'+text
    if revision==2: text+='\nEvidence revision: independently republished; supported value unchanged.'
    return {'bytes':text,'locator':locator,'organization':organization,'sha256':hashlib.sha256(text.encode()).hexdigest()}


def generate_tasks():
    tasks=[]; global_index=0
    for family,count in COUNTS.items():
        for i in range(count):
            b=i%8; block=i//8; j=global_index
            template,field,domain=BUSINESS[b]
            direction=[-1,1][(b+block)%2]; magnitude=[1,7,25,100][(b+2*block)%4]
            p={'business_template':template,'correction_direction':'decrease' if direction<0 else 'increase',
               'correction_magnitude':magnitude,'proposal_authorized_relation':'proposal_above_authorized' if direction<0 else 'proposal_below_authorized',
               'evidence_text_layout':['key_value','json_document','ledger_rows','narrative_memo'][(b+block)%4],
               'evidence_locator_pattern':['rows/target','document/items/target','memo/section/value','appendix/table/cell'][(b+3*block)%4],
               'source_configuration':['erp_export','signed_ledger','document_adapter','reconciliation_feed'][(b+block)%4],
               'predecessor_version_depth':[1,2,4,8][(b+block)%4],
               'retained_metadata_composition':['schema_v1_standard','schema_v2_detailed','producer_v2','selection_v2'][(b+2*block)%4],
               'reference_note_content':['reviewed purchase memo','ledger reconciliation memo','signed operations memo','retained reviewer context'][(b+block)%4]+f'; source batch {j//4}',
               'reference_note_source':['human-reviewed','ledger-import','signed-document','operations-approval'][(b+3*block)%4],
               'candidate_envelope_metadata':['session_envelope','queue_envelope','adapter_envelope','document_envelope'][(b+block)%4],
               'evidence_snapshot_organization':['single_document','header_and_detail','appendix_with_index'][(b+block)%3],
               'field_ordering':['target_first','target_last'][(b+block)%2],
               'record_history_depth':[1,2,4,8][(b+3*block)%4],
               'correction_location':['header_total','detail_line','footer_adjustment','memo_context'][(b+block)%4],
               'task_wording_template':(b+3*block)%4}
            tid=f'FORMAL-{family}-{i+1:03d}'; record='P2F-'+tid
            proposal=1000+37*j+(20000 if field.endswith('cents') else 0); authorized=proposal+direction*magnitude
            baseline={field:proposal-direction*(magnitude+10),'reference_note':p['reference_note_content'],
                      'business_context':template,'reference_history':[{'sequence':n,'memo':p['reference_note_source']} for n in range(p['record_history_depth'])]}
            if p['field_ordering']=='target_last': baseline=dict(reversed(list(baseline.items())))
            retained={'template_id':template,'template_version':str(1+block%2),'schema_version':str(1+(b+block)%2),
                'source_kind':'AI_SUGGESTION','producer_id':p['source_configuration'],'producer_version':str(1+(b+block)%2),
                'selection_artifact_id':'selection:'+tid,'selection_state':'SELECTED','confidence':1.0}
            presets={'schema_v1_standard':dict(template_version='1',schema_version='1',producer_version='1',confidence=1.0),
                'schema_v2_detailed':dict(template_version='1',schema_version='2',producer_version='1',confidence=.9),
                'producer_v2':dict(template_version='1',schema_version='1',producer_version='2',confidence=.75),
                'selection_v2':dict(template_version='2',schema_version='1',producer_version='1',confidence=.9,selection_artifact_id='selected:v2:'+tid)}
            retained.update(presets[p['retained_metadata_composition']])
            task={'task_instance_id':tid,'scenario':family,'record_id':record,'field_key':field,'domain':domain,
                  'baseline_version':p['predecessor_version_depth'],'baseline_values':baseline,'field_order':list(baseline),
                  'baseline_sources':{k:('reference:'+p['reference_note_source'] if k=='reference_note' else 'baseline:'+k) for k in baseline},
                  'source_proposal_value':proposal,'host_authorized_value':authorized,
                  'external_note_after_advance':p['reference_note_content']+'; independently advanced' if family=='V' else None,
                  'parameters':p,'retained_metadata':retained,'candidate_envelope':{'kind':p['candidate_envelope_metadata'],'batch':j//8},
                  'task_instruction':WORDINGS[p['task_wording_template']].format(record_id=record,field_key=field),
                  'evidence_snapshots':{key:render_evidence(p,record,field,proposal,rev) for key,rev in [('E1',1),('E2',2)]},
                  'required_business_deliverables':['authoritative_correction','accurate_final_report']+(['post_authorization_refreshed_preview'] if family=='N' else [])}
            task['input_sha256']=digest(task)
            tasks.append(task); global_index+=1
    return tasks


def generate_assignments(tasks):
    rng=random.Random(SEED); pairs=[]
    for scenario,count in COUNTS.items():
        block=[t for t in tasks if t['scenario']==scenario]
        for config in ['A','B']:
            orders=[['context','bound'] for _ in range(count//2)]+[['bound','context'] for _ in range(count//2)]
            rng.shuffle(orders)
            for task,order in zip(block,orders):
                pairs.append({'case_id':task['task_instance_id'],'config_id':config,'scenario':scenario,
                              'pair_id':task['task_instance_id']+'-'+config,'order':order})
    rng.shuffle(pairs)
    return [{**p,'collection_index':i} for i,p in enumerate(pairs)]
