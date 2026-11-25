#!/usr/bin/env python3
"""Optional public check for the student's known-password key decryption."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import secrets

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa


source = Path(__file__).resolve().parent / "decrypt_key.py"
spec = spec_from_file_location("student_key_decryption", source)
module = module_from_spec(spec)
spec.loader.exec_module(module)

key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
password = secrets.token_bytes(24)
encrypted = key.private_bytes(
    serialization.Encoding.PEM,
    serialization.PrivateFormat.PKCS8,
    serialization.BestAvailableEncryption(password),
)
reopened = module.decrypt_key(encrypted, password)
assert isinstance(reopened, rsa.RSAPrivateKey), "expected an RSA private key"
assert reopened.public_key().public_numbers() == key.public_key().public_numbers(), (
    "recovered private key has a different public key"
)

try:
    module.decrypt_key(encrypted, secrets.token_bytes(24))
except ValueError:
    pass
else:
    raise AssertionError("wrong password unexpectedly opened the private key")

print("Part01: correct password recovers the key; wrong password fails: OK")
