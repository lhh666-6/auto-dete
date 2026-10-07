import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('recovery', HERE / 'run_recovery.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class RecoveryTests(unittest.TestCase):
    def make_pair(self, root, name, quota=True, responded=False, config='A'):
        prefix = root / name / 'prefix'
        raw = prefix / 'provider-raw/0-0'
        raw.mkdir(parents=True)
        message = 'You have hit your usage limit' if quota else 'Network unavailable'
        (raw / 'stdout.jsonl').write_text(json.dumps({'type':'error','message':message}), encoding='utf-8')
        events = [{'event_type':'model_response'}] if responded else [{'event_type':'model_error'}]
        (prefix / 'events.jsonl').write_text('\n'.join(map(json.dumps, events)), encoding='utf-8')
        return {'status':'terminal','assignment':{'config_id':config},'result':{'checkpoint_reached':False}}

    def test_only_quota_failures_before_any_agent_response_are_eligible(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            pairs = {n:self.make_pair(root, n, **kw) for n,kw in [
                ('quota',{}),('network',{'quota':False}),
                ('responded',{'responded':True}),('other',{'config':'B'})]}
            self.assertEqual(module.eligible_pairs(root, {'pairs':pairs}), ['quota'])

    def test_recovery_preserves_old_bytes_and_skips_its_own_terminal_pairs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            original = root/'original'; original.mkdir()
            (original/'state.json').write_bytes(b'original immutable result')
            protected = module.hash_tree(original)
            calls = []
            def execute(case, provider, destination, order, resume=False):
                calls.append(case['task_instance_id'])
                destination.mkdir(parents=True, exist_ok=True)
                result = {'prefix':{'terminal':'checkpoint'},'deployment_changed':False,
                          'context':{'task_completion':True,'I':1},'bound':{'task_completion':True,'I':1}}
                (destination/'pair-result.json').write_text(json.dumps(result),encoding='utf-8')
                return result
            manifest = {'freeze_id':'test-recovery','pairs':[{'pair_id':'T-A','case_id':'T','order':['bound','context']}],
                        'tasks':{'T':{'task_instance_id':'T'}},'agent_config':{'id':'A'}}
            output = root/'recovery'
            module.collect(manifest, output, execute=execute, provider=object())
            module.collect(manifest, output, execute=execute, provider=object())
            self.assertEqual(calls, ['T'])
            self.assertEqual(module.hash_tree(original), protected)

    def test_quota_pauses_without_marking_pair_complete_and_preserves_attempt(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls=[]
            def execute(case, provider, destination, order, resume=False):
                calls.append(case['task_instance_id']); destination.mkdir(parents=True,exist_ok=True)
                return {'prefix':{'error':'ACCOUNT_QUOTA_EXHAUSTED'},'deployment_changed':False}
            manifest = {'freeze_id':'test-recovery','pairs':[{'pair_id':n+'-A','case_id':n,'order':['context','bound']} for n in ['T','U']],
                        'tasks':{n:{'task_instance_id':n} for n in ['T','U']},'agent_config':{'id':'A'}}
            out=Path(tmp)/'results'
            state=module.collect(manifest,out,execute=execute,provider=object())
            self.assertEqual(state['status'],'PAUSED_QUOTA')
            self.assertEqual(calls,['T'])
            self.assertEqual(state['pairs']['T-A']['status'],'waiting_for_quota')
            self.assertTrue((out/'T-A/attempt-001').exists())

    def test_quota_detection_does_not_treat_other_errors_as_quota(self):
        self.assertTrue(module.is_quota_text("You've hit your usage limit"))
        self.assertFalse(module.is_quota_text('HTTP 503 service unavailable'))

    def test_quota_resume_keeps_first_attempt_and_uses_a_new_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            calls=[]
            def execute(case, provider, destination, order, resume=False):
                destination.mkdir(parents=True,exist_ok=True)
                (destination/'raw.txt').write_text('preserve-'+destination.name,encoding='utf-8')
                calls.append(destination.name)
                if len(calls)==1: return {'prefix':{'error':'ACCOUNT_QUOTA_EXHAUSTED'}}
                return {'prefix':{'terminal':'checkpoint'},'context':{'I':1},'bound':{'I':1}}
            manifest={'freeze_id':'q','pairs':[{'pair_id':'T-A','case_id':'T','order':['context','bound']}],
                      'tasks':{'T':{'task_instance_id':'T'}},'agent_config':{'id':'A'}}
            output=Path(tmp)/'results'
            module.collect(manifest,output,execute=execute,provider=object())
            first=module.hash_tree(output/'T-A/attempt-001')
            state=module.collect(manifest,output,execute=execute,provider=object())
            self.assertEqual(calls,['attempt-001','attempt-002'])
            self.assertEqual(first,module.hash_tree(output/'T-A/attempt-001'))
            self.assertEqual(state['status'],'COMPLETE')

    def test_second_coordinator_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            lock=module.lock_output(Path(tmp))
            try:
                with self.assertRaises(OSError): module.lock_output(Path(tmp))
            finally: lock.close()


if __name__ == '__main__': unittest.main()
