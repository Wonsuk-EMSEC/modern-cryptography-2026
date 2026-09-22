"""Load completed Lab02 starters or instructor references for grading checks."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
STARTERS = {
    "part1": "part1_des_bruteforce/starter.py",
    "part2": "part2_double_des_mitm/starter.py",
    "part3": "part3_aes_cbc_pkcs7/starter.py",
    "part4": "part4_cbc_bit_flipping/starter.py",
    "part5": "part5_padding_oracle/starter.py",
    "part6": "part6_mte_vs_etm/starter.py",
    "part7": "part7_aes_cpa/starter.py",
}


def load(part: str):
    reference = os.environ.get("LAB02_IMPL")
    path = (Path(reference) / f"{part}.py" if reference
            else LAB_ROOT / STARTERS[part])
    # Part 4 and Part 6 both have a direct-execution helper named ``client``.
    # Remove an earlier helper import so a completed-starter test cannot reuse
    # the wrong Part's module from sys.modules.
    for helper in ("client", "oracle_client"):
        sys.modules.pop(helper, None)
    sys.path.insert(0, str(path.parent))
    sys.path.insert(0, str(LAB_ROOT))
    try:
        spec = importlib.util.spec_from_file_location(f"lab02_{part}", path)
        if spec is None or spec.loader is None:
            raise ImportError(path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)
        sys.path.pop(0)
        for helper in ("client", "oracle_client"):
            sys.modules.pop(helper, None)
