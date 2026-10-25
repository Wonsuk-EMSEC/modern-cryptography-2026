"""Check the supplied collision fixtures without a student implementation."""

import hashlib
import unittest
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]


class MD5CollisionTests(unittest.TestCase):
    def test_supplied_files_are_a_collision(self):
        data = LAB_ROOT / "part1_hashing" / "data"
        first = (data / "md5_collision_a.bin").read_bytes()
        second = (data / "md5_collision_b.bin").read_bytes()
        self.assertNotEqual(first, second)
        self.assertEqual(hashlib.md5(first).digest(), hashlib.md5(second).digest())
        self.assertNotEqual(
            hashlib.sha256(first).digest(), hashlib.sha256(second).digest()
        )


if __name__ == "__main__":
    unittest.main()
