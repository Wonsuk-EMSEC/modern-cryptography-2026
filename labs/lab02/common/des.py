"""Bounded DES helpers for Parts 1 and 2. DES is obsolete."""

from __future__ import annotations

from Crypto.Cipher import DES

MAX_KEY_BITS = 20


def make_des_key(key_id: int, key_bits: int) -> bytes:
    """Map an ID injectively into DES's 56 effective key bits.

    The ID occupies the low `key_bits` of a 56-bit payload. Each seven-bit
    group becomes the high bits of one DES key byte; its low bit is set for
    odd parity. PyCryptodome ignores those low parity bits during DES.
    """
    if not 1 <= key_bits <= MAX_KEY_BITS:
        raise ValueError("reduced DES spaces are limited to 1..20 bits")
    if not 0 <= key_id < (1 << key_bits):
        raise ValueError("key ID does not fit the selected space")
    encoded = bytearray()
    for shift in range(49, -1, -7):
        seven_bits = (key_id >> shift) & 0x7F
        parity = 1 ^ (seven_bits.bit_count() & 1)
        encoded.append((seven_bits << 1) | parity)
    return bytes(encoded)


def encrypt_block(block: bytes, key: bytes) -> bytes:
    if len(block) != 8 or len(key) != 8:
        raise ValueError("DES requires an 8-byte block and encoded key")
    return DES.new(key, DES.MODE_ECB).encrypt(block)


def decrypt_block(block: bytes, key: bytes) -> bytes:
    if len(block) != 8 or len(key) != 8:
        raise ValueError("DES requires an 8-byte block and encoded key")
    return DES.new(key, DES.MODE_ECB).decrypt(block)


def encrypt_bytes(data: bytes, key: bytes) -> bytes:
    if not data or len(data) % 8:
        raise ValueError("DES input must contain complete blocks")
    cipher = DES.new(key, DES.MODE_ECB)
    return b"".join(cipher.encrypt(data[i:i + 8]) for i in range(0, len(data), 8))


def decrypt_bytes(data: bytes, key: bytes) -> bytes:
    if not data or len(data) % 8:
        raise ValueError("DES input must contain complete blocks")
    cipher = DES.new(key, DES.MODE_ECB)
    return b"".join(cipher.decrypt(data[i:i + 8]) for i in range(0, len(data), 8))


def pad8(data: bytes) -> bytes:
    amount = 8 - len(data) % 8
    return data + bytes([amount]) * amount


def unpad8(data: bytes) -> bytes:
    if not data or len(data) % 8:
        raise ValueError("invalid padded DES plaintext")
    amount = data[-1]
    if not 1 <= amount <= 8 or data[-amount:] != bytes([amount]) * amount:
        raise ValueError("invalid padding")
    return data[:-amount]
