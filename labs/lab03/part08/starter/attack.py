#!/usr/bin/env python3
"""Recover the key from one CRT fault and prove it on a fresh representative."""

from __future__ import annotations


def recover_private_exponent(n: int, e: int, mu: int, faulty_signature: int) -> int:
    raise NotImplementedError("TODO: recover a factor, the second factor, and the private exponent")


def forge_signature(mu2: int, d: int, n: int) -> int:
    raise NotImplementedError("TODO: sign the fresh representative with the recovered key")


def attack(client, challenge: dict) -> None:
    session = challenge["session"]
    n, e = (int(challenge["public_key"][name]) for name in ("n", "e"))
    faulty = client.request("POST", "/part08/sign", {"session": session})
    d = recover_private_exponent(n, e, int(challenge["mu"]), int(faulty["faulty_signature"]))
    signature = forge_signature(int(faulty["mu2"]), d, n)
    # TODO: submit the fresh signature, test secure-sign with fault=true and
    # fault=false, and verify the normal signature using the public key.
    raise NotImplementedError("TODO: complete fresh proof and both countermeasure checks")


if __name__ == "__main__":
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
    from labs.lab03.part08.tests.check import main
    main(default_solution=Path(__file__))
