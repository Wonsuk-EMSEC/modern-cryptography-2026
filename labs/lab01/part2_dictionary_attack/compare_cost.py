#!/usr/bin/env python3
"""Run the two completed student attack implementations and compare work."""
import argparse
from pathlib import Path
from crack_unsalted import crack as unsalted
from crack_salted import crack as salted


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("data", type=Path, nargs="?", default=Path("../data"))
    args = parser.parse_args()
    wordlist = args.data / "lab01-small.txt"
    rows = [
        ("unsalted", unsalted(args.data / "unsalted_hashes.csv", wordlist)),
        ("salted", salted(args.data / "salted_hashes.csv", wordlist)),
    ]
    print(f"{'experiment':<12} {'found':>5} {'hashes':>8} {'seconds':>10} {'hashes/s':>12}")
    for name, (found, count, elapsed) in rows:
        print(f"{name:<12} {len(found):>5} {count:>8} {elapsed:>10.6f} {count / elapsed:>12.0f}")


if __name__ == "__main__":
    main()
