# Part05: RSA Low Public Exponent Attack

[한국어](../../../../labs/lab03/part05/README.md) | **English**

## 1. Learning Objectives

Exploit the absence of modular reduction when textbook RSA uses e=3 and
`m^3<n`. Implement exact integer cube roots without floating point, and
distinguish inputs to which this direct-root attack does not apply.

## 2. Challenge Scenario

Analyze an application encrypting short messages with public exponent 3 and no
encoding. Recover the message using only the public key and ciphertext.
Factoring n is unnecessary.

## 3. Provided Materials

- [data/challenge.json](../../../../labs/lab03/part05/data/challenge.json): decimal-string n/e/c for
  `positive` and `negative`, and the actual message's SHA-256. The positive case
  satisfies `m^3<n`; the negative case undergoes modular reduction and does not
  permit the direct-root attack.
- [starter/recover.py](../../../../labs/lab03/part05/starter/recover.py): exact-root and recovery TODOs.
- [tests/check.py](../../../../labs/lab03/part05/tests/check.py): re-encryption, negative cases, and large-integer boundaries.

## 4. Tasks

1. Implement `integer_cube_root(value)` returning
   `(floor(cuberoot(value)), is_exact)` for nonnegative integers. Raise
   `ValueError` for negatives. Binary search or integer Newton iteration is
   suitable. Do not rely on `float`, `value ** (1/3)`, or rounding.
2. In `recover(challenge)`, obtain an exact cube root, verify `m^3<n` and
   `pow(m,e,n)==c`, and return the integer. Return `None` if e is not 3, c lies
   outside `[0,n)`, or the direct-root attack does not apply.
3. Convert the recovered integer to minimal-length big-endian bytes and check
   the message and SHA-256. The recovered message contains this Part's flag.
4. Confirm that the negative case is rejected rather than treating a rounded-down
   root as plaintext. Do not expand the task to other low-exponent attacks or factoring.

## 5. How to Run

Use the shared `course` container from [Lab03 setup](../README.md#setup).

```console
cd /workspace/labs/lab03/part05
python3 tests/check.py
```

Actual incomplete-starter output, exit code 1:

```text
FAIL: AssertionError: submission failed: NotImplementedError: implement an exact integer cube root
```

After implementation, run the following command. This output was verified using
the instructor reference. Full JSON includes the recovered integer as evidence,
which the parent checker independently validates.

```console
python3 tests/check.py | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["status"]); print(r["receipt"])'
```

```text
PASS
LAB03{part05_local_checks_passed}
```

Use `--solution PATH` and `--data PATH` for alternate files and inputs. The
timeout is 10 seconds. If only large values fail, check floating-point
conversions, search bounds, and values adjacent to perfect cubes. The public
completion receipt is nonsecret local feedback, separate from the encrypted
challenge flag inside the message.

## 6. Success Conditions

For random large integers, perfect cubes, and their immediate neighbors,
require `root^3 <= value < (root+1)^3` and the correct exactness indicator.
Pass exact-root, range, re-encryption, and message-hash checks for the positive
case, and reject the negative case. Fresh integers and ciphertexts are tested
beyond the public fixture. Final grading uses independently generated messages
and moduli; printing a fixed flag cannot pass. Rejecting this negative case
does not establish security against every other attack.

## 7. Submission Requirements

Submit completed `recover.py`, recovered integer/message, re-encryption and
hash results, explanation of negative-case rejection, and the
[report](../REPORT_TEMPLATE.md).

## 8. Analysis Questions

1. Why does RSA encryption equal ordinary integer cubing when `m^3<n`?
2. What goes wrong with floating-point cube roots on large integers?
3. What happens when you round down and re-encrypt in the negative case?
4. How does randomized encoding affect this attack's conditions?
