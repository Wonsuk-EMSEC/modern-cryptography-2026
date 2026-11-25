"""Public fixture checks that do not try the word list."""

import unittest
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives.asymmetric import rsa


DATA = Path(__file__).resolve().parent / "data"


class MaterialsTests(unittest.TestCase):
    def test_fixture_shape(self) -> None:
        key_blob = (DATA / "encrypted_key.der").read_bytes()
        certificate = x509.load_pem_x509_certificate((DATA / "certificate.crt").read_bytes())
        public = certificate.public_key()
        self.assertIsInstance(public, rsa.RSAPublicKey)
        self.assertGreater(len(key_blob), 100)
        self.assertEqual(len((DATA / "flag.enc").read_bytes()), public.key_size // 8)
        self.assertGreater(len((DATA / "wordlist.txt").read_text(encoding="utf-8").splitlines()), 10)


if __name__ == "__main__":
    unittest.main()
