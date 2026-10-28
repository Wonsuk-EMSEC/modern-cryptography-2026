#!/usr/bin/env python3
"""Run one Part's local feedback checker from the shared workspace."""
from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--part", type=int, choices=range(1, 9), required=True)
    args, extra = parser.parse_known_args()
    checker = Path(__file__).parent / f"part{args.part:02d}" / "tests" / "check.py"
    try:
        return subprocess.run([sys.executable, str(checker), *extra], timeout=180).returncode
    except subprocess.TimeoutExpired:
        print("Local checker exceeded the 180 second limit.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
