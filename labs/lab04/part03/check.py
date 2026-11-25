#!/usr/bin/env python3
"""Optional public check: an incomplete chain and a wrong name must fail."""

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


part = Path(__file__).resolve().parent
spec = spec_from_file_location("student_inspector", part / "verify_chain.py")
module = module_from_spec(spec)
spec.loader.exec_module(module)
certs = part.parent / "part02/output"
root = certs / "root.pem"
intermediate = certs / "intermediate.pem"
leaf = certs / "server.pem"
assert module.verify_certificate(root, intermediate, leaf, "lab04.local.test").returncode == 0
assert module.verify_certificate(root, intermediate, leaf, "other.lab04.test").returncode != 0
assert module.verify_certificate(root, None, leaf, "lab04.local.test").returncode != 0
print("Part03: chain and hostname decisions: OK")
