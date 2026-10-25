# Part 4: System password records and table attacks

[한국어](../../../../labs/lab01/part4_system_hashes/README.md) | [English](README.md)

Code and data are shared in the [original directory](../../../../labs/lab01/part4_system_hashes/). Run all commands from the original exercise directory in the course container.

Run all Python programs inside the course Docker container. Read only the
synthetic files under this Part's `data/`; never read the host's `/etc/shadow`.
The fixed SHA-256 toy password space is an educational model, not a real
system-password configuration.

## Learning objectives and files

Parse a stored verifier, distinguish parsing from guessing, build a full table
and rainbow endpoints, replay chains to verify matches, and compare storage,
construction work, lookup work, and coverage. Explain why public unique salts
prevent reuse of one unsalted table across accounts.

| File | Role |
| --- | --- |
| `samples/analyze_shadow_hash.py` | Complete synthetic shadow-record parser |
| `samples/table_io_demo.py` | Complete public example of table-building ingredients |
| `table_common.py` | Provided bounded config, hashing, enumeration, and JSON helpers |
| `build_precomputation_table.py` | Empty full-table exercise |
| `build_rainbow_table.py` | Empty rainbow-construction exercise |
| `compare_table_attacks.py` | Empty database-lookup/comparison exercise |
| `data/rainbow_lab_config.json` | Required construction parameters |
| `data/rainbow_password_database.csv` | Same target database for both methods |
| `test_table_attacks.py` | Helper checks and opt-in implementation checks |
| `samples/flag_unlock_demo.py` | Public helper-usage example; no Part answer |
| `data/flag_challenge.json` | Encrypted completion flag, opened by the experiment result |

Write all imports, functions, CLI parsing, measurement, and execution guards.
During each step, imports must work without running a program. Add calls to
later functions only when those functions have been written.

The classroom configuration is SHA-256, alphabet `abc123`, length 4
(`6**4 = 1296` passwords), chain length 12, 96 unique starts, seed 2026.
Keep these bounds unchanged in the required experiment.

## 1. Run and inspect the samples

```console
cd /workspace/labs/lab01/part4_system_hashes
python3 samples/analyze_shadow_hash.py data/linux_hashes.txt
python3 samples/table_io_demo.py
python3 -m unittest test_table_attacks.py -v
```

The parser prints a dictionary for each fictional record with `account`,
algorithm `id`, human-readable `algorithm`, `salt_or_parameters`, and
`verifier`. Identify these fields in the supplied record. The parser does
not crack a password or contact a service.

The table sample prints the configured space size 1296, the tiny public space
`['aa', 'ab', 'ba', 'bb']`, digest length 64, and the integer/quotient/remainder
for hexadecimal `0f`: 15, 2, 3. It also prints reproducible seeded choices and
`Grouped values after JSON round trip: ['first', 'second']`.
`Temporary JSON exists: True` followed by `Temporary JSON removed` confirms
file creation and cleanup.

Study enumeration, hex-to-integer conversion, `divmod`, seeded selection,
`dict.setdefault`, and the JSON helpers. This sample does not construct a
graded attack table. Two helper tests pass before implementation; five
completion tests are skipped.

### Public flag utility sample

```console
python3 samples/flag_unlock_demo.py
```

Expected output:

```text
Wrong proof rejected: OK
FLAG{public_demo_only}
This public demo flag is not a Part completion flag.
```

The sample leaves no file behind. Inspect how the shared utility is imported,
how authentication failure is handled, and how a successful return value is
printed. Your final program will use its own experiment result, not this public
demo proof.

## 2. Write the full-table build_table(), then check a tiny space

In `build_precomputation_table.py`, implement:

```text
build_table(config: dict[str, int | str]) -> dict[str, str]
```

Enumerate `password_space(alphabet, password_length)`, hash each password once
with the configured algorithm, and return lowercase `digest -> password`
entries. The provided `hash_password()` is a fast toy hash, not a password KDF.

```console
python3 - <<'PY'
from build_precomputation_table import build_table
from table_common import hash_password
config = {"algorithm": "sha256", "alphabet": "ab", "password_length": 2}
entries = build_table(config)
assert len(entries) == 4
assert entries[hash_password("ab")] == "ab"
assert set(entries.values()) == {"aa", "ab", "ba", "bb"}
print("Full-table check: OK")
PY
```

Proceed after `Full-table check: OK`.

## 3. Write reduce_digest(), then check its mapping

In `build_rainbow_table.py`, define `MIX_CONSTANT = 0x9E3779B1` and implement:

```text
reduce_digest(digest_hex: str, column: int, alphabet: str, length: int) -> str
```

Compute `(int(digest_hex, 16) + column * MIX_CONSTANT) % (len(alphabet)**length)`.
Encode that integer as exactly `length` base-`len(alphabet)` digits,
most significant first, using `alphabet[digit]`; include leading zero digits.
This is a column-dependent map into a bounded password space, not an inverse
of SHA-256.

```console
python3 - <<'PY'
from build_rainbow_table import reduce_digest
assert reduce_digest("00", 0, "ab", 2) == "aa"
assert reduce_digest("01", 0, "ab", 2) == "ab"
assert reduce_digest("ff", 0, "ab", 2) == "bb"
assert reduce_digest("00", 1, "ab", 2) == "ab"
values = [reduce_digest("1234", i, "abc123", 4) for i in range(4)]
assert all(len(value) == 4 and set(value) <= set("abc123") for value in values)
assert len(set(values)) > 1
print("Reduction check: OK")
PY
```

Proceed after `Reduction check: OK`.

## 4. Write choose_starts() and check it; then write chain_endpoint()

First implement `choose_starts(config) -> list[str]`: enumerate the configured
space and use `random.Random(seed).sample(candidates, chain_count)` to choose
unique starts without changing global random state.

```console
python3 - <<'PY'
from build_rainbow_table import choose_starts
config = {"alphabet": "ab", "password_length": 2, "chain_count": 2, "seed": 2026}
starts = choose_starts(config)
assert starts == choose_starts(config)
assert len(starts) == len(set(starts)) == 2
assert set(starts) <= {"aa", "ab", "ba", "bb"}
print("Start-selection check: OK")
PY
```

After that check passes, implement
`chain_endpoint(start: str, config: dict[str, int | str]) -> str`.
Starting at `start`, hash the current password and reduce the digest for
columns `0 .. chain_length-1`. Return only the final reduced password.

```console
python3 - <<'PY'
from build_rainbow_table import chain_endpoint, reduce_digest
from table_common import hash_password
config = {"algorithm": "sha256", "alphabet": "ab", "password_length": 2, "chain_length": 1}
expected = reduce_digest(hash_password("ab"), 0, "ab", 2)
assert chain_endpoint("ab", config) == expected
config["chain_length"] = 2
expected = reduce_digest(hash_password(expected), 1, "ab", 2)
assert chain_endpoint("ab", config) == expected
print("Chain check: OK")
PY
```

Proceed after both messages end with `OK`.

## 5. Write rainbow build_table(), then check endpoint grouping

Implement `build_table(config) -> dict[str, list[str]]` in
`build_rainbow_table.py`. For every chosen start, calculate its endpoint and
append the start to that endpoint's list. Retain all starts when chains merge;
do not overwrite a previous start or store every intermediate password.

```console
python3 - <<'PY'
from unittest.mock import patch
import build_rainbow_table as rainbow
config = {"algorithm": "sha256", "alphabet": "ab", "password_length": 2,
          "chain_length": 2, "chain_count": 3, "seed": 2026}
starts = rainbow.choose_starts(config)
endpoints = rainbow.build_table(config)
assert sum(map(len, endpoints.values())) == 3
assert sorted(start for group in endpoints.values() for start in group) == sorted(starts)
with patch.object(rainbow, "chain_endpoint", return_value="aa"):
    merged = rainbow.build_table(config)
    assert merged == {"aa": starts}
print("Endpoint grouping check: OK")
PY
```

The forced merge is a public unit fixture. Proceed after
`Endpoint grouping check: OK`.

## 6. Write lookup_precomputation(), then check it

In `compare_table_attacks.py`, implement:

```text
lookup_precomputation(digest: str, entries: dict[str, str]) -> tuple[str | None, int]
```

Return a matching password, or `None`, and the number of new hash computations.
A dictionary lookup requires zero new hashes.

```console
python3 - <<'PY'
from compare_table_attacks import lookup_precomputation
from table_common import hash_password
digest = hash_password("ab")
assert lookup_precomputation(digest, {digest: "ab"}) == ("ab", 0)
assert lookup_precomputation(digest, {}) == (None, 0)
print("Full lookup check: OK")
PY
```

Proceed after `Full lookup check: OK`.

## 7. Write lookup_rainbow(), then check chain replay

Implement in `compare_table_attacks.py`:

```text
lookup_rainbow(digest: str, endpoints: dict[str, list[str]],
              config: dict[str, int | str]) -> tuple[str | None, int]
```

Try target columns from the last column to zero. Reduce the target digest at
the selected column, then hash/reduce forward through the remaining columns
to propose an endpoint. Replay each start stored at that endpoint from column
zero. Compare each replayed password's hash with the **original** target digest
before returning it; an endpoint collision alone is not a match.
Count every hash performed during endpoint prediction and replay, including
verification. Return `(None, count)` when no chain verifies.

A small rainbow table has incomplete coverage, so missing some valid passwords
is expected. The lookup must never invent an unverified match.

```console
python3 - <<'PY'
from build_rainbow_table import chain_endpoint, reduce_digest
from compare_table_attacks import lookup_rainbow
from table_common import hash_password
config = {"algorithm": "sha256", "alphabet": "ab", "password_length": 2, "chain_length": 2}
start = "aa"
endpoints = {chain_endpoint(start, config): [start]}
for password in (start, reduce_digest(hash_password(start), 0, "ab", 2)):
    found, count = lookup_rainbow(hash_password(password), endpoints, config)
    assert found == password and count > 0
found, count = lookup_rainbow(hash_password("outside"), endpoints, config)
assert found is None and count >= 0
print("Rainbow replay check: OK")
PY
```

Proceed after `Rainbow replay check: OK`.

## 8. Write database loading, check it, then add measurement

### Write load_database() and check its schema

In `compare_table_attacks.py`, implement
`load_database(path: Path) -> list[dict[str, str]]`: read nonempty CSV records,
require exactly `account,sha256` columns, and reject an invalid or empty
file with `ValueError`.

```console
python3 - <<'PY'
import tempfile
from pathlib import Path
from compare_table_attacks import load_database
from table_common import hash_password
digest = hash_password("ab")
with tempfile.TemporaryDirectory() as directory:
    path = Path(directory) / "public.csv"
    path.write_text(f"account,sha256\nexample,{digest}\n", encoding="utf-8")
    assert load_database(path) == [{"account": "example", "sha256": digest}]
    path.write_text("wrong,schema\nexample,value\n", encoding="utf-8")
    try:
        load_database(path)
    except ValueError:
        pass
    else:
        raise AssertionError("invalid schema was accepted")
print("Database loading check: OK")
PY
```

Proceed after `Database loading check: OK`.

### Write attack_database() and check its metrics

Implement `attack_database(database, lookup) -> tuple[dict[str, str], int, float]`:
call the supplied lookup on each lowercase target digest, sum lookup hash
counts, collect verified matches by account, and time the operation.

```console
python3 - <<'PY'
from compare_table_attacks import attack_database
from table_common import hash_password
digest = hash_password("ab")
rows = [{"account": "example", "sha256": digest}]
found, count, elapsed = attack_database(rows, lambda value: ("ab", 0))
assert found == {"example": "ab"} and count == 0 and elapsed >= 0
found, count, elapsed = attack_database(rows, lambda value: (None, 3))
assert found == {} and count == 3 and elapsed >= 0
print("Database measurement check: OK")
PY
```

Proceed after `Database measurement check: OK`.

## 9. Write the three main programs and JSON artifacts

Use `argparse`, `Path`, `perf_counter()`, `load_config()`, and
`write_json()`. Put generated files under `generated/`, which Git ignores.

| Program | Positional arguments | Required artifact fields |
| --- | --- | --- |
| `build_precomputation_table.py` | config JSON, output JSON | `type="full-precomputation"`, `config`, `build_hashes`, `build_seconds`, `entries` |
| `build_rainbow_table.py` | config JSON, output JSON | `type="rainbow-endpoints"`, `config`, `build_hashes`, `build_seconds`, `endpoints` |
| `compare_table_attacks.py` | database CSV, full-table JSON, rainbow JSON | Print a metrics row per method; no artifact required |

The full build hash count is the password-space size; rainbow build hashes
are `chain_count * chain_length`. Time table construction separately from JSON
serialization. Each builder reports entries/starts, distinct endpoints where
applicable, build hashes, seconds, and serialized file bytes.

The comparison reads both table JSON files, applies both methods to the same
database, and reports recovered/total accounts, build hashes, build seconds,
stored records, distinct endpoints, file bytes, lookup hashes, and lookup
seconds. A rainbow stored record is a start/endpoint pair, including starts
sharing an endpoint. Print counts rather than recovered course passwords.

```console
python3 -c "import build_precomputation_table, build_rainbow_table, compare_table_attacks; print('Import check: OK')"
LAB01_GRADE=1 python3 -m unittest test_table_attacks.py -v
```

All seven enabled tests should pass.

### Shared completion utility

The whole main program is still yours to write. Resolve the envelope relative
to your exercise file, rather than the shell's current directory. To import
the provided shared utility from a numbered Part exercise file, use:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from labs.lab01.common.flags import unlock_flag, canonical_account_proof
```

`unlock_flag(path, proof)` returns a `FLAG{...}` string after authenticating
the encrypted envelope. An incorrect proof raises `ValueError`; inspect your
implementation and proof format rather than changing the envelope.
The public demo proof opens only the demo artifact and cannot open this Part's
flag. Submit the computed Part flag through the instructor's designated channel.

### Open the flag after the full/rainbow comparison

In your `compare_table_attacks.py` main, retain the recovered account mapping
returned by the full-table attack. Require it to cover every account in the
input database, then call `canonical_account_proof(full_recovered)` and pass
the result to `unlock_flag()` for `data/flag_challenge.json`. Print the
returned `FLAG{...}` after both methods' metric rows.

The canonical text is compact JSON with sorted account keys and Unicode
preserved:
`json.dumps(mapping, sort_keys=True, separators=(',', ':'), ensure_ascii=False)`.
For the public mapping `{"b": "public-two", "a": "public-one"}`, it is
`{"a":"public-one","b":"public-two"}`. Use the shared encoder and do not
print the recovered course mapping or proof.

Use the **full-table** result as the proof because it guarantees coverage.
Rainbow's partial coverage remains an expected result, and implementing,
running, and interpreting the rainbow method is still mandatory.

## 10. Generate course tables and compare them

```console
python3 build_precomputation_table.py data/rainbow_lab_config.json generated/precomputation.json
python3 build_rainbow_table.py data/rainbow_lab_config.json generated/rainbow.json
python3 compare_table_attacks.py data/rainbow_password_database.csv generated/precomputation.json generated/rainbow.json
```

The full table contains 1,296 entries and uses 1,296 build hashes. Rainbow uses
96 starts and 1,152 build hashes; it has at most 96 distinct endpoints.
Fewer endpoints than starts indicates chain merges.

The full table should recover every supplied target with zero new lookup hashes.
Rainbow should demonstrate partial coverage and positive lookup work.
Exact elapsed times and JSON sizes vary. The comparison ends with the recovered
`FLAG{...}` after both metric rows. Do not add hard-coded target cases.

Finally observe why an unsalted table cannot be reused directly with a salt:

```console
python3 - <<'PY'
import hashlib
import json
from pathlib import Path
entries = json.loads(Path("generated/precomputation.json").read_text())["entries"]
public = b"abc1"
print("Unsalted present:", hashlib.sha256(public).hexdigest() in entries)
print("Salted present:", hashlib.sha256(b"public-salt:" + public).hexdigest() in entries)
PY
```

Expect `Unsalted present: True` and `Salted present: False`.
The public salt changes the lookup key; separate salts require separate
precomputation. Real password storage additionally needs a password KDF.

## 11. Completion and report

- [ ] All three initially empty files contain complete programs.
- [ ] Every staged public check and all enabled tests pass.
- [ ] Both artifacts have the required schema and deterministic configuration.
- [ ] Both methods attack the same course database without special cases.
- [ ] Full coverage and rainbow limitations are measured and explained.
- [ ] The salt observation and synthetic record parsing are documented.
- [ ] The final program authenticates its own `data/flag_challenge.json` and prints the Part flag.

Submit the three Python files and a report using this comparison table:

| Method | Build hashes | Build seconds | Stored records | Distinct endpoints | JSON bytes | Recovered/total | Lookup hashes | Lookup seconds |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Full | | | | N/A | | | | |
| Rainbow | | | | | | | | |

Explain parsing versus guessing, why reduction is not an inverse hash, why
endpoint merges affect coverage, what storage rainbow saves and what lookup
work it adds, and why salts prevent shared unsalted precomputation. Discuss
conceptual stored values as well as JSON overhead. Do not publish recovered
course passwords.
