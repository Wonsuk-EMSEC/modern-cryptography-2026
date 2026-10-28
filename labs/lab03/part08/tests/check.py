#!/usr/bin/env python3
"""Verify completion against the server's independently created session."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from labs.lab03.common.service_client import TargetClient


def check(solution: Path, url: str | None = None) -> dict:
    client = TargetClient(url)
    challenge = client.request("GET", "/part08/challenge")
    # Parent-owned session/result prevent submitted output or early exit from
    # impersonating server verification. Submitted code runs only locally.
    worker = """import importlib.util, json, sys
sys.path.insert(0, sys.argv[1])
from labs.lab03.common.service_client import TargetClient
try:
    spec = importlib.util.spec_from_file_location('lab03_submission', sys.argv[2])
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    module.attack(TargetClient(sys.argv[3]), json.loads(sys.argv[4]))
except SystemExit as error:
    raise RuntimeError('submission exited before completing the challenge') from error
"""
    try:
        process = subprocess.run([sys.executable, "-c", worker,
                                  str(Path(__file__).resolve().parents[4]),
                                  str(solution.resolve()), client.url, json.dumps(challenge)],
                                 capture_output=True, text=True, timeout=60)
    except subprocess.TimeoutExpired as error:
        raise RuntimeError("client exceeded the 60 second budget") from error
    if process.returncode:
        raise RuntimeError("client failed: " + process.stderr[-600:])
    result = client.request("GET", "/part08/result?session=" + challenge["session"])
    if not result.get("complete") or "flag" not in result:
        raise RuntimeError("target has not verified every Part08 objective")
    return result


def main(default_solution: Path | None = None) -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--solution", type=Path, default=default_solution or Path(__file__).parents[1] / "starter/attack.py")
    parser.add_argument("--url")
    args = parser.parse_args()
    try:
        result = check(args.solution, args.url)
    except (RuntimeError, ValueError, AttributeError, OSError) as error:
        parser.exit(1, f"Part08 incomplete: {error}\n")
    print("Part08 complete: target verified all objectives")
    print(result["flag"])


if __name__ == "__main__":
    main()
