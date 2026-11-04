# Part03: RSA Key Generation, Encryption, and CRT

[한국어](../../../../labs/lab03/part03/README.md) | **English**

You want to speed up a program whose RSA decryption is slow.
Implement decryption of the same ciphertext using one large exponentiation and using
CRT with two smaller exponentiations. Compare whether the results agree and how the speeds differ.

## 1. Learning Objectives

1. **Derive key values:** use supplied primes p and q to calculate the RSA key and CRT helpers.
2. **Encrypt and decrypt:** implement RSA encryption and direct decryption in C with OpenSSL BIGNUM.
3. **Compare CRT:** implement CRT decryption and compare correctness and speed with direct decryption.

This Part uses integer textbook RSA. Message encoding is addressed in Part06.

## 2. Provided Materials

- [starter/rsa_engine.c](../../../../labs/lab03/part03/starter/rsa_engine.c): four function TODOs
- [starter/rsa_engine.h](../../../../labs/lab03/part03/starter/rsa_engine.h): `LabRSA` structure and function interfaces
- [starter/rsa_io.c](../../../../labs/lab03/part03/starter/rsa_io.c): allocation/cleanup, prime-file reading, and byte-conversion helpers
- [data/](../../../../labs/lab03/part03/data/): primes p and q forming 2048- and 3072-bit n (two hexadecimal lines per file)
- [tests/check.py](../../../../labs/lab03/part03/tests/check.py), [tests/driver.c](../../../../labs/lab03/part03/tests/driver.c): compilation, correctness checks, and timing

**Edit `starter/rsa_engine.c`.** Use the supplied p and q rather than generating primes yourself.
The checker allocates the BIGNUM fields of `LabRSA` and supplies p, q, and e.
All four functions must check API results and temporary allocation failures, returning 1 on success and 0 on error.
Preserve the header and function interfaces; do not add a separate `main()`.

## 3. Tasks

### Stage 1: Derive RSA key values

- **`rsa_derive(key, ctx)`: calculate key values and CRT helpers**

    Preserve the supplied p, q, and e=65537. Calculate the following values and store them in the
    corresponding `key` fields. Compute d as the inverse modulo the phi below.

    $$n=pq,\quad \phi=(p-1)(q-1),\quad d=e^{-1}\bmod\phi$$

    $$dp=d\bmod(p-1),\quad dq=d\bmod(q-1),\quad qinv=q^{-1}\bmod p$$

    Do not decrement p or q themselves. Release temporary BIGNUMs after use.

### Stage 2: Implement encryption and direct decryption

> **Calculation goal**
>
> $$c=m^e\bmod n,\qquad m=c^d\bmod n$$
>
> m is the plaintext integer and c is the ciphertext integer.

- **`rsa_encrypt(out, message, key, ctx)`: encryption**

    Check `0 <= message < n`, returning 0 for out-of-range input.
    Call `BN_mod_exp` exactly once with e and n to store the ciphertext in `out`.
    Return 1 on success or 0 on failure.

- **`rsa_decrypt_direct(out, ciphertext, key, ctx)`: direct decryption**

    Check `0 <= ciphertext < n`, returning 0 for out-of-range input.
    Call `BN_mod_exp` exactly once with d and n to store the plaintext in `out`.
    Return 1 on success or 0 on failure.

### Stage 3: Implement and compare CRT decryption

- **`rsa_decrypt_crt(out, ciphertext, key, ctx)`: CRT decryption**

    Check `0 <= ciphertext < n`, returning 0 for out-of-range input.
    Call `BN_mod_exp` exactly twice to calculate:

    $$m_p=c^{dp}\bmod p,\qquad m_q=c^{dq}\bmod q$$

    Recombine the two results using the Chinese Remainder Theorem (CRT) and store the plaintext in `out`.
    You can use `qinv` from stage 1. Residue differences may be negative: handle them with
    `BN_mod_sub` or equivalent and keep the final result in `[0,n)`.
    Return 1 on success or 0 on error, and release temporary memory.

- **Compare results and speed**

    Check that both decryption results equal the original plaintext.
    Compare repeated timing medians and speedups for direct/CRT decryption with 2048- and 3072-bit keys.
    Use `BN_mod_exp` in both methods, excluding key generation, initialization, and I/O from timing.

## 4. How to Run

Complete [Lab03 setup](../README.md#setup), then run in the **course container terminal**.
The checker compiles the C source automatically. No extra installation or separate server is needed.

```console
cd /workspace/labs/lab03/part03
python3 tests/check.py
```

The incomplete starter is expected to produce this error; line numbers may differ.
Implement or fix the functions, then run the same command again.

```text
FAIL: AssertionError: 2048-bit check failed:
FAIL: saved_p && saved_q && rsa_derive(&k,ctx)==1 (line 99)
```

After passing with the supplied primes, check fresh primes as well. Generating them is excluded from timing.

```console
python3 tests/check.py --fresh
```

Successful JSON output includes these values (excerpt):

```json
{
  "status": "PASS",
  "receipt": "LAB03{part03_local_checks_passed}"
}
```

`LAB03{part03_local_checks_passed}` is not secret, so you may disclose it in your report.

<details>
<summary>Reading results and additional options</summary>

The JSON `performance` field contains measurements for each key size.

| Field | Meaning |
| --- | --- |
| `bits` | Bit length of RSA modulus n |
| `direct_ns`, `crt_ns` | Median direct/CRT decryption time in ns |
| `speedup` | Direct decryption time / CRT decryption time |
| `required_speedup` | Minimum speedup required in this environment |
| `baseline_direct_ns`, `baseline_split_ns` | Full/split exponentiation timings used for calibration |

Use `--solution PATH` for another C file or `--data PATH` for a prime-file directory.
Read error output for compilation failures. Compilation has a 20-second limit; each key-size run has 45 seconds.
Reduce CPU contention and rerun in the same container if performance fluctuates.

</details>

## 5. Success Conditions

- **Key derivation:** correct n, d, dp, dq, and qinv, preserving supplied p, q, and e.
- **Encryption/decryption:** handle 0, 1, n−1, p, q, and random plaintexts, rejecting out-of-range inputs.
- **Operations:** with the specified operands, call `BN_mod_exp` once for encryption/direct decryption and twice for CRT decryption.
- **Performance:** CRT meets the speedup criteria over direct decryption for both key sizes.

<details>
<summary>Performance criteria</summary>

Use nine-round medians after warm-up, with a fresh ciphertext per operation.
Input preparation, correctness comparisons, key generation, and file I/O are excluded.

The checker calculates baseline speedup R using full-modulus and two-small-modulus exponentiation in the same library.
The required speedup is `1 + 0.35*(R-1)`. Submitted direct and CRT times must each stay within 1.8 times their respective baselines.
There is no fixed millisecond threshold. Investigate the environment if R is at most 1.05.
Staff separately confirm course Docker measurements.

</details>

## 6. Submission Requirements

Submit completed `rsa_engine.c` and Part03 of the [report template](../REPORT_TEMPLATE.md).
Include warning-free build/check logs, direct/CRT median and speedup tables for both key sizes, and answers to every Checkpoint Question below.
If you changed the header, submit it and explain why.

## 7. Checkpoint Questions

1. Why does reducing exponents to dp and dq preserve the decryption result?
2. Does your implementation work for messages divisible by p or q?
3. Which cost dominates: the two exponentiations or recombination?
4. How would including key generation or I/O distort this comparison?
