import hashlib
import json
import unittest
import os

try:
    from ._load_impl import LAB_ROOT, load
except ImportError:  # unittest discovery adds this directory directly to sys.path
    from _load_impl import LAB_ROOT, load

impl = load("wpa2_offline")


@unittest.skipUnless(os.environ.get("LAB01_GRADE"), "complete the student starter first")
class WPA2OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(
            (LAB_ROOT / "data" / "wpa2_capture.json").read_text(encoding="utf-8")
        )

    def test_known_pbkdf2_vector(self):
        expected = hashlib.pbkdf2_hmac("sha1", b"password", b"IEEE", 4096, 32)
        self.assertEqual(impl.derive_pmk("password", "IEEE"), expected)

    def test_context_has_expected_length_and_order(self):
        context = impl.build_context(self.record)
        self.assertEqual(len(context), 76)
        macs = sorted(bytes.fromhex(self.record[key]) for key in ("ap_mac", "client_mac"))
        self.assertEqual(context[:12], b"".join(macs))

    def test_dictionary_recovers_exactly_one_candidate(self):
        words = [
            line.strip()
            for line in (LAB_ROOT / "data" / "wpa2_passwords.txt")
            .read_text(encoding="utf-8")
            .splitlines()
            if line.strip()
        ]
        match = impl.crack_capture(self.record, words)
        self.assertIn(match, words)
        self.assertEqual(
            sum(impl.candidate_mic(word, self.record).hex() == self.record["mic"] for word in words),
            1,
        )


if __name__ == "__main__":
    unittest.main()
