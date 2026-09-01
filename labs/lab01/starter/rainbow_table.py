#!/usr/bin/env python3
"""Student starter for a small rainbow-table-like experiment."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("ascii")).hexdigest()


def reduce_digest(digest_hex: str, column: int, alphabet: str, length: int) -> str:
    """Deterministically map a digest and chain column into the password space."""
    # TODO: interpret the digest as an integer, mix in column, and encode in base
    # len(alphabet), producing exactly `length` characters.
    raise NotImplementedError


def chain_endpoint(start: str, chain_length: int, alphabet: str, length: int) -> str:
    """Walk a chain and return its final password value."""
    # TODO: alternate hash_password and reduce_digest for each column.
    raise NotImplementedError


def generate_table(
    starts: list[str], chain_length: int, alphabet: str, length: int
) -> dict[str, list[str]]:
    """Map each endpoint to one or more starts; retain merged chains."""
    # TODO: store endpoints only. Multiple starts can share an endpoint.
    raise NotImplementedError


def lookup(
    target_digest: str,
    table: dict[str, list[str]],
    chain_length: int,
    alphabet: str,
    length: int,
) -> str | None:
    """Recover a password for target_digest, or return None."""
    # TODO: try possible target columns, search endpoints, then reconstruct and
    # verify candidate chains to eliminate false alarms.
    raise NotImplementedError


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("config")
    parser.add_argument("targets")
    args = parser.parse_args()
    config = json.loads(Path(args.config).read_text(encoding="utf-8"))
    table = generate_table(
        config["starts"], config["chain_length"], config["alphabet"], config["length"]
    )
    for digest in Path(args.targets).read_text(encoding="ascii").splitlines():
        result = lookup(
            digest, table, config["chain_length"], config["alphabet"], config["length"]
        )
        print(f"{digest}: {result if result is not None else 'not found'}")


if __name__ == "__main__":
    main()
