import tempfile, unittest, io
from pathlib import Path
from unittest.mock import patch
from phase2.providers import Provider, TransportError

class FakeResponse(io.BytesIO):
    pass

class ProviderTests(unittest.TestCase):
    def test_malformed_http200_is_finalizable_transport_error(self):
        p = Provider({'id': 'B', 'provider': 'deepseek', 'model': 'x'})
        with tempfile.TemporaryDirectory() as d, patch.dict('os.environ', {'ANTHROPIC_AUTH_TOKEN': 'test-token', 'ANTHROPIC_BASE_URL': 'https://example.invalid'}), patch('urllib.request.urlopen', return_value=FakeResponse(b'not-json')):
            with self.assertRaises(TransportError) as found:
                p.decide([], Path(d) / 'request')
            self.assertEqual(found.exception.code, 'PROVIDER_MALFORMED_ENVELOPE')
