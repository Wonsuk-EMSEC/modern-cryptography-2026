#!/usr/bin/env python3
"""Verify instructor-only WPA2 derivation vectors."""

from __future__ import annotations

import hashlib
import hmac
import json
import unittest
from pathlib import Path

VECTOR_PATH = Path(__file__).with_name("test_vectors") / "wpa2_pmk_ptk_kck.json"


def custom_prf512(key: bytes, context: bytes) -> bytes:
    """Derive 64 PTK bytes using the WPA/WPA2 pairwise expansion PRF."""
    output = b""
    counter = 0
    while len(output) < 64:
        output += hmac.new(
            key,
            b"Pairwise key expansion\x00" + context + bytes([counter]),
            hashlib.sha1,
        ).digest()
        counter += 1
    return output[:64]


def derive(vector: dict[str, str]) -> tuple[bytes, bytes, bytes]:
    """Return PMK, PTK, and KCK for one test vector."""
    pmk = hashlib.pbkdf2_hmac(
        "sha1",
        vector["passphrase"].encode("utf-8"),
        vector["ssid"].encode("utf-8"),
        4096,
        32,
    )
    macs = sorted(bytes.fromhex(vector[name]) for name in ("ap_mac", "client_mac"))
    nonces = sorted(bytes.fromhex(vector[name]) for name in ("anonce", "snonce"))
    ptk = custom_prf512(pmk, b"".join(macs + nonces))
    return pmk, ptk, ptk[:16]


class WPA2DerivationVectorTests(unittest.TestCase):
    def test_pmk_ptk_and_kck(self) -> None:
        vector = json.loads(VECTOR_PATH.read_text(encoding="utf-8"))
        pmk, ptk, kck = derive(vector)
        self.assertEqual(pmk.hex(), vector["pmk"])
        self.assertEqual(ptk.hex(), vector["ptk"])
        self.assertEqual(kck.hex(), vector["kck"])


if __name__ == "__main__":
    unittest.main()
