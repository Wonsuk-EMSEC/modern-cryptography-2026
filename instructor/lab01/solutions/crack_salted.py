import csv, hashlib, time
from pathlib import Path


def crack(target_csv: Path, wordlist: Path):
    with target_csv.open(newline="") as stream: targets = list(csv.DictReader(stream))
    found, count = {}, 0; start = time.perf_counter()
    for row in targets:
        salt = bytes.fromhex(row["salt_hex"])
        for word in filter(None, (line.strip() for line in wordlist.read_text().splitlines())):
            digest = hashlib.sha256(salt + word.encode()).hexdigest(); count += 1
            if digest == row["sha256"].lower(): found[row["account"]] = word; break
    return found, count, max(time.perf_counter() - start, 1e-12)
