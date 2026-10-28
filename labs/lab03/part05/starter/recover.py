"""Use integer arithmetic throughout; floating-point roots are insufficient."""


def integer_cube_root(value):
    """Return (floor(cuberoot(value)), is_exact); value must be nonnegative."""
    raise NotImplementedError('implement an exact integer cube root')


def recover(challenge):
    """Return recovered integer when c is an exact cube and reencryption holds.

    Return None when the direct-root attack does not apply. This does not mean
    the ciphertext is secure against every other attack.
    """
    raise NotImplementedError('recover and verify the candidate message')
