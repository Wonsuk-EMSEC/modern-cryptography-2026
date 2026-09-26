"""Checks enabled only after students complete the TODO implementations."""

from __future__ import annotations

import base64
import json
import os
import unittest
from pathlib import Path

import numpy as np
from Crypto.Cipher import AES

from labs.lab02.common.des import encrypt_block, make_des_key
from labs.lab02.tests._load_impl import load

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "labs" / "lab02"


def pad16(data: bytes) -> bytes:
    amount = 16 - len(data) % 16
    return data + bytes([amount]) * amount


def valid_padding(data: bytes) -> bool:
    if not data or len(data) % 16:
        return False
    amount = data[-1]
    return 1 <= amount <= 16 and data[-amount:] == bytes([amount]) * amount


@unittest.skipUnless(os.environ.get("LAB02_GRADE"), "complete the Lab02 starters first")
class CompletedStarterTests(unittest.TestCase):
    def test_part1_and_part2(self) -> None:
        part1 = load("part1")
        block, bits, key_id = b"CRYPTO26", 8, 111
        found, _, _ = part1.brute_force(block, encrypt_block(block, make_des_key(key_id, bits)), bits)
        self.assertEqual(found, key_id)

        part2 = load("part2")
        key1, key2 = make_des_key(7, bits), make_des_key(91, bits)
        pairs = [(b"CRYPTO26", part2.double_encrypt(b"CRYPTO26", key1, key2)),
                 (b"BLOCK-02", part2.double_encrypt(b"BLOCK-02", key1, key2))]
        self.assertEqual(part2.recover_keys(pairs, bits), [(7, 91)])

    def test_part3_padding_and_nist_prefix(self) -> None:
        part3 = load("part3")
        vector = json.loads((DATA / "part3_aes_cbc_pkcs7/data/nist_cbc_vector.json").read_text())
        key, iv = bytes.fromhex(vector["key"]), bytes.fromhex(vector["iv"])
        plaintext = bytes.fromhex(vector["plaintext"])
        expected = bytes.fromhex(vector["cbc_ciphertext_without_pkcs7_final_block"])
        encrypted = part3.cbc_encrypt(key, iv, plaintext)
        self.assertEqual(encrypted[:len(expected)], expected)
        self.assertEqual(part3.cbc_decrypt(key, iv, encrypted), plaintext)
        with self.assertRaises(ValueError):
            part3.pkcs7_unpad(b"invalid")

    def test_part4_bit_flip_and_part5_oracle(self) -> None:
        part4 = load("part4")
        key, iv = bytes(range(16)), bytes(range(16, 32))
        original = b"admin=0;userid=1042"
        packet = iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad16(original))
        forged = part4.forge_admin_token(base64.b64encode(packet).decode("ascii"))
        modified = base64.b64decode(forged, validate=True)
        recovered = AES.new(key, AES.MODE_CBC, modified[:16]).decrypt(modified[16:])
        self.assertIn(b"admin=1;", recovered)

        part5 = load("part5")
        plaintext = b"FLAG{test_flag_only}"
        packet = iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad16(plaintext))

        def oracle(candidate: bytes) -> bool:
            if len(candidate) < 32 or len(candidate) % 16:
                return False
            decrypted = AES.new(key, AES.MODE_CBC, candidate[:16]).decrypt(candidate[16:])
            return valid_padding(decrypted)

        self.assertEqual(part5.recover_plaintext(packet, oracle), plaintext)

    def test_part6_removes_encrypted_mac_after_oracle_recovery(self) -> None:
        import hashlib
        import hmac

        part6 = load("part6")
        key, iv, mac_key = bytes([9]) * 16, bytes([10]) * 16, bytes([11]) * 32
        message = b"FLAG{test_flag_only}"
        packet = iv + AES.new(key, AES.MODE_CBC, iv).encrypt(
            pad16(message + hmac.new(mac_key, message, hashlib.sha256).digest())
        )

        def padding_oracle(candidate: bytes) -> bool:
            if len(candidate) < 32 or len(candidate) % 16:
                return False
            decrypted = AES.new(key, AES.MODE_CBC, candidate[:16]).decrypt(candidate[16:])
            return valid_padding(decrypted)

        self.assertEqual(part6.recover_vulnerable_message(packet, padding_oracle), message)

    def test_part6_probe_uses_the_service_query_interface(self) -> None:
        part6 = load("part6")
        packet = bytes(range(48))
        calls: list[bytes] = []

        class Service:
            def query(self, candidate: bytes) -> str:
                calls.append(candidate)
                return "PADDING_OK"

        modified_iv = bytearray(packet)
        modified_iv[0] ^= 1
        modified_ciphertext = bytearray(packet)
        modified_ciphertext[20] ^= 1

        self.assertEqual(part6.probe(Service(), packet), ("PADDING_OK", "PADDING_OK"))
        self.assertEqual(calls, [bytes(modified_iv), bytes(modified_ciphertext)])

    def test_part7_low_noise_byte_and_full_key(self) -> None:
        part7 = load("part7")
        from labs.lab02.part7_aes_cpa.model import generate_traces
        key = bytes(range(16))
        plaintexts = np.random.default_rng(42).integers(0, 256, (180, 16), dtype=np.uint8)
        traces = generate_traces(plaintexts, key, noise_stddev=.45, seed=99)
        self.assertEqual(part7.recover_key_byte(traces, plaintexts, 0), key[0])
        self.assertEqual(part7.recover_full_key(traces, plaintexts), key)


if __name__ == "__main__":
    unittest.main()
