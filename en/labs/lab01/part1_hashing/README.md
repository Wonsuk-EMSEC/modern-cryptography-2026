[한국어](../../../../labs/lab01/part1_hashing/README.md) | **English**

# Part 1: Hash and salt

Use only fictional classroom passwords. All commands below run inside the course
Docker container. Raw SHA-256 and `SHA256(salt || password)` demonstrate mechanics;
production password storage requires a password KDF, which Part 3 introduces.

## Learning objectives and provided files

Learn to encode strings as UTF-8, distinguish hashing from encryption, recognize
deterministic digests, and explain the role and limitations of public salts.
Hashing has no decryption key. A salt prevents shared precomputation across
accounts; it neither strengthens a weak password nor makes each guess slow.

| File | Role |
| --- | --- |
| `samples/hash_bytes_demo.py` | Complete public message-hashing example |
| `samples/salt_bytes_demo.py` | Complete public salt, hex, and byte-concatenation example |
| `hash_password.py` | Empty student exercise file |
| `salted_hash.py` | Empty student exercise file |
| `test_hashing.py` | Baseline and opt-in implementation checks |
| `data/` | Optional MD5 collision fixtures, separate from these tasks |
| `samples/flag_unlock_demo.py` | Public helper-usage example; no Part answer |
| `data/flag_challenge.json` | Encrypted completion flag, opened by the experiment result |

The exercise files contain no imports, functions, or execution code. Write all
of them yourself. Keep executable work inside `main()` and call it only under
`if __name__ == "__main__":`, so importing a function never prompts for input.

## 1. Run and inspect the samples

```console
cd /workspace/labs/lab01/part1_hashing
python3 samples/hash_bytes_demo.py
python3 samples/salt_bytes_demo.py
pytest -q test_hashing.py
```

The first sample prints `Input bytes: b'Public sample'`, input length 13,
`Digest bytes: 32`, `Hex characters: 64`, a SHA-256 digest, and
`Repeat matches: True`. The hexadecimal digest stays the same across runs.
Study the optional `--input` argument to see how a complete program reads bytes.

The second sample prints `Salt bytes: 16`, a 32-character random salt hex,
a 64-character verifier, and three `True` checks for salt decoding,
reproducibility with the same salt, and the effect of a changed salt. The
generated salt and verifier normally change on each run. No generated file is
left behind. `bytes.fromhex(salt.hex())` reconstructs the original public salt.

Before implementation, pytest reports one passed baseline check and two skipped
implementation checks. Skips mean that the exercise is still to be written.

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

## 2. Write hash_password(), then check it

In `hash_password.py`, implement this interface before adding interactive code:

| Function | Input | Return |
| --- | --- | --- |
| `hash_password(password: str) -> str` | Fictional password text | Lowercase 64-character SHA-256 hex |

Encode the string using UTF-8 and hash the resulting bytes. Do not strip,
normalize, or otherwise change the supplied string. Add the imports you need.

Immediately run this public-fixture check; it uses only this function:

```console
python3 - <<'PY'
import hashlib
from hash_password import hash_password
for text in ("fictional", "한글-example", ""):
    result = hash_password(text)
    assert result == hashlib.sha256(text.encode("utf-8")).hexdigest()
assert hash_password("fictional") != hash_password("different")
print("Unsalted function check: OK")
PY
```

Proceed only after `Unsalted function check: OK`. Repeated inputs must repeat
their digest; changed inputs should change it.

## 3. Write salted_hash(), then check it

In `salted_hash.py`, implement:

| Function | Input | Return |
| --- | --- | --- |
| `salted_hash(password: str, salt: bytes) -> str` | Password text and supplied salt bytes | Lowercase SHA-256 hex of `salt || UTF8(password)` |

This function uses the caller's salt; it must not generate a replacement salt.
Generating a new salt belongs in registration or the interactive program.

```console
python3 - <<'PY'
import hashlib
from salted_hash import salted_hash
first, second = b"a" * 16, b"b" * 16
value = salted_hash("fictional", first)
assert value == hashlib.sha256(first + b"fictional").hexdigest()
assert value == salted_hash("fictional", first)
assert value != salted_hash("fictional", second)
assert salted_hash("한글", first) == hashlib.sha256(first + "한글".encode("utf-8")).hexdigest()
print("Salted function check: OK")
PY
```

Proceed only after `Salted function check: OK`. A server stores both the salt
and verifier so it can repeat the computation during login.

## 4. Add the interactive programs

Write a `main()` and execution guard in each file. Use `getpass.getpass()` so
the fictional input is not displayed or placed in shell arguments.

- `hash_password.py`: read one password and print its digest.
- `salted_hash.py`: read one password, generate 16 random salt bytes with
  `secrets.token_bytes()`, and print `salt=<hex>` and `digest=<hex>`.
- Both programs should identify fast SHA-256 as an educational construction.

Check that importing both files causes no prompt or output:

```console
python3 -c "import hash_password, salted_hash; print('Import check: OK')"
```

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

### Complete the public hash challenge

After the random-salt demonstration, the final `salted_hash.py` program must
open Part 1's completion flag. This challenge is public and requires both
of your hashing functions; it is separate from the fictional password you
entered and the random salt generated above.

Read `data/flag_challenge.json` using `json.loads()`. Its `challenge`
object supplies `input` and `salt_hex`. Compute the unsalted SHA-256 hex
through your `hash_password()`, decode the fixed public salt, and compute
the salted hex through your `salted_hash()`. The proof is:

```text
<unsalted lowercase hex>:<salted lowercase hex>
```

Use exactly one colon and no whitespace. Do not paste precomputed digests into
your program. Call `unlock_flag(flag_path, proof)` and print the returned
`FLAG{...}` as the final line. The fixed challenge salt does not replace the
random-salt demonstration; keep both observations.

## 5. Run the full exercise

```console
python3 hash_password.py
python3 hash_password.py
python3 salted_hash.py
python3 salted_hash.py
LAB01_GRADE=1 pytest -q test_hashing.py
```

Enter the same fictional password in all four runs. The unsalted outputs must
be equal; the random salts and salted digests should differ. Then repeat with
a different input. A digest is 64 hex characters; a salt is 32 hex characters.

The enabled tests should report `3 passed`. The final `salted_hash.py` output
includes a standalone `FLAG{...}` line after opening the public hash challenge.
No files are generated by these interactive programs.

## 6. Completion and report

- [ ] Both initially empty files contain your functions, imports, and main programs.
- [ ] Both small function checks and all enabled tests pass.
- [ ] Identical inputs repeat the unsalted digest.
- [ ] Random salts change the salted verifier.
- [ ] Imports cause no interactive work.
- [ ] The final program authenticates its own `data/flag_challenge.json` and prints the Part flag.

Submit both Python files, commands and observed digests/salts using fictional
inputs, test results, and a short explanation. Explain how hashing differs from
encryption, why a salt must be stored, why salts are public, and why salt plus
fast SHA-256 remains unsuitable for production password storage.
