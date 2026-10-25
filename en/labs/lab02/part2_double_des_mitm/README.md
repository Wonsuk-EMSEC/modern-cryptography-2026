# Part 2: Double-DES Meet-in-the-Middle Attack

[한국어](../../../../labs/lab02/part2_double_des_mitm/README.md) | **English**

**Estimated time:** 35 minutes. **Environment:** course Docker container.

Two independent reduced-space keys protect a record using
`C = E_K2(E_K1(P))`. Recover both key IDs with a meet-in-the-middle
(MITM) search and two known pairs, then decrypt the record.

`double_des_mitm.py` is provided as a **zero-byte file**. Write your complete
program there, including imports and `main()`. The samples show construction
and file formats without searching. Keep functions importable.

## 1. Run and understand the samples

Prepare the [course container](../README.md#setup), then run inside it:

```console
cd /workspace/labs/lab02/part2_double_des_mitm
python3 samples/double_des_roundtrip.py
python3 samples/data_loading.py
```

Read the round-trip sample in execution order. Public example key IDs
`17` and `93` each use an eight-bit space. The 18-byte plaintext receives
six `0x06` bytes, making 24 bytes or three DES blocks. Encryption applies
`key1` then `key2`; decryption reverses the order. Look for:

```text
Plaintext: b'Hello, Double DES!'
Recovered: b'Hello, Double DES!'
Intermediate-value check: OK
Double-DES round-trip check: OK
```

The intermediate check compares the first encryption result to the first
decryption result. For correct keys, `E_K1(P) = D_K2(C)`; this motivates
the search table. **Pad once before both layers and unpad once after both
layers.** Intermediate data already consists of complete blocks.

The data-loading sample reports `Bits per key ID: 16`, `Known pairs: 2`,
eight-byte blocks for each pair, and `Public data shape check: OK`.
The task uses **16 bits per key**, distinct from the sample's eight bits.
JSON pair strings need `bytes.fromhex()`; the encrypted record is binary
and needs `read_bytes()`.

## 2. Write and check `double_encrypt()`

Implement this interface in `double_des_mitm.py`:

```python
double_encrypt(block: bytes, key1: bytes, key2: bytes) -> bytes
```

It accepts one eight-byte block and two encoded DES keys. Use
`encrypt_block()` from `common.des` in the construction's order.
Do not pad or unpad the block.

The sample demonstrates shared-helper imports; your exercise file is one
directory above `samples/`, so adjust its path.

Check this function before adding decryption:

```console
PYTHONPATH=.. python3 - <<'PY'
from double_des_mitm import double_encrypt
from common.des import encrypt_bytes, make_des_key
block = b"CRYPTO26"
key1, key2 = make_des_key(7, 8), make_des_key(91, 8)
expected = encrypt_bytes(encrypt_bytes(block, key1), key2)
assert double_encrypt(block, key1, key2) == expected
print("Double-DES encryption check: OK")
PY
```

Expected: `Double-DES encryption check: OK`. These known example keys are
independent of the task.

## 3. Write and check `double_decrypt()`

Implement the corresponding one-block interface:

```python
double_decrypt(block: bytes, key1: bytes, key2: bytes) -> bytes
```

Use `decrypt_block()` twice in reverse key order. Do not pad or unpad.
Run this check using the function completed in Step 2:

```console
PYTHONPATH=.. python3 - <<'PY'
from double_des_mitm import double_encrypt, double_decrypt
from common.des import make_des_key
block = b"CRYPTO26"
key1, key2 = make_des_key(7, 8), make_des_key(91, 8)
assert double_decrypt(double_encrypt(block, key1, key2), key1, key2) == block
print("Double-DES decryption check: OK")
PY
```

Proceed after `Double-DES decryption check: OK`.

## 4. Write and check `recover_keys()`

Implement:

```python
recover_keys(pairs: list[tuple[bytes, bytes]], key_bits: int) -> list[tuple[int, int]]
```

Each input tuple contains `(plaintext, ciphertext)`. Return a list of
verified `(key1_id, key2_id)` tuples, not encoded key bytes.

1. Reject fewer than two pairs or `key_bits` outside `1..20`
   with `ValueError`.
2. For each first-key ID, compute the intermediate value for the first
   plaintext. Map intermediate bytes to a **list** of IDs, preserving collisions.
3. Walk all second-key IDs backward from the first ciphertext and find
   matching intermediate values.
4. Verify candidates against the remaining pair(s) and return only verified pairs.

Use `make_des_key()` for both mappings. Do not use a nested exhaustive
search over all first-key and second-key combinations as the default method.

```console
PYTHONPATH=.. python3 - <<'PY'
from double_des_mitm import double_encrypt, recover_keys
from common.des import make_des_key
bits, id1, id2 = 8, 7, 91
key1, key2 = make_des_key(id1, bits), make_des_key(id2, bits)
pairs = [(block, double_encrypt(block, key1, key2))
         for block in (b"CRYPTO26", b"BLOCK-02")]
assert recover_keys(pairs, bits) == [(id1, id2)]
for bad_pairs, bad_bits in ((pairs[:1], bits), (pairs, 21)):
    try:
        recover_keys(bad_pairs, bad_bits)
    except ValueError:
        pass
    else:
        raise AssertionError("reject invalid search parameters")
print("MITM small-fixture check: OK")
PY
```

Expected: `MITM small-fixture check: OK`. Resolve failures while each key
space has only 256 candidates.

## 5. Write and check `decrypt_flag()`

Implement:

```python
decrypt_flag(encrypted: bytes, key1_id: int, key2_id: int, key_bits: int) -> bytes
```

Map the IDs to keys, reverse both encryption layers for every block,
assemble the padded message, and call `unpad8()` once. You may use
`decrypt_bytes()`. Return unpadded bytes.

```console
PYTHONPATH=.. python3 - <<'PY'
from double_des_mitm import decrypt_flag
from common.des import encrypt_bytes, make_des_key, pad8
message, bits, id1, id2 = b"public Double-DES demo", 8, 7, 91
key1, key2 = make_des_key(id1, bits), make_des_key(id2, bits)
encrypted = encrypt_bytes(encrypt_bytes(pad8(message), key1), key2)
assert decrypt_flag(encrypted, id1, id2, bits) == message
print("Double-DES record check: OK")
PY
```

Expected: `Double-DES record check: OK`. This checks multiple blocks,
layer order, and final padding removal without searching.

## 6. Write `main()` and connect the files

Implement `main() -> None` with a guarded entry point. Locate `data/`
relative to `__file__` so execution works from the Part or Lab02 directory.

Read `data/known_pairs.json` as JSON. Its `key_bits` selects the space
for each key; each `pairs` entry has hexadecimal `plaintext` and
`ciphertext`. Convert them to blocks as shown in the data-loading sample.

Measure `recover_keys()` using `time.perf_counter()` and print seconds
and verified-pair count. The supplied instance should yield exactly one pair;
handle zero or multiple pairs clearly. Print both recovered IDs, read
`data/encrypted_flag.bin`, call `decrypt_flag()`, and print its ASCII result.

```console
python3 -c 'import double_des_mitm; print("Import check: OK")'
```

Expected: only `Import check: OK`, with no search starting on import.

## 7. Run the supplied instance and finish

```console
python3 double_des_mitm.py
cd /workspace/labs/lab02
make grade PART=2
```

## Example Output

A successful run has the following output format. Values are hidden in this
example. Include your actual results in your report. Run from
`/workspace/labs/lab02` inside the course container.

```console
python3 part2_double_des_mitm/double_des_mitm.py
verified_pairs=<verified pair count> elapsed=<seconds>s
key1_id=<recovered first ID> key2_id=<recovered second ID>
FLAG{<recovered value>}
```

Completion means the three function checks and import check pass, both known
pairs verify the recovered pair, the record decrypts, and selected-Part
grading passes. Keep the supplied 16-bit parameters. After completing all
Parts, run `make grade` without `PART`.

## Checkpoint Questions

Report elapsed time, verified-pair count, forward-table candidate count,
and number of distinct intermediate values. There are `2**key_bits`
candidate IDs; collisions can reduce distinct dictionary keys. Explain:

1. Why does a naive search require approximately `2**(2*n)` operations?
2. How does MITM change work and memory requirements?
3. Why retain a list of IDs per table entry?
4. Why verify a match with another pair?
5. Why does invoking a cipher twice not automatically double security?

Do not hard-code keys or plaintext. Submit the flag through the designated
course channel and keep it out of public code and sample output.

## Report Checklist

- [ ] Answers to the Checkpoint Questions
- [ ] Main code changes and an explanation of how they work
- [ ] Execution screenshots and the recovered FLAG
- [ ] Verified pair count and elapsed time (visible in the screenshot)
- [ ] Expected forward-table size, actual candidate count, and distinct intermediate-value count
