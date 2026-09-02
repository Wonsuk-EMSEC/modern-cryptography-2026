#!/usr/bin/env python3
"""Compute an educational SHA-256 password digest."""
import getpass
import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    print("Educational demo only; SHA-256 alone is unsafe for password storage.")
    print(hash_password(getpass.getpass("Password: ")))
