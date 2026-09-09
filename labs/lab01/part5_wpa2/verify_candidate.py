#!/usr/bin/env python3
"""Student starter: verify one candidate against supplied WPA2 metadata."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import hmac
import json
from pathlib import Path


PRF_LABEL = b"Pairwise key expansion"
PMK_ITERATIONS = 4096
PMK_LENGTH = 32
PTK_LENGTH = 64
KCK_LENGTH = 16
MIC_LENGTH = 16
EAPOL_MIC_OFFSET = 81


def derive_pmk(candidate: str, ssid: str) -> bytes:
    """Return the WPA2-Personal PMK for a candidate passphrase and SSID."""
    # TODO 1: Encode the two strings and apply PBKDF2-HMAC-SHA1 with the
    # constants above. The SSID is the salt.
    raise NotImplementedError


def build_context(record: dict[str, str]) -> bytes:
    """Return ordered MAC addresses followed by ordered nonces."""
    # TODO 2: Decode the hexadecimal AP/client MAC addresses and ANonce/SNonce.
    # Sort the two MAC byte strings and the two nonce byte strings independently,
    # then concatenate the four values. See the README derivation formula.
    raise NotImplementedError


def derive_ptk(pmk: bytes, context: bytes) -> bytes:
    """Expand a PMK into the 64-byte PTK used by this teaching record."""
    # TODO 3: Repeatedly compute HMAC-SHA1 over
    # PRF_LABEL || 0x00 || context || one-byte counter, starting at counter 0.
    # Concatenate digests until PTK_LENGTH bytes are available, then truncate.
    raise NotImplementedError


def derive_kck(ptk: bytes) -> bytes:
    """Extract the Key Confirmation Key from a PTK."""
    # TODO 4: The KCK is the first KCK_LENGTH bytes of the PTK.
    raise NotImplementedError


def normalized_eapol(record: dict[str, str]) -> bytes:
    """Return EAPOL bytes with the captured MIC field cleared."""
    # TODO 5: Decode record["eapol"] from hexadecimal, validate that it contains
    # the complete 16-byte MIC field, and replace bytes 81:97 with zero bytes.
    # Work on a bytearray and return immutable bytes.
    raise NotImplementedError


def compute_mic(kck: bytes, eapol: bytes) -> bytes:
    """Return the 16-byte WPA2 MIC for normalized EAPOL bytes."""
    # TODO 6: Compute HMAC-SHA1 with the KCK and truncate it to MIC_LENGTH.
    raise NotImplementedError


def verify(candidate: str, record: dict[str, str]) -> bool:
    """Return whether one candidate reproduces the captured MIC."""
    # TODO 7: Connect the complete PMK -> PTK -> KCK -> MIC pipeline. Decode
    # record["mic"] from hexadecimal and use hmac.compare_digest so comparison
    # time does not depend on the first differing byte.
    raise NotImplementedError


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("metadata", type=Path, help="instructor-provided local JSON")
    args = parser.parse_args()
    record = json.loads(args.metadata.read_text(encoding="utf-8"))
    candidate = getpass.getpass("Candidate: ")
    print("match" if verify(candidate, record) else "no match")


if __name__ == "__main__":
    main()
