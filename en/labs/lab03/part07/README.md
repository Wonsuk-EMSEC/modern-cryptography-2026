# Part07: RSA-PSS Signatures and Secure Verification

[한국어](../../../../labs/lab03/part07/README.md) | **English**

## 1. Learning Objectives

Implement RSA-PSS signing and verification with OpenSSL EVP APIs. Fix a fail-open
control flow that accepts invalid signatures, testing both valid and invalid inputs.

## 2. Challenge Scenario

A software-update tool processes packages even after signature verification
fails. Its trusted public key is provisioned beforehand and cannot be replaced
by a package. Demonstrate the vulnerable local policy and allow processing only
after successful verification. Update processing is an inert `ACCEPT` output;
package contents are never executed. CA and certificate validation are outside
this Part's scope.

## 3. Provided Materials

| File | Purpose |
| --- | --- |
| `data/trusted_public.pem` | Pretrusted RSA-2048 public key |
| `data/update.bin`, `data/update.sig` | Valid update and RSA-PSS signature |
| `starter/pss.h`, `starter/pss.c` | Function interfaces and signing/verification TODOs |
| `starter/update_vulnerable.c` | Deliberately vulnerable update policy |
| `starter/update.c` | Update-policy TODO |
| `tests/driver.c`, `tests/check.py` | Bounded file I/O and independent checks |

No private key is provided. The checker creates two fresh independent key pairs
and a fresh message on every run. Required parameters are **RSA-2048, SHA-256,
MGF1-SHA-256, exactly 32 salt bytes**.

Common files: [PSS starter](../../../../labs/lab03/part07/starter/pss.c),
[vulnerable policy](../../../../labs/lab03/part07/starter/update_vulnerable.c),
[update starter](../../../../labs/lab03/part07/starter/update.c).

## 4. Tasks

1. Implement `sign_message()` with EVP DigestSign APIs. Query the signature size
   before allocating its buffer, and manage ownership on failure. Return 1 for
   success and 0 for failure.
2. Implement `verify_message()` with EVP DigestVerify APIs. Explicitly configure
   PSS padding, MGF1 digest, and salt length. Return 1 for valid, 0 for invalid,
   and -1 for API/input errors.
3. Test modified messages, modified signatures, and incorrect public keys.
   Reject both invalid signatures and errors. Reject other padding, MGF1 hashes,
   and salt lengths as well.
4. Trace the result-0 path in `update_vulnerable.c`. Implement `update.c` so that
   it processes an update **only when the verification result is exactly 1**.
5. Pass both injected verification-API errors and normal-input checks. Accepting
   everything or rejecting everything cannot satisfy the challenge.

## 5. How to Run

Follow the [Lab03 setup](../README.md). From the repository root on the host:

```console
docker compose -f docker/compose.yml run --rm course
```

Docker startup output varies with installation state. Independently check the
public fixture inside the container:

```console
cd /workspace/labs/lab03/part07
openssl dgst -sha256 -verify data/trusted_public.pem -signature data/update.sig -sigopt rsa_padding_mode:pss -sigopt rsa_pss_saltlen:32 -sigopt rsa_mgf1_md:sha256 data/update.bin
```

Observed output:

```text
Verified OK
```

After completing the TODOs, build and run. GCC is silent on success.

```console
gcc -std=c11 -O2 -Wall -Wextra -Werror -I starter starter/pss.c starter/update.c tests/driver.c -Wl,--wrap=EVP_DigestVerifyFinal -lcrypto -o /tmp/lab03-pss
/tmp/lab03-pss update data/trusted_public.pem data/update.bin data/update.sig
python3 tests/check.py
```

The update output observed with the reference implementation is `ACCEPT`.
The checker then prints:

```text
Part07: fresh RSA-PSS signing, trusted verification, tampering, wrong key, malformed input, EVP error: OK
LAB03{part07_local_checks_passed}
```

The incomplete starter intentionally fails. Check alternative files with
`python3 tests/check.py --pss /path/pss.c --update /path/update.c`. To compare the
vulnerable policy, replace `starter/update.c` with `starter/update_vulnerable.c`
in the build command. For a modified message with the original signature, the
vulnerable policy should print `ACCEPT` and the corrected policy `REJECT`.
If OpenSSL headers are missing, check that you are inside the course container.
Students do not need to install packages manually.

## 6. Success Conditions

Freshly generated signatures must pass independent OpenSSL verification, and
valid updates must be processed. Reject modified messages/signatures, another
public key, short/empty signatures, malformed key files, other signature
parameters, and negative `EVP_DigestVerifyFinal()` errors. The public receipt is
nonsecret feedback. Final evaluation runs submitted source with fresh instances
in an isolated environment and awards the instructor result only after both
positive and negative behavior pass.

## 7. Submission Requirements

Submit `pss.c`, `update.c`, an explanation of the vulnerability and correction,
valid/tampered/error test logs, the local receipt, and analysis answers. Keep
private keys out of submitted source and student-release artifacts. Printing
fixed signatures or success strings cannot pass these checks.

## 8. Analysis Questions

1. What do verification return values 1, 0, and a negative value mean?
2. Why does the original control flow accept an invalid signature?
3. Why explicitly agree on PSS, MGF1, and salt settings on both sides?
4. Why is rejecting every input an incorrect fix?
5. What trust problem arises if a package may choose its own verification key?
6. Distinguish Part08's raw RSA integer signatures from this Part's RSA-PSS.
