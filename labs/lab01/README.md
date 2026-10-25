# Lab 01: Password-based Authentication

**Estimated time:** 2–3 hours. **Environment:** course Docker container.

## Ethical and authorized use

Use only synthetic credentials, hashes, metadata, and optional artifacts
provided specifically for this course. Do not use leaked passwords, access
`/etc/shadow`, scan arbitrary systems, capture third-party Wi-Fi traffic,
deauthenticate clients, or attack public services. Every exercise targets a
local file or instructor-controlled isolated system.

## Learning progression

Hash → Salt → Controlled Online Guessing → Offline Hash Guessing → Slow
Password Hashing → System Verifiers → Precomputation/Rainbow Tables → WPA2
Offline Cracking

After the lab you should be able to distinguish hashing from encryption,
explain salt and offline guessing, compare major password KDFs, interpret a
synthetic Linux password record, evaluate a time-memory tradeoff, and explain
offline WPA2 candidate checking.

## Setup and tests

For VS Code, follow the common [course-container setup](../../README.md#use-vs-code-with-the-course-container):
open the **repository root** and run **Dev Containers: Reopen in Container**.
Use that window for all Parts and labs. Its Python run/debug commands and
integrated terminal use the course environment, with
`/opt/course-venv/bin/python3` as the default interpreter. The common guide
also explains how to correct a previously saved interpreter selection once.

For a terminal-only session, run the commands below from the repository root
in a **host terminal** to build the common image if needed, start the shared
course container in the background, and check its status:

```console
docker compose -f docker/compose.yml build course
docker compose -f docker/compose.yml up -d course
docker compose -f docker/compose.yml ps
```

The `-d` option runs `course` in the background. `ps` should show it as `Up`
(running). Both labs use this same `docker/compose.yml` and course container.
The target servers have separate profiles and **do not start by default**:

| Target service | Profile | Used in |
| --- | --- | --- |
| `lab01-ssh-target` | `lab01-ssh` | Lab01 Part 2 |
| `lab02-target` | `lab02` | Lab02 Parts 4–6 |

Start a target only when its Part requires it, following that Part's README.
For Lab01 Part 2, follow the [SSH target setup](part2_dictionary_attack/README.md#step-1-build-and-start-the-isolated-target).

If using VS Code in the container, open its integrated terminal. For a
terminal-only session, open the running course container from the **host
terminal**:

```console
docker compose -f docker/compose.yml exec course bash
```

This command opens a container shell; it does not connect a host VS Code
window to the container.

Then run the lab tests **inside the container**:

```console
cd /workspace/labs/lab01
pytest -q
```

Each numbered Part has independent runnable examples in `samples/` and empty
exercise files. Follow the Part README from top to bottom: observe a Sample,
write one function, run its immediate small-example check, and repeat. Write
the program entry point and connect the supplied files after checking the
functions. The final section explains the required output and report evidence.
Basic fixture checks run while exercise files are empty; enable implementation
checks only after completing the corresponding functions. See [Tests](#tests)
for the test files, their roles, and commands for a completed Part.

Each Part ends by opening its own encrypted completion flag using the result of
that Part's exercise. Follow the Part README for the exact proof format and
print the resulting `FLAG{...}` line. The shared helper is documented in
[`common/README.md`](common/README.md); its public Sample works before any
student implementation is complete.

Each numbered part keeps its own fixtures in that part's `data/` directory, so
commands can be run from the part directory without consulting a shared data
folder.

## Numbered workflow

1. **Hash and salt (20 minutes).** Read
   [Part 1 README](part1_hashing/README.md); run the Samples, implement and check
   `hash_password.py` and `salted_hash.py`, then run both programs.
   Expected: a stable digest, then changing salt/digest pairs and the Part flag.
   Checkpoint: distinguish hashing from encryption and explain unique salts.
2. **Controlled online dictionary attack (25 minutes).** Read
   [Part 2 README](part2_dictionary_attack/README.md). If assigned,
   start the isolated Compose SSH target, write and check the bounded client, observe
   the local logs, and remove the target. Expected: redacted status, attempt
   count, server-visible failures, and the Part flag. Checkpoint: why can the SSH service
   observe and rate-limit these guesses?
3. **Offline cracking and password KDFs (40 minutes).** Read
   [Part 3 README](part3_password_kdfs/README.md), implement the unsalted
   and salted cracking programs, run `compare_cost.py`, then benchmark the KDFs
   and use the local register/verify demo. Expected: hash-count comparison,
   median KDF timings, authentication without stored plaintext, and the Part flag. Checkpoint:
   explain salt reuse prevention and compare SHA-256, PBKDF2, bcrypt, scrypt,
   and Argon2id.
4. **System hashes and table attacks (35 minutes).** Read
   [Part 4 README](part4_system_hashes/README.md), parse the supplied
   shadow-style file, then implement full precomputation and rainbow tables for
   the bounded toy password database. Expected: parsed verifier fields and a
   comparison of build work, storage, lookup work, coverage, and the Part flag. Checkpoint:
   explain the time-memory tradeoff and why salts prevent shared table reuse.
5. **WPA2 verification (40 minutes).** Read
   [Part 5 README](part5_wpa2/README.md), inspect the supplied course PCAP manually
   with Wireshark or TShark, complete the capture worksheet, implement the
   PMK → PTK → KCK → MIC pipeline, then run the bounded local checks. Expected:
   manual evidence of a complete M1–M4 sequence and one matching candidate from
   the course-only wordlist, plus the Part flag. Checkpoint: explain each derivation step and
   offline rate limiting.
6. **Report (15 minutes).** Summarize your results and answers to the
   checkpoints without including any real password.

No real credential is included. The supplied PCAP is restricted to this
authorized offline exercise. The instructor may optionally provide a deliberately
vulnerable Ubuntu VM on an isolated host-only network; it is not required for
the core lab.

## Tests

Tests automatically check supplied data, examples, and student functions.
Run them **inside the course container**:

```console
cd /workspace/labs/lab01
make test
```

`make test` runs `pytest -q`, collecting tests from the numbered Part
directories and `tests/`. Basic checks run before implementation; checks that
need student functions are skipped by default. A `skipped` result is expected
at this stage and does not mean an unfinished function is correct.

Use the test file in each Part to check the current numbered exercises:

| Test file | Role |
| --- | --- |
| [part1_hashing/test_hashing.py](part1_hashing/test_hashing.py) | Checks that samples exist, then checks deterministic hashing and the effect of different salts. |
| [part2_dictionary_attack/test_ssh_dictionary_attack.py](part2_dictionary_attack/test_ssh_dictionary_attack.py) | Checks the bounded wordlist, fixed SSH target settings, and candidate loading. |
| [part3_password_kdfs/test_dictionary_cost.py](part3_password_kdfs/test_dictionary_cost.py) | Checks data schemas, recovered candidates, and hash counts for unsalted and salted guessing. |
| [part4_system_hashes/test_table_attacks.py](part4_system_hashes/test_table_attacks.py) | Checks the supplied password space and database, then table construction, reduction, and lookup. |
| [part5_wpa2/test_wpa2_workflow.py](part5_wpa2/test_wpa2_workflow.py) | Checks metadata and the local PCAP, then PMK, PTK, KCK, MIC, and dictionary verification. |

After completing a Part's required functions, enable its implementation
checks with `LAB01_GRADE=1` and select that test file. For example, after
completing both Part 3 cracking programs:

```console
LAB01_GRADE=1 python3 -m pytest -q part3_password_kdfs/test_dictionary_cost.py
```

The environment variable enables implementation checks; the file path chooses
the Part. Each Part README provides its own verification command. Selecting
one completed Part avoids running checks for other unfinished exercises.

The repository also keeps these files in `tests/`:

| File | Role |
| --- | --- |
| `test_password_authentication.py` | Checks the register/verify and shadow-parser samples, plus opt-in checks of the Part 1 hashing and Part 5 verification functions. |
| `test_md5_collision.py` | Checks that the supplied collision files have distinct contents, matching MD5 digests, and different SHA-256 digests. This fixture check runs without student implementation. |
| `__init__.py` | Makes `tests/` a Python package for imports. |

These automated tests use local fixtures or small synthetic inputs. Part 2's
test file checks constants and wordlist handling without making SSH requests,
so no target server is required to run it. The actual Part 2 online experiment
still needs `lab01-ssh-target`; follow its README to start that service.
Passing tests checks selected behavior, so also run your completed program and
collect the output and completion flag required by the Part. Keep the test
files as supplied and implement the exercise files.
