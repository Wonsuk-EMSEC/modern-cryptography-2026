"""Public checks for the bounded SSH exercise starter."""

import unittest
from pathlib import Path

import ssh_dictionary_attack as attack


class SSHDictionaryAttackTests(unittest.TestCase):
    def test_target_is_fixed_to_compose_service(self) -> None:
        self.assertEqual(attack.TARGET_HOST, "lab01-ssh-target")
        self.assertEqual(attack.TARGET_PORT, 22)
        self.assertEqual(attack.TARGET_USERNAME, "labstudent")

    def test_course_wordlist_is_bounded(self) -> None:
        path = Path(__file__).resolve().parents[1] / "data" / "ssh-lab-wordlist.txt"
        candidates = attack.load_candidates(path)
        self.assertGreater(len(candidates), 1)
        self.assertLessEqual(len(candidates), attack.MAX_CANDIDATES)


if __name__ == "__main__":
    unittest.main()
