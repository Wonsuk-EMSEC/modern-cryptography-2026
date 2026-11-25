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
    # TODO: return a dictionary with the certificate's subject, issuer,
    # SHA-256 fingerprint, and DNS names in Subject Alternative Name.
    # The fingerprint should be hexadecimal; names should be a list.
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
