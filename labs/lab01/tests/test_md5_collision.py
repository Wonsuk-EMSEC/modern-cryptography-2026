import unittest
import os
from pathlib import Path

try:
    from ._load_impl import LAB_ROOT, load
except ImportError:  # unittest discovery adds this directory directly to sys.path
    from _load_impl import LAB_ROOT, load

impl = load("md5_collision")


@unittest.skipUnless(os.environ.get("LAB01_GRADE"), "complete the student starter first")
class MD5CollisionTests(unittest.TestCase):
    def test_supplied_files_are_a_collision(self):
        first = LAB_ROOT / "data" / "md5_collision_a.bin"
        second = LAB_ROOT / "data" / "md5_collision_b.bin"
        self.assertTrue(impl.files_are_distinct(first, second))
        self.assertEqual(impl.digest_file(first, "md5"), impl.digest_file(second, "md5"))
        self.assertNotEqual(
            impl.digest_file(first, "sha256"), impl.digest_file(second, "sha256")
        )


if __name__ == "__main__":
    unittest.main()
