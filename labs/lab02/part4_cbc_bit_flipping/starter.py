#!/usr/bin/env python3
"""Part 4 starter: change admin=0 to admin=1 without the AES key."""

from __future__ import annotations

import base64

import client


def forge_admin_token(normal_token: str) -> str:
    packet = bytearray(base64.b64decode(normal_token, validate=True))
    # The first plaintext block starts with b"admin=0;". The first 16 packet
    # bytes are the IV, which acts as the preceding block for plaintext block 0.
    # TODO: XOR the correct IV byte with the difference between b"0" and b"1".
    raise NotImplementedError


def main() -> None:
    normal = client.issue()
    print("normal:", client.verify(normal))
    forged = forge_admin_token(normal)
    print("modified:", client.verify(forged))


if __name__ == "__main__":
    main()
