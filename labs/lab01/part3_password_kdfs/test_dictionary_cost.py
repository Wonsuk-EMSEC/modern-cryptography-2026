"""Public tests for the Part 3 salted and unsalted cracking starters."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]


def load_implementation(name: str):
    base = Path(os.environ.get("LAB01_COST_IMPL", Path(__file__).resolve().parent))
    path = base / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lab01_cost_{name}", path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


crack_salted = load_implementation("crack_salted")
crack_unsalted = load_implementation("crack_unsalted")


class DictionaryFixtureTests(unittest.TestCase):
    def test_supplied_database_schemas(self) -> None:
        data = LAB_ROOT / "data"
        with (data / "unsalted_hashes.csv").open(newline="", encoding="utf-8") as stream:
            unsalted_fields = csv.DictReader(stream).fieldnames
        with (data / "salted_hashes.csv").open(newline="", encoding="utf-8") as stream:
            salted_fields = csv.DictReader(stream).fieldnames
        self.assertEqual(unsalted_fields, ["account", "sha256"])
        self.assertEqual(salted_fields, ["account", "salt_hex", "sha256"])


@unittest.skipUnless(os.environ.get("LAB01_GRADE"), "complete both crack() TODOs first")
class CompletedDictionaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.directory = Path(self.temporary.name)
        self.words = self.directory / "words.txt"
        self.words.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_unsalted_attack_reuses_candidate_hashes(self) -> None:
        targets = self.directory / "unsalted.csv"
        targets.write_text(
            "account,sha256\n"
            f"student_one,{hashlib.sha256(b'beta').hexdigest()}\n"
            f"student_two,{hashlib.sha256(b'gamma').hexdigest()}\n",
            encoding="utf-8",
        )
        recovered, computations, elapsed = crack_unsalted.crack(targets, self.words)
        self.assertEqual(recovered, {"student_one": "beta", "student_two": "gamma"})
        self.assertEqual(computations, 3)
        self.assertGreater(elapsed, 0)

    def test_salted_attack_computes_for_each_account(self) -> None:
        salt_one = b"fixture-salt-01"
        salt_two = b"fixture-salt-02"
        digest_one = hashlib.sha256(salt_one + b"beta").hexdigest()
        digest_two = hashlib.sha256(salt_two + b"gamma").hexdigest()
        targets = self.directory / "salted.csv"
        targets.write_text(
            "account,salt_hex,sha256\n"
            f"student_one,{salt_one.hex()},{digest_one}\n"
            f"student_two,{salt_two.hex()},{digest_two}\n",
            encoding="utf-8",
        )
        recovered, computations, elapsed = crack_salted.crack(targets, self.words)
        self.assertEqual(recovered, {"student_one": "beta", "student_two": "gamma"})
        self.assertEqual(computations, 5)
        self.assertGreater(elapsed, 0)


if __name__ == "__main__":
    unittest.main()
