[한국어](../../../../labs/lab01/part3_password_kdfs/README.md) | **English**

# Part 3: Offline password cracking and password KDFs

**Estimated time:** 40 minutes. Run everything inside the course Docker container.
Use only fictional course databases and local accounts. This experiment is
offline: guesses are computed locally and never reach a login service.

## Learning objectives and files

Compare the cost of unsalted and salted SHA-256 guessing, reuse work only when
inputs permit it, and connect guessing cost to dedicated password KDFs.
Learn CSV/hex handling, operation counting, timing, KDF parameters, and local
storage of a verifier without a plaintext password.

| File | Role |
| --- | --- |
| `samples/csv_hash_demo.py` | Complete single-candidate public CSV/hex/hash example |
| `samples/benchmark_kdfs.py` | Complete benchmark of five mechanisms |
| `samples/register_login_demo.py` | Complete local PBKDF2 registration/login example |
| `crack_unsalted.py`, `crack_salted.py` | Empty student exercise files |
| `compare_cost.py` | Provided comparison tool; run after both functions work |
| `data/unsalted_hashes.csv` | Synthetic `account,sha256` records |
| `data/salted_hashes.csv` | Synthetic `account,salt_hex,sha256` records |
| `data/lab01-small.txt` | Fixed classroom wordlist |
| `test_dictionary_cost.py` | Fixture and opt-in implementation checks |
| `samples/flag_unlock_demo.py` | Public helper-usage example; no Part answer |
| `data/flag_challenge.json` | Encrypted completion flag, opened by the experiment result |

Write imports, functions, CLI, and execution guards in both exercise files.
Keep interactive/executable work out of imports. Do not hard-code classroom
account names, passwords, target digests, or measured counts.

## 1. Run and inspect the CSV sample

```console
cd /workspace/labs/lab01/part3_password_kdfs
python3 samples/csv_hash_demo.py
python3 -m unittest test_dictionary_cost.py -v
```

The sample creates a temporary public record, reads it with `csv.DictReader`,
decodes its salt, checks one public candidate, and removes the temporary file.

```text
CSV fields: account, salt_hex, sha256
Account: example
Salt bytes: 11
Single candidate matches: True
Hash computations: 1
Elapsed: <seconds> seconds
```

All values except time are fixed. Study `Path`, CSV field access, UTF-8
encoding, `bytes.fromhex()`, and the boundary around the timed operation.
This is a one-candidate API example; your program must perform the bounded
dictionary search itself. The baseline suite reports one passed fixture check
and two skipped implementation checks.

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

## 2. Write unsalted crack(), then check it

In `crack_unsalted.py`, implement:

```text
crack(target_csv: Path, wordlist: Path) -> tuple[dict[str, str], int, float]
```

Return `(recovered_accounts, hash_computations, elapsed_seconds)`.
The first value maps account names to matching candidates.

Read `account,sha256` CSV rows and nonempty stripped UTF-8 wordlist lines.
For each candidate compute `SHA256(UTF8(candidate))` **once**, then compare
the digest against all account targets. Recover every matching account,
including accounts with equal target digests. Process the entire wordlist
even if all accounts have already matched, so the unsalted count is exactly
the number of nonempty candidate lines. Treat target hex case consistently.
Use `time.perf_counter()` around the candidate computations.

Run this public three-word fixture immediately:

```console
python3 - <<'PY'
import hashlib
import tempfile
from pathlib import Path
from crack_unsalted import crack
with tempfile.TemporaryDirectory() as directory:
    base = Path(directory)
    words, targets = base / "words.txt", base / "targets.csv"
    words.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    targets.write_text("account,sha256\n"
        + "example_a," + hashlib.sha256(b"beta").hexdigest() + "\n"
        + "example_b," + hashlib.sha256(b"gamma").hexdigest() + "\n", encoding="utf-8")
    found, count, elapsed = crack(targets, words)
    assert found == {"example_a": "beta", "example_b": "gamma"}
    assert count == 3 and elapsed > 0
print("Unsalted search check: OK")
PY
```

Proceed after `Unsalted search check: OK`. Three candidate hashes can serve
both accounts because no account-specific input changes the digest.

## 3. Write salted crack(), then check it

In `crack_salted.py`, implement the same function signature and tuple shape.
Read `account,salt_hex,sha256`; decode each account's public salt.
For each account, try candidates in wordlist order and compute
`SHA256(salt || UTF8(candidate))`. Stop that account's search at its first
match, then continue with the next account. Count every digest computation,
including successful comparisons. Accounts without matches are omitted from
the recovered mapping.

```console
python3 - <<'PY'
import hashlib
import tempfile
from pathlib import Path
from crack_salted import crack
with tempfile.TemporaryDirectory() as directory:
    base = Path(directory)
    words, targets = base / "words.txt", base / "targets.csv"
    words.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
    salts = [b"fixture-salt-01", b"fixture-salt-02"]
    rows = ["account,salt_hex,sha256"]
    for account, salt, word in zip(["example_a", "example_b"], salts, [b"beta", b"gamma"]):
        rows.append(f"{account},{salt.hex()},{hashlib.sha256(salt + word).hexdigest()}")
    targets.write_text("\n".join(rows) + "\n", encoding="utf-8")
    found, count, elapsed = crack(targets, words)
    assert found == {"example_a": "beta", "example_b": "gamma"}
    assert count == 5 and elapsed > 0
print("Salted search check: OK")
PY
```

Proceed after `Salted search check: OK`. The count is five because the first
account needs two candidates and the second needs three. This check imports
only the salted implementation.

## 4. Write the two main programs

Add `argparse`, `main()`, and execution guards. Each program accepts two local
positional arguments: the appropriate target CSV, then the wordlist.
Call its `crack()` and print recovered **count**, hash count, elapsed seconds,
and hashes per second. Avoid printing recovered course candidates; retain them
only in the function's returned mapping.

```console
python3 -c "import crack_unsalted, crack_salted; print('Import check: OK')"
LAB01_GRADE=1 python3 -m unittest test_dictionary_cost.py -v
```

The import check must not perform an attack. All three enabled tests must pass.

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

### Connect both results to the completion flag

Extend your `crack_salted.py` main after its own metrics: import the
`crack()` function from your completed `crack_unsalted.py`, and run it on
`unsalted_hashes.csv` beside the selected salted CSV, using the same wordlist.
Keep each script's own `crack()` return contract unchanged.

Require the two recovered account mappings to be identical and require all
account names in both input CSVs to have been recovered. A partial mapping
or disagreement is an incomplete experiment. Once those conditions hold, call
`canonical_account_proof(recovered)` and use its result as the proof for
`data/flag_challenge.json`. Print the returned `FLAG{...}` as the final
line of `crack_salted.py`.

The canonical encoding is JSON with lexicographically sorted account keys,
no extra whitespace, and Unicode preserved as text:
`json.dumps(mapping, sort_keys=True, separators=(',', ':'), ensure_ascii=False)`.
For the public mapping `{"b": "public-two", "a": "public-one"}`, the exact
proof text is `{"a":"public-one","b":"public-two"}`. Use the shared encoder;
never print the actual recovered mapping or its proof.

`compare_cost.py` remains the supplied metrics comparison. Both of your
search implementations and the measured comparison are required even after
the flag opens.

## 5. Run the KDF sample and interpret the timings

A password KDF deliberately raises the cost of every verification and guess.
Salt provides uniqueness; a work factor provides CPU or memory cost. Neither
adds entropy to a weak password.

```console
python3 samples/benchmark_kdfs.py --trials 3
python3 samples/benchmark_kdfs.py --trials 5
```

Each run prints median milliseconds for all five mechanisms:

| Row | Configuration | Observe |
| --- | --- | --- |
| `SHA-256 (unsafe)` | No work factor | Fast baseline |
| `PBKDF2-100k` | HMAC-SHA-256, 100,000 iterations | Repeated computation |
| `bcrypt-cost-10` | Logarithmic cost 10 | CPU cost |
| `scrypt-N=2^14` | `n=2**14, r=8, p=1` | Memory/CPU cost |
| `Argon2id-32MiB` | Time 2, 32,768 KiB, parallelism 1 | Memory cost |

The script warms up each operation before measuring. Exact times and ordering
can vary by host. Record parameters, medians, trial counts, and hardware
context. A fast result is not a desirable password-storage goal. The fixed
salt in this benchmark is for repeatable experiments, not registration.

## 6. Run the registration sample and inspect its record

Choose a fictional password and enter it interactively:

```console
python3 samples/register_login_demo.py register student01
python3 samples/register_login_demo.py verify student01
python3 samples/register_login_demo.py verify student01
python3 -m json.tool auth_db.json
```

The first command prints `registered`; the correct input prints `verified`;
a different input prints `authentication failed`. Inspect the JSON record for
algorithm `pbkdf2-sha256`, 200,000 iterations, a random 16-byte salt encoded
as hex, and a verifier. No plaintext password should be present. This generated
`auth_db.json` is ignored by Git.

For independent experiments, pass `--db /tmp/lab01-auth.json` to both commands.
Do not put passwords in shell arguments. Production KDF parameters must be
tuned on deployment hardware; these are classroom settings.

## 7. Run the course data and compare cost

```console
python3 crack_unsalted.py data/unsalted_hashes.csv data/lab01-small.txt
python3 crack_salted.py data/salted_hashes.csv data/lab01-small.txt
python3 compare_cost.py data
```

Your two programs should report their computed metrics; `crack_salted.py` also
prints the Part flag after the combined-result check. The provided comparison
tool prints:

```text
experiment   found   hashes    seconds     hashes/s
unsalted         <N>     <N>   <seconds>    <rate>
salted           <N>     <N>   <seconds>    <rate>
```

Both methods should recover the supplied fictional records. Record counts and
times; do not publish recovered passwords. Unsalted work is one hash per word;
salted work is up to `accounts × words`, with per-account early stopping.
Timing depends on the host and is noisy for small inputs, so discuss operation
counts alongside elapsed time. No output files are required for this comparison.

## 8. Completion and report

- [ ] Both empty exercise files now contain complete CLI programs.
- [ ] Both public search checks and all enabled tests pass.
- [ ] Both course-data searches and the comparison succeed.
- [ ] Five KDF medians and configurations are recorded.
- [ ] Correct and incorrect local login outcomes are observed.
- [ ] The stored JSON contains no plaintext password.
- [ ] The final program authenticates its own `data/flag_challenge.json` and prints the Part flag.

Submit the two exercise files, metric outputs, test results, and analysis.
Explain why unsalted candidate work is reusable, why distinct salts need
separate work, how stopping rules affect counts, why a KDF is needed in addition
to salt, which mechanisms consume memory, and why server rate limiting affects
Part 2 but cannot observe these offline guesses. Do not submit recovered
candidates or local authentication passwords in public reports.
