#!/usr/bin/env python3
"""Student starter for an offline dictionary attack."""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Iterable


def load_dictionary(path: str | Path) -> list[str]:
    """Return non-empty password candidates from *path*, in file order."""
    # TODO: read the file and strip line endings/blank lines.
    raise NotImplementedError


def crack_hashes(
    targets: Iterable[str], candidates: Iterable[str], algorithm: str = "sha256"
) -> dict[str, str]:
    """Map each recovered normalized target digest to its candidate password."""
    # TODO: hash each candidate once and compare it with the target set.
    raise NotImplementedError


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("dictionary")
    parser.add_argument("targets")
    parser.add_argument("--algorithm", default="sha256")
    args = parser.parse_args()
    targets = Path(args.targets).read_text(encoding="utf-8").splitlines()
    recovered = crack_hashes(targets, load_dictionary(args.dictionary), args.algorithm)
    for digest, password in recovered.items():
        print(f"{digest}: {password}")


if __name__ == "__main__":
    main()
