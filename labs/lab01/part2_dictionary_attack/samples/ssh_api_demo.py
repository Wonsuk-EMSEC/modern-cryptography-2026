#!/usr/bin/env python3
"""Offline Paramiko API sample: no authentication or network connection."""
import argparse
import time
from pathlib import Path

import paramiko


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--notes", type=Path, help="optional local text file to count")
    args = parser.parse_args()
    # This shows CLI/file handling, independent of the exercise wordlist.
    notes = args.notes.read_text(encoding="utf-8").splitlines() if args.notes else ["public", "sample"]
    print(f"Nonempty lines: {sum(bool(line.strip()) for line in notes)}")
    started = time.perf_counter()
    client = paramiko.SSHClient()
    try:
        # Only the disposable Compose target permits this policy in the exercise.
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        print(f"Client class: {type(client).__name__}")
        print(f"Transport before connect: {client.get_transport()}")
        print(f"Authentication error type: {paramiko.AuthenticationException.__name__}")
    finally:
        # finally runs on success and when the body raises an exception.
        client.close()
    print("Client closed; no network request sent")
    print(f"Elapsed: {time.perf_counter() - started:.6f} seconds")


if __name__ == "__main__":
    main()
