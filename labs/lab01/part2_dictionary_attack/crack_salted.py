#!/usr/bin/env python3
"""Starter for cracking toy SHA256(salt || password) records."""
import argparse
from pathlib import Path


def crack(target_csv: Path, wordlist: Path) -> tuple[dict[str, str], int, float]:
    """Return recovered fictional accounts, computation count, and seconds."""
    # TODO: parse account,salt_hex,sha256; hash every candidate separately per salt.
    raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("targets", type=Path)
    parser.add_argument("wordlist", type=Path)
    args = parser.parse_args()
    print(crack(args.targets, args.wordlist))
