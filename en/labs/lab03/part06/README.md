# Part06: Textbook RSA Malleability and RSA-OAEP

[한국어](../../../../labs/lab03/part06/README.md) | **English**

## 1. Learning Objectives

Explain the multiplicative relation in textbook RSA and its effect on application inputs.
Compare the same modification with RSA-OAEP using RSA-2048, SHA-256,
MGF1-SHA-256, and an empty label.

## 2. Challenge Scenario

A transfer service encrypts integer amounts with textbook RSA. Using only an intercepted
ciphertext and the public key, make the service process **twice** the original amount.
The server never returns the decrypted amount and accepts only the specified modification
of the ciphertext issued for that session.

## 3. Provided Materials

- [starter/attack.py](../../../../labs/lab03/part06/starter/attack.py): TODOs for modification, OAEP encryption, and requests.
- [data/protocol.json](../../../../labs/lab03/part06/data/protocol.json): public protocol and limits.
- [tests/check.py](../../../../labs/lab03/part06/tests/check.py): checks completion of a fresh server-created session.
- [Shared HTTP client](../../../../labs/lab03/common/service_client.py): `TargetClient.request(method, path, payload=None)`.
- `GET /part06/challenge`: issues fresh public challenge data and the public key at runtime.

Public integers are decimal strings without leading zeroes and must satisfy `0 <= value < n`.
Sessions are 32 lowercase hexadecimal characters and expire after 30 minutes. JSON requests
are limited to 16 KiB. The original amount, private key, and instructor grading flag are not provided.

## 4. Tasks

1. Read `public_key.n`, `public_key.e`, `ciphertext`, and `multiplier` from a fresh challenge.
   Analyze how the RSA relation `c' = c · r^e mod n` affects the amount.
2. Complete `modify_ciphertext()` and the textbook RSA step in `attack(client, challenge)`.
3. Implement `encrypt_oaep()` to encrypt the **ASCII bytes** of the public `oaep_amount`,
   rather than an integer's binary representation. Explicitly configure the hash, MGF1, and label.
4. Successfully submit a normal OAEP transfer first. Apply the same multiplier to **that
   exact ciphertext** and confirm rejection. Submitting arbitrary broken ciphertext is insufficient.
5. Check every response and query the result endpoint for the server's completion decision.

Request and response schemas follow. Extra JSON fields are rejected. The common response
field `ok` describes request processing; `accepted` describes application acceptance.

| Method / path | Request | Successful or application result |
|---|---|---|
| `GET /part06/challenge` | None | `session`, `public_key:{n,e}`, `ciphertext`, `multiplier:"2"`, `oaep_amount:"100"`, `oaep:{hash,mgf1_hash,label}`, `expires_in` |
| `POST /part06/transfer` | `{session,ciphertext}` | `accepted`, `status:MODIFIED_TRANSFER_ACCEPTED` or `OBJECTIVE_NOT_MET` |
| `POST /part06/oaep/transfer` | `{session,ciphertext,stage:"normal"}` | `accepted`, `status:NORMAL_TRANSFER_ACCEPTED` or `OAEP_REJECTED` |
| `POST /part06/oaep/transfer` | `{session,ciphertext,stage:"tampered"}` | `accepted:false`, `status:OAEP_REJECTED`; `OBJECTIVE_NOT_MET` for a different modification |
| `GET /part06/result?session=...` | This session | `complete`, `checks:{textbook_modified,oaep_normal,oaep_tamper_rejected}`; `flag` only when complete |

HTTP errors have `{ok:false,error:...}`. Invalid input returns 400, unknown or expired sessions
404, replayed completed steps or incorrect ordering 409, and oversized requests 413. Start a
fresh session on each run. The service provides no arbitrary plaintext decryption interface.

## 5. How to Run

Follow the [Lab03 setup](../README.md) first. The instructor must build or publish the local
target image; do not assume the GHCR tag has already been published. From the repository root
in the **host terminal**:

```console
docker compose -f docker/compose.yml --profile lab03 up -d --wait course lab03-target
docker compose -f docker/compose.yml --profile lab03 ps
docker compose -f docker/compose.yml exec course bash
```

The expected `ps` state for `lab03-target` is `healthy`; Docker output varies by environment.
Inside the course container, check health:

```console
cd /workspace
python3 -c 'from labs.lab03.common.service_client import TargetClient; print(TargetClient().request("GET", "/health"))'
```

Response verified in an actual HTTP test:

```text
{'ok': True, 'service': 'lab03-target'}
```

Run the incomplete starter:

```console
python3 labs/lab03/part06/tests/check.py
```

Actual incomplete-starter output, exit status 1:

```text
Part06 incomplete: TODO: implement textbook RSA ciphertext modification
```

After completing the TODOs, repeat that command. You can also run:

```console
python3 labs/lab03/part06/starter/attack.py
```

The completed checker prints this first line, followed by a runtime server-issued `LAB03{...}`
value. This first line was verified with the instructor reference implementation.

```text
Part06 complete: target verified all objectives
```

Use `--solution /workspace/path/attack.py` to check another file. Select an instructor-hosted
target with `--url https://instructor-provided-address` or `LAB03_TARGET_URL`. On connection
errors, check service health, execution inside the course container, and the URL. Request a
fresh session if one has expired. Inspect logs or stop the target from the host:

```console
docker compose -f docker/compose.yml --profile lab03 logs --tail=30 lab03-target
docker compose -f docker/compose.yml --profile lab03 stop lab03-target
```

## 6. Success Conditions

The server must verify **all three** objectives in one session: the specified textbook RSA
modification, a valid OAEP transfer, and rejection of its multiplicatively modified ciphertext.
Only then does it return the flag. Printing a success string, reusing another session's result,
or submitting arbitrary ciphertext does not satisfy these checks.

Local Docker is for practice. A user controlling Docker can inspect images, processes, and
memory. Local secret concealment is not grading security. Hidden evaluation uses a trusted
instructor-hosted server with separate keys and flags.

## 7. Submission Requirements

Submit the completed `attack.py`, request/response records for each step, the server flag,
and answers below. No private key is needed. Submit flags through the instructor's channel.

## 8. Analysis Questions

1. Why can you double an unknown amount? Why are amounts bounded to avoid modular wraparound?
2. Why must normal OAEP operation succeed before testing modification?
3. Does rejection of the modified OAEP ciphertext authenticate the sender or authorize a transfer?
4. Why does textbook success alone not release the flag?
