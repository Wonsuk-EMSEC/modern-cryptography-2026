#!/usr/bin/env python3
"""Inspect the certificate seen by a browser and the original lab server."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes


def describe(certificate_pem: bytes) -> dict[str, str | list[str]]:
    certificate = x509.load_pem_x509_certificate(certificate_pem)
    subject = certificate.subject.rfc4514_string()
    issuer = certificate.issuer.rfc4514_string()

    # TODO: Find the certificate's SHA-256 fingerprint (as hex) and DNS names
    # from SubjectAlternativeName (as a list). Return a dictionary with keys
    # "subject", "issuer", "fingerprint", and "dns_names".
    raise NotImplementedError("describe this certificate")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("original", type=Path, help="original server certificate PEM")
    parser.add_argument("intercepted", type=Path, help="certificate received through the proxy")
    args = parser.parse_args()
    original = describe(args.original.read_bytes())
    intercepted = describe(args.intercepted.read_bytes())
    print(json.dumps({"original": original, "intercepted": intercepted}, indent=2))
    print("Compare the names, issuers, and fingerprints in your report.")


if __name__ == "__main__":
    main()
