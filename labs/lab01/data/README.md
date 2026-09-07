# Lab 01 data

All accounts and passwords are fictional course fixtures.

- `lab01-small.txt`: deliberately tiny instructor-created wordlist.
- `ssh-lab-wordlist.txt`: bounded candidates for the Compose-only SSH target.
- `unsalted_hashes.csv`: `account,sha256`.
- `salted_hashes.csv`: `account,salt_hex,sha256`, where the verifier is
  `SHA256(salt || UTF8(password))`.
- `linux_hashes.txt`: synthetic shadow-style record.
- `rainbow_lab_config.json`: bounded password-space and chain parameters.
- `rainbow_password_database.csv`: fictional accounts with unsalted SHA-256
  targets for the Part 4 table comparison.
- `wpa2_capture.json`: synthetic WPA2 calculation metadata, not a PCAP.
- `wpa2/lab01-handshake.pcap`: instructor-approved 802.11/EAPOL course capture.
- `wpa2/lab01-pcap-wordlist.txt`: tiny candidate list for that capture only.

`rainbow_config.json`, `rainbow_targets.txt`, and `salted_targets.json` support
the earlier compact starter exercise retained in this lab. Part 4 uses the
separately named `rainbow_lab_config.json` and password database above.
