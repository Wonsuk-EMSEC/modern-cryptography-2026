#!/usr/bin/env python3
"""Demonstrate SHA256(salt || password); not production password storage."""
import getpass
import hashlib
import secrets


def salted_hash(password: str, salt: bytes) -> str:
    return hashlib.sha256(salt + password.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    value = getpass.getpass("Password: ")
    random_salt = secrets.token_bytes(16)
    print(f"salt={random_salt.hex()}")
    print(f"digest={salted_hash(value, random_salt)}")
    print("Educational demo only; use a password KDF in production.")
