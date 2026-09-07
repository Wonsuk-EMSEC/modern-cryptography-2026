# Lab 01 instructor notes

This directory contains reference implementations and deterministic fixture
generation. Do not copy it into student distributions.

## Preparation and validation

`generate_lab_data.py` deterministically regenerates all student datasets,
including the bounded Part 4 password database. It invokes the earlier
`generate_data.py` fixture generator. Run it from any working directory; paths
are resolved relative to the repository.

`render_part_pdfs.py` regenerates the five student handouts from the part
`README.md` source files without external PDF dependencies.

```console
python3 instructor/lab01/generate_lab_data.py
python3 instructor/lab01/render_part_pdfs.py
LAB01_GRADE=1 LAB01_IMPL=/workspace/instructor/lab01/solutions \
  python3 -m unittest discover -s labs/lab01/tests -v
python3 -m unittest instructor/lab01/test_table_attacks.py -v
```

The WPA2 record is deliberately synthetic and uses an EAPOL-like fixed byte
string. It teaches the password-verification computation without packet parsing
or interaction with a network.

## WPA2 derivation test vector

`test_vectors/wpa2_pmk_ptk_kck.json` contains an instructor-only known-answer
vector for the PBKDF2 PMK and pairwise PRF PTK/KCK derivation. It contains the
test passphrase, so do not copy it into student distributions. Verify it with:

```console
python3 -m unittest instructor/lab01/test_wpa2_vectors.py -v
```

This vector stops at KCK because no EAPOL frame or captured MIC was provided.
The separate synthetic record exercises MIC verification.

### Part 4 table comparison

The Part 4 configuration has 1,296 candidates, 96 deterministic starts, and 12
columns. The reference implementation stores 71 distinct endpoints after chain
merges. The full table recovers all five database rows; the intentionally small
rainbow table recovers four. Plaintexts remain only in
`generate_lab_data.py`, while the student database contains digests only.

`solutions/table_attacks.py` is the complete functional reference. Validate it
with `test_table_attacks.py`; do not copy either file into student materials.

Suggested core pacing: Part 1 (20 minutes), Part 2 (35 minutes), Part 3 (25
minutes), Part 4 (35 minutes), Part 5 (25 minutes), report/discussion (15
minutes). The controlled SSH extension and John command are optional.

### Controlled SSH extension

The Part 2 SSH target is opt-in through the `lab01-ssh` Compose profile. It has
one fictional non-root account, password authentication only, no published host
port, and an internal-only network. The student client is fixed to the Compose
service and a 20-candidate maximum. Do not weaken those boundaries.

Validate the reference client only while the target profile is running:

```console
docker compose -f docker/compose.yml --profile lab01-ssh up -d lab01-ssh-target
docker compose -f docker/compose.yml --profile lab01-ssh run --rm course \
  bash -lc 'cd /workspace && PYTHONPATH=instructor/lab01/solutions \
  python3 instructor/lab01/solutions/ssh_dictionary_attack.py \
  labs/lab01/data/ssh-lab-wordlist.txt'
docker compose -f docker/compose.yml --profile lab01-ssh \
  rm --stop --force lab01-ssh-target
```

## Conceptual answer guide

- Part 1: SHA-256 is deterministic and fast. A fresh public salt makes equal
  passwords produce different stored digests, but it does not slow a guess.
- Part 2: an unsalted candidate hash can be compared with every target, while
  salted targets require per-account computation. The opt-in SSH extension is
  online because each attempt reaches the isolated authentication service.
- Part 3: password KDF work factors raise each guess's cost; memory-hard designs
  also resist cheap parallelism. Cost cannot create password entropy.
- Part 4: a full table stores every digest/password pair and needs no lookup
  hashes. A rainbow table stores starts/endpoints and rebuilds chain material,
  saving storage at the cost of lookup work and incomplete coverage. Chains
  merge because reduction is many-to-one. A separate table is needed per salt.
- Part 5: the SSID, addresses, nonces, EAPOL bytes, and reference MIC enable
  offline checking. PBKDF2 raises per-guess cost but cannot give a low-entropy
  passphrase more entropy. Only authorized supplied records are in scope.
