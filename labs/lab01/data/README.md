# Lab 01 data

All accounts and passwords are fictional course fixtures.

- `lab01-small.txt`: deliberately tiny instructor-created wordlist.
- `unsalted_hashes.csv`: `account,sha256`.
- `salted_hashes.csv`: `account,salt_hex,sha256`, where the verifier is
  `SHA256(salt || UTF8(password))`.
- `linux_hashes.txt`: synthetic shadow-style record.
- `wpa2_capture.json`: synthetic WPA2 calculation metadata, not a PCAP.
- `wpa2/`: placeholder for an optional instructor-generated capture.

The other files support the earlier collision/rainbow-table enrichment
exercises retained in this lab.
