#!/usr/bin/env python3
"""Public table-building ingredients without constructing an attack table."""
import json
import random
import sys
import tempfile
from pathlib import Path

# Directly running a samples/ script puts samples/ on sys.path, so add the Part.
PART_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PART_DIR))
from table_common import hash_password, load_config, password_space, write_json


def main() -> None:
    config = load_config(PART_DIR / "data" / "rainbow_lab_config.json")
    print(f"Configured space: {len(str(config['alphabet'])) ** int(config['password_length'])}")
    print(f"Public tiny space: {list(password_space('ab', 2))}")
    print(f"Digest hex characters: {len(hash_password('public'))}")
    # Conversion primitives used when reasoning about a reduction function.
    value = int("0f", 16)
    quotient, remainder = divmod(value, 6)
    print(f"Hex 0f as integer: {value}; divmod by 6: {quotient}, {remainder}")
    print(f"Seeded public choices: {random.Random(2026).sample(['a', 'b', 'c', 'd'], 2)}")
    # Grouping preserves every value when multiple items share a key.
    groups = {}
    for label in ["first", "second"]:
        groups.setdefault("shared", []).append(label)
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "public.json"
        write_json(path, {"type": "public-example", "groups": groups})
        restored = json.loads(path.read_text(encoding="utf-8"))
        print(f"Grouped values after JSON round trip: {restored['groups']['shared']}")
        print(f"Temporary JSON exists: {path.exists()}")
    print("Temporary JSON removed")


if __name__ == "__main__":
    main()
