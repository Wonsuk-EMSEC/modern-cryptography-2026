import pytest

from labs.lab02.common.des import MAX_KEY_BITS, decrypt_block, encrypt_block, make_des_key


def test_reduced_des_mapping_is_deterministic_and_uses_odd_parity() -> None:
    key = make_des_key(731, 12)
    assert key == make_des_key(731, 12)
    assert all(byte.bit_count() % 2 == 1 for byte in key)
    assert len({make_des_key(value, 8) for value in range(256)}) == 256


def test_des_round_trip() -> None:
    block = b"CRYPTO26"
    key = make_des_key(17, 8)
    assert decrypt_block(encrypt_block(block, key), key) == block


def test_expanded_des_space_preserves_distinct_effective_keys() -> None:
    # Exercise each newly available high bit; parity-only differences do not
    # create distinct effective DES keys.
    identifiers = [17, *(17 | (1 << bit) for bit in range(20, 24)), (1 << 24) - 1]
    keys = [make_des_key(identifier, 24) for identifier in identifiers]
    effective_keys = {bytes(byte & 0xFE for byte in key) for key in keys}
    assert len(effective_keys) == len(identifiers)
    assert all(byte.bit_count() % 2 == 1 for key in keys for byte in key)
    assert keys[0] == make_des_key(17, 8)
    block = b"CRYPTO26"
    assert all(decrypt_block(encrypt_block(block, key), key) == block for key in keys)


@pytest.mark.parametrize("key_id,key_bits", [
    (0, 0),
    (0, MAX_KEY_BITS + 1),
    (-1, MAX_KEY_BITS),
    (1 << MAX_KEY_BITS, MAX_KEY_BITS),
])
def test_reduced_des_mapping_rejects_out_of_range_values(key_id: int, key_bits: int) -> None:
    with pytest.raises(ValueError):
        make_des_key(key_id, key_bits)
