#!/usr/bin/env python3
"""Part 5 starter: recover CBC plaintext using padding validity only."""

from __future__ import annotations

from pathlib import Path
from typing import Callable

from oracle_client import OracleClient

BLOCK = 16


def recover_block(previous: bytes, target: bytes,
                  query: Callable[[bytes], bool]) -> bytes:
    """Recover one plaintext block from a two-block oracle packet."""
    # TODO: work from byte 15 to byte 0. Maintain the intermediate value
    # D_K(target), force padding 01, then 02 02, and so on. Account for the
    # possible false positive when searching for padding length 1.
    raise NotImplementedError


def recover_plaintext(packet: bytes, query: Callable[[bytes], bool]) -> bytes:
    """Recover and PKCS#7-unpad every ciphertext block after the IV."""
    # TODO: split IV || ciphertext into blocks and call recover_block for each.
    raise NotImplementedError


def main() -> None:
    packet = (Path(__file__).with_name("data") / "ciphertext.hex").read_text().strip()
    with OracleClient() as oracle:
        plaintext = recover_plaintext(bytes.fromhex(packet), oracle.query)
        print(plaintext.decode("ascii"))
        print(f"oracle queries: {oracle.queries}")


if __name__ == "__main__":
    main()
