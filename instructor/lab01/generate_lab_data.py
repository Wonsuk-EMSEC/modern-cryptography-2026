#!/usr/bin/env python3
"""Regenerate deterministic Lab 01 fixtures without writing an answer key."""
import csv
import hashlib
import json
import subprocess
from pathlib import Path

import generate_data

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "labs/lab01/data"
WORDS = ["classroom1", "cryptolab", "correct-horse", "packet-free", "seoul2026",
         "offline-only", "wirelesslab", "moderncrypto"]
RECORDS = [("student_aurora", "cryptolab"), ("student_cedar", "moderncrypto")]
RAINBOW_CONFIG = {
    "algorithm": "sha256",
    "alphabet": "abc123",
    "password_length": 4,
    "chain_length": 12,
    "chain_count": 96,
    "seed": 2026,
}
RAINBOW_RECORDS = [
    ("student_maple", "121a"),
    ("student_river", "1cac"),
    ("student_sunset", "2cc1"),
    ("student_willow", "cbca"),
    ("student_zephyr", "a13a"),
]


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
    (DATA / "rainbow_lab_config.json").write_text(
        json.dumps(RAINBOW_CONFIG, indent=2) + "\n", encoding="utf-8"
    )
    with (DATA / "rainbow_password_database.csv").open("w", newline="") as stream:
        writer = csv.writer(stream, lineterminator="\n")
        writer.writerow(("account", "sha256"))
        for account, password in RAINBOW_RECORDS:
            writer.writerow((account, hashlib.sha256(password.encode("ascii")).hexdigest()))


if __name__ == "__main__":
    main()
