import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from datetime import datetime, timezone

spec=importlib.util.spec_from_file_location('monitor',Path(__file__).with_name('monitor.py'))
monitor=importlib.util.module_from_spec(spec)
spec.loader.exec_module(monitor)


class MonitorTests(unittest.TestCase):
    def fixture(self, root, status='RUNNING'):
        (root/'results').mkdir()
        (root/'recovery-manifest.json').write_text(json.dumps({'planned_pairs':3,'planned_arms':6}),encoding='utf-8')
        pairs={'T-A':{'status':'terminal','attempts':[{'started_utc':'2026-10-07T01:00:00+00:00',
            'finished_utc':'2026-10-07T01:02:00+00:00','directory':'T-A/attempt-001',
            'result':{'context':{'task_completion':False,'I':1,'terminal':'runtime_error'},
                      'bound':{'task_completion':True,'I':1,'terminal':'agent_final'}}}]} }
        (root/'results/collection-status.json').write_text(json.dumps({'status':status,'pairs':pairs}),encoding='utf-8')

    def test_terminal_pair_does_not_mean_two_successful_arms(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.fixture(root)
            s=monitor.snapshot(root)
            self.assertEqual(s['terminal_pairs'],1)
            self.assertEqual(s['successful_arms'],1)
            self.assertEqual(s['runtime_failure_arms'],1)
            self.assertEqual(s['remaining_pairs'],2)

    def test_paused_batch_has_no_wall_clock_finish_promise(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.fixture(root,'PAUSED_QUOTA')
            s=monitor.snapshot(root)
            self.assertEqual(s['remaining_run_seconds'],240)
            self.assertIsNone(s['estimated_finish_shanghai'])

    def test_live_append_with_incomplete_last_line_keeps_valid_events(self):
        with tempfile.TemporaryDirectory() as tmp:
            p=Path(tmp)/'events.jsonl'
            p.write_text('{"event_type":"model_response"}\n{"event_type":',encoding='utf-8')
            events=monitor.read_events(p)
            self.assertEqual(len(events),1)
            self.assertEqual(events[0]['event_type'],'model_response')

    def test_resume_launch_takes_precedence_over_original_pid(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); self.fixture(root)
            for filename,pid,hour in [('collection-launch.json',11,'01'),('resume-test.launch.json',22,'02')]:
                (root/filename).write_text(json.dumps({'pid':pid,'started_utc':f'2026-10-07T{hour}:00:00+00:00'}),encoding='utf-8')
            s=monitor.snapshot(root,process_check=lambda launch:launch['pid']==22)
            self.assertEqual(s['pid'],22)
            self.assertTrue(s['process_alive'])


if __name__=='__main__': unittest.main()
