"""Compatibility names for the public Part 7 leakage model.

New code should import :mod:`model`; this module preserves the original names
for notebooks or local work that already imported ``aes.py``.
"""

from __future__ import annotations

try:
    from .model import HAMMING_WEIGHTS, HW, SBOX as AES_SBOX, hamming_weight
except ImportError:  # pragma: no cover - direct execution from this directory.
    from model import HAMMING_WEIGHTS, HW, SBOX as AES_SBOX, hamming_weight
