#!/usr/bin/env python3
"""Part 2 starter: recover two reduced Double-DES keys with MITM."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB_ROOT))

from common.des import decrypt_block, decrypt_bytes, encrypt_block, make_des_key, unpad8


def double_encrypt(block: bytes, key1: bytes, key2: bytes) -> bytes:
    return encrypt_block(encrypt_block(block, key1), key2)


def double_decrypt(block: bytes, key1: bytes, key2: bytes) -> bytes:
    return decrypt_block(decrypt_block(block, key2), key1)


def recover_keys(pairs: list[tuple[bytes, bytes]], key_bits: int) -> list[tuple[int, int]]:
    if len(pairs) < 2 or not 1 <= key_bits <= 20:
        raise ValueError("two pairs and a 1..20-bit key space are required")
    # TODO phase 1: map E_K1(P1) to a LIST of K1 candidate IDs.
    # TODO phase 2: match D_K2(C1), then verify candidates with (P2, C2).
    raise NotImplementedError


def decrypt_flag(encrypted: bytes, key1_id: int, key2_id: int, key_bits: int) -> bytes:
    # TODO: reverse Double DES for every block and remove padding.
    raise NotImplementedError


def main() -> None:
    data = Path(__file__).with_name("data")
    record = json.loads((data / "known_pairs.json").read_text())
    pairs = [(bytes.fromhex(item["plaintext"]), bytes.fromhex(item["ciphertext"]))
             for item in record["pairs"]]
    started = time.perf_counter()
    candidates = recover_keys(pairs, record["key_bits"])
    elapsed = time.perf_counter() - started
    print(f"verified_pairs={len(candidates)} elapsed={elapsed:.3f}s")
    if len(candidates) != 1:
        raise SystemExit("expected one verified key pair")
    print(decrypt_flag((data / "encrypted_flag.bin").read_bytes(), *candidates[0],
                       record["key_bits"]).decode("ascii"))


if __name__ == "__main__":
    main()
