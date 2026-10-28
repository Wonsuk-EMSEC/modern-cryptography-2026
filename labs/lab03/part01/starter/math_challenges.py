"""Implement each TODO; importing this module must not start the search."""


def modular_exponentiation(base, exponent, modulus):
    """MSB-first square-and-multiply; exponent >= 0 and modulus > 0.

    Process every bit (including the leading bit), squaring before the
    optional multiply, and reduce after each multiplication. Do not use pow.
    Raise ValueError for a negative exponent or nonpositive modulus.
    """
    raise NotImplementedError("implement MSB-first square-and-multiply")


def naive_modular_exponentiation(base, exponent, modulus):
    """Multiply by base exponent times, with modular reduction."""
    raise NotImplementedError("implement the naive baseline")


def is_prime_exact(n):
    """Exact trial division, stopping at the integer square-root bound."""
    raise NotImplementedError("implement trial division")


def fermat_test(n, base):
    """Return False for n < 2 or a non-coprime base; use your modexp."""
    raise NotImplementedError("implement the Fermat screen")


def generate_pseudoprime(t_min, t_max):
    """Search inclusive bounds. Return {'t': t, 'factors': [p1,p2,p3], 'n': n}.

    Use prime64.is_prime64 for the factors; they fit in 64 bits.
    Raise ValueError if the bounded interval has no candidate.
    """
    raise NotImplementedError("search the supplied Chernick interval")
