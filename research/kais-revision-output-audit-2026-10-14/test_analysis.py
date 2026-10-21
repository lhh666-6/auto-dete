import json
import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
import analysis
from analysis import classify_response, terminal_diagnostic

ACTION = json.dumps({'kind': 'final', 'report': {'version': 2}})

def response(stop, text):
    return {'stop_reason': stop, 'content': [{'type': 'thinking', 'thinking': 'opaque'}, {'type': 'text', 'text': text}], 'usage': {'output_tokens': 4096}}

def attempt(stop='max_tokens', text='', repair=False, outcome='model_response', seq=1):
    return {**classify_response(response(stop, text)), 'format_repair_visible': repair,
            'outcome_event_type': outcome, 'decision_index': seq, 'request_sequence': seq,
            'response_event_id': str(seq)}

class ClassificationTests(unittest.TestCase):
    def test_truncated_empty(self):
        self.assertEqual(classify_response(response('max_tokens',''))['response_class'], 'max_tokens_empty')
    def test_truncated_partial(self):
        self.assertEqual(classify_response(response('max_tokens','{"kind":'))['response_class'], 'max_tokens_nonparseable_text')
    def test_truncated_parseable(self):
        self.assertEqual(classify_response(response('max_tokens',ACTION))['response_class'], 'max_tokens_parseable')
    def test_equal_tokens_is_not_truncation(self):
        self.assertFalse(classify_response(response('end_turn',ACTION))['truncated'])
    def test_natural_format_error_is_separate(self):
        self.assertEqual(classify_response(response('end_turn','hello'))['response_class'], 'natural_stop_nonparseable')
    def test_envelope_failure_is_separate(self):
        self.assertEqual(classify_response({'error': {'type': 'authentication_error'}})['response_class'], 'malformed_envelope')
    def test_frozen_parser_allows_normalized_action(self):
        self.assertTrue(classify_response(response('end_turn',ACTION))['parseable'])
    def test_frozen_parser_rejects_bad_nested_json(self):
        text = json.dumps({'kind':'tool','tool':'commit','arguments_json':'{','report_json':'{}'})
        self.assertFalse(classify_response(response('end_turn',text))['parseable'])
    def test_terminal_after_format_repair(self):
        self.assertEqual(terminal_diagnostic('invalid_output',[attempt(),attempt(repair=True,seq=2)]), 'invalid_output_after_output_truncation_after_format_repair')
    def test_early_truncation_does_not_overwrite_success(self):
        self.assertEqual(terminal_diagnostic('agent_final',[attempt(),attempt('end_turn',ACTION,True,seq=2)]),'agent_final')
    def test_transport_failure_after_truncation_is_not_truncation_terminal(self):
        self.assertEqual(terminal_diagnostic('runtime_error',[attempt(),attempt(outcome='model_error',seq=2)]),'runtime_error')
    def test_final_natural_format_failure_after_early_truncation(self):
        self.assertEqual(terminal_diagnostic('invalid_output',[attempt(),attempt('end_turn','bad',True,seq=2)]),'invalid_output_other_last_response')
    def test_missing_termination_stays_missing(self):
        self.assertEqual(terminal_diagnostic('termination_missing',[attempt()]),'termination_missing')
    def test_parseable_truncation_is_not_terminal_cause(self):
        self.assertEqual(terminal_diagnostic('invalid_output',[attempt(text=ACTION)]),'invalid_output_unresolved')
    def test_missing_outcome_after_old_response_stays_unresolved(self):
        self.assertEqual(terminal_diagnostic('invalid_output',[attempt(),attempt(outcome='missing_outcome',seq=2)]),'invalid_output_unresolved')
    def test_intervening_action_does_not_make_history_a_consecutive_retry(self):
        rows = [attempt(), attempt('end_turn', ACTION, True, seq=2), attempt(repair=True, seq=3)]
        self.assertEqual(terminal_diagnostic('invalid_output', rows),'invalid_output_after_output_truncation_after_format_repair')
    def test_no_visible_repair_cannot_claim_repair_chain(self):
        self.assertEqual(terminal_diagnostic('invalid_output',[attempt(),attempt(seq=2)]),'invalid_output_after_output_truncation')
    def test_http_error_artifact_is_retained(self):
        with tempfile.TemporaryDirectory(dir=analysis.OUT) as tmp:
            root = Path(tmp)
            raw = root/'FORMAL-G-001-B/context/provider-raw/0-0'
            raw.mkdir(parents=True)
            (raw/'http-error.txt').write_text('authentication failure', encoding='utf-8')
            with patch.object(analysis, 'RAW', root):
                rows, _ = analysis.scan_phase('FORMAL-G-001-B','context',4096,[])
            self.assertIsNotNone(rows[0]['http_error_file'])
            self.assertFalse(rows[0]['truncated'])
    def test_true_partial_transport_bytes_are_not_output_truncation(self):
        with tempfile.TemporaryDirectory(dir=analysis.OUT) as tmp:
            root = Path(tmp)
            raw = root/'FORMAL-G-001-B/context/provider-raw/0-0'
            raw.mkdir(parents=True)
            (raw/'partial-response.bin').write_bytes(b'{incomplete')
            (raw/'transport-error.json').write_text('{"exception_type":"IncompleteRead"}', encoding='utf-8')
            with patch.object(analysis, 'RAW', root):
                rows, _ = analysis.scan_phase('FORMAL-G-001-B','context',4096,[])
            self.assertEqual(rows[0]['partial_response_bytes'],11)
            self.assertEqual(rows[0]['transport_error_detail']['exception_type'],'IncompleteRead')
            self.assertFalse(rows[0]['truncated'])

if __name__ == '__main__':
    unittest.main()
