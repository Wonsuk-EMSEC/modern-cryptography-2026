#!/usr/bin/env python3
from __future__ import annotations

import hashlib


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("ascii")).hexdigest()


def reduce_digest(digest_hex: str, column: int, alphabet: str, length: int) -> str:
    value = (int(digest_hex, 16) + column) % (len(alphabet) ** length)
    chars = []
    for _ in range(length):
        value, digit = divmod(value, len(alphabet))
        chars.append(alphabet[digit])
    return "".join(reversed(chars))


def chain_endpoint(start: str, chain_length: int, alphabet: str, length: int) -> str:
    password = start
    for column in range(chain_length):
        password = reduce_digest(hash_password(password), column, alphabet, length)
    return password


def generate_table(starts: list[str], chain_length: int, alphabet: str, length: int) -> dict[str, list[str]]:
    table: dict[str, list[str]] = {}
    for start in starts:
        table.setdefault(chain_endpoint(start, chain_length, alphabet, length), []).append(start)
    return table


def lookup(target_digest: str, table: dict[str, list[str]], chain_length: int, alphabet: str, length: int) -> str | None:
    target_digest = target_digest.lower()
    for target_column in range(chain_length - 1, -1, -1):
        digest = target_digest
        endpoint = ""
        for column in range(target_column, chain_length):
            endpoint = reduce_digest(digest, column, alphabet, length)
            if column + 1 < chain_length:
                digest = hash_password(endpoint)
        for start in table.get(endpoint, []):
            password = start
            for column in range(chain_length):
                digest = hash_password(password)
                if digest == target_digest:
                    return password
                password = reduce_digest(digest, column, alphabet, length)
    return None
