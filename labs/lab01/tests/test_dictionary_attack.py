import hashlib
import tempfile
import unittest
from pathlib import Path

try:
    from ._load_impl import load
except ImportError:  # unittest discovery adds this directory directly to sys.path
    from _load_impl import load

impl = load("dictionary_attack")


class DictionaryAttackTests(unittest.TestCase):
    def test_load_dictionary_ignores_blank_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "words.txt"
            path.write_text("alpha\n\n beta \n", encoding="utf-8")
            self.assertEqual(impl.load_dictionary(path), ["alpha", "beta"])

    def test_cracks_and_normalizes_targets(self):
        digest = hashlib.sha256(b"beta").hexdigest()
        self.assertEqual(
            impl.crack_hashes([digest.upper(), "0" * 64], ["alpha", "beta"]),
            {digest: "beta"},
        )


if __name__ == "__main__":
    unittest.main()
