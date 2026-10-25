# Part 3: AES-CBC and PKCS#7

**Estimated time:** 35 minutes. **Environment:** course Docker container.

Build PKCS#7 padding and AES-CBC from the one-block AES primitive, then decrypt
a supplied record. The key and IV are exercise inputs; recovering an unknown
AES key is not the goal.

`aes_cbc_pkcs7.py` is provided as a **zero-byte file**. Write imports,
functions, file loading, output, and a guarded entry point there.
Keep functions importable without processing task files.

## 1. Run and understand the library sample

Prepare the [course container](../README.md#setup), then run inside it:

```console
cd /workspace/labs/lab02/part3_aes_cbc_pkcs7
python3 samples/aes_cbc_demo.py
```

Read the sample's execution flow: pad a message, encrypt, decrypt, remove
padding, and check equality. It uses public example key and IV values and
library CBC/padding to show expected behavior. Look for:

```text
Plaintext: b'Hello, AES-CBC!'
Lengths: 15 bytes -> 16 padded bytes
Recovered: b'Hello, AES-CBC!'
AES-CBC round-trip check: OK
Aligned input: 16 bytes -> 32 padded bytes
Full-block padding: 10101010101010101010101010101010
Malformed padding rejected: OK
```

The 15-byte message needs one `0x01` byte. An aligned message needs a
full block of sixteen `0x10` bytes; displayed hex `10` means decimal 16.
AES decryption preserves padding; it must be validated before removal.
A final `0x00` byte cannot represent a valid PKCS#7 length.

**Required functions must implement CBC and padding themselves.** Use
`AES.new(key, AES.MODE_ECB)` only as the single-block AES primitive.
Do not use `AES.MODE_CBC`, library padding helpers, or another library
mode implementation in required functions. The sample and fixture commands
use library operations as independent references.

## 2. Write and check `pkcs7_pad()`

Implement in `aes_cbc_pkcs7.py`:

```python
pkcs7_pad(data: bytes, block_size: int = 16) -> bytes
```

Append one to `block_size` bytes, all equal to the padding length.
Aligned and empty inputs receive a full padding block. Return new bytes.
Support block sizes `1..255`; reject invalid sizes with `ValueError`.

```console
python3 - <<'PY'
from aes_cbc_pkcs7 import pkcs7_pad
assert pkcs7_pad(b"") == b"\x10" * 16
assert pkcs7_pad(b"hello") == b"hello" + b"\x0b" * 11
assert pkcs7_pad(b"A" * 16) == b"A" * 16 + b"\x10" * 16
assert pkcs7_pad(b"A" * 17) == b"A" * 17 + b"\x0f" * 15
assert pkcs7_pad(b"hello", 8) == b"hello" + b"\x03" * 3
print("PKCS#7 padding checks: OK")
PY
```

Expected: `PKCS#7 padding checks: OK`. Fix failures before continuing.

## 3. Write and check `pkcs7_unpad()`

Implement:

```python
pkcs7_unpad(data: bytes, block_size: int = 16) -> bytes
```

Reject empty/unaligned input, a padding length outside `1..block_size`,
or a suffix whose bytes do not all equal that length. Raise `ValueError`
for malformed input or invalid block sizes. Return original bytes on success.

```console
python3 - <<'PY'
from aes_cbc_pkcs7 import pkcs7_pad, pkcs7_unpad
for message in (b"", b"hello", b"A" * 16, b"A" * 33):
    assert pkcs7_unpad(pkcs7_pad(message)) == message
assert pkcs7_unpad(pkcs7_pad(b"hello", 8), 8) == b"hello"
for invalid in (b"", b"short", b"A" * 15 + b"\x00",
                b"A" * 15 + b"\x11", b"A" * 14 + b"\x01\x02"):
    try:
        pkcs7_unpad(invalid)
    except ValueError:
        pass
    else:
        raise AssertionError("malformed padding accepted")
print("PKCS#7 validation checks: OK")
PY
```

Expected: `PKCS#7 validation checks: OK`. The last invalid case requires
checking every padding byte, not just the last byte.

## 4. Write and check `xor_bytes()`

Implement:

```python
xor_bytes(left: bytes, right: bytes) -> bytes
```

Return bytewise XOR for equal-length inputs. Raise `ValueError` for unequal
lengths; do not silently truncate.

```console
python3 - <<'PY'
from aes_cbc_pkcs7 import xor_bytes
assert xor_bytes(b"\x00\xff", b"\x55\x0f") == b"\x55\xf0"
try:
    xor_bytes(b"a", b"ab")
except ValueError:
    pass
else:
    raise AssertionError("unequal XOR lengths accepted")
print("XOR checks: OK")
PY
```

Expected: `XOR checks: OK`.

## 5. Write and check `cbc_encrypt()`

Implement:

```python
cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes
```

Pad the plaintext with your function. For each 16-byte AES block, compute
`C_i = E_K(P_i XOR C_(i-1))`, with the IV as the first preceding block.
Use your XOR function and AES-ECB. Return ciphertext only, without the IV.
Reject an IV length other than 16 with `ValueError`.

Check the public NIST vector now:

```console
python3 - <<'PY'
import json
from pathlib import Path
from aes_cbc_pkcs7 import cbc_encrypt
vector = json.loads(Path("data/nist_cbc_vector.json").read_text())
key, iv = bytes.fromhex(vector["key"]), bytes.fromhex(vector["iv"])
plaintext = bytes.fromhex(vector["plaintext"])
expected = bytes.fromhex(vector["cbc_ciphertext_without_pkcs7_final_block"])
actual = cbc_encrypt(key, iv, plaintext)
assert actual[:len(expected)] == expected
assert len(actual) == len(expected) + 16
print("NIST CBC encryption check: OK")
PY
```

Expected: `NIST CBC encryption check: OK`. The vector omits padding;
your function adds a full final block, so compare the vector to its prefix.

## 6. Write and check `cbc_decrypt()`

Implement:

```python
cbc_decrypt(key: bytes, iv: bytes, ciphertext: bytes) -> bytes
```

Reject non-16-byte IVs, empty ciphertext, and unaligned ciphertext with
`ValueError`. Compute `P_i = D_K(C_i) XOR C_(i-1)` for each block.
Preserve the ciphertext needed for the next block, assemble padded plaintext,
then validate/remove padding once with your `pkcs7_unpad()`.

```console
python3 - <<'PY'
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from aes_cbc_pkcs7 import cbc_encrypt, cbc_decrypt
key, iv = bytes(range(16)), bytes(range(16, 32))
for message in (b"", b"hello", b"A" * 16, b"A" * 33):
    reference = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(message, 16))
    assert cbc_encrypt(key, iv, message) == reference
    assert cbc_decrypt(key, iv, reference) == message
for malformed in (b"", b"x"):
    try:
        cbc_decrypt(key, iv, malformed)
    except ValueError:
        pass
    else:
        raise AssertionError("malformed ciphertext accepted")
invalid_padding = AES.new(key, AES.MODE_CBC, iv).encrypt(b"A" * 15 + b"\x00")
try:
    cbc_decrypt(key, iv, invalid_padding)
except ValueError:
    pass
else:
    raise AssertionError("invalid padding accepted after decryption")
print("CBC decryption and round-trip checks: OK")
PY
```

Expected: `CBC decryption and round-trip checks: OK`. This independently
compares empty, short, aligned, and multiple-block messages. Library mode
and padding calls belong to the fixture, not your required implementation.

## 7. Write `main()`, run the record, and finish

Implement `main() -> None` with a guarded execution entry point. Locate
`data/` relative to `__file__` for execution from Part or Lab02 directories.

| Input | Meaning |
| --- | --- |
| `data/key.bin` | AES key, read as bytes |
| `data/iv.bin` | CBC IV, read as bytes |
| `data/encrypted_flag.bin` | Ciphertext, read as bytes |
| `data/nist_cbc_vector.json` | Public known-answer fixture used above |

Call your `cbc_decrypt()` with these binary inputs and print its ASCII
plaintext. Do not print/embed the task key or hard-code the decrypted message.

```console
python3 -c 'import aes_cbc_pkcs7; print("Import check: OK")'
python3 aes_cbc_pkcs7.py
cd /workspace/labs/lab02
make grade PART=3
```

Importing prints only `Import check: OK`; direct execution prints
`FLAG{...}`. Completion means all five function checks pass, CBC uses
AES-ECB only as a primitive, padding is validated, the supplied record
decrypts, and selected-Part grading passes. After all Parts, run `make grade`.

## Example Output

A successful run has the following output format. Values are hidden in this
example. Include your actual results in your report. Run from
`/workspace/labs/lab02` inside the course container.

```console
python3 part3_aes_cbc_pkcs7/aes_cbc_pkcs7.py
FLAG{<recovered value>}
```

## Checkpoint Questions

Report which cases you checked and their outcomes, then explain:

1. Why must aligned plaintext receive a full padding block?
2. What does the IV provide for the first CBC block?
3. Which plaintext blocks can change if one ciphertext block is modified?
4. Why validate every claimed padding byte?
5. Why is AES-ECB acceptable here only as an underlying one-block primitive,
   while an ECB mode applied directly to a multi-block message has different
   security properties?

Submit the flag through the designated course channel and keep it out of
public code and sample output.

## Report Checklist

- [ ] Answers to the Checkpoint Questions
- [ ] Main code changes and an explanation of how they work
- [ ] Execution screenshots and the recovered FLAG
- [ ] Implementation check results (`make grade PART=3`, then `make grade` after all Parts)
