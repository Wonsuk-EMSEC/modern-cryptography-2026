#!/usr/bin/env python3
"""Public checks for the Part 5 WPA2 implementation exercises."""

from __future__ import annotations

import importlib.util
import json
import os
import unittest
from pathlib import Path


PART_DIR = Path(__file__).resolve().parent
DATA_DIR = PART_DIR.parent / "data"
IMPLEMENTATION_DIR = Path(os.environ.get("LAB01_PART5_IMPL", PART_DIR))
COMPLETION_TESTS = bool(os.environ.get("LAB01_GRADE"))


def load_module(filename: str):
    path = IMPLEMENTATION_DIR / filename
    module_name = f"lab01_part5_{path.stem}_{abs(hash(path))}"
    spec = importlib.util.spec_from_file_location(module_name, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_record() -> dict[str, str]:
    return json.loads((DATA_DIR / "wpa2_capture.json").read_text(encoding="utf-8"))


class SuppliedDataTests(unittest.TestCase):
    """Checks that run before students complete any TODO."""

    def test_metadata_has_required_lengths(self) -> None:
        record = load_record()
        self.assertTrue(record["ssid"])
        self.assertEqual(len(bytes.fromhex(record["ap_mac"])), 6)
        self.assertEqual(len(bytes.fromhex(record["client_mac"])), 6)
        self.assertEqual(len(bytes.fromhex(record["anonce"])), 32)
        self.assertEqual(len(bytes.fromhex(record["snonce"])), 32)
        self.assertGreaterEqual(len(bytes.fromhex(record["eapol"])), 97)
        self.assertEqual(len(bytes.fromhex(record["mic"])), 16)

    def test_supplied_pcap_is_locally_readable(self) -> None:
        capture = (DATA_DIR / "wpa2/lab01-handshake.pcap").read_bytes()
        self.assertGreater(len(capture), 24)
        self.assertEqual(capture[:4], b"\xd4\xc3\xb2\xa1")


@unittest.skipUnless(COMPLETION_TESTS, "set LAB01_GRADE=1 after completing the TODOs")
class CompletedImplementationTests(unittest.TestCase):
    """Behavior checks enabled after the implementation is complete."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.verifier = load_module("verify_candidate.py")
        cls.record = load_record()

    def test_derives_a_deterministic_pmk(self) -> None:
        first = self.verifier.derive_pmk("classroom-candidate", self.record["ssid"])
        second = self.verifier.derive_pmk("classroom-candidate", self.record["ssid"])
        other_ssid = self.verifier.derive_pmk("classroom-candidate", "DifferentSSID")
        self.assertEqual(len(first), 32)
        self.assertEqual(first, second)
        self.assertNotEqual(first, other_ssid)

    def test_builds_an_ordered_context(self) -> None:
        context = self.verifier.build_context(self.record)
        macs = sorted(bytes.fromhex(self.record[key]) for key in ("ap_mac", "client_mac"))
        nonces = sorted(bytes.fromhex(self.record[key]) for key in ("anonce", "snonce"))
        self.assertEqual(context, b"".join(macs + nonces))
        self.assertEqual(len(context), 76)

    def test_derives_ptk_and_kck(self) -> None:
        pmk = self.verifier.derive_pmk("classroom-candidate", self.record["ssid"])
        context = self.verifier.build_context(self.record)
        ptk = self.verifier.derive_ptk(pmk, context)
        changed = self.verifier.derive_ptk(pmk, context[:-1] + bytes([context[-1] ^ 1]))
        self.assertEqual(len(ptk), 64)
        self.assertNotEqual(ptk, changed)
        self.assertEqual(self.verifier.derive_kck(ptk), ptk[:16])

    def test_normalizes_eapol_mic_field(self) -> None:
        eapol = self.verifier.normalized_eapol(self.record)
        self.assertEqual(len(eapol), len(bytes.fromhex(self.record["eapol"])))
        self.assertEqual(eapol[81:97], bytes(16))

    def test_rejects_truncated_eapol_data(self) -> None:
        truncated = dict(self.record)
        truncated["eapol"] = bytes(96).hex()
        with self.assertRaises(ValueError):
            self.verifier.normalized_eapol(truncated)

    def test_computes_a_truncated_mic(self) -> None:
        eapol = self.verifier.normalized_eapol(self.record)
        mic = self.verifier.compute_mic(bytes(range(16)), eapol)
        changed = self.verifier.compute_mic(bytes(range(16)), eapol + b"\x00")
        self.assertEqual(len(mic), 16)
        self.assertNotEqual(mic, changed)

    def test_dictionary_contains_exactly_one_match(self) -> None:
        words = (DATA_DIR / "lab01-small.txt").read_text(encoding="utf-8").splitlines()
        self.assertEqual(sum(self.verifier.verify(word, self.record) for word in words), 1)


if __name__ == "__main__":
    unittest.main()
