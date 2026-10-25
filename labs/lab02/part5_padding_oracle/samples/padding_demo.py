#!/usr/bin/env python3
"""Inspect public PKCS#7 examples and optionally make one normal oracle query.

This sample creates no recovery loop. Its public padding examples show why
the receiver must inspect the whole padding suffix, not just its last byte.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from Crypto.Util.Padding import pad, unpad

PART_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PART_ROOT))
from oracle_client import OracleClient


def local_example() -> None:
    message = b"Sample record"
    padded = pad(message, 16)
    print(f"message: {message!r}")
    print(f"padded: {padded!r}")
    print(f"length: {len(message)} -> {len(padded)} bytes")
    print(f"valid suffix: {unpad(padded, 16) == message}")
    damaged = bytearray(padded)
    damaged[-2] ^= 1  # The last byte still claims three padding bytes.
    try:
        unpad(bytes(damaged), 16)
    except ValueError:
        print("damaged suffix: rejected")
    else:
        raise AssertionError("the altered padding suffix should be rejected")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", action="store_true", help="query the supplied unmodified packet once")
    args = parser.parse_args()
    local_example()
    if args.target:
        packet = bytes.fromhex((PART_ROOT / "data" / "ciphertext.hex").read_text().strip())
        print(f"packet has IV plus {len(packet) // 16 - 1} ciphertext blocks")
        with OracleClient() as oracle:
            print(f"original padding valid: {oracle.query(packet)}")
            print(f"queries: {oracle.queries}")


if __name__ == "__main__":
    main()
