#!/usr/bin/env python3
"""Reconstruct and inspect a historical MD5 rogue CA certificate."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess

from cryptography import x509
from cryptography.x509.oid import ExtensionOID


DATA = Path(__file__).resolve().parent / "data"
OUTPUT = Path("/tmp/lab04-rogue-reconstructed.der")
# 2004-08-05 00:00:00 UTC, within the historical certificates' validity period.
HISTORICAL_TIME = "1091664000"


def collision_evidence(legitimate_der: bytes, template_der: bytes) -> bool:
    """Check different TBS bytes, matching MD5, and different SHA-256 values."""
    # TODO: parse both DER certificates and compare their tbs_certificate_bytes.
    raise NotImplementedError("compare the two signed certificate bodies")


def transplant_signature(legitimate_der: bytes, template_der: bytes,
                         offset: int, size: int) -> bytes:
    """Return the rogue template with the legitimate certificate's signature."""
    # TODO: extract the legitimate certificate's signature and replace only the
    # empty signature bytes at [offset:offset+size] in the rogue template.
    raise NotImplementedError("reuse the CA signature on the colliding TBS")


def verify_chain(level: int, rogue_path: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["openssl", "verify", "-auth_level", str(level), "-attime", HISTORICAL_TIME,
         "-CAfile", str(DATA / "historical_root.crt"),
         "-untrusted", str(rogue_path), str(DATA / "historical_server.der")],
        capture_output=True, text=True, timeout=15,
    )


def main() -> None:
    legitimate_der = (DATA / "legitimate.der").read_bytes()
    template_der = (DATA / "rogue_template.der").read_bytes()
    locations = json.loads((DATA / "template.json").read_text())
    if not collision_evidence(legitimate_der, template_der):
        raise ValueError("the signed certificate bodies do not meet the collision conditions")

    rogue_der = transplant_signature(legitimate_der, template_der,
                                     locations["signature_offset"], locations["signature_bytes"])
    legitimate = x509.load_der_x509_certificate(legitimate_der)
    rogue = x509.load_der_x509_certificate(rogue_der)
    template = x509.load_der_x509_certificate(template_der)
    if rogue.tbs_certificate_bytes != template.tbs_certificate_bytes:
        raise ValueError("the rogue signed body was changed")
    if rogue.signature != legitimate.signature:
        raise ValueError("the CA signature was not transplanted")
    if not rogue.extensions.get_extension_for_oid(ExtensionOID.BASIC_CONSTRAINTS).value.ca:
        raise ValueError("the reconstructed certificate has no CA authority")

    OUTPUT.write_bytes(rogue_der)
    legacy = verify_chain(0, OUTPUT)
    modern = verify_chain(1, OUTPUT)
    print("legitimate CA role:", legitimate.extensions.get_extension_for_oid(
        ExtensionOID.BASIC_CONSTRAINTS).value.ca)
    print("rogue CA role:", rogue.extensions.get_extension_for_oid(
        ExtensionOID.BASIC_CONSTRAINTS).value.ca)
    print("TBS MD5:", hashlib.md5(rogue.tbs_certificate_bytes).hexdigest())
    print("legacy chain:", "accepted" if legacy.returncode == 0 else legacy.stderr.strip())
    print("modern chain:", "rejected" if modern.returncode else "accepted")
    if legacy.returncode or modern.returncode == 0:
        raise RuntimeError("the historical and current verification results differ from the exercise")
    completion = hashlib.sha256(rogue_der + (DATA / "historical_server.der").read_bytes()).hexdigest()[:16]
    print(f"LAB04{{{completion}}}")
    print("reconstructed certificate:", OUTPUT)


if __name__ == "__main__":
    main()
