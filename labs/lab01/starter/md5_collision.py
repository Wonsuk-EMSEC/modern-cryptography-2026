#!/usr/bin/env python3
"""Student starter for comparing the supplied MD5 collision files."""

from __future__ import annotations

import hashlib
from pathlib import Path


def digest_file(path: str | Path, algorithm: str) -> str:
    """Return the lowercase hexadecimal digest of a file read as binary."""
    # TODO: stream the file into hashlib.new(algorithm) in chunks.
    raise NotImplementedError


def files_are_distinct(first: str | Path, second: str | Path) -> bool:
    """Return True exactly when the files contain different bytes."""
    # TODO: compare binary contents (or chunks), not filenames.
    raise NotImplementedError
