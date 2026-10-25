"""Fixture checks work with an empty exercise; implementation checks opt in."""

import unittest
import importlib.util
import os
from pathlib import Path


PART_DIR = Path(__file__).resolve().parent


def load_implementation():
    base = Path(os.environ.get("LAB01_SSH_IMPL", PART_DIR))
    path = base / "ssh_dictionary_attack.py"
    spec = importlib.util.spec_from_file_location("lab01_ssh_implementation", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SSHDictionaryAttackTests(unittest.TestCase):
    @unittest.skipUnless(os.environ.get("LAB01_GRADE"), "write the fixed constants first")
    def test_target_is_fixed_to_compose_service(self) -> None:
        attack = load_implementation()
        self.assertEqual(attack.TARGET_HOST, "lab01-ssh-target")
        self.assertEqual(attack.TARGET_PORT, 22)
        self.assertEqual(attack.TARGET_USERNAME, "labstudent")

    def test_course_wordlist_is_bounded(self) -> None:
        path = Path(__file__).resolve().parent / "data" / "ssh-lab-wordlist.txt"
        candidates = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
        self.assertEqual(len(candidates), 107)
        self.assertEqual(len(candidates), len(set(candidates)))
        self.assertLessEqual(len(candidates), 120)

    @unittest.skipUnless(os.environ.get("LAB01_GRADE"), "implement load_candidates() first")
    def test_wordlist_loader_preserves_bounded_input(self) -> None:
        attack = load_implementation()
        path = PART_DIR / "data" / "ssh-lab-wordlist.txt"
        self.assertEqual(len(attack.load_candidates(path)), 107)
        self.assertEqual(attack.MAX_CANDIDATES, 120)


if __name__ == "__main__":
    unittest.main()
