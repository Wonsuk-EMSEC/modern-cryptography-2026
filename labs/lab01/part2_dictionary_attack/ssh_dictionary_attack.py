#!/usr/bin/env python3
"""Student starter for the bounded Lab 01 SSH dictionary exercise."""

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
    """Load the small course wordlist while enforcing the exercise limit."""
    candidates = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(candidates) > MAX_CANDIDATES:
        raise ValueError(f"course SSH wordlist is limited to {MAX_CANDIDATES} candidates")
    return candidates


def try_candidate(candidate: str) -> bool:
    """Try one password against the fixed Compose-only SSH target."""
    # TODO: create an SSHClient, use AutoAddPolicy only for this disposable
    # course container, attempt password-only authentication, return False for
    # AuthenticationException, and always close the client.
    raise NotImplementedError


def dictionary_attack(candidates: list[str], delay: float = 0.25) -> tuple[str | None, int, float]:
    """Try bounded candidates sequentially and return match, attempts, seconds."""
    start = time.perf_counter()
    for attempts, candidate in enumerate(candidates, 1):
        if try_candidate(candidate):
            return candidate, attempts, time.perf_counter() - start
        time.sleep(delay)
    return None, len(candidates), time.perf_counter() - start


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Try the supplied wordlist against the fixed Lab 01 SSH container only."
    )
    parser.add_argument("wordlist", type=Path)
    args = parser.parse_args()
    candidates = load_candidates(args.wordlist)
    print(f"Target: {TARGET_USERNAME}@{TARGET_HOST}:{TARGET_PORT}")
    match, attempts, elapsed = dictionary_attack(candidates)
    print(f"Attempts: {attempts}")
    print(f"Elapsed: {elapsed:.3f} seconds")
    print("Result: candidate found" if match is not None else "Result: no candidate matched")


if __name__ == "__main__":
    main()
