#!/usr/bin/env python3
"""Known-answer and tradeoff checks for the Part 4 reference implementation."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "labs/lab01/data"
SOLUTION = Path(__file__).with_name("solutions") / "table_attacks.py"
SPEC = importlib.util.spec_from_file_location("table_attacks_solution", SOLUTION)
assert SPEC and SPEC.loader
TABLES = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(TABLES)


class TableAttackReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.config = json.loads((DATA / "rainbow_lab_config.json").read_text(encoding="utf-8"))
        with (DATA / "rainbow_password_database.csv").open(newline="", encoding="utf-8") as stream:
            cls.database = list(csv.DictReader(stream))
        cls.full = TABLES.build_precomputation(cls.config)
        cls.rainbow = TABLES.build_rainbow(cls.config)

    def test_expected_space_and_endpoint_counts(self) -> None:
        self.assertEqual(len(self.full), 1296)
        self.assertEqual(sum(map(len, self.rainbow.values())), self.config["chain_count"])
        self.assertEqual(len(self.rainbow), 71)

    def test_full_table_recovers_every_database_row(self) -> None:
        recovered = [TABLES.lookup_precomputation(row["sha256"], self.full)[0] for row in self.database]
        self.assertTrue(all(recovered))

    def test_rainbow_table_demonstrates_incomplete_coverage(self) -> None:
        recovered = [
            TABLES.lookup_rainbow(row["sha256"], self.rainbow, self.config)[0]
            for row in self.database
        ]
        self.assertEqual(sum(value is not None for value in recovered), 4)
        self.assertEqual(sum(value is None for value in recovered), 1)

    def test_unsalted_table_does_not_match_salted_digest(self) -> None:
        salted = hashlib.sha256(b"public-salt:" + b"abc1").hexdigest()
        self.assertIsNone(TABLES.lookup_precomputation(salted, self.full)[0])


if __name__ == "__main__":
    unittest.main()
