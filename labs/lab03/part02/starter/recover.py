"""Recover the whole PDF; never hardcode a seed, key, receipt, or plaintext.

Use glibc srand/rand (ctypes is available in Python's standard library).
The public IV lets you screen candidate seeds before attempting AES decryption.
"""
import argparse
import json
from pathlib import Path


def recover(encrypted: bytes, start: int, end: int) -> bytes:
    """Search the inclusive epoch-second interval and return the complete PDF."""
    raise NotImplementedError("TODO: reproduce C rand(), recover key, decrypt and validate")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("recovered.pdf"))
    parser.add_argument("--data-dir", type=Path, default=Path(__file__).resolve().parents[1] / "data")
    args = parser.parse_args()
    data = args.data_dir
    info = json.loads((data / "challenge.json").read_text())
    pdf = recover((data / "confidential_report.enc").read_bytes(),
                  info["start_epoch"], info["end_epoch"])
    args.output.write_bytes(pdf)
    print(f"Recovered {len(pdf)} PDF bytes")
