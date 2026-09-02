#!/usr/bin/env python3
"""Small, deployment-independent password-KDF timing comparison."""
import argparse, hashlib, statistics, time
import bcrypt
from argon2.low_level import Type, hash_secret_raw


def operations(password: bytes):
    salt = b"0123456789abcdef"
    return {
        "SHA-256 (unsafe)": lambda: hashlib.sha256(password).digest(),
        "PBKDF2-100k": lambda: hashlib.pbkdf2_hmac("sha256", password, salt, 100_000),
        "bcrypt-cost-10": lambda: bcrypt.hashpw(password, bcrypt.gensalt(rounds=10)),
        "scrypt-N=2^14": lambda: hashlib.scrypt(password, salt=salt, n=2**14, r=8, p=1),
        "Argon2id-32MiB": lambda: hash_secret_raw(password, salt, 2, 32768, 1, 32, Type.ID),
    }


def benchmark(password: bytes, trials: int = 3) -> dict[str, float]:
    results = {}
    for name, operation in operations(password).items():
        operation()  # warm-up
        samples = []
        for _ in range(trials):
            start = time.perf_counter(); operation(); samples.append(time.perf_counter() - start)
        results[name] = statistics.median(samples)
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--trials", type=int, default=3)
    args = parser.parse_args()
    for name, seconds in benchmark(b"classroom-benchmark-only", args.trials).items():
        print(f"{name:<20} {seconds * 1000:9.3f} ms")
    print("Results are machine-specific; tune parameters for each deployment.")
