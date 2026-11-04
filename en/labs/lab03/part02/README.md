# Part02: Predictable Key Recovery and Secure Random Generation

[한국어](../../../../labs/lab03/part02/README.md) | **English**

You have obtained a confidential PDF encrypted with AES-128 and the C code used to encrypt it.
The code uses the encryption timestamp as the random generator's seed.
Can knowing the approximate time let you recover the key and PDF?

## 1. Learning Objectives

1. **Recover the PDF:** reproduce timestamp-seeded random output to find the encryption key.
2. **Fix random generation:** generate the key and IV with OpenSSL and stop encryption if generation fails.

## 2. Provided Materials

- [starter/pdf_encryption.c](../../../../labs/lab03/part02/starter/pdf_encryption.c): original encryption code to analyze
- [starter/recover.py](../../../../labs/lab03/part02/starter/recover.py): recovery function TODO and supplied CLI
- [starter/secure_random.c](../../../../labs/lab03/part02/starter/secure_random.c): secure key/IV generation TODO
- [data/confidential_report.enc](../../../../labs/lab03/part02/data/confidential_report.enc): encrypted PDF
- [data/challenge.json](../../../../labs/lab03/part02/data/challenge.json): search interval, file format, and original PDF SHA-256
- [tests/check.py](../../../../labs/lab03/part02/tests/check.py), [tests/rng_driver.c](../../../../labs/lab03/part02/tests/rng_driver.c): recovery, round-trip, and error-handling checks

Encryption occurred within **2026-10-07 10:00:00–11:59:59, Asia/Seoul (UTC+09:00)**.
`start_epoch` and `end_epoch` in `challenge.json` express the interval in epoch seconds.
Including both endpoints gives **7,200 candidates**. The exact time and key are not supplied.

## 3. Tasks

### Stage 1: Recover the PDF using the timestamp-generated key

First, inspect `srand()` and the key/IV generation order in `starter/pdf_encryption.c`.

> **Encrypted file structure**
>
> `8-byte header | 16-byte IV | AES-128-CBC ciphertext`
>
> The header is `LAB03E1\n`, where `\n` is one actual LF byte. The file does not contain the key.

- **`recover(encrypted, start, end) -> bytes`: recover the PDF**

    Implement this in `starter/recover.py`. `encrypted` contains all file bytes;
    `start` and `end` are the epoch-second search bounds. For each candidate time, including both
    endpoints, generate the key and IV in the same order as the original code.
    You can use the IV stored in the file to screen candidates.

    Reproduce **glibc's `srand()`/`rand()`** output, not Python's `random` output.
    Python's standard-library `ctypes` can call the C library.
    Run inside the shared `course` container to avoid differences between operating systems' generators.

    Decrypt with AES-128-CBC, remove PKCS#7 padding, and return **all PDF bytes**.
    Do not hardcode the key, seed, PDF, or practice receipt.

- **Check the recovered result**

    Confirm that the PDF opens and compare its SHA-256 with `sha256` in `challenge.json`.
    Record the receipt inside the PDF, candidate count, and runtime.
    The checker also verifies the PDF's page and xref (object-location table) structure.

### Stage 2: Switch to secure key/IV generation

- **`generate_key_iv(key, iv)`: generate secure randomness**

    Implement this in `starter/secure_random.c`. Generate the 16-byte key with
    `RAND_priv_bytes(key, 16)` and the 16-byte IV with `RAND_bytes(iv, 16)`.
    **Return 1 only when both calls return 1**; return 0 if either fails.
    The caller does not begin encryption when this function returns 0.

    Do not fall back to `rand()`, timestamps, or fixed values, or set a seed yourself.
    Besides normal round trips, the checker injects 0 and negative return values into
    each API to verify that encryption stops.

## 4. How to Run

Complete [Lab03 setup](../README.md#setup), then run in the **course container terminal**.
No additional installation or separate server is needed.

After implementing both functions, run the checker. It compiles the C source automatically.
Failure is expected while TODOs remain.

```console
cd /workspace/labs/lab03/part02
python3 tests/check.py
```

Successful output:

```text
Part02: PDF SHA-256, glibc recovery, secure round-trip, RNG failures, bounded attack: OK
LAB03{part02_local_checks_passed}
```

After passing, save a separate copy of the PDF for submission and check its hash:

```console
mkdir -p output
python3 starter/recover.py --output output/recovered.pdf
sha256sum output/recovered.pdf
```

The supplied data produces `Recovered 710 PDF bytes`.
Open `labs/lab03/part02/output/recovered.pdf` on the host to inspect it.
`output/` is inside the repository, so it persists after the container exits.
Do not put recovered PDFs or key files in `data/`.

`LAB03{part02_local_checks_passed}` is not secret, so you may disclose it in your report.

<details>
<summary>Check alternate implementation files or data</summary>

```console
python3 tests/check.py --recovery /path/recover.py --secure /path/secure_random.c
```

Use `--data-dir` for other data in the same format.
If `openssl/evp.h` or libraries cannot be found, check that you are running inside `course`.

</details>

## 5. Success Conditions

- **PDF recovery:** the entire PDF's SHA-256 and page/xref structure match the checks.
- **Random generation:** use the two specified OpenSSL APIs for the key/IV and pass a normal round trip.
- **Error handling:** do not begin encryption if either API returns 0 or a negative value.
- **Repeat the attack:** the original 7,200 timestamp candidates cannot recover the new key/IV.

Failure of this bounded attack alone does not prove security against every attack.

## 6. Submission Requirements

Submit completed `recover.py`, `secure_random.c`, and Part02 of the [report template](../REPORT_TEMPLATE.md).
Also submit the recovered PDF through the designated private course channel and include answers to every Checkpoint Question below.

## 7. Checkpoint Questions

1. Why is this generator's search space small despite a 128-bit AES key?
2. Why does the public IV generated after the key help identify candidate seeds?
3. What could change when using a C library other than glibc?
4. Explain the different roles of the key and IV and their random-generation APIs.
5. Why should RNG failure stop encryption without a substitute value?
6. Does CBC alone ensure integrity? Distinguish this from the cause of the recovery attack.
