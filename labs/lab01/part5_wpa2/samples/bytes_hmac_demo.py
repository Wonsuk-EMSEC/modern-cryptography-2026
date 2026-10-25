#!/usr/bin/env python3
"""Public byte/HMAC/KDF primitives, independent of any captured WPA2 key."""
import hashlib
import hmac
import json


def main() -> None:
    # JSON represents bytes as hexadecimal text; decode before sorting/slicing.
    record = json.loads('{"left": "0201", "right": "0102"}')
    ordered = sorted(bytes.fromhex(record[key]) for key in ("left", "right"))
    print(f"Ordered public bytes: {b''.join(ordered).hex()}")
    message = bytearray(b"public-data")
    message[0:2] = bytes(2)
    print(f"Cleared first two bytes: {bytes(message).hex()}")
    # This sample uses SHA-256 and 1000 iterations; use the README's WPA2
    # parameters in the exercise rather than copying these public toy choices.
    derived = hashlib.pbkdf2_hmac("sha256", b"public-password", b"public-salt", 1000, dklen=16)
    tag = hmac.new(derived, bytes(message), hashlib.sha256).digest()
    print(f"Toy KDF bytes: {len(derived)}")
    print(f"SHA-256 HMAC bytes: {len(tag)}")
    print(f"Truncated example bytes: {len(tag[:8])}")
    print(f"Same message verifies: {hmac.compare_digest(tag, hmac.new(derived, bytes(message), hashlib.sha256).digest())}")
    print(f"Changed message verifies: {hmac.compare_digest(tag, hmac.new(derived, bytes(message) + b'!', hashlib.sha256).digest())}")


if __name__ == "__main__":
    main()
