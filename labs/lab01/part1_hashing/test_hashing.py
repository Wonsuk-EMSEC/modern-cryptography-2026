from hash_password import hash_password
from salted_hash import salted_hash


def test_hash_is_deterministic():
    assert hash_password("fictional") == hash_password("fictional")


def test_salts_change_digest():
    assert salted_hash("fictional", b"a" * 16) != salted_hash("fictional", b"b" * 16)
