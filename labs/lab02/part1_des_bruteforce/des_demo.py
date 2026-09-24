#!/usr/bin/env python3
"""Try the lab's DES and padding helpers with public example values."""

from __future__ import annotations

import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB_ROOT))

from common.des import decrypt_bytes, encrypt_bytes, make_des_key, pad8, unpad8


def main() -> None:
    # These public example values are separate from the supplied task data.
    key_id, key_bits = 17, 8
    key = make_des_key(key_id, key_bits)
    plaintext = b"Hello, DES!"

    # DES processes eight-byte blocks. pad8() adds five 0x05 bytes to this
    # eleven-byte message, producing two complete blocks for encrypt_bytes().
    padded_plaintext = pad8(plaintext)
    ciphertext = encrypt_bytes(padded_plaintext, key)

    # Decryption restores the padded bytes first. Remove padding once, after
    # decrypting the whole message, to recover the original plaintext.
    decrypted_padded = decrypt_bytes(ciphertext, key)
    recovered = unpad8(decrypted_padded)

    print("DES encryption/decryption with the lab helpers")
    print(f"Example ID: {key_id} ({key_bits}-bit example space)")
    print(f"DES key: {key.hex()}")
    print(f"Plaintext: {plaintext!r}")
    print(f"Padded plaintext: {padded_plaintext!r}")
    print(f"Lengths: {len(plaintext)} bytes -> {len(padded_plaintext)} padded bytes")
    print(f"Ciphertext: {ciphertext.hex()}")
    print(f"Decrypted padded bytes: {decrypted_padded!r}")
    print(f"Recovered: {recovered!r}")
    assert recovered == plaintext
    print("Padding round-trip check: OK")


if __name__ == "__main__":
    main()
