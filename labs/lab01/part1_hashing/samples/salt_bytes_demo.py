#!/usr/bin/env python3
"""Public salt/byte-message example for understanding concatenation."""
import hashlib
import secrets


def main() -> None:
    message = b"Public sample"
    # A salt is bytes, and its hexadecimal representation can be stored as text.
    salt = secrets.token_bytes(16)
    restored = bytes.fromhex(salt.hex())
    verifier = hashlib.sha256(salt + message).hexdigest()
    print(f"Salt bytes: {len(salt)}")
    print(f"Salt hex: {salt.hex()}")
    print(f"Salt round trip: {restored == salt}")
    print(f"Verifier: {verifier}")
    print(f"Same salt repeats: {verifier == hashlib.sha256(restored + message).hexdigest()}")
    print(f"Changed salt differs: {verifier != hashlib.sha256(bytes(16) + message).hexdigest()}")
    print("Fast SHA-256 is only a mechanics demonstration, not a password KDF.")


if __name__ == "__main__":
    main()
