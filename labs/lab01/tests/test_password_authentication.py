import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).parents[1]


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path); module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module); return module


def test_hash_and_salt():
    h = load(ROOT / "part1_hashing/hash_password.py")
    s = load(ROOT / "part1_hashing/salted_hash.py")
    assert len(h.hash_password("fictional")) == 64
    assert s.salted_hash("fictional", b"a" * 16) != s.salted_hash("fictional", b"b" * 16)


def test_register_verifier_success_and_failure():
    auth = load(ROOT / "part3_password_kdfs/register_login_demo.py")
    verifier = auth.derive("fictional", b"0" * 16, 1000)
    assert verifier == auth.derive("fictional", b"0" * 16, 1000)
    assert verifier != auth.derive("incorrect", b"0" * 16, 1000)


def test_shadow_parser():
    parser = load(ROOT / "part4_system_hashes/analyze_shadow_hash.py")
    row = parser.parse_record((ROOT / "data/linux_hashes.txt").read_text())
    assert row["id"] == "6" and row["account"].startswith("student_")


def test_wpa2_fixture_has_one_dictionary_match():
    verifier = load(ROOT / "part5_wpa2/verify_candidate.py")
    row = json.loads((ROOT / "data/wpa2_capture.json").read_text())
    words = (ROOT / "data/lab01-small.txt").read_text().splitlines()
    assert sum(verifier.verify(word, row) for word in words) == 1
