"""Guardrails for the independent supplementary analysis (synthetic ledgers)."""
import copy
import unittest
from analyze import select_attempts, paired_summary, include_failure, check_identity, terminal_error_code, check_attempt_inventory
from audit_usage import unexpected_actions


def fixture():
    pair = {'pair_id':'T-A','case_id':'T','scenario':'G','config_id':'A','order':['context','bound']}
    manifest = {'freeze_id':'recovery','planned_pairs':1,'planned_arms':2,'pairs':[pair]}
    attempt = {'directory':'T-A/attempt-001','finished_utc':'2026-10-07','result':{'checkpoint_reached':True,'context':{'task_completion':False},'bound':{'task_completion':False}}}
    status = {'freeze_id':'recovery','status':'COMPLETE','terminal_pairs':1,'pairs':{'T-A':{'assignment':pair,'status':'terminal','attempts':[attempt]}}}
    return copy.deepcopy(manifest), copy.deepcopy(status)


class LedgerTests(unittest.TestCase):
    def test_terminal_failure_remains_selected(self):
        m,s=fixture(); self.assertEqual(select_attempts(m,s)[0]['attempt']['result']['bound']['task_completion'],False)
    def test_missing_pair_rejected(self):
        m,s=fixture(); s['pairs']={}
        with self.assertRaisesRegex(ValueError,'PAIR_SET'): select_attempts(m,s)
    def test_nonterminal_rejected(self):
        m,s=fixture(); s['pairs']['T-A']['status']='running'
        with self.assertRaisesRegex(ValueError,'NONTERMINAL'): select_attempts(m,s)
    def test_duplicate_manifest_rejected(self):
        m,s=fixture(); m['pairs']*=2
        with self.assertRaisesRegex(ValueError,'DUPLICATE'): select_attempts(m,s)
    def test_duplicate_attempt_rejected(self):
        m,s=fixture(); s['pairs']['T-A']['attempts']*=2
        with self.assertRaisesRegex(ValueError,'DUPLICATE'): select_attempts(m,s)
    def test_assignment_drift_rejected(self):
        m,s=fixture(); s['pairs']['T-A']['assignment']['order'].reverse()
        with self.assertRaisesRegex(ValueError,'ASSIGNMENT'): select_attempts(m,s)
    def test_unfinished_latest_rejected(self):
        m,s=fixture(); s['pairs']['T-A']['attempts'].append({'directory':'T-A/attempt-002'})
        with self.assertRaisesRegex(ValueError,'UNFINISHED'): select_attempts(m,s)
    def test_freeze_drift_rejected(self):
        m,s=fixture(); s['freeze_id']='other'
        with self.assertRaisesRegex(ValueError,'FREEZE'): select_attempts(m,s)
    def test_event_identity_drift_rejected(self):
        m,s=fixture()
        with self.assertRaisesRegex(ValueError,'IDENTITY'): check_identity([{'freeze_id':'other'}],{'freeze_id':'recovery'},'test')
    def test_failure_and_unknown_retained(self):
        self.assertTrue(include_failure({'task_completion':False,'I':1}))
        self.assertTrue(include_failure({'task_completion':True,'I':0}))
        self.assertTrue(include_failure({'task_completion':True,'I':'unknown'}))
        self.assertFalse(include_failure({'task_completion':True,'I':1}))
    def test_single_a_paired_estimate_no_fabricated_b(self):
        rows=[{'task_instance_id':'T','scenario':'G','policy':p,'task_completion':v} for p,v in [('context',False),('bound',True)]]
        result=paired_summary(rows,'task_completion',iterations=100,seed=1)
        self.assertEqual(result['estimate'],1); self.assertEqual(result['interval'],[1,1])
    def test_missing_arm_rejected(self):
        rows=[{'task_instance_id':'T','scenario':'G','policy':'context','task_completion':False}]
        with self.assertRaisesRegex(ValueError,'MISSING_ARM'): paired_summary(rows,'task_completion',100,1)
    def test_unknown_not_dropped(self):
        rows=[{'task_instance_id':'T','scenario':'G','policy':p,'x':v} for p,v in [('context',None),('bound',0)]]
        self.assertIsNone(paired_summary(rows,'x',100,1)['estimate'])
    def test_nested_runtime_error_code_retained(self):
        self.assertEqual(terminal_error_code({'runtime_error':{'code':'DEPLOYMENT_CHANGED'}}),'DEPLOYMENT_CHANGED')
    def test_native_error_item_is_not_a_tool_action(self):
        self.assertEqual(unexpected_actions([{'type':'item.completed','item':{'type':'error'}}]),[])
        self.assertEqual(unexpected_actions([{'type':'item.completed','item':{'type':'command_execution'}}]),['command_execution'])
    def test_bootstrap_keeps_scenario_weights(self):
        rows=[{'task_instance_id':s,'scenario':s,'policy':p,'task_completion':v} for s,c,b in [('G',False,True),('N',True,True)] for p,v in [('context',c),('bound',b)]]
        result=paired_summary(rows,'task_completion',100,1)
        self.assertEqual(result['estimate'],.5); self.assertEqual(result['interval'],[.5,.5])
    def test_untracked_attempt_directory_rejected(self):
        with self.assertRaisesRegex(ValueError,'ATTEMPT_INVENTORY'): check_attempt_inventory(['T-A/attempt-001'],['T-A/attempt-001','T-A/attempt-002'])
    def test_missing_attempt_directory_rejected(self):
        with self.assertRaisesRegex(ValueError,'ATTEMPT_INVENTORY'): check_attempt_inventory(['T-A/attempt-001'],[])


if __name__=='__main__': unittest.main()
