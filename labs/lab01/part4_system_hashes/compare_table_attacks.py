#!/usr/bin/env python3
"""Student starter: crack one toy database with full and rainbow tables."""

from __future__ import annotations

import argparse
import csv
import json
import time
from pathlib import Path

from build_rainbow_table import reduce_digest
from table_common import hash_password


def load_database(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows or set(rows[0]) != {"account", "sha256"}:
        raise ValueError("database schema must be account,sha256")
    return rows


def lookup_precomputation(digest: str, entries: dict[str, str]) -> tuple[str | None, int]:
    """Return a full-table match and the number of new hash computations."""
    # TODO: use the digest as a dictionary key. Lookup should compute no hashes.
    raise NotImplementedError


def lookup_rainbow(
    digest: str,
    endpoints: dict[str, list[str]],
    config: dict[str, int | str],
) -> tuple[str | None, int]:
    """Reconstruct candidate chains; return match and hashes computed."""
    # TODO: try every possible target column from last to first. Advance the
    # target digest to a possible endpoint, then replay each matching start from
    # column zero. Verify the original digest before returning a password.
    raise NotImplementedError


def attack_database(
    database: list[dict[str, str]],
    lookup,
) -> tuple[dict[str, str], int, float]:
    recovered: dict[str, str] = {}
    computations = 0
    started = time.perf_counter()
    for row in database:
        password, used = lookup(row["sha256"].lower())
        computations += used
        if password is not None:
            recovered[row["account"]] = password
    return recovered, computations, time.perf_counter() - started


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path)
    parser.add_argument("precomputation_table", type=Path)
    parser.add_argument("rainbow_table", type=Path)
    args = parser.parse_args()
    database = load_database(args.database)
    full = json.loads(args.precomputation_table.read_text(encoding="utf-8"))
    rainbow = json.loads(args.rainbow_table.read_text(encoding="utf-8"))
    methods = (
        (
            "full",
            lambda digest: lookup_precomputation(digest, full["entries"]),
            args.precomputation_table,
            len(full["entries"]),
            "-",
            int(full["build_hashes"]),
            float(full["build_seconds"]),
        ),
        (
            "rainbow",
            lambda digest: lookup_rainbow(digest, rainbow["endpoints"], rainbow["config"]),
            args.rainbow_table,
            sum(len(starts) for starts in rainbow["endpoints"].values()),
            str(len(rainbow["endpoints"])),
            int(rainbow["build_hashes"]),
            float(rainbow["build_seconds"]),
        ),
    )
    print(
        f"{'method':<10} {'recovered':>10} {'build hashes':>12} {'build sec':>10} "
        f"{'records':>8} {'endpoints':>10} {'bytes':>10} {'lookup hashes':>14} {'lookup sec':>10}"
    )
    for name, lookup, path, stored, endpoints, build_hashes, build_seconds in methods:
        recovered, computations, elapsed = attack_database(database, lookup)
        print(
            f"{name:<10} {len(recovered):>7}/{len(database):<2} {build_hashes:>12} "
            f"{build_seconds:>10.6f} {stored:>8} {endpoints:>10} "
            f"{path.stat().st_size:>10} {computations:>14} {elapsed:>10.6f}"
        )


if __name__ == "__main__":
    main()
