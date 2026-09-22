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

Build the course image from the repository root:

```console
docker compose -f docker/compose.yml build course
```

Parts 1–3 and 7 run only in the course container:

```console
docker compose -f docker/compose.lab02.student.yml run --rm lab02-course bash
cd /workspace/labs/lab02
```

Parts 4–6 use the course-operated target service named `lab02-target`. Course
staff start it from an instructor-only checkout on the course Docker host and
attach it to the internal Lab02 course network before the lab begins. The
target image, server code, and secret data are deliberately absent from the
student release.
Open the course shell as usual:

```console
docker compose -f docker/compose.lab02.student.yml run --rm lab02-course bash
cd /workspace/labs/lab02
```

The supplied clients always use the fixed course service name; they do not
accept a host argument. If a connection fails, contact course staff rather
than changing the client or probing another service.

## Working through the Parts

Read each Part README before opening its starter file. Complete the TODOs,
run the supplied command, and record both the recovered flag and your answers
to the analysis questions. Do not look for flags in filenames or source code:
the supplied artifacts are designed so the intended cryptographic work reveals
them.

```console
python3 part1_des_bruteforce/starter.py
python3 part2_double_des_mitm/starter.py
python3 part3_aes_cbc_pkcs7/starter.py
python3 part4_cbc_bit_flipping/starter.py
python3 part5_padding_oracle/starter.py
python3 part6_mte_vs_etm/starter.py
python3 part7_aes_cpa/starter.py
```

The Part 4–6 commands require the course-operated target to be available. Part
7 also produces plots in a directory you choose with its `--plots` option.

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
