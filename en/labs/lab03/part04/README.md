# Part04: RSA Factorization Attack

[한국어](../../../../labs/lab03/part04/README.md) | **English**

Part03 supplied primes p and q; this time you receive only the public key and ciphertext.
However, you know that one prime used to generate the RSA key is too small.
Find that small factor and recover the private exponent and original message.

## 1. Learning Objectives

1. **Factorization:** find a factor of n by trial division within the supplied bound.
2. **Plaintext recovery:** derive the private exponent from p and q and decrypt the ciphertext.
3. **Verification:** check recovered byte length, hash, and re-encryption.

## 2. Provided Materials

- [starter/recover.py](../../../../labs/lab03/part04/starter/recover.py): `solve(challenge)` to implement
- [data/challenge.json](../../../../labs/lab03/part04/data/challenge.json): public key, ciphertext, and search conditions
- [tests/check.py](../../../../labs/lab03/part04/tests/check.py): factor, private-exponent, and plaintext checks

| Input field | Meaning |
| --- | --- |
| `n`, `e`, `c` | RSA modulus, public exponent, and ciphertext (decimal strings) |
| `factor_bound` | Inclusive upper bound for the small-factor search |
| `message_bytes` | Original message length in bytes |
| `plaintext_sha256` | SHA-256 for verifying recovery |

## 3. Tasks

> **Attack sequence**
>
> $$n=pq\quad\longrightarrow\quad\phi=(p-1)(q-1),\quad d=e^{-1}\bmod\phi\quad\longrightarrow\quad m=c^d\bmod n$$
>
> Small practice example: n=55, e=3, c=13. Use `challenge.json` for the actual task.

- **`solve(challenge)`: recover plaintext by factorization**

    Implement this in `starter/recover.py`. `challenge` is a dictionary loaded and passed by the checker.
    Convert `n`, `e`, and `c` to integers, then find a factor by trial division from 2 through `factor_bound`.
    Let p be that factor and calculate q=n/p using integer arithmetic. Do not exceed the search bound.

    Calculate phi and d, verifying `e*d mod phi == 1`, then decrypt the ciphertext.
    You may use built-in `pow` in this Part.

    Convert the decrypted integer into **exactly `message_bytes` big-endian bytes**.
    Preserve leading zeros, since they are part of the original message. Check that SHA-256 matches
    `plaintext_sha256` and that re-encrypting the recovered integer gives the original c.

    Return p, q, and d as integers and `message_hex` as the recovered bytes' hexadecimal string.
    Do not hardcode factors, the private exponent, or plaintext answers.

    ```python
    {'p': p, 'q': q, 'd': d, 'message_hex': message.hex()}
    ```

## 4. How to Run

Complete [Lab03 setup](../README.md#setup), then run in the **course container terminal**.
No additional installation or separate server is needed.

```console
cd /workspace/labs/lab03/part04
python3 tests/check.py
```

The incomplete starter is expected to produce this error.
Implement or fix `solve()`, then run the same command again.

```text
FAIL: AssertionError: submission failed: NotImplementedError: factor the weak modulus and decrypt
```

Successful JSON output includes these values (excerpt):

```json
{
  "status": "PASS",
  "receipt": "LAB03{part04_local_checks_passed}"
}
```

`proof` contains the returned p, q, d, and `message_hex`. The recovered message is this challenge's
short verification value; no PDF or separate file is generated.
`LAB03{part04_local_checks_passed}` is not secret, so you may disclose it in your report.

<details>
<summary>Additional options and troubleshooting</summary>

Use `--solution PATH` for another implementation or `--data PATH` for another JSON input.
The whole checker has a 10-second limit; the subprocess executing your function has an 8-second limit.
For timeouts, check the search bound. For hash mismatches, check integer conversion, byte length, and big-endian order.

</details>

## 5. Success Conditions

- **Factorization:** p and q are distinct, each greater than 1, their product is n, and the smaller factor is within the bound.
- **Private exponent:** `0 < d < phi` and `e*d mod phi == 1`.
- **Recovery:** decryption/re-encryption agree, and byte length and SHA-256 match the supplied values.

## 6. Submission Requirements

Submit completed `recover.py` and Part04 of the [report template](../REPORT_TEMPLATE.md).
Include p, q, d, recovered-byte hexadecimal, candidate count, runtime, hash/re-encryption results,
and answers to every Checkpoint Question below.

## 7. Checkpoint Questions

1. Why does a small factor enable this attack even when the other factor is large?
2. Why does factoring n allow recovery of the private exponent?
3. Why specify a length when converting the decrypted integer into bytes?
4. Which errors do re-encryption and SHA-256 checks detect respectively?
