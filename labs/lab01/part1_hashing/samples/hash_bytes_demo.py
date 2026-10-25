#!/usr/bin/env python3
"""Public byte-message sample; no classroom target password is used."""
import argparse
import hashlib
from pathlib import Path


def inspect_message(message: bytes) -> None:
    # Hash objects accept bytes. digest() returns bytes; hexdigest() is text.
    digest = hashlib.sha256(message)
    print(f"Input bytes: {message!r}")
    print(f"Input length: {len(message)}")
    print(f"Digest bytes: {len(digest.digest())}")
    print(f"Hex characters: {len(digest.hexdigest())}")
    print(f"SHA-256: {digest.hexdigest()}")
    print(f"Repeat matches: {digest.digest() == hashlib.sha256(message).digest()}")


def main() -> None:
    # An optional local input demonstrates Path.read_bytes and CLI parsing.
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, help="optional local byte-message file")
    args = parser.parse_args()
    message = args.input.read_bytes() if args.input else "Public sample".encode("utf-8")
    inspect_message(message)


if __name__ == "__main__":
    main()
