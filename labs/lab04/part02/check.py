#!/usr/bin/env python3
"""Optional public inspection of an issued certificate and its CSR."""

from pathlib import Path
import subprocess

from cryptography import x509
from cryptography.hazmat.primitives import serialization


part = Path(__file__).resolve().parent
data = part / "output"
csr = x509.load_pem_x509_csr((data / "request.csr").read_bytes())
leaf = x509.load_pem_x509_certificate((data / "server.pem").read_bytes())
assert csr.is_signature_valid, "CSR signature invalid"
for name in ("intermediate.pem", "root.pem"):
    assert (data / name).is_file(), f"missing {name}"
spki = lambda key: key.public_bytes(serialization.Encoding.DER,
                                     serialization.PublicFormat.SubjectPublicKeyInfo)
assert spki(csr.public_key()) == spki(leaf.public_key()), "CA replaced the public key"
assert not leaf.extensions.get_extension_for_class(x509.BasicConstraints).value.ca
assert "lab04.local.test" in leaf.extensions.get_extension_for_class(
    x509.SubjectAlternativeName).value.get_values_for_type(x509.DNSName)
checked = subprocess.run(["openssl", "verify", "-no-CApath", "-no-CAstore",
                          "-CAfile", str(data / "root.pem"),
                          "-untrusted", str(data / "intermediate.pem"),
                          "-purpose", "sslserver", "-verify_hostname", "lab04.local.test",
                          str(data / "server.pem")], capture_output=True, text=True)
assert checked.returncode == 0, checked.stderr
print("Part02: CSR, public key, extensions, and trusted chain: OK")
