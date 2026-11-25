#!/usr/bin/env python3
"""Find the MD5 collision among the provided binary samples."""

from __future__ import annotations

import hashlib
from pathlib import Path


DATA = Path(__file__).resolve().parent / "data"


def find_collision(samples: list[Path]) -> tuple[Path, Path]:
    """Return two distinct files with different bytes and the same MD5 digest."""
    # TODO: read every sample, group by MD5, and return the collision pair.
    raise NotImplementedError("find the two different samples with matching MD5")


def main() -> None:
    samples = sorted(DATA.glob("sample_*.bin"))
    first, second = find_collision(samples)
    a, b = first.read_bytes(), second.read_bytes()
    if first == second or a == b or hashlib.md5(a).digest() != hashlib.md5(b).digest():
        raise ValueError("the selected files are not a collision")
    if hashlib.sha256(a).digest() == hashlib.sha256(b).digest():
        raise ValueError("SHA-256 comparison did not distinguish the samples")
    print("files:", first.name, second.name)
    print("MD5:", hashlib.md5(a).hexdigest())
    print("SHA-256 #1:", hashlib.sha256(a).hexdigest())
    print("SHA-256 #2:", hashlib.sha256(b).hexdigest())
    left, right = sorted((a, b))
    completion = hashlib.sha256(b"lab04-part05:" + left + right).hexdigest()[:16]
    print(f"LAB04{{{completion}}}")


if __name__ == "__main__":
    main()
