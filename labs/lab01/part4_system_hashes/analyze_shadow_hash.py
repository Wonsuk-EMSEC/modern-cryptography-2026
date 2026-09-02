#!/usr/bin/env python3
"""Parse supplied shadow-style records; never reads /etc/shadow."""
import argparse
from pathlib import Path

ALGORITHMS = {"1": "MD5-crypt", "5": "SHA-256-crypt", "6": "SHA-512-crypt", "y": "yescrypt"}


def parse_record(line: str) -> dict[str, str]:
    account, encoded, *_ = line.strip().split(":")
    fields = encoded.split("$")
    if len(fields) < 4:
        raise ValueError("expected a $id$salt$verifier shadow-style record")
    return {"account": account, "id": fields[1], "algorithm": ALGORITHMS.get(fields[1], "unknown"),
            "salt_or_parameters": fields[2], "verifier": "$".join(fields[3:])}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("file", type=Path); args = parser.parse_args()
    for line in args.file.read_text().splitlines():
        if line.strip() and not line.startswith("#"): print(parse_record(line))
