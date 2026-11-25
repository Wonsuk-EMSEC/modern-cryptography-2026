#!/usr/bin/env python3
"""Open an encrypted PKCS#8 private key and check its public key."""

from __future__ import annotations

import argparse
from getpass import getpass
import hashlib
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


PART = Path(__file__).resolve().parent
ENCRYPTED_KEY = PART / "output/private_encrypted.pem"
PUBLIC_KEY = PART / "output/public.pem"


def decrypt_key(encrypted_pem: bytes, password: bytes) -> rsa.RSAPrivateKey:
    """Return the RSA private key opened with its known password."""
    # The OpenSSL command in the README creates an encrypted PKCS#8 PEM.
    if not encrypted_pem.startswith(b"-----BEGIN ENCRYPTED PRIVATE KEY-----"):
        raise ValueError("expected an encrypted PKCS#8 PEM file")

    # TODO: Pass encrypted_pem and the password bytes to
    # serialization.load_pem_private_key(). Return the RSA private key;
    # let an incorrect password raise ValueError.
    raise NotImplementedError("decrypt the encrypted private key")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--encrypted-key", type=Path, default=ENCRYPTED_KEY)
    parser.add_argument("--public-key", type=Path, default=PUBLIC_KEY)
    args = parser.parse_args()

    encrypted_pem = args.encrypted_key.read_bytes()
    public_pem = args.public_key.read_bytes()
    password = getpass("Part01 private-key password: ").encode("utf-8")
    try:
        private_key = decrypt_key(encrypted_pem, password)
    except ValueError as error:
        raise SystemExit("Could not open the private key with that password") from error

    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise TypeError("the decrypted key must be an RSA private key")
    public_key = serialization.load_pem_public_key(public_pem)
    if not isinstance(public_key, rsa.RSAPublicKey):
        raise TypeError("the public-key file must contain an RSA public key")
    expected = public_key.public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    actual = private_key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    if actual != expected:
        raise RuntimeError("the decrypted private key does not match public.pem")

    print(f"Encrypted private key: {args.encrypted_key}")
    print(f"Public key: {args.public_key}")
    print("Private/public key match: OK")
    print("LAB04{" + hashlib.sha256(expected).hexdigest()[:16] + "}")


if __name__ == "__main__":
    main()
