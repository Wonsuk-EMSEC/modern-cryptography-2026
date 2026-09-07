# Lab 01: Password-based Authentication

**Estimated time:** 2–3 hours. **Environment:** course Docker container.

## Ethical and authorized use

Use only synthetic credentials, hashes, metadata, and optional artifacts
provided specifically for this course. Do not use leaked passwords, access
`/etc/shadow`, scan arbitrary systems, capture third-party Wi-Fi traffic,
deauthenticate clients, or attack public services. Every exercise targets a
local file or instructor-controlled isolated system.

## Learning progression

Hash → Salt → Controlled Online Guessing → Offline Hash Guessing → Slow
Password Hashing → System Verifiers → Precomputation/Rainbow Tables → WPA2
Offline Cracking

After the lab you should be able to distinguish hashing from encryption,
explain salt and offline guessing, compare major password KDFs, interpret a
synthetic Linux password record, evaluate a time-memory tradeoff, and explain
offline WPA2 candidate checking.

## Setup and tests

```console
docker compose -f docker/compose.yml build
docker compose -f docker/compose.yml run --rm course bash
cd /workspace/labs/lab01
pytest -q
```

Attack starters contain TODOs; their tests guide your implementation. Other
demonstrations are runnable immediately.

## Numbered workflow

1. **Hash and salt (20 minutes).** Read
   `part1_hashing/PART1_HASHING_GUIDE.pdf`; run both
   scripts. Expected: a stable digest, then changing salt/digest pairs.
   Checkpoint: distinguish hashing from encryption and explain unique salts.
2. **Controlled online dictionary attack (25 minutes).** Read
   `part2_dictionary_attack/PART2_DICTIONARY_ATTACK_GUIDE.pdf`. If assigned,
   start the isolated Compose SSH target, complete the bounded client, observe
   the local logs, and remove the target. Expected: redacted status, attempt
   count, and server-visible failures. Checkpoint: why can the SSH service
   observe and rate-limit these guesses?
3. **Offline cracking and password KDFs (40 minutes).** Read
   `part3_password_kdfs/PART3_PASSWORD_KDFS_GUIDE.pdf`, implement the unsalted
   and salted cracking starters, run `compare_cost.py`, then benchmark the KDFs
   and use the local register/verify demo. Expected: hash-count comparison,
   median KDF timings, and authentication without stored plaintext. Checkpoint:
   explain salt reuse prevention and compare SHA-256, PBKDF2, bcrypt, scrypt,
   and Argon2id.
4. **System hashes and table attacks (35 minutes).** Read
   `part4_system_hashes/PART4_SYSTEM_HASHES_GUIDE.pdf`, parse the supplied
   shadow-style file, then implement full precomputation and rainbow tables for
   the bounded toy password database. Expected: parsed verifier fields and a
   comparison of build work, storage, lookup work, and coverage. Checkpoint:
   explain the time-memory tradeoff and why salts prevent shared table reuse.
5. **WPA2 verification (25 minutes).** Read
   `part5_wpa2/PART5_WPA2_GUIDE.pdf`, inspect the supplied course PCAP and
   synthetic metadata, then run the local dictionary check. Expected: a complete
   M1–M4 sequence and one matching candidate from the course-only wordlist.
   Checkpoint: explain PMK → PTK → KCK → MIC and offline rate limiting.
6. **Report (15 minutes).** Complete `report/LAB_REPORT_TEMPLATE.md` without
   including any real password.

No real credential is included. The supplied PCAP is restricted to this
authorized offline exercise. The instructor may optionally provide a deliberately
vulnerable Ubuntu VM on an isolated host-only network; it is not required for
the core lab. Complete reference attacks remain under `/workspace/instructor/lab01`.

The part PDFs are the student handouts. Their `README.md` files are retained as
editable source documents so course staff can regenerate the PDFs consistently.
