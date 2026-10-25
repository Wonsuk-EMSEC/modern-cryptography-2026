#!/usr/bin/env python3
"""Run the shared public completion-flag example for this Part."""
import sys
from pathlib import Path

# Make the repository package importable when running this samples/ file.
sys.path.insert(0, str(Path(__file__).resolve().parents[4]))
from labs.lab01.common.samples.flag_unlock_demo import main


if __name__ == "__main__":
    main()
