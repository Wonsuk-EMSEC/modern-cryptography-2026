#!/usr/bin/env python3
"""Student starter: build a full digest-to-password precomputation table."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

from table_common import hash_password, load_config, password_space, write_json


def build_table(config: dict[str, int | str]) -> dict[str, str]:
    """Return every digest-to-password pair in the configured toy space."""
    # TODO: enumerate password_space(), hash every password exactly once, and
    # map each lowercase digest to its password.
    raise NotImplementedError


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("config", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    config = load_config(args.config)
    started = time.perf_counter()
    entries = build_table(config)
    elapsed = time.perf_counter() - started
    payload: dict[str, object] = {
        "type": "full-precomputation",
        "config": config,
        "build_hashes": len(entries),
        "build_seconds": elapsed,
        "entries": entries,
    }
    write_json(args.output, payload)
    print(f"Entries: {len(entries)}")
    print(f"Build hashes: {len(entries)}")
    print(f"Build time: {elapsed:.6f} seconds")
    print(f"File size: {args.output.stat().st_size} bytes")


if __name__ == "__main__":
    main()
