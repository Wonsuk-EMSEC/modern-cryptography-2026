#!/usr/bin/env python3
"""Inspect public file formats without recovering a key or decrypting a record."""

import json
from pathlib import Path


def main() -> None:
    data = Path(__file__).resolve().parents[1] / "data"
    parameters = json.loads((data / "parameters.json").read_text())
    plaintext = (data / "known_plaintext.bin").read_bytes()
    ciphertext = (data / "known_ciphertext.bin").read_bytes()
    encrypted = (data / "encrypted_flag.bin").read_bytes()
    print(f"Key-ID bits: {parameters['key_bits']}")
    print(f"Known plaintext: {len(plaintext)} bytes")
    print(f"Known ciphertext: {len(ciphertext)} bytes")
    print(f"Encrypted record: {len(encrypted)} bytes")
    assert len(plaintext) == len(ciphertext) == 8
    assert encrypted and len(encrypted) % 8 == 0
    print("Public data shape check: OK")


if __name__ == "__main__":
    main()
