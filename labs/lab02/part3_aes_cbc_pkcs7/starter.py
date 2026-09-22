#!/usr/bin/env python3
"""Part 3 starter: implement PKCS#7 and CBC using AES-ECB blocks."""

from __future__ import annotations

from pathlib import Path

from Crypto.Cipher import AES

BLOCK_SIZE = 16


def pkcs7_pad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    # TODO: always append padding, including a full block for aligned input.
    raise NotImplementedError


def pkcs7_unpad(data: bytes, block_size: int = BLOCK_SIZE) -> bytes:
    # TODO: validate every padding byte and reject malformed input.
    raise NotImplementedError


def xor_bytes(left: bytes, right: bytes) -> bytes:
    if len(left) != len(right):
        raise ValueError("XOR operands must have equal length")
    return bytes(a ^ b for a, b in zip(left, right))


def cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    # TODO: pad, XOR each plaintext block with the previous ciphertext (or IV),
    # then encrypt it using AES.MODE_ECB. Do not use AES.MODE_CBC.
    raise NotImplementedError


def cbc_decrypt(key: bytes, iv: bytes, ciphertext: bytes) -> bytes:
    # TODO: decrypt each block with AES.MODE_ECB, XOR with the previous
    # ciphertext (or IV), join the blocks, then validate/remove padding.
    raise NotImplementedError


def main() -> None:
    data = Path(__file__).with_name("data")
    plaintext = cbc_decrypt(
        (data / "key.bin").read_bytes(),
        (data / "iv.bin").read_bytes(),
        (data / "encrypted_flag.bin").read_bytes(),
    )
    print(plaintext.decode("ascii"))


if __name__ == "__main__":
    main()
