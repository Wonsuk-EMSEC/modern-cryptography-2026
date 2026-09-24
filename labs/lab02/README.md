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
already built this common image and used this container.** Use the same
repository and refresh the environment as described below.

**If you have not built the course image yet**, first complete the
[prerequisites](../../README.md#0-prerequisites) and
[clone the repository](../../README.md#1-clone-the-course-repository).
Make sure Docker is running. In your **host terminal** (Ubuntu/WSL on
Windows), go to the repository root containing `docker/` and `labs/`, then
run:

```console
docker compose -f docker/compose.yml build course
```

This command uses `docker/Dockerfile` to build the shared
`modern-cryptography-2026` image, including the tools and Python libraries
required for the labs. The first build may take several minutes. Once it
finishes successfully, your image is ready: continue to
[step 2](#2-start-the-services-you-need) to start the container. You do not
need to repeat the same build in step 1 below.

Parts 4–6 also need a target container running on your own computer. This is
the same workflow used for the SSH target in Lab 01 Part 2. The Lab02 target
is supplied as a prebuilt image that Docker Compose downloads automatically
from GitHub Container Registry (GHCR). No instructor-hosted server is needed.

| Service | Purpose |
| --- | --- |
| `course` | Your shell, Python code, and repository files, shared by all labs |
| `lab02-target` | The local application you interact with in Parts 4–6 |

### 1. Prepare the common course image

- **Starting with Lab02:** follow the [prerequisites](../../README.md#0-prerequisites)
  and [repository cloning instructions](../../README.md#1-clone-the-course-repository)
  in the main README, then build the course image with the command below.
- **Already completed the Lab 01 setup:** use the repository you prepared
  there. **We recommend repeating the image build below and the service
  start commands in step 2 before beginning Lab02.** `docker/Dockerfile`
  and `docker/compose.yml` may have been updated since Lab 01 to add
  dependencies or change service settings. Use the current course files
  so these commands apply the Lab02 environment updates.

`docker/Dockerfile` is the build recipe for the shared course image. It
installs Python, cryptographic libraries, and the other tools needed for all
labs, including the Part 7 plotting libraries. `docker/compose.yml` tells
Docker how to build that image and run the `course` container with your
repository mounted at `/workspace`. You do not need to install lab
dependencies manually.

In your **host terminal** (Ubuntu/WSL on Windows), make sure Docker is running
and go to the repository root containing `docker/` and `labs/`. If you are
still inside a course shell, run `exit` first. Build the course image:

```console
docker compose -f docker/compose.yml build course
```

This is the same image-build command used in the Lab 01 setup. The initial
build may take several minutes; subsequent builds reuse cached layers where
possible. After preparing the environment for Lab02, you only need to rebuild
when updated environment files are provided.

Additional target services have separate build recipes:
`docker/lab01-ssh-target/Dockerfile` for the Lab 01 SSH target and
`docker/lab02-target/Dockerfile` for the Lab02 application. The instructor
builds the Lab02 target from private server files and provides its image.
For Parts 4–6, start that image in step 2; the common course build above
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
as `Up` (running). Run the `up` command even if `course` is already running:
Compose recreates the container when needed to apply a rebuilt image or
changed service settings.

The `lab02` profile enables the `lab02-target` service. This target does not
start by default. Start it only for Parts 4–6, following the instructions
below.

The goal of Parts 4–6 is to recover flags by applying cryptographic attacks.
Reading the server source code and secret data could reveal the flags
directly, bypassing the intended exercises. Therefore, these files are not
included in the student repository. The instructor builds `lab02-target`
in advance and publishes it on GitHub Container Registry (GHCR). Docker
Compose downloads and runs that image, so students do not build the target
locally.

The image can still be inspected locally. For this lab, recover flags through
the supplied clients instead of reading files inside the image.

The target uses the following GHCR image name:

```text
ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab02-target:2026-lab02-v1
```

`docker/compose.yml` specifies this image without a `build` section. Compose
pulls it automatically when needed; no manual download, `docker load`, or
registry login is needed for the public package. The Lab02 files and target
image are a paired **`2026-lab02-v1`** release: Part 5's ciphertext must match
the target image. Keep them on the same release when updating.

For **Parts 4–6**, start the course container and Lab02 target in the **host
terminal** at the repository root with the commands below. If you
completed Lab 01 Part 2, this is the same Compose workflow you used to start
the SSH target, with the `lab02` profile and `lab02-target` service:

```console
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

The first `up` may take longer while it downloads the target image. The
command then waits until the services are ready. `ps` should show
`lab02-target` as `healthy`. Docker Compose creates the internal network
automatically. The target runs on your computer and has no published host
port. The `lab02` profile enables this additional service; the course
container is the same one used for the other labs.

If the image pull reports `denied` or `manifest unknown`, ask the instructor
to confirm that this release has been published and the GHCR package is
public. You do not need to change the clients or build the target locally.

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
step 3. The built and downloaded images remain on your computer.

If you are finished with the Lab02 session and want to remove its target,
the course container, and their networks, run from the **host terminal**:

```console
docker compose -f docker/compose.yml --profile lab02 down
```

Use the target-only `stop` command above if you want to keep working in other
labs with the course container.

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
