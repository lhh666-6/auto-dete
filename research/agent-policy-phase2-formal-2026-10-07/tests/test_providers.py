import tempfile, unittest, io
from pathlib import Path
from unittest.mock import patch
from phase2.providers import Provider, TransportError

class FakeResponse(io.BytesIO):
    pass

class ProviderTests(unittest.TestCase):
    def test_mid_response_network_read_interrupts_are_retryable(self):
        import http.client
        class BrokenResponse(FakeResponse):
            def read(self,*args,**kwargs): raise http.client.IncompleteRead(b'partial',100)
        p=Provider({'id':'B','provider':'deepseek','model':'x'})
        with tempfile.TemporaryDirectory() as d, patch.dict('os.environ',{'ANTHROPIC_AUTH_TOKEN':'test-token','ANTHROPIC_BASE_URL':'https://example.invalid'}), patch('urllib.request.urlopen',return_value=BrokenResponse()):
            with self.assertRaises(TransportError) as found: p.decide([],Path(d)/'request')
            self.assertTrue(found.exception.retryable)
            self.assertEqual((Path(d)/'request/partial-response.bin').read_bytes(),b'partial')
    def test_malformed_http200_is_finalizable_transport_error(self):
        p = Provider({'id': 'B', 'provider': 'deepseek', 'model': 'x'})
        with tempfile.TemporaryDirectory() as d, patch.dict('os.environ', {'ANTHROPIC_AUTH_TOKEN': 'test-token', 'ANTHROPIC_BASE_URL': 'https://example.invalid'}), patch('urllib.request.urlopen', return_value=FakeResponse(b'not-json')):
            with self.assertRaises(TransportError) as found:
                p.decide([], Path(d) / 'request')
            self.assertEqual(found.exception.code, 'PROVIDER_MALFORMED_ENVELOPE')
