#!/usr/bin/env python3
"""Starter for cracking instructor-provided toy unsalted SHA-256 hashes."""
import argparse
from pathlib import Path


def crack(target_csv: Path, wordlist: Path) -> tuple[dict[str, str], int, float]:
    """Return recovered fictional accounts, computation count, and seconds."""
    # TODO: parse account,sha256; hash every candidate once; use perf_counter.
    raise NotImplementedError


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("targets", type=Path)
    parser.add_argument("wordlist", type=Path)
    args = parser.parse_args()
    print(crack(args.targets, args.wordlist))
