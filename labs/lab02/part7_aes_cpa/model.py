"""Public, non-secret model helpers for the Part 7 CPA exercise.

The model describes a generic first-round AES leakage experiment.  It has no
embedded course key, plaintext, ciphertext, or flag, so it may safely be
included in a student release.
"""

from __future__ import annotations

import hashlib
import struct

import numpy as np


SBOX = np.frombuffer(bytes.fromhex(
    "637c777bf26b6fc53001672bfed7ab76"
    "ca82c97dfa5947f0add4a2af9ca472c0"
    "b7fd9326363ff7cc34a5e5f171d83115"
    "04c723c31896059a071280e2eb27b275"
    "09832c1a1b6e5aa0523bd6b329e32f84"
    "53d100ed20fcb15b6acbbe394a4c58cf"
    "d0efaafb434d338545f9027f503c9fa8"
    "51a3408f929d38f5bcb6da2110fff3d2"
    "cd0c13ec5f974417c4a77e3d645d1973"
    "60814fdc222a908846eeb814de5e0bdb"
    "e0323a0a4906245cc2d3ac629195e479"
    "e7c8376d8dd54ea96c56f4ea657aae08"
    "ba78252e1ca6b4c6e8dd741f4bbd8b8a"
    "703eb5664803f60e613557b986c11d9e"
    "e1f8981169d98e949b1e87e9ce5528df"
    "8ca1890dbfe6426841992d0fb054bb16"
), dtype=np.uint8)

HAMMING_WEIGHTS = np.array([value.bit_count() for value in range(256)], dtype=np.uint8)
# Short name retained for the equations and simple student experiments.
HW = HAMMING_WEIGHTS
BLOCK_SIZE = 16
DEFAULT_SAMPLE_COUNT = 240
LEAKAGE_POSITIONS = tuple(8 + 14 * byte_index for byte_index in range(BLOCK_SIZE))


def hamming_weight(value: np.ndarray | int) -> np.ndarray | np.uint8:
    """Return the number of set bits in one or more unsigned byte values."""
    return HAMMING_WEIGHTS[np.asarray(value, dtype=np.uint8)]


def _deterministic_noise(seed: int, count: int) -> list[float]:
    """Return a reproducible zero-centered noise vector in approximately [-1, 1).

    A hash stream keeps the public trace generator stable across NumPy random
    generator changes.  The output is intentionally synthetic; it is not a
    model of a particular physical device.
    """
    material = bytearray()
    counter = 0
    prefix = b"lab02-public-cpa-noise/v1\0" + str(seed).encode("ascii")
    while len(material) < count * 2:
        material.extend(hashlib.sha256(prefix + counter.to_bytes(8, "big")).digest())
        counter += 1
    return [int.from_bytes(material[offset:offset + 2], "big", signed=True) / 32768.0
            for offset in range(0, count * 2, 2)]


def generate_traces(plaintexts: np.ndarray, key: bytes | np.ndarray, *,
                    sample_count: int = DEFAULT_SAMPLE_COUNT,
                    noise_stddev: float = 1.20,
                    leakage_scale: float = 1.65,
                    seed: int = 0) -> np.ndarray:
    """Generate deterministic synthetic first-round Hamming-weight traces.

    Each key-byte leakage peak is positioned separately so a byte-wise CPA can
    find it.  Callers supply the key and seed; this public helper never stores
    course secret material itself.
    """
    plaintexts = np.asarray(plaintexts, dtype=np.uint8)
    if isinstance(key, (bytes, bytearray, memoryview)):
        key_array = np.frombuffer(bytes(key), dtype=np.uint8)
    else:
        key_array = np.asarray(key, dtype=np.uint8)
    if plaintexts.ndim != 2 or plaintexts.shape[1] != BLOCK_SIZE:
        raise ValueError("plaintexts must have shape (trace_count, 16)")
    if key_array.shape != (BLOCK_SIZE,):
        raise ValueError("key must contain exactly 16 AES-128 bytes")
    if sample_count <= LEAKAGE_POSITIONS[-1] + 2:
        raise ValueError("sample_count leaves no room for the last leakage peak")
    if noise_stddev < 0 or leakage_scale <= 0:
        raise ValueError("noise_stddev must be non-negative and leakage_scale positive")

    trace_count = plaintexts.shape[0]
    traces = [noise * float(noise_stddev)
              for noise in _deterministic_noise(seed, trace_count * sample_count)]
    pulse = ((-2, 0.20), (-1, 0.65), (0, 1.00), (1, 0.65), (2, 0.20))
    for byte_index, position in enumerate(LEAKAGE_POSITIONS):
        for trace_index in range(trace_count):
            sbox_input = int(plaintexts[trace_index, byte_index]) ^ int(key_array[byte_index])
            leakage = int(HAMMING_WEIGHTS[int(SBOX[sbox_input])]) - 4
            row_start = trace_index * sample_count
            for offset, amplitude in pulse:
                index = row_start + position + offset
                traces[index] += leakage * (float(leakage_scale) * amplitude)
    encoded = bytearray(trace_count * sample_count * 4)
    for index, value in enumerate(traces):
        struct.pack_into("<f", encoded, index * 4, value)
    return np.frombuffer(encoded, dtype="<f4").copy().reshape(trace_count, sample_count)
