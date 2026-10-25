#!/usr/bin/env python3
"""Observe library CBC and padding using public example values.

The exercise implements these operations manually using AES-ECB blocks;
this sample deliberately uses library operations as an independent example.
"""

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad


def main() -> None:
    key, iv = bytes(range(16)), bytes(range(16, 32))
    plaintext = b"Hello, AES-CBC!"
    padded = pad(plaintext, 16)
    ciphertext = AES.new(key, AES.MODE_CBC, iv).encrypt(padded)
    restored = AES.new(key, AES.MODE_CBC, iv).decrypt(ciphertext)
    recovered = unpad(restored, 16)
    print(f"Plaintext: {plaintext!r}")
    print(f"Padded plaintext: {padded!r}")
    print(f"Lengths: {len(plaintext)} bytes -> {len(padded)} padded bytes")
    print(f"Ciphertext: {ciphertext.hex()}")
    print(f"Recovered: {recovered!r}")
    assert recovered == plaintext
    print("AES-CBC round-trip check: OK")
    aligned = pad(b"A" * 16, 16)
    print(f"Aligned input: 16 bytes -> {len(aligned)} padded bytes")
    print(f"Full-block padding: {aligned[-16:].hex()}")
    try:
        unpad(b"A" * 15 + b"\x00", 16)
    except ValueError:
        print("Malformed padding rejected: OK")
    else:
        raise AssertionError("invalid padding was accepted")


if __name__ == "__main__":
    main()
