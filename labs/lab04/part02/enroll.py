#!/usr/bin/env python3
"""Use the key from Part01 to request a server certificate from lab04-ca."""

from __future__ import annotations

import argparse
from getpass import getpass
import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization


PART = Path(__file__).resolve().parent
KEY = PART.parent / "part01/output/private_encrypted.pem"
HOSTNAME = "lab04.local.test"
DEFAULT_CA_URL = "http://lab04-ca:8080"


def make_csr(private_key, hostname: str) -> bytes:
    """Create a PEM CSR with this key and hostname in subjectAltName."""
    # TODO: Build and sign a CSR. Put hostname in DNS subjectAltName;
    # use SHA-256 and return PEM bytes. The key stays in this container.
    raise NotImplementedError("create a CSR with DNS subjectAltName")


def request_certificate(csr_pem: bytes, ca_url: str) -> dict[str, str]:
    payload = json.dumps({"csr_pem": csr_pem.decode("ascii")}).encode("utf-8")
    request = Request(ca_url.rstrip("/") + "/issue", data=payload,
                      method="POST", headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=10) as response:
            answer = json.load(response)
    except HTTPError as error:
        detail = error.read(1000).decode(errors="replace")
        raise RuntimeError(f"CA rejected request (HTTP {error.code}): {detail}") from error
    except URLError as error:
        raise RuntimeError(f"CA unavailable at {ca_url}: {error.reason}") from error
    if not isinstance(answer, dict) or not all(
        isinstance(answer.get(name), str)
        for name in ("certificate_pem", "intermediate_pem", "root_pem")
    ):
        raise RuntimeError("CA returned an incomplete certificate response")
    return answer


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--key", type=Path, default=KEY)
    parser.add_argument("--output-dir", type=Path, default=PART / "output")
    parser.add_argument("--url", default=os.environ.get("LAB04_CA_URL", DEFAULT_CA_URL))
    args = parser.parse_args()
    password = getpass("Part01 private-key password: ")
    private_key = serialization.load_pem_private_key(args.key.read_bytes(), password.encode())
    csr_pem = make_csr(private_key, HOSTNAME)
    csr = x509.load_pem_x509_csr(csr_pem)
    if not csr.is_signature_valid:
        raise RuntimeError("CSR signature verification failed")
    answer = request_certificate(csr_pem, args.url)
    certificate = x509.load_pem_x509_certificate(answer["certificate_pem"].encode())
    expected = private_key.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    actual = certificate.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    if expected != actual:
        raise RuntimeError("issued certificate has a different public key")
    if HOSTNAME not in certificate.extensions.get_extension_for_class(
        x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName):
        raise RuntimeError("issued certificate lacks the requested DNS name")
    if certificate.extensions.get_extension_for_class(x509.BasicConstraints).value.ca:
        raise RuntimeError("CA issued a CA certificate instead of a server certificate")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for name, content in (
        ("request.csr", csr_pem),
        ("server.pem", answer["certificate_pem"].encode()),
        ("intermediate.pem", answer["intermediate_pem"].encode()),
        ("root.pem", answer["root_pem"].encode()),
    ):
        (args.output_dir / name).write_bytes(content)
    print(f"Certificate files: {args.output_dir}")
    print(f"Issued name: {HOSTNAME}; CSR and certificate public key match: OK")
    print("LAB04{" + hashlib.sha256(certificate.public_bytes(
        serialization.Encoding.DER)).hexdigest()[:16] + "}")


if __name__ == "__main__":
    main()
