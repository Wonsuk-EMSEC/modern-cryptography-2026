# Part07: Dictionary Attack on an Encrypted Private Key

[한국어](../../../../labs/lab04/part07/README.md) | **English**

## Goals and background

In Part01, you opened your own PBKDF2-protected PKCS#8 private key with a
password you knew. This Part models a separate synthetic case where an attacker
has a **copy of the file and its weak password appears in a small dictionary**.
PBES2 in this file uses
PBKDF2-HMAC-SHA256 to derive an AES encryption key. Every candidate is tested
locally inside Docker. [OpenSSL PKCS#8 documentation](https://docs.openssl.org/3.0/man1/openssl-pkcs8/)

## Materials and task

| File | Role |
|---|---|
| [attack.py](../../../../labs/lab04/part07/attack.py) | Directly runnable lab code with a `find_password()` TODO |
| [data/encrypted_key.der](../../../../labs/lab04/part07/data/encrypted_key.der) | Encrypted PKCS#8 private key |
| [data/certificate.crt](../../../../labs/lab04/part07/data/certificate.crt) | Corresponding public certificate |
| [data/wordlist.txt](../../../../labs/lab04/part07/data/wordlist.txt) | Small synthetic password dictionary |
| [data/flag.enc](../../../../labs/lab04/part07/data/flag.enc) | Flag encrypted with that public key using RSA-OAEP |
| [test_part07_materials.py](../../../../labs/lab04/part07/test_part07_materials.py) | Public check of the fixture structure |

You must complete the `find_password()` TODO in `attack.py` yourself.

In `find_password(encrypted_key, candidates)`, skip empty lines and try each
candidate in order. Return the successful UTF-8 password **bytes** and the
attempt count including that success; raise `ValueError` if none match. The
provided `main()` checks that the recovered key's public part matches the
certificate, then decrypts `flag.enc`. Do not print the password or private
key. Use the installed `cryptography` library's `load_der_private_key()` for
private-key decoding and decryption.

## Run and finish

From `/workspace` in the **course container**:

```console
python3 labs/lab04/part07/test_part07_materials.py
python3 labs/lab04/part07/attack.py
```

The first command checks materials and passes before the TODO is done. Once
implemented, the second prints attempts, elapsed time, attempts per second,
and the Flag. Do not hard-code a candidate password. Relate the cost of one
attempt to the PBKDF2 iteration count you inspected in Part01.

## What to check after completing the TODO

When `attack.py` finishes, its output has this form. The numbers and Flag depend
on the exercise files and execution environment; these are placeholders.

```text
Attempts: <tries through the successful candidate>
Elapsed seconds: <measured time>
Attempts per second: <measured rate>
LAB04{...}
```

`Attempts` includes the successful candidate. The final Flag line means the
recovered private key's public part matched the supplied certificate and the
key opened `flag.enc`. If the elapsed time is too short to calculate a rate,
`Elapsed too short to measure` appears instead of the rate line. The public
materials check prints `OK` after checking file structure; it does not check
whether your password-search TODO is correct.

Submit the modified `attack.py`, the Flag and attempt/time output, and answers
to these questions. Do not submit the password or decrypted private-key file.

## Checkpoint Questions

1. Why can someone with a file copy try candidates without a login rate limit?
2. Why can a dictionary still be tried against one salted file?
3. How do iteration count and password predictability each affect attack cost?
