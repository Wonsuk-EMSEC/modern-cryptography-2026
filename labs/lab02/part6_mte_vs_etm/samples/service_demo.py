#!/usr/bin/env python3
"""Demonstrate binary packets and unchanged requests to the two services.

The offline example demonstrates HMAC-SHA-256 and base64 with public values.
Optional target requests establish baselines only: infer construction order
from your own controlled modifications in the exercise.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import hmac
import sys
from pathlib import Path

PART_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PART_ROOT))
from client import ServiceClient


def local_example() -> None:
    message = b"Sample record"
    tag = hmac.new(b"public-demo-key", message, hashlib.sha256).digest()
    encoded = base64.b64encode(message + tag).decode("ascii")
    recovered = base64.b64decode(encoded, validate=True)
    recovered_message, recovered_tag = recovered[:-32], recovered[-32:]
    expected = hmac.new(b"public-demo-key", recovered_message, hashlib.sha256).digest()
    print(f"message: {recovered_message!r}")
    print(f"HMAC-SHA-256 tag: {len(recovered_tag)} bytes")
    print(f"public packet: {len(recovered)} bytes")
    print(f"tag verification: {hmac.compare_digest(recovered_tag, expected)}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", action="store_true", help="also obtain and submit unchanged service items")
    args = parser.parse_args()
    local_example()
    if args.target:
        for name in ("A", "B"):
            with ServiceClient(name) as service:
                packet = service.item()  # Already decoded to bytes by the client.
                print(f"Service {name}: item={len(packet)} bytes; original={service.query(packet)}; queries={service.queries}")


if __name__ == "__main__":
    main()
