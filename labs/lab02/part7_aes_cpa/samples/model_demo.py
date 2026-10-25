#!/usr/bin/env python3
"""Public AES model, NumPy correlation, and AES-CBC I/O examples.

All keys and plaintexts in this file are public teaching values. This sample
does not rank guesses, recover a key, or load the encrypted course record.
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

PART_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PART_ROOT))
from model import SBOX, generate_traces, hamming_weight


def main() -> None:
    values = np.array([0, 1, 3, 255], dtype=np.uint8)
    print(f"Hamming weights: {hamming_weight(values).tolist()}")
    print(f"SBox[0]: 0x{int(SBOX[0]):02x}")
    plaintexts = np.arange(64, dtype=np.uint8).reshape(4, 16)
    traces = generate_traces(plaintexts, bytes(range(16)), seed=7)
    print(f"public plaintexts: shape={plaintexts.shape}, dtype={plaintexts.dtype}")
    print(f"public traces: shape={traces.shape}, dtype={traces.dtype}")
    # Correlate two public vectors across observations, preserving the sign.
    observations = np.array([0.0, 1.0, 2.0, 3.0])
    print(f"toy positive correlation: {np.corrcoef(observations, 2 * observations)[0, 1]:.1f}")
    print(f"toy negative correlation: {np.corrcoef(observations, -observations)[0, 1]:.1f}")
    key, iv, message = bytes(range(16)), bytes(range(16, 32)), b"Sample record"
    ciphertext = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(message, 16))
    packet = iv + ciphertext
    recovered = unpad(AES.new(key, AES.MODE_CBC, packet[:16]).decrypt(packet[16:]), 16)
    print(f"public CBC packet: {len(packet)} bytes")
    print(f"CBC recovered: {recovered!r}")
    assert recovered == message


if __name__ == "__main__":
    main()
