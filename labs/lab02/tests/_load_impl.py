"""Load student exercises or private instructor references for grading."""

from __future__ import annotations

import importlib.util
import os
import sys
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]
EXERCISES = {
    "part1": "part1_des_bruteforce/des_bruteforce.py",
    "part2": "part2_double_des_mitm/double_des_mitm.py",
    "part3": "part3_aes_cbc_pkcs7/aes_cbc_pkcs7.py",
    "part4": "part4_cbc_bit_flipping/cbc_bit_flipping.py",
    "part5": "part5_padding_oracle/padding_oracle.py",
    "part6": "part6_mte_vs_etm/mte_vs_etm.py",
    "part7": "part7_aes_cpa/aes_cpa.py",
}


def load(part: str):
    reference = os.environ.get("LAB02_IMPL")
    path = (Path(reference) / f"{part}.py" if reference
            else LAB_ROOT / EXERCISES[part])
    if not path.is_file() or path.stat().st_size == 0:
        raise RuntimeError(f"Implement {path.name} using this Part's README before grading.")
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
