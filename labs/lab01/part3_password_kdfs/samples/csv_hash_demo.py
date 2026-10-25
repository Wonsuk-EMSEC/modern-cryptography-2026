#!/usr/bin/env python3
"""Public single-candidate CSV example, not a dictionary-attack solution."""
import csv
import hashlib
import tempfile
import time
from pathlib import Path


def main() -> None:
    # All example values are public. TemporaryDirectory cleans up the file.
    candidate = "public-example"
    salt = b"public-salt"
    expected = hashlib.sha256(salt + candidate.encode("utf-8")).hexdigest()
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "example.csv"
        with path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.DictWriter(stream, fieldnames=["account", "salt_hex", "sha256"])
            writer.writeheader()
            writer.writerow({"account": "example", "salt_hex": salt.hex(), "sha256": expected})
        with path.open(newline="", encoding="utf-8") as stream:
            row = next(csv.DictReader(stream))
        started = time.perf_counter()
        computed = hashlib.sha256(bytes.fromhex(row["salt_hex"]) + candidate.encode("utf-8")).hexdigest()
        elapsed = time.perf_counter() - started
        print(f"CSV fields: {', '.join(row)}")
        print(f"Account: {row['account']}")
        print(f"Salt bytes: {len(bytes.fromhex(row['salt_hex']))}")
        print(f"Single candidate matches: {computed == row['sha256']}")
        print("Hash computations: 1")
        print(f"Elapsed: {elapsed:.6f} seconds")


if __name__ == "__main__":
    main()
