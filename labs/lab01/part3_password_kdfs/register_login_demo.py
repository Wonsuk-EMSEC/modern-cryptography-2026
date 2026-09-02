#!/usr/bin/env python3
"""Register and verify local fictional users with PBKDF2-HMAC-SHA-256."""
import argparse, getpass, hashlib, hmac, json, secrets
from pathlib import Path


def derive(password: str, salt: bytes, iterations: int) -> bytes:
    return hashlib.pbkdf2_hmac("sha256", password.encode(), salt, iterations)


def load_db(path: Path) -> dict:
    return json.loads(path.read_text()) if path.exists() else {}


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("register", "verify")); parser.add_argument("username")
    parser.add_argument("--db", type=Path, default=Path("auth_db.json")); args = parser.parse_args()
    db = load_db(args.db); password = getpass.getpass("Password: ")
    if args.command == "register":
        salt, iterations = secrets.token_bytes(16), 200_000
        db[args.username] = {"algorithm": "pbkdf2-sha256", "iterations": iterations,
                             "salt": salt.hex(), "verifier": derive(password, salt, iterations).hex()}
        args.db.write_text(json.dumps(db, indent=2) + "\n"); print("registered")
    else:
        row = db.get(args.username)
        valid = bool(row) and hmac.compare_digest(
            derive(password, bytes.fromhex(row["salt"]), row["iterations"]).hex(), row["verifier"])
        print("verified" if valid else "authentication failed")


if __name__ == "__main__": main()
