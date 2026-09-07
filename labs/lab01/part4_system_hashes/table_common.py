#!/usr/bin/env python3
"""Shared, non-solution helpers for the Part 4 table experiments."""

from __future__ import annotations

import hashlib
import itertools
import json
from collections.abc import Iterator
from pathlib import Path


def hash_password(password: str, algorithm: str = "sha256") -> str:
    """Hash one ASCII toy password and return lowercase hexadecimal."""
    return hashlib.new(algorithm, password.encode("ascii")).hexdigest()


def password_space(alphabet: str, length: int) -> Iterator[str]:
    """Yield the fixed-length password space in deterministic order."""
    for characters in itertools.product(alphabet, repeat=length):
        yield "".join(characters)


def load_config(path: Path) -> dict[str, int | str]:
    """Load and validate the bounded classroom configuration."""
    config = json.loads(path.read_text(encoding="utf-8"))
    required = {"algorithm", "alphabet", "password_length", "chain_length", "chain_count", "seed"}
    if not required <= config.keys():
        raise ValueError(f"missing configuration keys: {sorted(required - config.keys())}")
    alphabet = str(config["alphabet"])
    length = int(config["password_length"])
    space_size = len(alphabet) ** length
    if not alphabet or len(set(alphabet)) != len(alphabet):
        raise ValueError("alphabet must contain unique characters")
    if length < 1 or space_size > 10_000:
        raise ValueError("toy password space must contain between 1 and 10,000 candidates")
    if not 1 <= int(config["chain_count"]) <= space_size:
        raise ValueError("chain_count must fit inside the password space")
    if not 1 <= int(config["chain_length"]) <= 100:
        raise ValueError("chain_length must be between 1 and 100")
    return config


def write_json(path: Path, value: dict[str, object]) -> None:
    """Write a readable generated artifact, creating its directory if needed."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")
