from labs.lab02.common.des import decrypt_block, encrypt_block, make_des_key


def test_reduced_des_mapping_is_deterministic_and_uses_odd_parity() -> None:
    key = make_des_key(731, 12)
    assert key == make_des_key(731, 12)
    assert all(byte.bit_count() % 2 == 1 for byte in key)
    assert len({make_des_key(value, 8) for value in range(256)}) == 256


def test_des_round_trip() -> None:
    block = b"CRYPTO26"
    key = make_des_key(17, 8)
    assert decrypt_block(encrypt_block(block, key), key) == block
