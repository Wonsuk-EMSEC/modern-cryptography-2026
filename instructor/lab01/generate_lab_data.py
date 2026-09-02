#!/usr/bin/env python3
"""Regenerate deterministic Lab 01 fixtures without writing an answer key."""
import csv
import hashlib
import subprocess
from pathlib import Path

import generate_data

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "labs/lab01/data"
WORDS = ["classroom1", "cryptolab", "correct-horse", "packet-free", "seoul2026",
         "offline-only", "wirelesslab", "moderncrypto"]
RECORDS = [("student_aurora", "cryptolab"), ("student_cedar", "moderncrypto")]


def main() -> None:
    generate_data.main()
    (DATA / "lab01-small.txt").write_text("\n".join(WORDS) + "\n")
    with (DATA / "unsalted_hashes.csv").open("w", newline="") as stream:
        writer = csv.writer(stream); writer.writerow(("account", "sha256"))
        for account, password in RECORDS:
            writer.writerow((account, hashlib.sha256(password.encode()).hexdigest()))
    with (DATA / "salted_hashes.csv").open("w", newline="") as stream:
        writer = csv.writer(stream); writer.writerow(("account", "salt_hex", "sha256"))
        for index, (account, password) in enumerate(RECORDS, 1):
            salt = f"acct-{index:02d}".encode().ljust(16, b"\0")
            writer.writerow((account, salt.hex(), hashlib.sha256(salt + password.encode()).hexdigest()))
    shadow = subprocess.run(
        ["openssl", "passwd", "-6", "-salt", "classroom", "cryptolab"],
        check=True, capture_output=True, text=True,
    ).stdout.strip()
    (DATA / "linux_hashes.txt").write_text(f"student_orchid:{shadow}:20000:0:99999:7:::\n")


if __name__ == "__main__":
    main()
