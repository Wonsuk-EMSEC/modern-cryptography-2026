# Part 4: System password hashes

**Ethical and authorized use:** use only `../data/linux_hashes.txt`. The parser
does not access `/etc/shadow`. Never obtain or test another person's hashes.

Run `python3 analyze_shadow_hash.py ../data/linux_hashes.txt`. A shadow-style
value uses `$identifier$salt-or-parameters$verifier`; the identifier selects the
password-hashing scheme. Classify this exercise as online or offline and
justify your answer.

## Parse the supplied record

```console
cd /workspace/labs/lab01/part4_system_hashes
python3 analyze_shadow_hash.py ../data/linux_hashes.txt
```

Expected output has this structure:

```text
{'account': 'student_...', 'id': '6', 'algorithm': 'SHA-512-crypt',
 'salt_or_parameters': '...', 'verifier': '...'}
```

The `$6$` identifier selects SHA-512-crypt. The salt and verifier are stored
data; neither field is the plaintext password. Notice that the script accepts
an explicit local filename and never opens `/etc/shadow` automatically.

Optional local cracking command:

```console
john --wordlist=../data/lab01-small.txt ../data/linux_hashes.txt
```

To display John the Ripper's result for this supplied file, run:

```console
john --show ../data/linux_hashes.txt
```

Runtime and exact status messages can vary. The important observation is that
all guesses are checked locally, without sending login attempts to a service.

Use only the supplied synthetic file. If an instructor separately provides a
Victim Ubuntu VM, it must be deliberately vulnerable and connected only to an
isolated host-only network. Worksheet (manual observation only): list the VM's
instructor-provided address, visible services, evidence of isolation, and which
service would authenticate users. Do not scan arbitrary addresses.

## Checkpoint questions

1. Does the hash format reveal the plaintext?
2. Which fields must be stored so legitimate verification remains possible?
3. Is this an online or offline activity? What evidence supports your answer?
4. Why must an optional Victim VM use an isolated host-only network?
