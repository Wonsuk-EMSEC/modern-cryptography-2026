# Part01: Modular Exponentiation and Primality Testing

[한국어](../../../../labs/lab03/part01/README.md) | **English**

## 1. Learning Objectives

Implement MSB-first Square-and-Multiply and evaluate correctness, operation
counts, and relative runtime. Compare trial division through the square-root
bound with a Fermat screen, and construct a 128-bit composite passing base 2.

## 2. Challenge Scenario

Develop exponentiation and prime screening for a constrained cryptographic device.
A correct implementation that is too slow fails the performance challenge.
As an attacker, construct a structured composite that fools the screen. Never
use this composite as an RSA prime in subsequent Parts.

## 3. Provided Materials

- [starter/math_challenges.py](../../../../labs/lab03/part01/starter/math_challenges.py): five function contracts and TODOs.
- [starter/prime64.py](../../../../labs/lab03/part01/starter/prime64.py): exact primality helper for `0 <= n < 2**64`.
  Use it to validate Challenge 3 factors; it does not replace your trial division.
- [data/challenge.json](../../../../labs/lab03/part01/data/challenge.json): prevalidated 16-, 20-, 24-, 28-, and 32-bit inputs,
  and four disjoint, solvable search intervals of at most 100,001 candidates each.
- [tests/check.py](../../../../labs/lab03/part01/tests/check.py): public feedback that checks actual returned values.

## 4. Tasks

1. Implement `naive_modular_exponentiation(base, exponent, modulus)` and
   `modular_exponentiation(...)`. Raise `ValueError` for negative exponents or
   nonpositive moduli. Handle exponent zero, modulus one, and negative bases.
2. The fast function processes every exponent bit, including the leading bit,
   from MSB to LSB. Square for each bit, multiply by the base for a one bit,
   and reduce immediately after every multiplication. Do not substitute `pow`,
   `**`, or an external exponentiation helper for your implementation.
3. Implement `is_prime_exact(n)` by trial division through the square-root bound.
   `fermat_test(n, base)` must call your fast exponentiation function. Return
   false for `n < 2` or a base not coprime to n. Compare equal-sized primes,
   composites with small factors, and composites without small factors.
4. Actually search the supplied inclusive interval in `generate_pseudoprime(t_min, t_max)`.
   If `p1=6t+1`, `p2=12t+1`, `p3=18t+1` are prime, test their product n and return
   `{'t': t, 'factors': [p1,p2,p3], 'n': n}`. Require exactly 128 bits and a
   passing base-2 Fermat test. Raise `ValueError` if no candidate exists.
   Do not trial-divide the entire 128-bit number.
5. Report multiplication counts and times for all three exponentiation methods,
   and primality results by input type. Explain exact versus probable primality.

## 5. How to Run

Start the shared `course` container using [Lab03 setup](../README.md#setup).
Run the following inside its `/workspace`; no additional installation is needed.

```console
cd /workspace/labs/lab03/part01
python3 tests/check.py
```

Actual incomplete-starter output, with exit code 1:

```text
FAIL: NotImplementedError: implement MSB-first square-and-multiply
```

After implementation, summarize the result using the following command. This
success output was verified with the instructor reference. Full JSON includes
operation counts and timings measured in your current environment.

```console
python3 tests/check.py | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["status"]); print(r["receipt"])'
```

```text
PASS
LAB03{part01_local_checks_passed}
```

The checker has a 30-second limit. Reduce competing CPU work and rerun inside
the same container if relative measurements fluctuate. Use `--solution PATH`
and `--data PATH` for alternate submission files and inputs. Importing the
submission must not start a search automatically.

## 6. Success Conditions

Pass random and edge cases, MSB processing checks, and exactly
`L+popcount(exponent)` multiplications for an L-bit exponent. The naive method
must multiply exponent times. For exponents 75,001, 125,003, and 200,003,
compare repeated medians after warm-up, excluding startup and file I/O.
The required speedup is calibrated from this runtime's naive/built-in-pow gap:
`min(10, max(2, naive_time / pow_time / 20))`. There is no fixed millisecond
threshold. Staff separately confirm final performance records in course Docker.

Pass both primality methods and Fermat counterexamples such as 561. For distinct
answers in every search interval, the verifier checks prime factors, structure,
factor product, compositeness, 128-bit length, and base 2. The public
`LAB03{part01_local_checks_passed}` receipt is nonsecret local feedback. Final
grading executes source on new inputs and intervals; printing a receipt is insufficient.

## 7. Submission Requirements

Submit completed `math_challenges.py`, t/three factors/n for each interval,
operation-count and median-timing tables, environment and commands, and the
[report](../REPORT_TEMPLATE.md). Functions must be importable.

## 8. Analysis Questions

1. How do the two implementations scale when the exponent grows by a factor k?
2. Which primality method is faster on composites with small factors, and why?
3. Why does passing base 2 fail to prove primality?
4. Why do the three factors and construction constraints provide stronger evidence than a Fermat pass alone?
