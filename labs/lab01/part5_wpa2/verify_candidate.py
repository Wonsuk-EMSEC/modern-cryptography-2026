#!/usr/bin/env python3
"""Verify one candidate against local synthetic WPA2 metadata only."""
import argparse, getpass, hashlib, hmac, json
from pathlib import Path


def prf(key: bytes, context: bytes) -> bytes:
    out = b""
    for counter in range(4): out += hmac.new(key, b"Pairwise key expansion\0" + context + bytes([counter]), hashlib.sha1).digest()
    return out[:64]


def verify(candidate: str, row: dict[str, str]) -> bool:
    macs = sorted(bytes.fromhex(row[k]) for k in ("ap_mac", "client_mac"))
    nonces = sorted(bytes.fromhex(row[k]) for k in ("anonce", "snonce"))
    pmk = hashlib.pbkdf2_hmac("sha1", candidate.encode(), row["ssid"].encode(), 4096, 32)
    kck = prf(pmk, b"".join(macs + nonces))[:16]
    mic = hmac.new(kck, bytes.fromhex(row["eapol"]), hashlib.sha1).digest()[:16]
    return hmac.compare_digest(mic, bytes.fromhex(row["mic"]))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("metadata", type=Path); args = parser.parse_args()
    row = json.loads(args.metadata.read_text()); print("match" if verify(getpass.getpass("Candidate: "), row) else "no match")
