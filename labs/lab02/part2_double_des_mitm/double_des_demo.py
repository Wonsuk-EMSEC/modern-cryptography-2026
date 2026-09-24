#!/usr/bin/env python3
"""Try Double DES with public example keys and the lab's DES helpers."""

from __future__ import annotations

import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB_ROOT))

from common.des import decrypt_bytes, encrypt_bytes, make_des_key, pad8, unpad8


def main() -> None:
    # These public example IDs are separate from the task's unknown keys.
    key1_id, key2_id, key_bits = 17, 93, 8
    key1 = make_des_key(key1_id, key_bits)
    key2 = make_des_key(key2_id, key_bits)
    plaintext = b"Hello, Double DES!"

    # Pad once, then encrypt each complete block first with K1 and then K2.
    padded_plaintext = pad8(plaintext)
    intermediate = encrypt_bytes(padded_plaintext, key1)
    ciphertext = encrypt_bytes(intermediate, key2)

    # Undo the layers in reverse order: K2 first, then K1. Remove padding
    # only after both layers have been decrypted.
    reversed_middle = decrypt_bytes(ciphertext, key2)
    decrypted_padded = decrypt_bytes(reversed_middle, key1)
    recovered = unpad8(decrypted_padded)

    print("Double DES encryption/decryption with the lab helpers")
    print(f"Example IDs: K1={key1_id}, K2={key2_id} ({key_bits}-bit example spaces)")
    print(f"DES key K1: {key1.hex()}")
    print(f"DES key K2: {key2.hex()}")
    print(f"Plaintext: {plaintext!r}")
    print(f"Padded plaintext: {padded_plaintext!r}")
    print(f"Lengths: {len(plaintext)} bytes -> {len(padded_plaintext)} padded bytes")
    print(f"Intermediate E_K1(P): {intermediate.hex()}")
    print(f"Ciphertext E_K2(E_K1(P)): {ciphertext.hex()}")
    print(f"Intermediate D_K2(C): {reversed_middle.hex()}")
    print(f"Decrypted padded bytes: {decrypted_padded!r}")
    print(f"Recovered: {recovered!r}")
    assert reversed_middle == intermediate
    assert recovered == plaintext
    print("Intermediate-value check: OK")
    print("Double-DES round-trip check: OK")


if __name__ == "__main__":
    main()
