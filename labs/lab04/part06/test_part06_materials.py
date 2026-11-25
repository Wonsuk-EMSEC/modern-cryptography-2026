"""Check that the offline certificate files and template metadata are usable."""

import json
from pathlib import Path
import unittest

from cryptography import x509


DATA = Path(__file__).resolve().parent / "data"


class HistoricalMaterialsTests(unittest.TestCase):
    def test_files_and_template_metadata(self):
        legitimate_der = (DATA / "legitimate.der").read_bytes()
        template_der = (DATA / "rogue_template.der").read_bytes()
        x509.load_der_x509_certificate(legitimate_der)
        x509.load_der_x509_certificate(template_der)
        x509.load_der_x509_certificate((DATA / "historical_server.der").read_bytes())
        x509.load_pem_x509_certificate((DATA / "historical_root.crt").read_bytes())
        locations = json.loads((DATA / "template.json").read_text())
        start = locations["signature_offset"]
        count = locations["signature_bytes"]
        self.assertIsInstance(start, int)
        self.assertIsInstance(count, int)
        self.assertGreater(start, 0)
        self.assertGreater(count, 0)
        self.assertLessEqual(start + count, len(template_der))
        self.assertEqual(template_der[start:start + count], bytes(count))


if __name__ == "__main__":
    unittest.main()
