import csv, hashlib, time
from pathlib import Path


def crack(target_csv: Path, wordlist: Path):
    with target_csv.open(newline="") as stream:
        targets = {row["sha256"].lower(): row["account"] for row in csv.DictReader(stream)}
    found, count = {}, 0; start = time.perf_counter()
    for word in filter(None, (line.strip() for line in wordlist.read_text().splitlines())):
        digest = hashlib.sha256(word.encode()).hexdigest(); count += 1
        if digest in targets: found[targets[digest]] = word
    return found, count, max(time.perf_counter() - start, 1e-12)
