"""Baseline sample checks and opt-in checks of student hashing functions."""
import importlib.util
import os
from pathlib import Path

import pytest


def load_implementation(name):
    base = Path(os.environ.get("LAB01_PART1_IMPL", Path(__file__).resolve().parent))
    spec = importlib.util.spec_from_file_location(f"lab01_part1_{name}", base / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_public_samples_are_provided():
    samples = Path(__file__).resolve().parent / "samples"
    assert (samples / "hash_bytes_demo.py").is_file()
    assert (samples / "salt_bytes_demo.py").is_file()


@pytest.mark.skipif(not os.environ.get("LAB01_GRADE"), reason="implement hash_password() first")
def test_hash_is_deterministic():
    hash_password = load_implementation("hash_password").hash_password
    assert hash_password("fictional") == hash_password("fictional")


@pytest.mark.skipif(not os.environ.get("LAB01_GRADE"), reason="implement salted_hash() first")
def test_salts_change_digest():
    salted_hash = load_implementation("salted_hash").salted_hash
    assert salted_hash("fictional", b"a" * 16) != salted_hash("fictional", b"b" * 16)
