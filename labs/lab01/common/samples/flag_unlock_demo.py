#!/usr/bin/env python3
"""Open an explicitly public demo flag, independent of graded task data."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from labs.lab01.common.flags import unlock_flag


def main() -> None:
    path = Path(__file__).with_name("public_flag_challenge.json")
    try:
        unlock_flag(path, "incorrect-public-proof")
    except ValueError:
        print("Wrong proof rejected: OK")
    else:
        raise AssertionError("the incorrect demo proof was accepted")
    print(unlock_flag(path, "public-demo-proof"))
    print("This public demo flag is not a Part completion flag.")


if __name__ == "__main__":
    main()
