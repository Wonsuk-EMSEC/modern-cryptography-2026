import itertools
import unittest
import os

try:
    from ._load_impl import load
except ImportError:  # unittest discovery adds this directory directly to sys.path
    from _load_impl import load

impl = load("rainbow_table")


@unittest.skipUnless(os.environ.get("LAB01_GRADE"), "complete the student starter first")
class RainbowTableTests(unittest.TestCase):
    def test_reduction_stays_in_space_and_uses_column(self):
        digest = impl.hash_password("aaa")
        values = [impl.reduce_digest(digest, i, "abcd", 3) for i in range(4)]
        self.assertTrue(all(len(v) == 3 and set(v) <= set("abcd") for v in values))
        self.assertGreater(len(set(values)), 1)

    def test_table_can_recover_values_in_its_chains(self):
        starts = ["".join(p) for p in itertools.product("abcd", repeat=3)][::4]
        table = impl.generate_table(starts, 5, "abcd", 3)
        self.assertLessEqual(len(table), len(starts))
        recovered = impl.lookup(impl.hash_password(starts[0]), table, 5, "abcd", 3)
        self.assertEqual(recovered, starts[0])

    def test_unknown_digest_returns_none(self):
        table = impl.generate_table(["aaa"], 2, "abcd", 3)
        self.assertIsNone(impl.lookup("0" * 64, table, 2, "abcd", 3))


if __name__ == "__main__":
    unittest.main()
