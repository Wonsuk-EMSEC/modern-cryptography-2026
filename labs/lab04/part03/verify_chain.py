#!/usr/bin/env python3
"""Compare certificate chain validation with server identity validation."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import subprocess

from cryptography import x509
from cryptography.hazmat.primitives import serialization


PART = Path(__file__).resolve().parent
DEFAULT_CERT_DIR = PART.parent / "part02/output"


def verify_certificate(root: Path, intermediate: Path | None,
                       leaf: Path, hostname: str) -> subprocess.CompletedProcess[str]:
    """Run OpenSSL's server-certificate verification and return its result."""
    # TODO: Build an openssl verify command with root as the only trusted CA,
    # intermediate as an untrusted chain certificate when present, server
    # purpose, and hostname checking. Capture both stdout and stderr.
    raise NotImplementedError("verify both trust chain and requested DNS name")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cert-dir", type=Path, default=DEFAULT_CERT_DIR)
    args = parser.parse_args()
    root = args.cert_dir / "root.pem"
    intermediate = args.cert_dir / "intermediate.pem"
    leaf = args.cert_dir / "server.pem"
    cases = (
        ("trusted chain and correct name", intermediate, "lab04.local.test", True),
        ("trusted chain, wrong name", intermediate, "other.lab04.test", False),
        ("missing intermediate", None, "lab04.local.test", False),
    )
    for description, chain_cert, name, expected in cases:
        result = verify_certificate(root, chain_cert, leaf, name)
        accepted = result.returncode == 0
        print(f"{description}: {'ACCEPT' if accepted else 'REJECT'}")
        if accepted != expected:
            print(result.stderr.strip())
            raise RuntimeError(f"unexpected verification outcome: {description}")
    certificate = x509.load_pem_x509_certificate(leaf.read_bytes())
    digest = hashlib.sha256(certificate.public_bytes(serialization.Encoding.DER)).hexdigest()
    print("LAB04{" + digest[16:32] + "}")


if __name__ == "__main__":
    main()
