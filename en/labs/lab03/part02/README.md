# Part02: Predictable Key Recovery and Secure Random Generation

[한국어](../../../../labs/lab03/part02/README.md) | **English**

## 1. Learning Objectives

Distinguish AES strength from key-generation security, reproduce actual glibc
`srand()`/`rand()` output, and recover an encrypted PDF. Use OpenSSL random APIs
and stop encryption when random generation fails.

## 2. Challenge Scenario

A company encrypted a confidential report with AES-128. An audit recovered the
ciphertext and its original C source. The report was created **around 11:00 on
2026-10-07**; encryption occurred within **2026-10-07 10:00:00–11:59:59,
Asia/Seoul (UTC+09:00)**. Both epoch-second endpoints in the public metadata are
inclusive. The key and exact encryption time are withheld.

No original course PDF-encryption source was available, so this challenge was
created using AES-128-CBC and PKCS#7. It uses the real glibc C PRNG seeded with
the second returned by `time(NULL)`. Python's `random` does not reproduce this
stream. Generate and recover data in the common course container's glibc environment.

## 3. Provided Materials

| File | Purpose |
| --- | --- |
| `data/confidential_report.enc` | Encrypted PDF containing its own header and IV |
| `data/challenge.json` | Time interval, format, original PDF SHA-256 |
| `starter/pdf_encryption.c` | Original vulnerable code found in the audit |
| `starter/recover.py` | Recovery-function TODO and CLI |
| `starter/secure_random.c` | Secure key/IV generation TODO |
| `tests/check.py`, `tests/rng_driver.c` | Public feedback and independent encryption caller |

The format is 8 bytes `LAB03E1\n`, 16 IV bytes, then CBC ciphertext. The final
`\n` is one actual LF byte. Padding is OpenSSL EVP's default PKCS#7. The key is
absent. The receipt inside the recovered PDF is a local completion artifact;
hidden instructor grading flags belong to separate instances.

Common files: [recovery starter](../../../../labs/lab03/part02/starter/recover.py),
[original source](../../../../labs/lab03/part02/starter/pdf_encryption.c),
[secure RNG starter](../../../../labs/lab03/part02/starter/secure_random.c).

## 4. Tasks

1. Analyze the order in which the original C source generates the seed, key, and IV.
2. Implement `recover(encrypted, start, end) -> bytes`. Enumerate the stated
   interval, reproduce the C library output, and recover the complete PDF. The
   public IV can help screen candidates. Do not hardcode keys, seeds, PDFs, or receipts.
3. Check the original hash and PDF structure; report the receipt inside the PDF.
4. Implement `generate_key_iv()`. Use `RAND_priv_bytes(key, 16)` for the key and
   `RAND_bytes(iv, 16)` for the IV. Succeed **only when each call returns 1**.
   Return 0 on failure so the caller stops before encryption. Never substitute
   `rand()`, timestamps, or fixed values, and do not seed the generator yourself.
5. Run the public PDF encryption/decryption, RNG failure-injection, and bounded
   timestamp-attack checks. Keep key files and recovered PDFs out of `data/`.

## 5. How to Run

Follow the [Lab03 setup](../README.md). From the repository root on the host:

```console
docker compose -f docker/compose.yml run --rm course
```

Docker startup output varies with installation state. Inside the container:

```console
cd /workspace/labs/lab03/part02
gcc -std=c11 -O2 -Wall -Wextra -Werror starter/pdf_encryption.c -lcrypto -o /tmp/lab03-pdf-encryption
python3 starter/recover.py --output /tmp/lab03-recovered.pdf
python3 tests/check.py
```

GCC is silent on success. After completing the TODOs, the recovery CLI prints
`Recovered 710 PDF bytes` for the distributed instance. Checker output observed
with the completed reference implementation:

```text
Part02: PDF SHA-256, glibc recovery, secure round-trip, RNG failures, bounded attack: OK
LAB03{part02_local_checks_passed}
```

The incomplete starter intentionally fails. To check files elsewhere, use
`python3 tests/check.py --recovery /path/recover.py --secure /path/secure_random.c`.
Use `--data-dir` for another instance in the same format. If OpenSSL headers or
libraries are missing, check that you are inside the common course container.
Students do not need to install packages manually.

## 6. Success Conditions

The complete PDF must match its SHA-256 and page/xref structure. The secure
implementation must call both actual OpenSSL RNG APIs, complete normal
encryption/decryption, and stop before encryption when either API returns 0 or
a negative result in the injected tests. The original 7,200 timestamp candidates
must not recover the new key/IV. Failure of this attack or statistical testing
does not prove complete security. Local receipts are nonsecret feedback; final
grading uses fresh inputs in an isolated environment.

## 7. Submission Requirements

Submit `recover.py`, `secure_random.c`, the recovered PDF's SHA-256 and receipt,
candidate count, elapsed time, test logs, and analysis answers. Submit recovered
PDFs and sensitive intermediate values through the designated private course
channel. Hardcoded public answers or printed success messages cannot satisfy the checker.

## 8. Analysis Questions

1. Why is this generator's search space small despite a 128-bit AES key?
2. Why does the public IV generated after the key help identify candidate seeds?
3. What could change when using a C library other than glibc?
4. Explain the different roles of the key and IV and their random-generation APIs.
5. Why should RNG failure stop encryption without a substitute value?
6. Does CBC alone ensure integrity? Distinguish this from the cause of the recovery attack.
