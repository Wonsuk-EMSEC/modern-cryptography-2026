#!/usr/bin/env python3
"""Issue, revoke, and reissue a server certificate with the local CA."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization


PART = Path(__file__).resolve().parent
DEFAULT_CSR = PART.parent / "part02/output/request.csr"
DEFAULT_CA_URL = "http://lab04-ca:8080"
HOSTNAME = "lab04.local.test"


def verify_with_crl(root: Path, intermediate: Path, leaf: Path,
                    crl: Path | None, hostname: str) -> subprocess.CompletedProcess[str]:
    """Verify the server chain and name, adding leaf CRL checking when given a CRL."""
    # TODO: Run `openssl verify` and return subprocess.CompletedProcess.
    # Trust only root; use intermediate as an untrusted chain certificate.
    # Check server purpose and hostname. If crl is not None, supply that CRL
    # and enable revocation checking for the leaf certificate. Capture output.
    raise NotImplementedError("verify the chain, name, and optional leaf CRL")


def _request(ca_url: str, path: str, payload: dict[str, str] | None = None):
    url = ca_url.rstrip("/") + path
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(url, data=body,
                      method="GET" if body is None else "POST",
                      headers={"Content-Type": "application/json"} if body else {})
    try:
        with urlopen(request, timeout=10) as response:
            content = response.read()
    except HTTPError as error:
        detail = error.read(1000).decode(errors="replace")
        raise RuntimeError(f"CA rejected {path} (HTTP {error.code}): {detail}") from error
    except URLError as error:
        raise RuntimeError(f"CA unavailable at {url}: {error.reason}") from error
    if path == "/crl":
        return content
    try:
        return json.loads(content)
    except (ValueError, UnicodeError) as error:
        raise RuntimeError(f"CA returned invalid JSON for {path}") from error


def _issue(ca_url: str, csr_pem: bytes) -> dict[str, str]:
    answer = _request(ca_url, "/issue", {"csr_pem": csr_pem.decode("ascii")})
    if not isinstance(answer, dict) or not all(
        isinstance(answer.get(name), str)
        for name in ("certificate_pem", "intermediate_pem", "root_pem")
    ):
        raise RuntimeError("CA returned an incomplete certificate response")
    return answer


def _write_crl(ca_url: str, destination: Path) -> None:
    content = _request(ca_url, "/crl")
    if not isinstance(content, bytes) or not content.startswith(b"-----BEGIN X509 CRL-----"):
        raise RuntimeError("CA returned an invalid PEM CRL")
    x509.load_pem_x509_crl(content)
    destination.write_bytes(content)


def _check(label: str, result: subprocess.CompletedProcess[str],
           *, accept: bool, revoked: bool = False) -> None:
    observed = result.returncode == 0
    print(f"{label}: {'ACCEPT' if observed else 'REJECT'}")
    detail = (result.stdout or "") + "\n" + (result.stderr or "")
    if observed != accept or (revoked and "certificate revoked" not in detail.lower()):
        raise RuntimeError(f"unexpected verification result for {label}: {detail.strip()}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--csr", type=Path, default=DEFAULT_CSR)
    parser.add_argument("--output-dir", type=Path, default=PART / "output")
    parser.add_argument("--url", default=os.environ.get("LAB04_CA_URL", DEFAULT_CA_URL))
    args = parser.parse_args()

    csr_pem = args.csr.read_bytes()
    csr = x509.load_pem_x509_csr(csr_pem)
    if not csr.is_signature_valid:
        raise RuntimeError("Part02 CSR signature is invalid")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    old_path = args.output_dir / "old.pem"
    new_path = args.output_dir / "new.pem"
    root_path = args.output_dir / "root.pem"
    intermediate_path = args.output_dir / "intermediate.pem"
    before_path = args.output_dir / "before.crl"
    after_path = args.output_dir / "after.crl"

    # 1. Issue a new certificate from the CSR already made in Part02.
    first = _issue(args.url, csr_pem)
    old_path.write_text(first["certificate_pem"], encoding="ascii")
    root_path.write_text(first["root_pem"], encoding="ascii")
    intermediate_path.write_text(first["intermediate_pem"], encoding="ascii")
    old = x509.load_pem_x509_certificate(old_path.read_bytes())

    # 2. Download the current CRL and check the certificate before revocation.
    _write_crl(args.url, before_path)
    _check("before revocation with CRL",
           verify_with_crl(root_path, intermediate_path, old_path, before_path, HOSTNAME),
           accept=True)

    # 3. Revoke this exact certificate. A client that omits CRL checking still
    # accepts it; a client that checks the refreshed CRL must reject it.
    revoked = _request(args.url, "/revoke", {"certificate_pem": first["certificate_pem"]})
    if not isinstance(revoked, dict) or revoked.get("revoked") is not True:
        raise RuntimeError("CA did not confirm certificate revocation")
    _write_crl(args.url, after_path)
    _check("after revocation without CRL",
           verify_with_crl(root_path, intermediate_path, old_path, None, HOSTNAME),
           accept=True)
    _check("after revocation with CRL",
           verify_with_crl(root_path, intermediate_path, old_path, after_path, HOSTNAME),
           accept=False, revoked=True)

    # 4. The same CSR has the same public key, but receives a fresh serial.
    second = _issue(args.url, csr_pem)
    if (second["root_pem"] != first["root_pem"] or
            second["intermediate_pem"] != first["intermediate_pem"]):
        raise RuntimeError("CA changed during the experiment; run it again")
    new_path.write_text(second["certificate_pem"], encoding="ascii")
    new = x509.load_pem_x509_certificate(new_path.read_bytes())
    if new.serial_number == old.serial_number:
        raise RuntimeError("CA reused a serial number")
    csr_key = csr.public_key().public_bytes(
        serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
    for cert in (old, new):
        cert_key = cert.public_key().public_bytes(
            serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
        if cert_key != csr_key:
            raise RuntimeError("CA issued a certificate for a different public key")
    _check("new certificate with CRL",
           verify_with_crl(root_path, intermediate_path, new_path, after_path, HOSTNAME),
           accept=True)

    digest = hashlib.sha256(old.fingerprint(hashes.SHA256()) +
                            new.fingerprint(hashes.SHA256()) + after_path.read_bytes()).hexdigest()
    print("LAB04{" + digest[:16] + "}")


if __name__ == "__main__":
    main()
