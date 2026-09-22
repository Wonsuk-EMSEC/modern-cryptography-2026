#!/usr/bin/env python3
"""Client for the fixed local Part 4 token service."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(LAB_ROOT))

from common.service_client import TargetConnection


def issue() -> str:
    with TargetConnection() as target:
        response = target.request("P4 ISSUE")
    if not response.startswith("TOKEN "):
        raise RuntimeError(response)
    return response.removeprefix("TOKEN ")


def verify(token: str) -> str:
    with TargetConnection() as target:
        return target.request(f"P4 VERIFY {token}")


def main() -> None:
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("issue")
    verify_parser = sub.add_parser("verify")
    verify_parser.add_argument("token")
    args = parser.parse_args()
    print(issue() if args.command == "issue" else verify(args.token))


if __name__ == "__main__":
    main()
