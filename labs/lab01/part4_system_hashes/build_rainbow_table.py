#!/usr/bin/env python3
"""Student starter: build a rainbow-table-like chain endpoint structure."""

from __future__ import annotations

import argparse
import random
import time
from pathlib import Path

from table_common import hash_password, load_config, password_space, write_json

MIX_CONSTANT = 0x9E3779B1


def reduce_digest(digest_hex: str, column: int, alphabet: str, length: int) -> str:
    """Map a digest and column back into the configured password space."""
    # TODO: combine the digest integer with column * MIX_CONSTANT, reduce it
    # modulo len(alphabet) ** length, then encode it as exactly length base-N
    # characters from alphabet.
    raise NotImplementedError


def choose_starts(config: dict[str, int | str]) -> list[str]:
    """Choose deterministic, unique chain starts from the toy space."""
    candidates = list(password_space(str(config["alphabet"]), int(config["password_length"])))
    return random.Random(int(config["seed"])).sample(candidates, int(config["chain_count"]))


def chain_endpoint(start: str, config: dict[str, int | str]) -> str:
    """Walk one hash/reduction chain and return only its endpoint."""
    # TODO: for columns 0..chain_length-1, hash the current password and apply
    # the column-specific reduction.
    raise NotImplementedError


def build_table(config: dict[str, int | str]) -> dict[str, list[str]]:
    """Map each endpoint to all starts that reach it, preserving chain merges."""
    # TODO: choose starts, calculate each endpoint, and use setdefault so two
    # starts that merge at the same endpoint are both retained.
    raise NotImplementedError


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    config = load_config(args.config)
    started = time.perf_counter()
    endpoints = build_table(config)
    elapsed = time.perf_counter() - started
    build_hashes = int(config["chain_count"]) * int(config["chain_length"])
    payload: dict[str, object] = {
        "type": "rainbow-endpoints",
        "config": config,
        "build_hashes": build_hashes,
        "build_seconds": elapsed,
        "endpoints": endpoints,
    }
    write_json(args.output, payload)
    print(f"Starts: {config['chain_count']}")
    print(f"Distinct endpoints: {len(endpoints)}")
    print(f"Build hashes: {build_hashes}")
    print(f"Build time: {elapsed:.6f} seconds")
    print(f"File size: {args.output.stat().st_size} bytes")


if __name__ == "__main__":
    main()
