#!/usr/bin/env python3
"""Explain fields from instructor-provided WPA2 metadata."""
import argparse, json
from pathlib import Path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("metadata", type=Path); args = parser.parse_args()
    row = json.loads(args.metadata.read_text())
    for key in ("ssid", "ap_mac", "client_mac", "anonce", "snonce", "mic"):
        print(f"{key}: {row[key]}")
    print("candidate+SSID -> PBKDF2-SHA1 PMK -> PRF(MACs, nonces) PTK -> KCK -> EAPOL MIC -> compare")
    print("PMK is password-derived; PTK is session-specific; KCK authenticates the EAPOL data.")
