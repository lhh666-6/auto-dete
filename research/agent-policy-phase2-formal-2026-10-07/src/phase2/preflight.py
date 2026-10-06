"""Scripted fixture decisions only. These are never online model evidence."""
class DeterministicAgent:
    config={'id':'TEST','provider':'deterministic_fixture','model':'NO_ONLINE_MODEL'}
    def action(self,name,**arguments):
        return {'action':{'kind':'tool','tool':name,'arguments':arguments},'usage':None,
                'model':'DETERMINISTIC_NOT_ONLINE','provider_request_id':'fixture'}
    def decide(self,messages,directory,timeout=90):
        task=messages[0]['task']; initial=messages[0]['initial_state']
        results=[m for m in messages if m.get('kind')=='tool_result']
        ok=[m for m in results if m['result']['status']=='ok']
        proposals=[m['result'] for m in ok if m['tool_name']=='propose']
        grants=[m['result'] for m in ok if m['tool_name']=='request_authorization']
        states=[m['result'] for m in ok if m['tool_name']=='get_state']
        notices=[m for m in messages if m.get('kind') in ('evidence_update','external_state_advance')]
        rejects=[m for m in results if m['result']['status']=='rejected']
        root=states[-1]['root_certificate_id'] if states else initial['root_certificate_id']
        evidence='E2' if any(m['kind']=='evidence_update' for m in notices) else 'E1'
        def proposal():
            return self.action('propose',record_id=task['record_id'],field_key=task['field_key'],
                proposal_value=task['source_proposal_value'],evidence_ref=evidence,parent_certificate_id=root)
        if not proposals: return proposal()
        if not grants: return self.action('request_authorization',candidate_id=proposals[-1]['candidate_id'])
        if any(m['kind']=='evidence_update' for m in notices) and not any(c['context']['evidence_file_id']=='E2' for c in proposals):
            if not any(m['tool_name']=='inspect_evidence' for m in ok): return self.action('inspect_evidence',evidence_ref='E2')
            return proposal()
        if notices and rejects:
            if not states: return self.action('get_state',record_id=task['record_id'])
            if evidence=='E2' and not any(m['tool_name']=='inspect_evidence' and m['result'].get('locator') for m in ok):
                return self.action('inspect_evidence',evidence_ref='E2')
            c=proposals[-1]
            if c['context']['expected_fact_version']!=states[-1]['version'] or c['context']['evidence_file_id']!=evidence:
                return proposal()
            if grants[-1]['reviewed_candidate_id']!=c['candidate_id']:
                return self.action('request_authorization',candidate_id=c['candidate_id'])
        if any(m.get('kind')=='business_notice' for m in messages) and len(proposals)<2: return proposal()
        accepted=[m['result'] for m in ok if m['tool_name']=='commit']
        handoff=next((m for m in messages if m.get('kind')=='external_executor_notice'),None)
        if not accepted and not (handoff and handoff['result']['status']=='ok'):
            g=grants[-1]
            return self.action('commit',candidate_id=(proposals[-1]['candidate_id'] if evidence=='E2' else g['reviewed_candidate_id']),authorization_id=g['authorization_id'],
                committed_value=g['authorized_value'],idempotency_key='fixture-'+g['authorization_id'])
        if accepted and not any(m['tool_name']=='get_receipt' for m in results):
            return self.action('get_receipt',commit_request_id=accepted[-1]['commit_request_id'])
        latest_commit_index=max([i for i,m in enumerate(results) if m['tool_name']=='commit' and m['result']['status']=='ok'] or [-1])
        if not states or not any(i>latest_commit_index and m['tool_name']=='get_state' for i,m in enumerate(results)):
            return self.action('get_state',record_id=task['record_id'])
        h=states[-1]
        return {'action':{'kind':'final','report':{'record_id':task['record_id'],'version':h['version'],
            'value':h['values'][task['field_key']]}},'usage':None,'model':'DETERMINISTIC_NOT_ONLINE','provider_request_id':'fixture'}
