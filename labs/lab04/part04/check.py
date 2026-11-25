"""Optional public check for the certificate description function."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from urllib.request import urlopen


PART = Path(__file__).resolve().parent
spec = spec_from_file_location("student_certificate_inspector", PART / "compare_certificates.py")
module = module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)

base = "http://lab04-proxy:8080"
with urlopen(base + "/lab04-target-cert.pem", timeout=5) as response:
    original = module.describe(response.read())
with urlopen(base + "/lab04-intercept-cert.pem", timeout=5) as response:
    intercepted = module.describe(response.read())

for row in (original, intercepted):
    assert isinstance(row, dict)
    assert set(row) == {"subject", "issuer", "fingerprint", "dns_names"}
    assert "lab04.local.test" in row["dns_names"]
    assert len(row["fingerprint"]) == 64
assert original["issuer"] != intercepted["issuer"]
assert original["fingerprint"] != intercepted["fingerprint"]
print("Part04: original and intercepted certificate identities: OK")
