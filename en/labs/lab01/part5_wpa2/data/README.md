# Part 5 data

[한국어](../../../../../labs/lab01/part5_wpa2/data/README.md) | [English](README.md)

Code and data are shared in the [original directory](../../../../../labs/lab01/part5_wpa2/data/). Run all commands from the original exercise directory in the course container.

All files in this directory are intentionally created, authorized classroom
fixtures.

- `wpa2_capture.json`: synthetic WPA2 calculation metadata. It is not a PCAP
  and is separate from the course capture below.
- `wpa2_passwords.txt`: bounded candidate list for the synthetic calculation
  fixture.
- `wpa2/lab01-handshake.pcap`: instructor-approved 802.11/EAPOL capture for
  manual Wireshark or TShark inspection.
- `wpa2/lab01-pcap-wordlist.txt`: bounded candidate list for that PCAP only.

Do not replace these files with captured or downloaded third-party traffic or
use either wordlist against another network.
