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

You can start Lab02 without completing Lab 01. All labs share the same Docker
environment: you build the course image, start the `course` container, and run
your Python code inside it. **If you completed the Lab 01 setup, you have
already built this common image and used this container.** Reuse that setup
as described below.

Parts 4–6 also need a target container running on your own computer. This is
the same workflow used for the SSH target in Lab 01 Part 2. The Lab02 target
is supplied as a prebuilt image, which you load instead of building from
server source. No instructor-hosted server is needed.

| Service | Purpose |
| --- | --- |
| `course` | Your shell, Python code, and repository files, shared by all labs |
| `lab02-target` | The local application you interact with in Parts 4–6 |

### 1. Prepare the common course image

- **Starting with Lab02:** follow the [prerequisites](../../README.md#0-prerequisites)
  and [repository cloning instructions](../../README.md#1-clone-the-course-repository)
  in the main README, then build the course image with the command below.
- **Already completed the Lab 01 setup:** use the repository and image you
  prepared there. If `docker/Dockerfile` has changed since your last build
  (for example, to add Lab02 dependencies), rebuild with the same command.
  Otherwise, skip the build and continue to step 2.

`docker/Dockerfile` is the build recipe for the shared course image. It
installs Python, cryptographic libraries, and the other tools needed for all
labs, including the Part 7 plotting libraries. `docker/compose.yml` tells
Docker how to build that image and run the `course` container with your
repository mounted at `/workspace`. You do not need to install lab
dependencies manually.

In your **host terminal** (Ubuntu/WSL on Windows), make sure Docker is running
and go to the repository root containing `docker/` and `labs/`. If you are
still inside a course shell, run `exit` first. Build the image when needed:

```console
docker compose -f docker/compose.yml build course
```

This is the same image-build command used in the Lab 01 setup. The initial
build may take several minutes; you do not need to repeat it at every session.

Additional target services have separate build recipes:
`docker/lab01-ssh-target/Dockerfile` for the Lab 01 SSH target and
`docker/lab02-target/Dockerfile` for the Lab02 application. The instructor
builds the Lab02 target from private server files and provides its image.
For Parts 4–6, load that image in step 2; the common course build above
prepares only your working environment.

### 2. Start the services you need

For **Parts 1–3 and 7**, start only the common course container in the **host
terminal** at the repository root, then continue to step 3:

```console
docker compose -f docker/compose.yml up -d course
docker compose -f docker/compose.yml ps
```

These commands use the shared `docker/compose.yml` to start `course` in the
background (`-d`) and check its status. The `ps` output should show `course`
as `Up` (running). The target servers are in separate profiles:
`lab01-ssh` enables `lab01-ssh-target`, and `lab02` enables `lab02-target`.
Neither target starts by default. Start a target only when the relevant
Part's instructions require it.

For **Parts 4–6**, download `lab02-target-image.tar.gz` provided with these lab
materials and place it in the repository root. Load it once in the **host
terminal**:

```console
docker load -i lab02-target-image.tar.gz
```

Use the image supplied with the same version of the Lab02 files; Part 5's
ciphertext must match that image. Load a replacement only when the instructor
provides an updated bundle.

Start the course container and Lab02 target with the commands below. If you
completed Lab 01 Part 2, this is the same Compose workflow you used to start
the SSH target, with the `lab02` profile and `lab02-target` service:

```console
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

The first command waits until the services are ready. `ps` should show
`lab02-target` as `healthy`. Docker Compose creates the internal network
automatically. The target runs on your computer and has no published host
port. The `lab02` profile enables this additional service; the course
container is the same one used for the other labs.

### 3. Enter the common course container

From the **host terminal** at the repository root:

```console
docker compose -f docker/compose.yml exec course bash
```

You are now **inside the container**. Change to the Lab02 directory:

```console
cd /workspace/labs/lab02
```

The repository is mounted at `/workspace`, the shared location used in every
lab. Changes to files there are saved in your host repository. Run Python
commands in this shell for every Part. The clients for Parts 4–6 already know
the local service name `lab02-target`; you do not need to enter an address.

## Working through the Parts

Read each Part README before opening its starter file. Complete the TODOs,
run the supplied command, and record both the recovered flag and your answers
to the analysis questions. Do not look for flags in filenames or source code:
the supplied artifacts are designed so the intended cryptographic work reveals
them.

After completing each Part's TODOs, run its command **inside the course
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

Exiting the shell leaves the course container and target running. Your files
remain in the host repository. If you have finished Parts 4–6, stop only the
Lab02 target from the **host terminal** at the repository root:

```console
docker compose -f docker/compose.yml --profile lab02 stop lab02-target
```

The course container remains available for other Parts and labs. Next time,
repeat the appropriate start command in step 2 and enter the shell as in
step 3. The loaded images remain on your computer.

If you have finished all lab work and no longer need any course containers,
stop and remove them and their networks from the **host terminal**:

```console
docker compose -f docker/compose.yml --profile lab01-ssh --profile lab02 down
```

If a client cannot connect, check `ps` in the host terminal and confirm that
the target is running. If you reach the query limit while debugging Parts
5–6, correct your loop, then reset the counter in the **host terminal**:

```console
docker compose -f docker/compose.yml --profile lab02 restart lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

Wait for `healthy` before trying again. Restarting the same image preserves
the keys, so your supplied Part 5 ciphertext remains usable.

## Tests

Run the lightweight public checks inside the course container at
`/workspace/labs/lab02`:

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
