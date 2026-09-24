#!/usr/bin/env python3
"""Try single-block DES with public example values, independently of lab data."""

from __future__ import annotations

import sys
from pathlib import Path

from Crypto.Cipher import DES

LAB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB_ROOT))

from common.des import decrypt_block, encrypt_block, make_des_key


def main() -> None:
    # These are public example values, not the key or plaintext of the task.
    key = bytes.fromhex("133457799BBCDFF1")
    plaintext = bytes.fromhex("0123456789ABCDEF")
    expected_ciphertext = bytes.fromhex("85E813540F0AB405")

    # One DES block is eight bytes. ECB encrypts that block directly, without
    # an IV. This exactly one-block example does not need padding.
    encryptor = DES.new(key, DES.MODE_ECB)
    ciphertext = encryptor.encrypt(plaintext)
    decryptor = DES.new(key, DES.MODE_ECB)
    recovered = decryptor.decrypt(ciphertext)

    print("Direct DES API: public example")
    print(f"Key:        {key.hex()}")
    print(f"Plaintext:  {plaintext.hex()}")
    print(f"Ciphertext: {ciphertext.hex()}")
    print(f"Recovered:  {recovered.hex()}")
    assert ciphertext == expected_ciphertext
    assert recovered == plaintext
    print("Known-answer and round-trip checks: OK")

    # A small, public ID demonstrates the lab's key encoding. This example is
    # separate from the supplied 24-bit search data.
    example_id, example_bits = 17, 8
    example_key = make_des_key(example_id, example_bits)
    example_plaintext = b"CRYPTO26"
    example_ciphertext = encrypt_block(example_plaintext, example_key)
    example_recovered = decrypt_block(example_ciphertext, example_key)

    print("\nLab helpers: public example")
    print(f"Example ID: {example_id} ({example_bits}-bit example space)")
    print(f"DES key:    {example_key.hex()}")
    print(f"Plaintext:  {example_plaintext!r}")
    print(f"Ciphertext: {example_ciphertext.hex()}")
    print(f"Recovered:  {example_recovered!r}")
    assert example_recovered == example_plaintext
    print("Helper round-trip check: OK")


if __name__ == "__main__":
    main()
