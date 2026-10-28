"""Provided exact primality helper ONLY for integers below 2**64.

Deterministic Miller-Rabin witness set for this bounded domain. The Part01
exact-primality assignment still requires trial division of the smaller inputs.
"""


def is_prime64(n):
    if not isinstance(n, int) or not 0 <= n < 2**64:
        raise ValueError("prime64 only supports unsigned 64-bit integers")
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in (2, 325, 9375, 28178, 450775, 9780504, 1795265022):
        if a % n == 0:
            continue
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True
