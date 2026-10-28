# Part04: RSA Factorization Attack

[한국어](../../../../labs/lab03/part04/README.md) | **English**

## 1. Learning Objectives

Factor an RSA modulus with a small factor using bounded trial division, then
recover the private exponent and plaintext. Explain why total modulus bit
length alone does not determine factorization difficulty.

## 2. Challenge Scenario

You obtained a legacy application's public key and an encrypted short
verification value. An audit notes that one prime is too small. Use the public
search bound to reconstruct the private key.

## 3. Provided Materials

- [data/challenge.json](../../../../labs/lab03/part04/data/challenge.json): decimal strings `n`, `e`, `c`,
  inclusive small-factor upper bound `factor_bound`, plaintext byte length, and
  SHA-256. Factors, private exponent, and plaintext answers are not disclosed.
- [starter/recover.py](../../../../labs/lab03/part04/starter/recover.py): `solve(challenge)` TODO.
- [tests/check.py](../../../../labs/lab03/part04/tests/check.py): public factor/key/plaintext verifier.

A separate documentation example is `n=55`, `e=3`, `m=7`, `c=13`. This public
practice example does not disclose the actual challenge factors or plaintext.

## 4. Tasks

1. Parse `n`, `e`, and `c` as integers. Find a factor by trial division within the
   public bound, then obtain the other factor. Advanced factoring is unnecessary.
2. Compute phi and d; verify `e*d mod phi == 1`.
3. Convert the decrypted integer into exactly `message_bytes` big-endian bytes,
   preserving leading zeros, and verify SHA-256.
4. Return `{'p': int, 'q': int, 'd': int, 'message_hex': str}`. Re-encrypt the
   plaintext to verify the ciphertext. Do not embed challenge answers as constants.

## 5. How to Run

Start the shared `course` container using [Lab03 setup](../README.md#setup).

```console
cd /workspace/labs/lab03/part04
python3 tests/check.py
```

Actual incomplete-starter output, exit code 1:

```text
FAIL: AssertionError: submission failed: NotImplementedError: factor the weak modulus and decrypt
```

After implementation, run the following command. This output was verified with
the instructor reference. Full JSON includes factor/d/plaintext evidence that
the parent checker independently validates.

```console
python3 tests/check.py | python3 -c 'import json,sys; r=json.load(sys.stdin); print(r["status"]); print(r["receipt"])'
```

```text
PASS
LAB03{part04_local_checks_passed}
```

Use `python3 tests/check.py --solution PATH --data PATH` for alternate files and
inputs. The runtime budget is 10 seconds. Do not search indefinitely or divide
through the large factor. Check integer conversion, byte length, and big-endian
order when diagnosing hash mismatches.

## 6. Success Conditions

Distinct nontrivial factors must multiply to n, with the smaller factor within
the public bound. d must be the correct inverse modulo phi. Decryption,
re-encryption, original byte length, and SHA-256 must all match. The recovered
five bytes are this challenge's verification value. The public
`LAB03{part04_local_checks_passed}` receipt is nonsecret local feedback. Final
grading uses independently generated keys and plaintexts; printing the receipt
or reusing the public answer is insufficient.

## 7. Submission Requirements

Submit completed `recover.py`, p/q/d and recovered-byte hex, number of candidates
searched and elapsed time, hash/re-encryption results, and the
[report](../REPORT_TEMPLATE.md).

## 8. Analysis Questions

1. Why does a small factor enable this attack even when the other factor is large?
2. Why does factoring n allow recovery of the private exponent?
3. Why specify a length when converting the decrypted integer into bytes?
4. Which errors do re-encryption and SHA-256 checks detect respectively?
