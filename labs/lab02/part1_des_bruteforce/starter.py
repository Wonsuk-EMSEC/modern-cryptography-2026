#!/usr/bin/env python3
"""Part 1 starter: recover a reduced-space DES key and decrypt the flag."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB_ROOT))

from common.des import MAX_KEY_BITS, decrypt_bytes, encrypt_block, make_des_key, unpad8


def brute_force(plaintext: bytes, ciphertext: bytes, key_bits: int) -> tuple[int | None, int, float]:
    """Return (recovered ID, candidates tested, elapsed seconds)."""
    if not 1 <= key_bits <= MAX_KEY_BITS:
        raise ValueError("refusing an impractical key space")
    # TODO: test every candidate with make_des_key() and encrypt_block().
    # Stop at the first match and measure time with time.perf_counter().
    raise NotImplementedError


def decrypt_flag(encrypted: bytes, key_id: int, key_bits: int) -> bytes:
    # TODO: construct the recovered key, decrypt all blocks, and remove padding.
    raise NotImplementedError


def main() -> None:
    data = Path(__file__).with_name("data")
    parameters = json.loads((data / "parameters.json").read_text())
    key_id, tested, elapsed = brute_force(
        (data / "known_plaintext.bin").read_bytes(),
        (data / "known_ciphertext.bin").read_bytes(),
        parameters["key_bits"],
    )
    if key_id is None:
        raise SystemExit("key not found")
    rate = tested / elapsed if elapsed else float("inf")
    print(f"candidate={key_id} tested={tested} elapsed={elapsed:.3f}s rate={rate:.0f} keys/s")
    print(decrypt_flag((data / "encrypted_flag.bin").read_bytes(), key_id,
                       parameters["key_bits"]).decode("ascii"))


if __name__ == "__main__":
    main()
