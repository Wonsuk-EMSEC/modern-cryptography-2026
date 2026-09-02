#!/usr/bin/env python3
"""Deterministically generate Lab 01 datasets. Instructor-only."""

from __future__ import annotations

import hashlib
import hmac
import itertools
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "labs" / "lab01" / "data"

COLLISION_A = """
d131dd02c5e6eec4693d9a0698aff95c2fcab58712467eab4004583eb8fb7f89
55ad340609f4b30283e488832571415a085125e8f7cdc99fd91dbdf280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e2b487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080a80d1ec69821bcb6a8839396f9652b6ff72a70
"""
COLLISION_B = """
d131dd02c5e6eec4693d9a0698aff95c2fcab50712467eab4004583eb8fb7f89
55ad340609f4b30283e4888325f1415a085125e8f7cdc99fd91dbd7280373c5b
d8823e3156348f5bae6dacd436c919c6dd53e23487da03fd02396306d248cda0
e99f33420f577ee8ce54b67080280d1ec69821bcb6a8839396f965ab6ff72a70
"""


def prf512(key: bytes, label: bytes, context: bytes) -> bytes:
    output = b""
    counter = 0
    while len(output) < 64:
        output += hmac.new(
            key, label + b"\x00" + context + bytes([counter]), hashlib.sha1
        ).digest()
        counter += 1
    return output[:64]


def write_text(name: str, value: str) -> None:
    (DATA / name).write_text(value, encoding="utf-8")


def main() -> None:
    DATA.mkdir(parents=True, exist_ok=True)

    targets = ["spring2026", "lab-access-01", "blueberry", "moderncrypto"]
    write_text(
        "sha256_targets.txt",
        "\n".join(hashlib.sha256(word.encode()).hexdigest() for word in targets) + "\n",
    )

    alphabet, length = "abcd", 3
    space = ["".join(chars) for chars in itertools.product(alphabet, repeat=length)]
    config = {"alphabet": alphabet, "length": length, "chain_length": 6, "starts": space[::3]}
    write_text("rainbow_config.json", json.dumps(config, indent=2) + "\n")
    rainbow_passwords = ["abc", "bda", "cbd", "ddd"]
    write_text(
        "rainbow_targets.txt",
        "\n".join(hashlib.sha256(word.encode()).hexdigest() for word in rainbow_passwords) + "\n",
    )
    salted = [
        {
            "salt": salt.hex(),
            "digest": hashlib.sha256(salt + password.encode("ascii")).hexdigest(),
        }
        for salt, password in zip((b"acct-01", b"acct-02", b"acct-03"), rainbow_passwords)
    ]
    write_text("salted_targets.json", json.dumps(salted, indent=2) + "\n")

    for name, block in (("md5_collision_a.bin", COLLISION_A), ("md5_collision_b.bin", COLLISION_B)):
        (DATA / name).write_bytes(bytes.fromhex("".join(block.split())))

    record = {
        "format": "synthetic-wpa2-teaching-record-v1",
        "ssid": "MCA-Lab-01",
        "ap_mac": "020000000001",
        "client_mac": "0200000000a1",
        "anonce": bytes(range(32)).hex(),
        "snonce": bytes(range(63, 31, -1)).hex(),
        "eapol": bytes.fromhex("0203005f02010a00100000000000000001")
        .ljust(99, b"\x00")
        .hex(),
    }
    macs = sorted(bytes.fromhex(record[key]) for key in ("ap_mac", "client_mac"))
    nonces = sorted(bytes.fromhex(record[key]) for key in ("anonce", "snonce"))
    context = b"".join(macs + nonces)
    pmk = hashlib.pbkdf2_hmac("sha1", b"offline-only", record["ssid"].encode(), 4096, 32)
    kck = prf512(pmk, b"Pairwise key expansion", context)[:16]
    record["mic"] = hmac.new(kck, bytes.fromhex(record["eapol"]), hashlib.sha1).digest()[:16].hex()
    write_text("wpa2_capture.json", json.dumps(record, indent=2) + "\n")

if __name__ == "__main__":
    main()
