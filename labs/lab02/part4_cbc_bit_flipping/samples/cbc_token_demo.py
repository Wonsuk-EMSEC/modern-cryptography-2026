#!/usr/bin/env python3
"""Public AES-CBC/base64 example; optionally call the normal-token client.

The key and message below are teaching examples, unrelated to target secrets.
This sample demonstrates packet handling and a program entry point; it does
not forge privileges or contain the exercise's attack implementation.
"""

from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

PART_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PART_ROOT))
import client


def local_example() -> None:
    key = bytes(range(16))  # Public toy key; never used by the target.
    iv = bytes(range(16, 32))
    message = b"Sample token"
    ciphertext = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(message, 16))
    encoded = base64.b64encode(iv + ciphertext).decode("ascii")
    packet = base64.b64decode(encoded, validate=True)
    # Bytes 0..15 are the IV; the remaining complete blocks are ciphertext.
    decoded_iv, decoded_ciphertext = packet[:16], packet[16:]
    recovered = unpad(AES.new(key, AES.MODE_CBC, decoded_iv).decrypt(decoded_ciphertext), 16)
    print(f"message: {message!r}")
    print(f"packet: {len(packet)} bytes = {len(decoded_iv)} IV + {len(decoded_ciphertext)} ciphertext")
    print(f"base64 round-trip: {packet == iv + ciphertext}")
    print(f"recovered: {recovered!r}")
    assert recovered == message
    print("CBC round-trip: OK")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", action="store_true", help="also issue and verify a normal service token")
    args = parser.parse_args()
    local_example()
    if args.target:
        token = client.issue()
        packet = base64.b64decode(token, validate=True)
        print(f"target packet: {len(packet)} bytes; block-aligned: {len(packet) % 16 == 0}")
        print(f"normal verification: {client.verify(token)}")


if __name__ == "__main__":
    main()
