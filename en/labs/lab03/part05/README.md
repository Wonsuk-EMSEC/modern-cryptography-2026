# Part05: RSA Low Public Exponent Attack

[한국어](../../../../labs/lab03/part05/README.md) | **English**

Analyze a program encrypting short messages with RSA, public exponent e=3, and no encoding.
If the message is small enough, you can recover it without factoring n or finding the private key.
Use the ciphertext's cube root to recover the message and distinguish inputs where this method does not apply.

## 1. Learning Objectives

1. **Integer cube roots:** compute cube roots of large integers without floating point.
2. **Plaintext recovery:** check attack conditions and recover a message from an exact root.
3. **Scope:** return `None` instead of incorrect plaintext when the attack does not apply.

## 2. Provided Materials

- [starter/recover.py](../../../../labs/lab03/part05/starter/recover.py): two function TODOs
- [data/challenge.json](../../../../labs/lab03/part05/data/challenge.json): positive/negative cases and message hash
- [tests/check.py](../../../../labs/lab03/part05/tests/check.py): integer-root, recovery, and boundary checks

| Input field | Meaning |
| --- | --- |
| `positive` | n, e, c (decimal strings) for a case satisfying m³<n |
| `negative` | n, e, c for a case with modular reduction where the direct cube-root attack does not apply |
| `message_sha256` | SHA-256 of the message to recover from positive |

## 3. Tasks

> **Attack condition**
>
> $$e=3,\quad m^3<n\quad\Longrightarrow\quad c=m^3\bmod n=m^3\quad\Longrightarrow\quad m=\sqrt[3]{c}$$
>
> Example: n=55 and m=3 give c=27, whose cube root 3 recovers the plaintext.

### Stage 1: Compute an exact integer cube root

- **`integer_cube_root(value)`: return an integer root and exactness flag**

    Implement this in `starter/recover.py`. For a nonnegative integer, return `(root, is_exact)`.
    `root` is the floor of the cube root, and `is_exact` is a bool indicating whether `root³ == value`.
    For example, return `(3, True)` for 27 and `(3, False)` for 28.

    Use binary search or integer Newton iteration. Do not depend on floating-point rounding,
    such as `float` or `value ** (1/3)`. Handle 0 and 1, and raise `ValueError` for negative inputs.

### Stage 2: Recover plaintext and check applicability

- **`recover(challenge)`: return plaintext only when the attack applies**

    Implement this in the same file. `challenge` contains n, e, c from **one positive or negative case**.
    Convert the three values to integers and compute c's cube root with `integer_cube_root()`.

    For an exact root m, verify `m³<n` and `pow(m,e,n)==c`, then return **integer m**.
    Return `None` if e is not 3, c is outside `[0,n)`, or the root is not exact.
    Do not accept a rounded-down root as plaintext or extend the task to other low-exponent attacks or factorization.

- **Check the message**

    Convert the recovered integer to minimal-length big-endian bytes and compare its SHA-256
    with `message_sha256` in `challenge.json`. The message contains this Part's flag.
    Distinguish this from Part04's fixed-length byte conversion.

## 4. How to Run

Complete [Lab03 setup](../README.md#setup), then run in the **course container terminal**.
No additional installation or separate server is needed.

```console
cd /workspace/labs/lab03/part05
python3 tests/check.py
```

The incomplete starter is expected to produce this error.
Implement or fix both functions, then run the same command again.

```text
FAIL: AssertionError: submission failed: NotImplementedError: implement an exact integer cube root
```

Successful JSON output includes these values (excerpt):

```json
{
  "status": "PASS",
  "receipt": "LAB03{part05_local_checks_passed}"
}
```

`proof.m` is the recovered integer; `proof.negative_rejected` indicates rejection of the negative case.
The checker does not print the message text, so convert the recovered integer to bytes to inspect it.
`LAB03{part05_local_checks_passed}` is not secret, so you may disclose it in your report.
This completion marker is separate from the flag inside the recovered message.

<details>
<summary>Additional options and troubleshooting</summary>

Use `--solution PATH` for another implementation or `--data PATH` for another JSON input.
The whole checker has a 10-second limit; the subprocess executing your functions has an 8-second limit.
If only large integers fail, check floating-point use, search bounds, and values adjacent to perfect cubes.

</details>

## 5. Success Conditions

- **Integer root:** for large integers, perfect cubes, and their immediate neighbors,
  `root³ <= value < (root+1)³` holds and the exactness flag is correct.
- **Positive recovery:** exact root, range, re-encryption, and message SHA-256 all match.
- **Negative rejection:** return `None` when the direct cube-root attack does not apply.
  Checks also use fresh integers/ciphertexts and invalid e/c inputs beyond the public data.

Rejecting the negative case does not establish security against every other attack.

## 6. Submission Requirements

Submit completed `recover.py` and Part05 of the [report template](../REPORT_TEMPLATE.md).
Include the recovered integer/message, re-encryption/hash results, the reason for negative-case rejection,
and answers to every Checkpoint Question below.

## 7. Checkpoint Questions

1. Why does RSA encryption equal ordinary integer cubing when `m^3<n`?
2. What goes wrong with floating-point cube roots on large integers?
3. What happens when you round down and re-encrypt in the negative case?
4. How does randomized encoding affect this attack's conditions?
