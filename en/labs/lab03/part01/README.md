# Part01: Modular Exponentiation and Primality Testing

[한국어](../../../../labs/lab03/part01/README.md) | **English**

You are reviewing a primality-testing program intended for RSA key generation.
Its developer claims that any number passing the Fermat test can be used as a prime.
Can you trust that claim?

First, implement the exponentiation needed by the test, then compare trial division
and the Fermat test for results and speed. Finally, find a 128-bit composite that
passes the Fermat test to evaluate the developer's claim. Do not use the composite
for actual RSA key generation.

## 1. Learning Objectives

This Part has three stages:

1. **Exponentiation:** implement and compare a slow and a fast method for the same result.
2. **Primality tests:** compare exact testing with a fast screening method.
3. **Find a counterexample:** find a 128-bit composite that passes the Fermat test.

## 2. Provided Materials

- [starter/math_challenges.py](../../../../labs/lab03/part01/starter/math_challenges.py): implement five function TODOs.
- [starter/prime64.py](../../../../labs/lab03/part01/starter/prime64.py): `is_prime64()` checks the smaller factors in stage 3.
- [data/challenge.json](../../../../labs/lab03/part01/data/challenge.json): primality comparison inputs and composite search intervals.
- [tests/check.py](../../../../labs/lab03/part01/tests/check.py): implementation checks and timing.

`challenge.json` contains 16-, 20-, 24-, 28-, and 32-bit comparison inputs and four
solvable search intervals. Each interval contains at most 100,001 candidate t values.

## 3. Tasks

### Stage 1: Compute the same power in two ways

Implement the following two functions in `starter/math_challenges.py` and compare multiplication counts and execution times.

> **Calculation goal**
>
> $$r = b^e \bmod m$$
>
> Example:
>
> $$3^5 \bmod 7 = 243 \bmod 7 = 5$$
>
> Here, `b = base`, `e = exponent`, and `m = modulus`.

- **`naive_modular_exponentiation(base, exponent, modulus)`: repeated multiplication**

    Start with `1 % modulus`, multiply by the base `exponent` times, and reduce after each multiplication.
    Raise `ValueError` for negative exponents or nonpositive moduli.
    For exponent zero, return the initial value without multiplying; also handle modulus one and negative bases.
    Do not replace repeated multiplication with `pow`, `**`, or external exponentiation helpers.

- **`modular_exponentiation(base, exponent, modulus)`: Square-and-Multiply**

    Start with `1 % modulus` and process the exponent's binary representation from its leading bit (MSB-first).
    Square the current result for every bit, including the leading bit; for a one bit, also multiply by the base.
    Reduce after each multiplication. For example, exponent 13 is `1101`, requiring four squares and three additional multiplications.
    Raise `ValueError` for negative exponents or nonpositive moduli; handle exponent zero, modulus one, and negative bases.
    Do not replace your implementation with `pow`, `**`, or external exponentiation helpers.

- **Compare results and speed**

    Check that both functions agree with built-in `pow(base, exponent, modulus)`.
    Compare multiplication counts for your two functions and timings for both functions and built-in `pow`.
    Use built-in `pow` only for correctness checks and timing comparisons.

### Stage 2: Compare two primality tests

Implement the next two functions in the same file. Both return `True` or `False`,
but **`True` has a different meaning in each test**.

- **`is_prime_exact(n)`: exact testing by trial division**

    Check for divisors from 2 through the square-root bound, including the boundary.
    Return `False` if a divisor exists and `True` otherwise. Return `False` for `n < 2`.
    Implement this directly; do not substitute the supplied `is_prime64()`.

- **`fermat_test(n, base)`: screen prime candidates with the Fermat test**

    When `base` and n are coprime, test `base^(n-1) mod n == 1`.
    Call **your `modular_exponentiation()` from stage 1** for exponentiation.
    Return `False` for `n < 2` or when the greatest common divisor is not 1.
    Here, `True` means the number passed the test, not that it is guaranteed to be prime.

- **Compare results and speed**

    Use `prime_sets` in `data/challenge.json`. Each group's `values` contain an equal-bit-length
    prime, a composite with small factors, and a composite without small factors.
    Compare both functions' return values and timings, using 2 as the Fermat `base`.

### Stage 3: Find a composite that passes the Fermat test

- **`generate_pseudoprime(t_min, t_max)`: find a composite that passes the Fermat test**

    Implement this in the same file. Vary t within the interval, including both endpoints, to construct:

    $$p_1=6t+1,\quad p_2=12t+1,\quad p_3=18t+1,\quad n=p_1p_2p_3$$

    Use the supplied `prime64.is_prime64()` to check that all three factors are prime.
    Each factor fits within the function's supported range, `0 <= n < 2**64`.
    The product n must be exactly 128 bits and pass the base-2 Fermat test.
    Check bit length with `n.bit_length()`. **Do not trial-divide the 128-bit n.**

    Return `{'t': t, 'factors': [p1, p2, p3], 'n': n}` when you find a candidate,
    or raise `ValueError` if none exists. Actually search the supplied interval;
    do not hardcode an answer or start the search when the module is imported.

The checker passes each of the four intervals in `search_windows` in `data/challenge.json` separately.

## 4. How to Run

Complete [Lab03 setup](../README.md#setup), then run in the **course container terminal**.
No additional installation or separate server is needed.

```console
cd /workspace/labs/lab03/part01
python3 tests/check.py
```

The incomplete starter is expected to produce the following error. The checker stops at the first failure;
implement or fix the relevant function, then run the same command again.

```text
FAIL: NotImplementedError: implement MSB-first square-and-multiply
```

When all checks pass, the JSON output includes these values (excerpt):

```json
{
  "status": "PASS",
  "receipt": "LAB03{part01_local_checks_passed}"
}
```

`LAB03{part01_local_checks_passed}` is not secret, so you may disclose it in your report.

<details>
<summary>Reading results and additional options</summary>

| JSON field | Contents |
| --- | --- |
| `performance` | Exponentiation times, operation counts, and relative speed |
| `primality` | Trial-division and Fermat timings by input |
| `proof` | t, three factors, and n found in each interval |

`naive_ns` times the checker's reference implementation. Record your own naive function's timing
and primality return values separately. The internal multiplication count of built-in `pow` is not provided.

The checker has a 30-second limit. If performance fluctuates, reduce competing CPU work and rerun in the
same container. Use `--solution PATH` and `--data PATH` to check alternate implementation files and inputs.

</details>

## 5. Success Conditions

- **Stage 1:** both functions return correct results, including edge cases, and follow the specified operation
  order and multiplication counts. The fast function must also meet the speedup requirement over the reference naive implementation.
- **Stage 2:** both primality tests behave as defined, including Fermat passes for composites such as 561.
- **Stage 3:** find a distinct candidate in each of the four intervals, satisfying prime-factor, structure,
  product, 128-bit length, and base-2 checks.

<details>
<summary>Operation counts and performance criteria</summary>

The naive function must multiply exponent times. The fast function must use
`L + popcount(exponent)` multiplications for a positive L-bit exponent.
`popcount` is the number of one bits in its binary representation.

Performance comparisons use exponents 75,001, 125,003, and 200,003, with repeated medians after warm-up.
Process startup and file I/O are excluded. The required speedup is calibrated to the environment as
`min(10, max(2, naive_time / pow_time / 20))`.
`naive_time` measures the checker's reference implementation and `pow_time` measures built-in `pow`;
there is no fixed millisecond threshold. Staff separately confirm final performance records in course Docker.

</details>

## 6. Submission Requirements

Submit your completed `math_challenges.py` and the Part01 section of the
[report template](../REPORT_TEMPLATE.md). Include answers to every Checkpoint Question below.

## 7. Checkpoint Questions

1. How do the two implementations scale when the exponent grows by a factor k?
2. Which primality method is faster on composites with small factors, and why?
3. Why does passing base 2 fail to prove primality?
4. Why do the three factors and construction constraints provide stronger evidence than a Fermat pass alone?
