"""Load a lab module from LAB01_IMPL (defaults to the student starter)."""

from __future__ import annotations

import importlib.util
import os
from pathlib import Path

LAB_ROOT = Path(__file__).resolve().parents[1]


def load(name: str):
    base = Path(os.environ.get("LAB01_IMPL", LAB_ROOT / "starter"))
    path = base / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"lab01_{name}", path)
    if spec is None or spec.loader is None:
        raise ImportError(path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
