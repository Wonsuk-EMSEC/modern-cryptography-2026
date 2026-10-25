# Part 1: DES Brute-Force Attack

[한국어](../../../../labs/lab02/part1_des_bruteforce/README.md) | **English**

**Estimated time:** 25 minutes. **Environment:** course Docker container.

Recover a reduced-space DES key from one known plaintext/ciphertext block,
decrypt a separate record, and measure the cost of searching. Real DES has
56 effective key bits; this exercise searches only the supplied **24-bit
key-ID space** of **16,777,216 candidates**.

`des_bruteforce.py` is provided as a **zero-byte file**. Write your complete
program there: imports, functions, file loading, output, and the entry point.
The samples demonstrate the supplied APIs; they do not perform the search.
Keep functions importable without starting the production search.

## 1. Run and understand the samples

Prepare the [course container](../README.md#setup). All commands below run
**inside that container**:

```console
cd /workspace/labs/lab02/part1_des_bruteforce
python3 samples/des_roundtrip.py
python3 samples/data_loading.py
```

Read both samples from imports through `main()` and its execution guard.
The round-trip sample constructs a key from public example ID `17` in an
**8-bit example space**, pads `b"Hello, DES!"`, encrypts, decrypts, and
removes padding. Look for:

```text
Plaintext: b'Hello, DES!'
Lengths: 11 bytes -> 16 padded bytes
Recovered: b'Hello, DES!'
Padding round-trip check: OK
```

DES processes eight-byte blocks. The five appended bytes are all `0x05`;
decryption preserves them until `unpad8()` validates and removes them.
The key and ciphertext are displayed in hexadecimal, but helpers operate on
`bytes`. For an eight-byte plaintext, `pad8()` adds a full block of
eight `0x08` bytes. Try that length and verify the round trip.

The data-loading sample reports `Key-ID bits: 24`, eight-byte known
plaintext and ciphertext blocks, and an encrypted-record length divisible
by eight. Its final line is `Public data shape check: OK`.
`json.loads()` reads parameters; `read_bytes()` reads binary files.
The known block is already exactly eight bytes: **do not pad it for candidate
comparison**. The separate record is padded. Neither sample recovers its key.

## 2. Write and check `brute_force()`

Implement this interface in `des_bruteforce.py`:

```python
brute_force(plaintext: bytes, ciphertext: bytes, key_bits: int) -> tuple[int | None, int, float]
```

Use `make_des_key(key_id, key_bits)` from `common.des` for the required
deterministic key mapping; an integer ID is not an encoded key.
`encrypt_block(block, key)` accepts an eight-byte block and eight-byte key.
The samples show how to import shared helpers; your exercise file is one
directory above `samples/`, so adjust its path accordingly.

1. Reject `key_bits` outside `1..MAX_KEY_BITS` with `ValueError`;
   `MAX_KEY_BITS` is 24.
2. Test IDs from `0` through `2**key_bits - 1` in order, mapping each
   ID and encrypting the known block.
3. Stop at the first match and return `(key_id, tested, elapsed)`.
   Count the matching candidate and measure seconds with `time.perf_counter()`.
4. If none matches, return `(None, 2**key_bits, elapsed)`.

Check this function now, using a small public fixture:

```console
PYTHONPATH=.. python3 - <<'PY'
from des_bruteforce import brute_force
from common.des import encrypt_block, make_des_key
block, bits, expected_id = b"CRYPTO26", 8, 17
ciphertext = encrypt_block(block, make_des_key(expected_id, bits))
found, tested, elapsed = brute_force(block, ciphertext, bits)
assert found == expected_id
assert tested == expected_id + 1
assert elapsed >= 0
try:
    brute_force(block, ciphertext, 25)
except ValueError:
    pass
else:
    raise AssertionError("reject an excessive key space")
print("brute_force small-fixture check: OK")
PY
```

Expected: `brute_force small-fixture check: OK`. Resolve failures before
moving on. The example ID is not the answer to the 24-bit task.

## 3. Write and check `decrypt_flag()`

Implement:

```python
decrypt_flag(encrypted: bytes, key_id: int, key_bits: int) -> bytes
```

Reconstruct the key, decrypt every block with `decrypt_bytes(data, key)`,
and validate/remove padding with `unpad8()` once after assembling the
complete plaintext. Return unpadded bytes.

```console
PYTHONPATH=.. python3 - <<'PY'
from des_bruteforce import decrypt_flag
from common.des import encrypt_bytes, make_des_key, pad8
message, key_id, bits = b"public demo record", 17, 8
encrypted = encrypt_bytes(pad8(message), make_des_key(key_id, bits))
assert decrypt_flag(encrypted, key_id, bits) == message
print("decrypt_flag small-fixture check: OK")
PY
```

Expected: `decrypt_flag small-fixture check: OK`. This checks decryption
independently of searching.

## 4. Write `main()` and connect the files

Implement `main() -> None` and call it only under
`if __name__ == "__main__":`. Locate `data/` relative to `__file__`
so the program works from the Part directory or Lab02 root.

| Input | Read as | Use |
| --- | --- | --- |
| `data/parameters.json` | JSON | Its `key_bits` selects the space |
| `data/known_plaintext.bin` | bytes | Known eight-byte plaintext |
| `data/known_ciphertext.bin` | bytes | Ciphertext to compare |
| `data/encrypted_flag.bin` | bytes | Record to decrypt after recovery |

Call `brute_force()`, handle a missing match clearly, calculate keys per
second as `tested / elapsed` with a zero-time guard, and call
`decrypt_flag()`. Decode the record as ASCII. Print the recovered ID,
candidate count, seconds, rate, and plaintext.

```console
python3 -c 'import des_bruteforce; print("Import check: OK")'
```

Expected: only `Import check: OK`, with no search starting on import.

## 5. Run the supplied instance and finish

```console
python3 des_bruteforce.py
cd /workspace/labs/lab02
make grade PART=1
```

## Example Output

A successful run has the following output format. Values are hidden in this
example. Include your actual results in your report. Run from
`/workspace/labs/lab02` inside the course container.

```console
python3 part1_des_bruteforce/des_bruteforce.py
candidate=<key ID> tested=<candidate count> elapsed=<seconds>s rate=<keys per second> keys/s
FLAG{<recovered value>}
```

A sequential search may take roughly 1–3 minutes, depending on CPU, Docker
resources, and implementation, and may be quiet until it finishes. Measure
the actual search without delays. Keep parameters and ciphertexts together;
changing only `key_bits` does not change the hidden key. Use the original
24-bit data for your final measurement.

Completion means the two function checks and import check pass, the
recovered key verifies the known pair, the record decrypts to `FLAG{...}`,
and the selected-Part grading checks pass. After completing all Parts,
run `make grade` without `PART`.

## Checkpoint Questions

Report candidate count, elapsed time, and measured rate, then answer:

1. Why do we use a reduced space rather than all `2**56` effective keys?
2. At your measured rate, how long would `2**56` checks take? State assumptions.
3. Why does Python timing not predict GPU, FPGA, or ASIC speed?
4. What role do parity bits play, and why must IDs map to distinct effective keys?
5. Does this result show a mathematical weakness in every DES round function,
   or a practical limitation of its key-space size? Explain.

Do not hard-code an ID or decrypted output. Submit the flag only through the
designated course channel and keep it out of public code and sample output.

## Report Checklist

- [ ] Answers to the Checkpoint Questions
- [ ] Main code changes and an explanation of how they work
- [ ] Execution screenshots and the recovered FLAG
- [ ] Candidate count, elapsed time, and keys per second (visible in the screenshot)
