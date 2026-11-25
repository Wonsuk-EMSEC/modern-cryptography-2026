"""Try a local word list against an encrypted PKCS#8 key and open a challenge."""

from __future__ import annotations

from pathlib import Path
import time

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


PART = Path(__file__).resolve().parent


def find_password(encrypted_key: bytes, candidates: list[str]) -> tuple[bytes, int]:
    """Return (UTF-8 password bytes, attempts), including the successful try.

    Try each nonempty word in order with serialization.load_der_private_key().
    A candidate that cannot unlock this key is not a match. Raise ValueError if
    the list has no match. Do not print the password or decrypted private key.
    """
    attempts = 0
    for candidate in candidates:
        if not candidate:
            continue
        attempts += 1
        password = candidate.encode("utf-8")
        # TODO: Try serialization.load_der_private_key(encrypted_key, password=...).
        # A wrong password raises ValueError; continue to the next candidate.
        # When a key opens, return (password, attempts). If none opens, raise
        # ValueError instead of printing a password or a private key.
    raise NotImplementedError("try the candidate passwords against the key")


def main() -> None:
    data = PART / "data"
    encrypted_key = (data / "encrypted_key.der").read_bytes()
    candidates = (data / "wordlist.txt").read_text(encoding="utf-8").splitlines()

    start = time.perf_counter()
    password, attempts = find_password(encrypted_key, candidates)
    elapsed = time.perf_counter() - start

    key = serialization.load_der_private_key(encrypted_key, password=password)
    if not isinstance(key, rsa.RSAPrivateKey):
        raise ValueError("the challenge expects an RSA private key")
    certificate = x509.load_pem_x509_certificate((data / "certificate.crt").read_bytes())
    actual_public = key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    expected_public = certificate.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo
    )
    if actual_public != expected_public:
        raise ValueError("the recovered key does not match the certificate")

    ciphertext = (data / "flag.enc").read_bytes()
    flag = key.decrypt(
        ciphertext,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    ).decode("ascii")
    print(f"Attempts: {attempts}")
    print(f"Elapsed seconds: {elapsed:.3f}")
    print(f"Attempts per second: {attempts / elapsed:.1f}" if elapsed else "Elapsed too short to measure")
    print(flag)


if __name__ == "__main__":
    main()
