"""Public tests for Part 4 precomputation and rainbow table implementations."""

import json
import os
import sys
import unittest
from pathlib import Path

IMPLEMENTATION = os.environ.get("LAB01_TABLE_IMPL")
if IMPLEMENTATION:
    sys.path.insert(0, IMPLEMENTATION)

import build_precomputation_table as full
import build_rainbow_table as rainbow
import compare_table_attacks as compare
from table_common import hash_password, load_config, password_space

ROOT = Path(__file__).resolve().parents[1]
CONFIG = load_config(ROOT / "data" / "rainbow_lab_config.json")


class TableHelperTests(unittest.TestCase):
    def test_bounded_password_space(self) -> None:
        candidates = list(password_space(str(CONFIG["alphabet"]), int(CONFIG["password_length"])))
        self.assertEqual(len(candidates), 1296)
        self.assertEqual(len(candidates), len(set(candidates)))

    def test_database_schema(self) -> None:
        rows = compare.load_database(ROOT / "data" / "rainbow_password_database.csv")
        self.assertEqual(len(rows), 5)
        self.assertTrue(all(len(row["sha256"]) == 64 for row in rows))


@unittest.skipUnless(os.environ.get("LAB01_GRADE"), "complete the table TODOs first")
class CompletedTableTests(unittest.TestCase):
    def test_full_table_covers_space(self) -> None:
        entries = full.build_table(CONFIG)
        self.assertEqual(len(entries), 1296)

    def test_reduction_is_column_specific_and_bounded(self) -> None:
        digest = hash_password("abc1")
        values = [rainbow.reduce_digest(digest, column, "abc123", 4) for column in range(4)]
        self.assertTrue(all(len(value) == 4 and set(value) <= set("abc123") for value in values))
        self.assertGreater(len(set(values)), 1)

    def test_rainbow_table_stores_only_endpoints(self) -> None:
        endpoints = rainbow.build_table(CONFIG)
        self.assertLess(len(endpoints), 1296)
        self.assertEqual(sum(len(starts) for starts in endpoints.values()), CONFIG["chain_count"])

    def test_precomputation_lookup_needs_no_new_hashes(self) -> None:
        digest = hash_password("abc1")
        password, computations = compare.lookup_precomputation(digest, {digest: "abc1"})
        self.assertEqual(password, "abc1")
        self.assertEqual(computations, 0)

    def test_rainbow_lookup_reconstructs_a_chain(self) -> None:
        endpoints = rainbow.build_table(CONFIG)
        start = rainbow.choose_starts(CONFIG)[0]
        password, computations = compare.lookup_rainbow(hash_password(start), endpoints, CONFIG)
        self.assertEqual(password, start)
        self.assertGreater(computations, 0)


if __name__ == "__main__":
    unittest.main()
