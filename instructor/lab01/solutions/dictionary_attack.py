#!/usr/bin/env python3
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Iterable


def load_dictionary(path: str | Path) -> list[str]:
    return [line.strip() for line in Path(path).read_text(encoding="utf-8").splitlines() if line.strip()]


def crack_hashes(targets: Iterable[str], candidates: Iterable[str], algorithm: str = "sha256") -> dict[str, str]:
    wanted = {target.strip().lower() for target in targets if target.strip()}
    found: dict[str, str] = {}
    for candidate in candidates:
        digest = hashlib.new(algorithm, candidate.encode("utf-8")).hexdigest()
        if digest in wanted:
            found[digest] = candidate
    return found
