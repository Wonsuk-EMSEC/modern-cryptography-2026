# Lab 01 instructor notes

This directory contains reference implementations and deterministic fixture
generation. Do not copy it into student distributions.

## Preparation and validation

`generate_data.py` deterministically regenerates the student datasets. Run it
from any working directory; paths are resolved relative to the repository.

`render_part_pdfs.py` regenerates the five student handouts from the part
`README.md` source files without external PDF dependencies.

```console
python3 instructor/lab01/generate_data.py
python3 instructor/lab01/render_part_pdfs.py
LAB01_IMPL=/workspace/instructor/lab01/solutions \
  python3 -m unittest discover -s labs/lab01/tests -v
```

The WPA2 record is deliberately synthetic and uses an EAPOL-like fixed byte
string. It teaches the password-verification computation without packet parsing
or interaction with a network.

Suggested pacing: Part 1 (35 minutes), Part 2 (45 minutes), Part 3 (20 minutes),
Part 4 (45 minutes), discussion (15 minutes).

## Conceptual answer guide

- Part 1: with candidate hashes reused, at most `D` hash computations plus
  target-set lookups; salts prevent cross-account reuse; unique salts and a
  deliberately expensive, memory-hard password hash are expected.
- Part 2: only chain endpoints and starts are stored, while lookup rebuilds
  possible suffixes/chains. Chains merge because hash/reduction mapping is
  many-to-one. Salts are public uniqueness values; a separate precomputation is
  needed per salt.
- Part 3: the pair violates collision resistance, not arbitrary preimage
  resistance. Collision-dependent signatures and content identifiers are
  examples at risk.
- Part 4: the SSID, addresses, nonces, fixed message bytes, and reference MIC
  enable checking. PBKDF2 raises per-guess
  cost but cannot give a low-entropy password more entropy. Only explicitly
  authorized, supplied offline records are in scope.
