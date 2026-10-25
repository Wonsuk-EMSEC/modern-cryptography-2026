[한국어](../../../../../labs/lab01/part3_password_kdfs/data/README.md) | **English**

# Part 3 data

All accounts and passwords in this directory are fictional course fixtures.

- `lab01-small.txt`: deliberately tiny wordlist used by the current Part 3
  exercises.
- `unsalted_hashes.csv`: `account,sha256` targets.
- `salted_hashes.csv`: `account,salt_hex,sha256` targets, where the verifier is
  `SHA256(salt || UTF8(password))`.
- `passwords.txt` and `sha256_targets.txt`: optional additional public
  fixtures for comparing candidate lists and unsalted SHA-256 digests.
