# Part03: RSA Key Generation, Encryption, and CRT

[한국어](../../../../labs/lab03/part03/README.md) | **English**

## 1. Learning Objectives

Implement RSA key relations using C and OpenSSL BIGNUM. Compare correctness
and median performance of direct and CRT decryption using the same modular
exponentiation routine.

## 2. Challenge Scenario

Develop an RSA engine for a constrained device. First implement RSA correctly,
then accelerate private operations using two smaller moduli and CRT
recombination. Integer textbook RSA here is an implementation exercise;
message encoding is addressed in Part06.

## 3. Provided Materials

- [starter/rsa_engine.h](../../../../labs/lab03/part03/starter/rsa_engine.h): `LabRSA` fields and four function contracts.
- [starter/rsa_engine.c](../../../../labs/lab03/part03/starter/rsa_engine.c): TODOs for core calculations.
- [starter/rsa_io.c](../../../../labs/lab03/part03/starter/rsa_io.c): allocation/cleanup, hexadecimal prime-file reading,
  and `lab_from_bytes`/`lab_to_bytes` conversion helpers.
- [data/](../../../../labs/lab03/part03/data/): public primes p and q forming 2048- and 3072-bit n.
  Each file contains two hexadecimal lines. These primes are intentionally public
  for this key-implementation exercise.
- [tests/driver.c](../../../../labs/lab03/part03/tests/driver.c) and [tests/check.py](../../../../labs/lab03/part03/tests/check.py): independent checks and benchmarks.

## 4. Tasks

1. Preserve supplied p, q, and e=65537. In `rsa_derive`, compute n and d using
   `phi=(p-1)(q-1)`. Also compute `dp=d mod(p-1)`, `dq=d mod(q-1)`, and `qinv=q^-1 mod p`.
2. Implement `rsa_encrypt` and `rsa_decrypt_direct`, each calling `BN_mod_exp`
   exactly once with e/n or d/n respectively. Inputs must lie in `[0,n)`.
3. `rsa_decrypt_crt` must call `BN_mod_exp` exactly twice to obtain
   `mp=c^dp mod p` and `mq=c^dq mod q`, then reconstruct with CRT.
   Handle negative residue differences using `BN_mod_sub` or equivalent and
   return a result in `[0,n)`.
4. Check all API return values and allocations. Return 1 on success and 0 on
   error. Preserve header interfaces and do not add a separate `main`.
5. Report direct/CRT decryption medians and speedups for 2048 and 3072 bits,
   excluding key generation, initialization, and I/O. Use the same `BN_mod_exp` in both.

## 5. How to Run

Use the shared `course` container from [Lab03 setup](../README.md#setup).
GCC and OpenSSL development files are included. The checker compiles submitted
source in a temporary directory using `gcc -std=c11 -O2 -Wall -Wextra -Werror ... -lcrypto`.

```console
cd /workspace/labs/lab03/part03
python3 tests/check.py
```

Actual incomplete-starter output, exit code 1; line numbers may change:

```text
FAIL: AssertionError: 2048-bit check failed:
FAIL: saved_p && saved_q && rsa_derive(&k,ctx)==1 (line 99)
```

After implementation, run the following. This success output was verified using the instructor reference.

```console
python3 tests/check.py --fresh | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["status"]); print(r["receipt"])'
```

```text
PASS
LAB03{part03_local_checks_passed}
```

`--fresh` generates new 2048- and 3072-bit keys before measurement. Use
`--solution PATH` for another C file. Omit the pipe to inspect full JSON metrics.
Read stderr for compilation errors; reduce CPU contention and repeat unstable
measurements. Compilation has a 20-second timeout; each key-size run has 45 seconds.

## 6. Success Conditions

Pass checks for n/d/dp/dq/inverses, round trips for 0/1/n-1/p/q and random
messages, and rejection of out-of-range input. A linker wrapper checks actual
`BN_mod_exp` operands and call counts. Calling direct decryption from the CRT
function or merely printing success cannot pass.

Use nine-round medians after warm-up, with a new ciphertext per operation.
Input preparation, correctness comparisons, key generation, and file I/O stay
outside timing. Measure full-modulus and two-small-modulus exponentiation
baselines in the same library. For baseline speedup R, require
`1 + 0.35*(R-1)`. Submitted direct and CRT times must also stay within 1.8 times
their respective baselines. There is no fixed millisecond threshold. Investigate
the measurement environment if R is at most 1.05. Staff separately confirm course Docker measurements.

The public `LAB03{part03_local_checks_passed}` receipt is nonsecret local
feedback. Final grading executes source in isolation on fresh primes and messages.

## 7. Submission Requirements

Submit completed `rsa_engine.c`, warning-free build/check logs, direct/CRT median
and speedup tables for both key sizes, and the [report](../REPORT_TEMPLATE.md).
If you changed the header, submit it and explain why.

## 8. Analysis Questions

1. Why does reducing exponents to dp and dq preserve the decryption result?
2. Does your implementation work for messages divisible by p or q?
3. Which cost dominates: the two exponentiations or recombination?
4. How would including key generation or I/O distort this comparison?
