#!/usr/bin/env python3
"""Complete the attack and OAEP comparison; imports must not contact the target."""

from __future__ import annotations


def modify_ciphertext(ciphertext: int, multiplier: int, n: int, e: int) -> int:
    """Return a modified RSA ciphertext satisfying the requested multiplier."""
    raise NotImplementedError("TODO: implement textbook RSA ciphertext modification")


def encrypt_oaep(amount: str, n: int, e: int) -> int:
    """Encrypt ASCII amount with RSA-OAEP/SHA256/MGF1-SHA256/empty label."""
    raise NotImplementedError("TODO: construct the public key and encrypt using OAEP")


def attack(client, challenge: dict) -> None:
    n, e = (int(challenge["public_key"][name]) for name in ("n", "e"))
    session = challenge["session"]
    multiplier = int(challenge["multiplier"])
    ciphertext = modify_ciphertext(int(challenge["ciphertext"]), multiplier, n, e)
    normal = encrypt_oaep(challenge["oaep_amount"], n, e)
    # TODO: submit the textbook attack, then the valid OAEP ciphertext, then its
    # modification. Check all application responses. Use the endpoint schemas
    # in README.md. Do not return a locally invented flag.
    raise NotImplementedError("TODO: complete the three server interactions")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
    from labs.lab03.part06.tests.check import main
    main(default_solution=Path(__file__))
