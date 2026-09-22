#!/usr/bin/env python3
"""Optional Part 7 experiment: repeat one CPA byte attack with more traces."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np

try:
    from .starter import recover_key_byte
except ImportError:  # pragma: no cover - direct execution.
    from starter import recover_key_byte


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--byte", type=int, default=0, dest="byte_index")
    parser.add_argument("--counts", type=int, nargs="+",
                        default=[10, 25, 50, 100, 200, 400, 550])
    args = parser.parse_args()
    data = Path(__file__).with_name("data")
    plaintexts = np.load(data / "plaintexts.npy", allow_pickle=False)
    traces = np.load(data / "traces.npy", allow_pickle=False)
    if not 0 <= args.byte_index < 16:
        parser.error("byte must be in 0..15")
    print("traces  recovered_byte")
    for count in args.counts:
        if not 2 <= count <= len(traces):
            parser.error(f"trace counts must be between 2 and {len(traces)}")
        guess = recover_key_byte(traces[:count], plaintexts[:count], args.byte_index)
        print(f"{count:6d}  0x{guess:02x}")


if __name__ == "__main__":
    main()
