"""Synthetic raw provider envelopes for audit tests, never online evidence."""
import hashlib,json,tempfile,unittest
from pathlib import Path
from phase2.kernel import canonical,digest,fixtures
from phase2.providers import OUTPUT_RULE
from phase2.preflight import DeterministicAgent
from phase2.runner import execute_pair,validate_run

class RawFixture(DeterministicAgent):
    config={'id':'B','provider':'synthetic_audit_fixture','model':'SYNTHETIC_NOT_ONLINE'}
    def decide(self,messages,directory,timeout=90):
        result=super().decide(messages,directory,timeout)
        action=result['action']
        text=canonical({'kind':action['kind'],'tool':action.get('tool',''),
            'arguments_json':canonical(action.get('arguments',{})),'report_json':canonical(action.get('report',{}))})
        directory.mkdir(parents=True,exist_ok=False)
        (directory/'prompt.txt').write_text(OUTPUT_RULE+'\nVISIBLE CONVERSATION:\n'+canonical(messages),encoding='utf-8')
        envelope={'id':'synthetic-fixture','model':'SYNTHETIC_NOT_ONLINE','usage':{},
            'content':[{'type':'text','text':text}],'engineering_fixture':True}
        (directory/'response.json').write_text(canonical(envelope),encoding='utf-8')
        return {'raw_action':text,'usage':{},'model':envelope['model'],'provider_request_id':envelope['id']}

class ProvenanceTests(unittest.TestCase):
    def test_tool_and_final_report_require_raw_provider_provenance(self):
        with tempfile.TemporaryDirectory() as d:
            directory=Path(d)
            execute_pair(fixtures()[0],RawFixture(),directory,['context','bound'])
            self.assertEqual(validate_run(directory/'bound')['errors'],[])
            arm=directory/'bound';report=arm/'agent-final-report.json'
            report.write_text(canonical({'record_id':'fabricated','version':2,'value':212}),encoding='utf-8')
            file=arm/'events.jsonl';events=[json.loads(line) for line in file.read_text(encoding='utf-8').splitlines()]
            ref=events[-1]['payload']['agent_report_ref'];ref['sha256']=hashlib.sha256(report.read_bytes()).hexdigest()
            events[-1]['event_hash']=digest({k:v for k,v in events[-1].items() if k!='event_hash'})
            file.write_text('\n'.join(canonical(e) for e in events)+'\n',encoding='utf-8')
            self.assertIn('final_report_not_grounded_in_provider',validate_run(arm)['errors'])

if __name__=='__main__':unittest.main()
