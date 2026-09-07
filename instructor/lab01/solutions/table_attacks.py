#!/usr/bin/env python3
"""Reference implementation for Part 4 full and rainbow table experiments."""

from __future__ import annotations

import hashlib
import itertools
import random

MIX_CONSTANT = 0x9E3779B1


def hash_password(password: str, algorithm: str = "sha256") -> str:
    return hashlib.new(algorithm, password.encode("ascii")).hexdigest()


def password_space(alphabet: str, length: int):
    for characters in itertools.product(alphabet, repeat=length):
        yield "".join(characters)


def build_precomputation(config: dict[str, int | str]) -> dict[str, str]:
    algorithm = str(config["algorithm"])
    return {
        hash_password(password, algorithm): password
        for password in password_space(str(config["alphabet"]), int(config["password_length"]))
    }


def reduce_digest(digest_hex: str, column: int, alphabet: str, length: int) -> str:
    value = (int(digest_hex, 16) + column * MIX_CONSTANT) % (len(alphabet) ** length)
    characters: list[str] = []
    for _ in range(length):
        value, digit = divmod(value, len(alphabet))
        characters.append(alphabet[digit])
    return "".join(reversed(characters))


def choose_starts(config: dict[str, int | str]) -> list[str]:
    candidates = list(password_space(str(config["alphabet"]), int(config["password_length"])))
    return random.Random(int(config["seed"])).sample(candidates, int(config["chain_count"]))


def chain_endpoint(start: str, config: dict[str, int | str]) -> str:
    password = start
    for column in range(int(config["chain_length"])):
        digest = hash_password(password, str(config["algorithm"]))
        password = reduce_digest(
            digest, column, str(config["alphabet"]), int(config["password_length"])
        )
    return password


def build_rainbow(config: dict[str, int | str]) -> dict[str, list[str]]:
    endpoints: dict[str, list[str]] = {}
    for start in choose_starts(config):
        endpoint = chain_endpoint(start, config)
        endpoints.setdefault(endpoint, []).append(start)
    return endpoints


def lookup_precomputation(digest: str, entries: dict[str, str]) -> tuple[str | None, int]:
    return entries.get(digest.lower()), 0


def lookup_rainbow(
    target_digest: str,
    endpoints: dict[str, list[str]],
    config: dict[str, int | str],
) -> tuple[str | None, int]:
    target_digest = target_digest.lower()
    alphabet = str(config["alphabet"])
    length = int(config["password_length"])
    chain_length = int(config["chain_length"])
    algorithm = str(config["algorithm"])
    computations = 0
    for target_column in range(chain_length - 1, -1, -1):
        digest = target_digest
        endpoint = ""
        for column in range(target_column, chain_length):
            endpoint = reduce_digest(digest, column, alphabet, length)
            if column + 1 < chain_length:
                digest = hash_password(endpoint, algorithm)
                computations += 1
        for start in endpoints.get(endpoint, []):
            password = start
            for column in range(chain_length):
                digest = hash_password(password, algorithm)
                computations += 1
                if digest == target_digest:
                    return password, computations
                password = reduce_digest(digest, column, alphabet, length)
    return None, computations
