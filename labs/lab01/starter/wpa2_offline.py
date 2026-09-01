#!/usr/bin/env python3
"""Student starter: check guesses against supplied synthetic WPA2 data only."""

from __future__ import annotations

import argparse
import hashlib
import hmac
import json
from pathlib import Path


def derive_pmk(password: str, ssid: str) -> bytes:
    """Derive a 32-byte PMK using the WPA2-Personal PBKDF2 parameters."""
    # TODO
    raise NotImplementedError


def custom_prf512(key: bytes, label: bytes, context: bytes) -> bytes:
    """Return 64 bytes using the teaching record's HMAC-SHA1 PRF."""
    # For counter values 0, 1, ... append HMAC-SHA1(key,
    # label + b"\x00" + context + one-byte counter), then truncate to 64 bytes.
    # TODO
    raise NotImplementedError


def build_context(record: dict[str, str]) -> bytes:
    """Concatenate ordered MAC addresses followed by ordered nonces."""
    # Decode each field from hex. Use lexicographic byte ordering independently
    # for the two MACs and the two nonces.
    # TODO
    raise NotImplementedError


def candidate_mic(password: str, record: dict[str, str]) -> bytes:
    """Compute the 16-byte candidate MIC for this synthetic record."""
    # TODO: PMK -> PTK -> first 16-byte KCK -> truncated HMAC-SHA1.
    raise NotImplementedError


def crack_capture(record: dict[str, str], candidates: list[str]) -> str | None:
    """Return the matching candidate, if any, using constant-time MIC compare."""
    # TODO
    raise NotImplementedError


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("capture")
    parser.add_argument("dictionary")
    args = parser.parse_args()
    record = json.loads(Path(args.capture).read_text(encoding="utf-8"))
    candidates = [
        line.strip()
        for line in Path(args.dictionary).read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    match = crack_capture(record, candidates)
    print(match if match is not None else "not found")


if __name__ == "__main__":
    main()
