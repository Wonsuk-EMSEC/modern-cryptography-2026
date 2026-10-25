#!/usr/bin/env python3
"""Inspect known-pair JSON and binary data without running the MITM search."""

import json
from pathlib import Path


def main() -> None:
    data = Path(__file__).resolve().parents[1] / "data"
    record = json.loads((data / "known_pairs.json").read_text())
    pairs = [(bytes.fromhex(item["plaintext"]), bytes.fromhex(item["ciphertext"]))
             for item in record["pairs"]]
    encrypted = (data / "encrypted_flag.bin").read_bytes()
    print(f"Bits per key ID: {record['key_bits']}")
    print(f"Known pairs: {len(pairs)}")
    for index, (plaintext, ciphertext) in enumerate(pairs, start=1):
        print(f"Pair {index}: plaintext={len(plaintext)} bytes, ciphertext={len(ciphertext)} bytes")
    print(f"Encrypted record: {len(encrypted)} bytes")
    assert len(pairs) >= 2 and all(len(p) == len(c) == 8 for p, c in pairs)
    assert encrypted and len(encrypted) % 8 == 0
    print("Public data shape check: OK")


if __name__ == "__main__":
    main()
