# Lab 02: Practical Security of Block Ciphers

**Estimated time:** 4–5 hours. **Environment:** course Docker container.

This is a local CTF-style lab. Each Part is a cryptographic puzzle that ends
when you recover a value in the form `FLAG{...}`. Work only against the data
and local services supplied for this course. Do not use these techniques on
systems, devices, accounts, or services without explicit authorization.

## Learning progression

| Part | Topic | Main lesson |
| --- | --- | --- |
| 1 | DES Brute-Force Attack | Short key spaces are dangerous. |
| 2 | Double-DES Meet-in-the-Middle Attack | Cryptographic composition matters. |
| 3 | AES-CBC and PKCS#7 | Understand the construction before attacking it. |
| 4 | CBC Bit-Flipping Attack | Confidentiality does not imply integrity. |
| 5 | Padding Oracle Attack | Decryption behavior can leak plaintext. |
| 6 | MAC-then-Encrypt vs. Encrypt-then-MAC | Authentication order matters. |
| 7 | CPA against AES | Implementation leakage can expose strong cryptographic keys. |

The Parts use only bounded searches, generated data, an isolated course target
service, and synthetic traces. The final message is:

> Cryptographic security depends not only on the cipher itself, but also on
> key size, composition, mode of operation, authentication, error handling,
> and implementation.

## Setup

### Parts 1–3 and 7

If you completed Lab 01 on this computer, use the same course container in
the same way. From the repository root, start it if needed and enter it:

```console
docker compose -f docker/compose.yml up -d course
docker compose -f docker/compose.yml exec course bash
cd /workspace/labs/lab02
```

You only need to build the image when you have not completed the Lab 01 setup
on this computer, or when the instructor announces an image update:

```console
docker compose -f docker/compose.yml build course
```

### Parts 4–6

These Parts communicate with a service that course staff prepare before the
lab. You do **not** download, start, configure, or inspect that service. When
staff say that Parts 4–6 are ready, run their commands from your normal host
terminal, not from the Lab 01 `course` shell. For example:

```console
docker compose -f docker/compose.lab02.student.yml run --rm lab02-course \
  python3 part4_cbc_bit_flipping/starter.py
```

This starts a temporary course container that can reach the class service, then
removes it when the command finishes. The supplied clients connect to the
correct service automatically. If you see a connection error, contact course
staff; do not change a client address or try another host.

## Working through the Parts

Read each Part README before opening its starter file. Complete the TODOs,
run the supplied command, and record both the recovered flag and your answers
to the analysis questions. Do not look for flags in filenames or source code:
the supplied artifacts are designed so the intended cryptographic work reveals
them.

For Parts 1–3 and 7, run these commands **inside** the Lab 01 `course` shell:

```console
python3 part1_des_bruteforce/starter.py
python3 part2_double_des_mitm/starter.py
python3 part3_aes_cbc_pkcs7/starter.py
python3 part7_aes_cpa/starter.py
```

For Parts 4–6, run these commands **from your normal host terminal** after
course staff announce that the service is ready:

```console
docker compose -f docker/compose.lab02.student.yml run --rm lab02-course \
  python3 part4_cbc_bit_flipping/starter.py
docker compose -f docker/compose.lab02.student.yml run --rm lab02-course \
  python3 part5_padding_oracle/starter.py
docker compose -f docker/compose.lab02.student.yml run --rm lab02-course \
  python3 part6_mte_vs_etm/starter.py
```

Part 7 can save its plots in a directory you choose with `--plots`.

## Tests

Run the lightweight public checks from the Lab02 directory:

```console
make test
```

After completing the TODOs, run the implementation checks with the supplied
reference-free test fixtures:

```console
make grade
```

`make test` remains useful while TODOs are unfinished; implementation checks
are skipped in that mode. `make grade` exercises the completed Part 1–7
functions with obvious test-only values and does not reveal the lab flags. The
report template is in `report/LAB_REPORT_TEMPLATE.md`.
