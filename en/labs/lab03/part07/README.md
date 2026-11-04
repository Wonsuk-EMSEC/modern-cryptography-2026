# Part07: RSA-PSS Signatures and Secure Verification

[한국어](../../../../labs/lab03/part07/README.md) | **English**

A software updater is accepting packages with invalid signatures.
Implement signing and verification, then change the updater to **accept only successfully verified updates**.
Update processing is simulated by printing `ACCEPT`; no package code is executed.

## 1. Learning Objectives

1. **Signing:** generate RSA-PSS signatures with OpenSSL EVP APIs.
2. **Verification:** distinguish valid signatures, invalid signatures, and API errors.
3. **Update policy:** fix fail-open behavior that continues processing after verification fails.

You do not need to complete Part06 first, and no separate server is required.

## 2. Provided Materials

- [starter/pss.c](../../../../labs/lab03/part07/starter/pss.c), [starter/pss.h](../../../../labs/lab03/part07/starter/pss.h): signing/verification TODOs and interfaces
- [starter/update.c](../../../../labs/lab03/part07/starter/update.c): update policy to fix
- [starter/update_vulnerable.c](../../../../labs/lab03/part07/starter/update_vulnerable.c): vulnerable update policy to analyze
- [data/trusted_public.pem](../../../../labs/lab03/part07/data/trusted_public.pem): pretrusted RSA-2048 public key
- [data/update.bin](../../../../labs/lab03/part07/data/update.bin), [data/update.sig](../../../../labs/lab03/part07/data/update.sig): valid update and signature
- [tests/check.py](../../../../labs/lab03/part07/tests/check.py), [tests/driver.c](../../../../labs/lab03/part07/tests/driver.c): compilation, signing, verification, and error checks

**Edit `starter/pss.c` and `starter/update.c`.**
No private key is supplied; the checker generates two fresh key pairs and messages to test signing as well.
The public key is a trust input that the update package cannot replace. Certificate/CA validation is outside this Part.

## 3. Tasks

### Stage 1: Implement signing and verification

> **Signature settings**
>
> RSA-2048 · RSA-PSS · SHA-256 · MGF1-SHA-256 · 32-byte salt
>
> Explicitly configure the same settings for signing and verification.

- **`sign_message()`: generate an RSA-PSS signature**

    Implement this in `starter/pss.c` using EVP DigestSign APIs.
    Query the required signature size, allocate a buffer, then sign.
    On success, return the signature buffer and length through the output parameters and return 1.
    Use a buffer the caller can release with `OPENSSL_free()`.
    On API or allocation failure, clean up resources and return 0.

- **`verify_message()`: verify a signature**

    Implement this in the same file using EVP DigestVerify APIs. Explicitly set PSS padding,
    SHA-256, the MGF1 hash, and salt length, and distinguish the return values below.
    Reject signatures using other padding, MGF1 hashes, or salt lengths.

    | Return value | Meaning |
    | --- | --- |
    | `1` | Valid signature |
    | `0` | Invalid signature |
    | `-1` | API or input error |

### Stage 2: Accept updates only after successful verification

First, read `starter/update_vulnerable.c` and trace what happens when verification returns 0.

- **`process_update()`: decide whether to accept an update**

    Call `verify_message()` in `starter/update.c`.
    **Return 1 only when the result is exactly 1**; return 0 for invalid signatures or errors.
    The driver prints these decisions as `ACCEPT` and `REJECT`, respectively.
    Rejecting every input is not a correct fix: valid signatures must be accepted.

- **Compare valid, modified, and error cases**

    Confirm that valid updates are accepted while modified messages/signatures and wrong public keys are rejected.
    The checker also injects a negative error return from `EVP_DigestVerifyFinal()`.

## 4. How to Run

Complete [Lab03 setup](../README.md#setup), then run in the **course container terminal**.
No additional installation or separate server is needed.

First, use OpenSSL to verify the supplied signature. This works before implementing the TODOs.

```console
cd /workspace/labs/lab03/part07
openssl dgst -sha256 -verify data/trusted_public.pem -signature data/update.sig \
  -sigopt rsa_padding_mode:pss -sigopt rsa_pss_saltlen:32 \
  -sigopt rsa_mgf1_md:sha256 data/update.bin
```

Expect `Verified OK`. After implementing the three functions, run the checker in the same directory.
It compiles the C source automatically. Failure is expected while TODOs remain.

```console
python3 tests/check.py
```

Successful output:

```text
Part07: fresh RSA-PSS signing, trusted verification, tampering, wrong key, malformed input, EVP error: OK
LAB03{part07_local_checks_passed}
```

`LAB03{part07_local_checks_passed}` is not secret, so you may disclose it in your report.

<details>
<summary>Compare the vulnerable and fixed versions directly</summary>

After implementing `pss.c` and `update.c`, run in the same container terminal and directory.
Keep the original message and create a modified copy in `/tmp`.

```console
cp data/update.bin /tmp/lab03-update-modified.bin
printf '\nmodified\n' >> /tmp/lab03-update-modified.bin
gcc -std=c11 -O2 -Wall -Wextra -Werror -I starter \
  starter/pss.c starter/update_vulnerable.c tests/driver.c \
  -Wl,--wrap=EVP_DigestVerifyFinal -lcrypto -o /tmp/lab03-pss-vulnerable
gcc -std=c11 -O2 -Wall -Wextra -Werror -I starter \
  starter/pss.c starter/update.c tests/driver.c \
  -Wl,--wrap=EVP_DigestVerifyFinal -lcrypto -o /tmp/lab03-pss-fixed
/tmp/lab03-pss-vulnerable update data/trusted_public.pem /tmp/lab03-update-modified.bin data/update.sig
/tmp/lab03-pss-fixed update data/trusted_public.pem /tmp/lab03-update-modified.bin data/update.sig
/tmp/lab03-pss-fixed update data/trusted_public.pem data/update.bin data/update.sig
```

Expected output, in order: `ACCEPT`, `REJECT`, `ACCEPT`.

</details>

<details>
<summary>Check alternate implementation files</summary>

```console
python3 tests/check.py --pss /path/pss.c --update /path/update.c
```

If OpenSSL headers cannot be found, check that you are running inside `course`.

</details>

## 5. Success Conditions

- **Signing:** signatures on fresh messages pass independent OpenSSL verification.
- **Valid inputs:** updates with valid signatures produce `ACCEPT`.
- **Invalid inputs:** reject modified messages/signatures, wrong public keys, short or empty signatures, malformed key files, and different signature settings.
- **API errors:** a negative `EVP_DigestVerifyFinal()` result also produces `REJECT`.

## 6. Submission Requirements

Submit completed `pss.c`, `update.c`, and Part07 of the [report template](../REPORT_TEMPLATE.md).
Include the vulnerability cause and fix, valid/modified/error test logs, the local completion marker,
and answers to every Checkpoint Question below. Do not submit private keys.

## 7. Checkpoint Questions

1. What do verification return values 1, 0, and a negative value mean?
2. Why does the original control flow accept an invalid signature?
3. Why explicitly agree on PSS, MGF1, and salt settings on both sides?
4. Why is rejecting every input an incorrect fix?
5. What trust problem arises if a package may choose its own verification key?
6. Distinguish Part08's raw RSA integer signatures from this Part's RSA-PSS.
