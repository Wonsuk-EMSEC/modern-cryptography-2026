"""Open completion flags after an experiment has produced its proof.

This module does not recover passwords or implement any lab attack. Envelopes
are local AES-GCM ciphertexts; an incorrect proof fails authentication.
"""

from __future__ import annotations

import hashlib
import json
from collections.abc import Mapping
from pathlib import Path

from Crypto.Cipher import AES

DOMAIN = b"modern-cryptography-2026/lab01/completion-flag/v1\x00"


def canonical_account_proof(accounts: Mapping[str, str]) -> str:
    """Encode recovered accounts as compact UTF-8-compatible, sorted JSON text."""
    if not accounts or not all(isinstance(k, str) and isinstance(v, str) for k, v in accounts.items()):
        raise ValueError("proof requires a nonempty account-to-password mapping")
    return json.dumps(dict(accounts), sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _derive_key(part: str, proof: str) -> bytes:
    if not isinstance(proof, str) or not proof:
        raise ValueError("proof must be nonempty text")
    return hashlib.sha256(DOMAIN + part.encode("utf-8") + b"\x00" + proof.encode("utf-8")).digest()


def _authenticated_header(envelope: dict) -> bytes:
    header = {key: envelope[key] for key in ("version", "algorithm", "part", "challenge")}
    return json.dumps(header, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def unlock_flag(path: str | Path, proof: str) -> str:
    """Return the UTF-8 FLAG string, or raise ValueError for an invalid proof/envelope.

    The Part identifier and public challenge metadata are authenticated together
    with the ciphertext, so modifying them does not produce a valid completion.
    """
    try:
        envelope = json.loads(Path(path).read_text(encoding="utf-8"))
        if not isinstance(envelope, dict):
            raise ValueError("invalid flag envelope")
        if type(envelope.get("version")) is not int or envelope["version"] != 1:
            raise ValueError("unsupported flag version")
        if envelope.get("algorithm") != "AES-256-GCM":
            raise ValueError("unsupported flag algorithm")
        if not isinstance(envelope.get("part"), str) or not envelope["part"]:
            raise ValueError("invalid Part identifier")
        if not isinstance(envelope.get("challenge"), dict):
            raise ValueError("invalid challenge metadata")
        nonce = bytes.fromhex(envelope["nonce_hex"])
        ciphertext = bytes.fromhex(envelope["ciphertext_hex"])
        tag = bytes.fromhex(envelope["tag_hex"])
        if len(nonce) != 12 or len(tag) != 16 or not ciphertext:
            raise ValueError("invalid flag field lengths")
        cipher = AES.new(_derive_key(envelope["part"], proof), AES.MODE_GCM, nonce=nonce)
        cipher.update(_authenticated_header(envelope))
        flag = cipher.decrypt_and_verify(ciphertext, tag).decode("utf-8")
        if not flag.startswith("FLAG" + "{") or not flag.endswith("}"):
            raise ValueError("invalid completion message")
        return flag
    except (KeyError, TypeError, ValueError, UnicodeError) as error:
        raise ValueError("flag could not be opened: check the proof and envelope") from error
