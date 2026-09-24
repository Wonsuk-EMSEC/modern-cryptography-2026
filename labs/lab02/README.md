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

You have already used a target container in Lab 01 Part 2. Lab02 follows the
same workflow: you start a target on your own computer, enter the course
container, and run your Python code there. No instructor-hosted server is
needed. The difference is that the Lab02 target is supplied as a prebuilt
image, which you load instead of building from server source.

| Service | Purpose |
| --- | --- |
| `lab02-course` | Your shell, Python code, and files, using the Lab 01 course image |
| `lab02-target` | The local application you interact with in Parts 4–6 |

### 1. Update the course image once for Lab02

Use the repository you already cloned for Lab 01. In your **host terminal**
(Ubuntu/WSL on Windows), go to the repository root containing `docker/` and
`labs/`. If you are still inside a course shell, run `exit` first.

```console
docker compose -f docker/compose.yml build course
```

This updates the existing image with the Lab02 dependencies, including the
Part 7 plotting libraries. You do not need to rebuild at every session.

### 2. Load and start your local target for Parts 4–6

Download `lab02-target-image.tar.gz` provided with these lab materials and
place it in the repository root. Load it once in the **host terminal**:

```console
docker load -i lab02-target-image.tar.gz
```

Use the image supplied with the same version of the Lab02 files; Part 5's
ciphertext must match that image. Load a replacement only when the instructor
provides an updated bundle.

Now start the target, just as you started the SSH target in Lab 01:

```console
docker compose -f docker/compose.lab02.student.yml --profile lab02 up -d --wait lab02-target
docker compose -f docker/compose.lab02.student.yml --profile lab02 ps
```

The first command waits until the service is ready. `ps` should show
`lab02-target` as `healthy`. Docker Compose creates the internal network
automatically. The service runs on your computer and has no published host
port. Parts 1–3 and 7 do not need the target, so you can skip this step for
those Parts.

### 3. Enter the Lab02 course container

From the **host terminal** at the repository root:

```console
docker compose -f docker/compose.lab02.student.yml run --rm lab02-course bash
```

You are now **inside the container**, already at `/workspace/labs/lab02`.
Run Python commands here. This uses the same course image as Lab 01; the
Lab02 Compose file connects your shell to the local target and mounts your
Lab02 files. Changes to these files are saved in your host repository.

Use this shell for every Part. The clients for Parts 4–6 already know the
local service name `lab02-target`; you do not need to enter an address.

## Working through the Parts

Read each Part README before opening its starter file. Complete the TODOs,
run the supplied command, and record both the recovered flag and your answers
to the analysis questions. Do not look for flags in filenames or source code:
the supplied artifacts are designed so the intended cryptographic work reveals
them.

After completing each Part's TODOs, run its command **inside the Lab02
container** at `/workspace/labs/lab02`:

```console
python3 part1_des_bruteforce/starter.py
python3 part2_double_des_mitm/starter.py
python3 part3_aes_cbc_pkcs7/starter.py
python3 part4_cbc_bit_flipping/starter.py
python3 part5_padding_oracle/starter.py
python3 part6_mte_vs_etm/starter.py
python3 part7_aes_cpa/starter.py --all
```

The Part 6 command first probes the two services. Follow that Part's README
to select a service and run recovery. Part 7's README also explains how to
recover one byte first and save plots before recovering the full key.

## Finish or restart a session

Leave the course shell with:

```console
exit
```

The temporary shell container is removed, but your files remain. The target
keeps running until you stop it. In the **host terminal**, from the repository
root, stop the Lab02 target and remove the Lab02 network:

```console
docker compose -f docker/compose.lab02.student.yml --profile lab02 down
```

Next time, repeat the target-start and shell commands in steps 2 and 3. The
loaded images remain on your computer.

If a client cannot connect, check `ps` in the host terminal and confirm that
you entered the shell using the Lab02 Compose file. If you reach the query
limit while debugging Parts 5–6, correct your loop, then reset the counter in
the **host terminal**:

```console
docker compose -f docker/compose.lab02.student.yml --profile lab02 restart lab02-target
docker compose -f docker/compose.lab02.student.yml --profile lab02 ps
```

Wait for `healthy` before trying again. Restarting the same image preserves
the keys, so your supplied Part 5 ciphertext remains usable.

## Tests

Run the lightweight public checks inside the Lab02 container:

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
