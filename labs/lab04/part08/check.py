#!/usr/bin/env python3
"""Optional public check for the Part08 certificate and CRL experiment."""

import argparse
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import serialization


part = Path(__file__).resolve().parent
parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--output-dir", type=Path, default=part / "output")
args = parser.parse_args()
data = args.output_dir

spec = spec_from_file_location("student_revocation", part / "revoke.py")
student = module_from_spec(spec)
spec.loader.exec_module(student)

root = data / "root.pem"
intermediate = data / "intermediate.pem"
old_path = data / "old.pem"
new_path = data / "new.pem"
before = data / "before.crl"
after = data / "after.crl"
old = x509.load_pem_x509_certificate(old_path.read_bytes())
new = x509.load_pem_x509_certificate(new_path.read_bytes())
issuer = x509.load_pem_x509_certificate(intermediate.read_bytes())
before_crl = x509.load_pem_x509_crl(before.read_bytes())
after_crl = x509.load_pem_x509_crl(after.read_bytes())

assert old.serial_number != new.serial_number, "CA must issue a new serial"
spki = lambda cert: cert.public_key().public_bytes(
    serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)
assert spki(old) == spki(new), "both certificates should use the Part02 CSR key"
assert before_crl.is_signature_valid(issuer.public_key()), "old CRL signature invalid"
assert after_crl.is_signature_valid(issuer.public_key()), "new CRL signature invalid"
assert before_crl.get_revoked_certificate_by_serial_number(old.serial_number) is None
assert after_crl.get_revoked_certificate_by_serial_number(old.serial_number) is not None
assert after_crl.get_revoked_certificate_by_serial_number(new.serial_number) is None

verify = student.verify_with_crl
hostname = "lab04.local.test"
assert verify(root, intermediate, old_path, before, hostname).returncode == 0
assert verify(root, intermediate, old_path, None, hostname).returncode == 0
revoked_result = verify(root, intermediate, old_path, after, hostname)
assert revoked_result.returncode != 0
assert "certificate revoked" in (
    (revoked_result.stdout or "") + (revoked_result.stderr or "")
).lower(), "rejection should be caused by revocation"
assert verify(root, intermediate, new_path, after, hostname).returncode == 0
assert verify(root, intermediate, new_path, after, "wrong.lab04.test").returncode != 0
print("Part08: CRL, serial numbers, and hostname decisions: OK")
