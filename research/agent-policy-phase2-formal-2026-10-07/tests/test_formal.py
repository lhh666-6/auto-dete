import copy, tempfile, unittest
from pathlib import Path
from phase2.kernel import Host, fixtures, canonical
from phase2.oracle import integrity, utility


class FormalHostTests(unittest.TestCase):
    def case(self, scenario):
        case = copy.deepcopy(fixtures()[0])
        case.update(scenario=scenario, baseline_version=4,
            external_note_after_advance='verified external memo',
            evidence_snapshots={'E1': {'bytes': 'source 211 first', 'locator': 'row/1'},
                                'E2': {'bytes': 'source 211 changed evidence', 'locator': 'appendix/2'}})
        return case

    def propose(self, h, evidence='E1'):
        state = h.call('get_state', {'record_id': h.case['record_id']})
        return h.call('propose', {'record_id': h.case['record_id'], 'field_key': h.case['field_key'],
            'proposal_value': h.case['source_proposal_value'], 'evidence_ref': evidence,
            'parent_certificate_id': state['root_certificate_id']})

    def commit(self, h, c, g, key):
        return h.call('commit', {'candidate_id': c['candidate_id'], 'authorization_id': g['authorization_id'],
            'committed_value': g['authorized_value'], 'idempotency_key': key})

    def test_rendered_history_depth_and_evidence_are_real(self):
        h = Host(self.case('L'))
        self.assertEqual(h.state['head']['version'], 4)
        self.assertEqual(h.state['evidence']['E1']['bytes'], 'source 211 first')
        self.assertEqual(integrity(h.state)['I'], 1)

    def test_e_same_value_changed_context_rejects_both_old_grants(self):
        for policy in ['context', 'bound']:
            h = Host(self.case('E'), policy)
            c = self.propose(h); g = h.call('request_authorization', {'candidate_id': c['candidate_id']})
            h.publish_evidence()
            self.assertEqual(self.commit(h,c,g,'superseded')['error_code'],'EVIDENCE_SUPERSEDED')
            c2 = self.propose(h, 'E2')
            result = self.commit(h, c2, g, 'old')
            self.assertEqual(result['error_code'], 'CONTEXT_MISMATCH')
            self.assertTrue(result['decision']['same_value'])
            self.assertFalse(result['decision']['same_context'])
            g2 = h.call('request_authorization', {'candidate_id': c2['candidate_id']})
            self.assertEqual(self.commit(h, c2, g2, 'fresh')['status'], 'ok')
            self.assertEqual(integrity(h.state)['I'], 1)

    def test_v_advance_refresh_recovery_preserves_external_note(self):
        for policy in ['context', 'bound']:
            h = Host(self.case('V'), policy)
            c=self.propose(h); g=h.call('request_authorization', {'candidate_id': c['candidate_id']})
            h.advance(h.case['external_note_after_advance'])
            self.assertEqual(self.commit(h,c,g,'stale')['error_code'], 'STALE_VERSION')
            c2=self.propose(h); g2=h.call('request_authorization', {'candidate_id': c2['candidate_id']})
            self.commit(h,c2,g2,'fresh')
            report={'record_id': h.case['record_id'], 'version': h.state['head']['version'], 'value': g2['authorized_value']}
            self.assertTrue(utility(h.state,report)['task_completion'])
            self.assertEqual(integrity(h.state)['I'], 1)

    def test_r_unavailable_receipt_idempotent_retry_and_semantic_replay(self):
        for policy in ['context', 'bound']:
            h=Host(self.case('R'),policy); c=self.propose(h)
            g=h.call('request_authorization', {'candidate_id':c['candidate_id']})
            r=self.commit(h,c,g,'one')
            self.assertEqual(h.call('get_receipt', {'commit_request_id':r['commit_request_id']})['error_code'], 'CAPABILITY_UNAVAILABLE')
            self.assertEqual(self.commit(h,c,g,'one'), r)
            self.assertEqual(self.commit(h,c,g,'new')['error_code'], 'AUTHORIZATION_INVALID')
            self.assertEqual(len(h.state['transitions']), 1)
            self.assertEqual(h.call('get_state', {'record_id':h.case['record_id']})['status'],'ok')


class GenerationTests(unittest.TestCase):
    def test_128_tasks_non_cosmetic_diversity_balanced_orders_and_hashes(self):
        from phase2.generator import generate_tasks, generate_assignments
        from collections import Counter
        tasks=generate_tasks()
        self.assertEqual(Counter(t['scenario'] for t in tasks), dict(L=32,N=32,G=16,E=16,V=16,R=16))
        self.assertEqual(tasks, generate_tasks())
        vectors=[canonical(t['parameters']) for t in tasks]
        self.assertEqual(len(set(vectors)),128)
        for dimension in tasks[0]['parameters']:
            self.assertGreater(len({canonical(t['parameters'][dimension]) for t in tasks}),1,dimension)
        pairs=generate_assignments(tasks)
        self.assertEqual(len(pairs),256)
        for scenario,count in Counter(t['scenario'] for t in tasks).items():
            for config in ['A','B']:
                block=[p for p in pairs if p['scenario']==scenario and p['config_id']==config]
                self.assertEqual(sum(p['order'][0]=='bound' for p in block),count//2)


class FormalRunnerTests(unittest.TestCase):
    def test_e_v_r_real_logged_workflow_and_feedback(self):
        from phase2.generator import generate_tasks
        from phase2.preflight import DeterministicAgent
        from phase2.runner import execute_pair, validate_run
        for scenario in ['E','V','R']:
            case=next(t for t in generate_tasks() if t['scenario']==scenario)
            with tempfile.TemporaryDirectory() as directory:
                result=execute_pair(case,DeterministicAgent(),Path(directory),['bound','context'])
                for policy in ['bound','context']:
                    self.assertEqual(result[policy]['I'],1,(scenario,policy,result[policy]))
                    self.assertTrue(result[policy]['task_completion'],(scenario,policy))
                    self.assertEqual(validate_run(Path(directory)/policy)['errors'],[])
                    self.assertEqual(validate_run(Path(directory)/policy)['violations'],[])
                    self.assertTrue(result[policy]['episodes'],scenario)


class TaxonomyTests(unittest.TestCase):
    def test_table2_missing_evidence_stays_unknown_and_violation_dominates(self):
        from phase2.export import trivalent_and
        self.assertIsNone(trivalent_and([True,None]))
        self.assertFalse(trivalent_and([False,None]))

    def test_e_independent_oracle_catches_superseded_evidence_mutant(self):
        from phase2.generator import generate_tasks
        case=next(c for c in generate_tasks() if c['scenario']=='E')
        h=Host(case,'context')
        helper=FormalHostTests();c=helper.propose(h);g=h.call('request_authorization',{'candidate_id':c['candidate_id']})
        h.publish_evidence()
        h.valid=lambda candidate:None  # Deliberate host bug; oracle must independently detect it.
        helper.commit(h,c,g,'mutant')
        self.assertEqual(integrity(h.state)['I'],0)
        self.assertIn('transition-1:current_evidence',integrity(h.state)['violations'])

    def test_export_actual_workflows_not_only_empty_planned_rows(self):
        import json,csv
        from phase2.generator import generate_tasks
        from phase2.export import export_tables
        from phase2.runner import execute_pair
        from phase2.preflight import DeterministicAgent
        cases=[next(t for t in generate_tasks() if t['scenario']==s) for s in ['N','G','E','V','R']]
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);f=root/'freeze';f.mkdir();pairs=[]
            for case in cases:
                for config in ['A','B']:
                    pair_id=case['task_instance_id']+'-'+config
                    pairs.append({'case_id':case['task_instance_id'],'scenario':case['scenario'],'config_id':config,'pair_id':pair_id,'order':['context','bound']})
                    execute_pair(case,DeterministicAgent(),root/'results'/pair_id,['context','bound'])
            (f/'assignment-manifest.json').write_text(json.dumps({'pairs':pairs}))
            result=export_tables(f,root/'results',root/'analysis',bootstrap_iterations=20)
            self.assertEqual(result['planned_arms'],20)
            with (root/'analysis/table3-recovery.csv').open(encoding='utf-8-sig') as stream:
                episodes=list(csv.DictReader(stream))
            self.assertTrue(any(e['recovery_strategy']=='successful-confirmation-via-state' for e in episodes))
            self.assertEqual(result['failure_arms'],2)

    def test_hallucinated_success_requires_known_contradiction(self):
        from phase2.trajectories import classify_terminal
        self.assertNotIn('hallucinated-success',classify_terminal({'I':'unknown','task_completion':False,'state_goal':False},None,'agent_final'))
        self.assertIn('hallucinated-success',classify_terminal({'I':1,'task_completion':False,'state_goal':False}, {'status':'success'},'agent_final'))
        self.assertNotIn('hallucinated-success',classify_terminal({'I':1,'task_completion':False,'state_goal':False,'accurate_report':True}, {'record_id':'r','version':1,'value':7},'agent_final'))

    def test_failure_in_planned_denominator_and_task_cluster_effect(self):
        from phase2.analysis import paired_estimates
        rows=[{'task_instance_id':'a','scenario':'L','config_id':c,'policy':p,'task_completion':p=='context','continuity_failure_incidence':None}
              for c in ['A','B'] for p in ['context','bound']]
        result=paired_estimates(rows,iterations=20)
        self.assertEqual(result['planned_arms'],4)
        self.assertEqual(result['completion']['estimate'],-1)
        self.assertEqual(result['continuity']['unknown_arms'],4)

    def test_full_512_planned_ledger_exports_four_tables_without_dropping_missing(self):
        import json,csv
        from phase2.generator import generate_tasks,generate_assignments
        from phase2.export import export_tables
        with tempfile.TemporaryDirectory() as d:
            root=Path(d);f=root/'freeze';f.mkdir()
            pairs=generate_assignments(generate_tasks())
            (f/'assignment-manifest.json').write_text(json.dumps({'pairs':pairs}))
            result=export_tables(f,root/'no_collected_arms',root/'analysis',bootstrap_iterations=20)
            self.assertEqual(result['planned_arms'],512)
            self.assertEqual(result['paired_units'],256)
            self.assertEqual(result['failure_arms'],512)
            self.assertFalse(result['formal_inference_allowed'])
            self.assertEqual(len(result['unique_shared_prefix_accounting']),256)
            with (root/'analysis/table1-outcomes.csv').open(encoding='utf-8-sig') as stream:
                rows=list(csv.DictReader(stream))
            self.assertEqual(sum(int(r['planned']) for r in rows),512)
            self.assertEqual(sum(int(r['unknown']) for r in rows),512)
            for name in ['table2-continuity.csv','table3-recovery.csv','table4-utility-friction.csv','paired-effects.csv']:
                self.assertTrue((root/'analysis'/name).is_file())

    def test_global_stop_prevents_next_other_lane_decision(self):
        import threading
        from phase2.orchestrator import IdentityProvider
        from phase2.providers import TransportError
        from unittest.mock import patch
        stop=threading.Event();p=IdentityProvider({'id':'B','actual_returned_identifier':'old'},stop)
        with patch('phase2.providers.Provider.decide',return_value={'model':'new'}):
            with self.assertRaises(TransportError): p.decide([],Path('unused'))
        self.assertTrue(stop.is_set())
        with patch('phase2.providers.Provider.decide',side_effect=AssertionError('must stop before request')):
            with self.assertRaises(TransportError) as found: p.decide([],Path('unused'))
        self.assertEqual(found.exception.code,'COLLECTION_PAUSED')


class ResumeTests(unittest.TestCase):
    def test_completed_pair_resume_does_not_call_provider_again(self):
        from phase2.preflight import DeterministicAgent
        from phase2.runner import execute_pair
        case=fixtures()[0]
        class Forbidden(DeterministicAgent):
            def decide(self,*args,**kwargs): raise AssertionError('completed pair must not resample')
        with tempfile.TemporaryDirectory() as d:
            original=execute_pair(case,DeterministicAgent(),Path(d),['context','bound'])
            resumed=execute_pair(case,Forbidden(),Path(d),['context','bound'],resume=True)
            self.assertEqual(original,resumed)

    def test_between_decisions_resume_has_same_history_and_budget(self):
        from phase2.preflight import DeterministicAgent
        from phase2.runner import loop,Log
        from phase2.runner import initial_messages
        class Interrupted(DeterministicAgent):
            def decide(self,messages,*args,**kwargs):
                if len(messages)>1: raise KeyboardInterrupt('simulated process stop')
                return super().decide(messages,*args,**kwargs)
        with tempfile.TemporaryDirectory() as d:
            case=fixtures()[0]; host=Host(case); path=Path(d)/'prefix'
            log=Log(path,case,DeterministicAgent.config,'pre_policy')
            ref=log.snapshot(host,'initial'); log.event('initialization',{'state_ref':ref})
            with self.assertRaises(KeyboardInterrupt): loop(host,Interrupted(),initial_messages(case),log,prefix=True)
            resumed=Log(path,case,DeterministicAgent.config,'pre_policy',resume=True)
            outcome=loop(host,DeterministicAgent(),[],resumed,prefix=True)
            self.assertEqual(outcome['terminal'],'checkpoint')
            self.assertEqual(outcome['tools'],2)

    def test_concurrency_budget_config_and_explicit_start_gate(self):
        from phase2.orchestrator import validate_start
        with self.assertRaises(ValueError): validate_start({'status':'NO'},'yes',2)
        with self.assertRaises(ValueError): validate_start({'status':'YES','workers':2},'yes',3)

    def test_provider_returned_identity_change_stops_without_semantic_execution(self):
        from unittest.mock import patch
        from phase2.orchestrator import IdentityProvider
        from phase2.providers import Provider,TransportError
        provider=IdentityProvider({'id':'B','actual_returned_identifier':'frozen-alias'})
        with patch.object(Provider,'decide',return_value={'model':'changed-alias'}):
            with self.assertRaises(TransportError) as caught: provider.decide([],Path('unused'))
        self.assertEqual(caught.exception.code,'DEPLOYMENT_CHANGED')

    def test_interrupt_during_semantic_action_is_not_reexecuted(self):
        from phase2.preflight import DeterministicAgent
        from phase2.runner import loop,Log,initial_messages,record_tool
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            case=fixtures()[0]; host=Host(case); path=Path(d)/'prefix'
            log=Log(path,case,DeterministicAgent.config,'pre_policy')
            ref=log.snapshot(host,'initial'); log.event('initialization',{'state_ref':ref})
            def interrupted(*args,**kwargs):
                record_tool(*args,**kwargs)
                raise KeyboardInterrupt('crash after action before boundary')
            with patch('phase2.runner.record_tool',side_effect=interrupted):
                with self.assertRaises(KeyboardInterrupt): loop(host,DeterministicAgent(),initial_messages(case),log,prefix=True)
            resumed=Log(path,case,DeterministicAgent.config,'pre_policy',resume=True)
            outcome=loop(host,DeterministicAgent(),[],resumed,prefix=True)
            self.assertEqual(outcome['error'],'INTERRUPTED_SEMANTIC_STEP')
            self.assertEqual(host.state['candidate_counter'],1)

    def test_resume_without_boundary_never_samples_empty_history(self):
        from phase2.preflight import DeterministicAgent
        from phase2.runner import loop,Log
        class Forbidden(DeterministicAgent):
            def decide(self,*args,**kwargs): raise AssertionError('no boundary, no sampling')
        with tempfile.TemporaryDirectory() as d:
            case=fixtures()[0]; h=Host(case); path=Path(d)/'arm'
            log=Log(path,case,DeterministicAgent.config,'pre_policy')
            ref=log.snapshot(h,'initial');log.event('initialization',{'state_ref':ref})
            resumed=Log(path,case,DeterministicAgent.config,'pre_policy',resume=True)
            outcome=loop(h,Forbidden(),[],resumed)
            self.assertEqual(outcome['error'],'RESUME_BOUNDARY_MISSING')

    def test_deployment_change_in_prefix_has_no_suffix_model_calls(self):
        from phase2.preflight import DeterministicAgent
        from phase2.providers import TransportError
        from phase2.runner import execute_pair
        class Drift(DeterministicAgent):
            def __init__(self): self.calls=0
            def decide(self,*args,**kwargs): self.calls+=1;raise TransportError('DEPLOYMENT_CHANGED')
        with tempfile.TemporaryDirectory() as d:
            p=Drift();result=execute_pair(fixtures()[0],p,Path(d),['context','bound'])
            self.assertTrue(result['deployment_changed'])
            self.assertEqual(p.calls,1)

    def test_prefix_resume_preserves_already_persisted_authorization(self):
        from phase2.preflight import DeterministicAgent
        from phase2.runner import execute_pair,record_tool
        from unittest.mock import patch
        with tempfile.TemporaryDirectory() as d:
            case=fixtures()[0]
            def interrupted(log,host,tool,*args,**kwargs):
                out=record_tool(log,host,tool,*args,**kwargs)
                if tool=='request_authorization': raise KeyboardInterrupt('after durable grant')
                return out
            with patch('phase2.runner.record_tool',side_effect=interrupted):
                with self.assertRaises(KeyboardInterrupt): execute_pair(case,DeterministicAgent(),Path(d),['bound','context'])
            self.assertEqual(len(Host.load(Path(d)/'prefix/state.sqlite','bound').state['grants']),1)
            execute_pair(case,DeterministicAgent(),Path(d),['bound','context'],resume=True)
            self.assertEqual(len(Host.load(Path(d)/'prefix/state.sqlite','bound').state['grants']),1)


if __name__ == '__main__': unittest.main()
