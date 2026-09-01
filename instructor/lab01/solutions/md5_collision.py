#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path


def digest_file(path: str | Path, algorithm: str) -> str:
    digest = hashlib.new(algorithm)
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(8192), b""):
            digest.update(chunk)
    return digest.hexdigest()


def files_are_distinct(first: str | Path, second: str | Path) -> bool:
    return Path(first).read_bytes() != Path(second).read_bytes()
