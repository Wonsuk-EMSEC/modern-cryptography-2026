# Part08: RSA-CRT Fault Attack

[한국어](../../../../labs/lab03/part08/README.md) | **English**

## 1. Learning Objectives

Explain why a fault in one CRT branch can expose an RSA private key, and evaluate whether
public-key verification before output prevents leakage in this fault model. This educational
raw RSA integer-representative primitive differs from Part07's RSA-PSS scheme.

## 2. Challenge Scenario

An embedded device injects an error into one residue of its CRT signature calculation.
Recover the private key using the public key, representative `mu`, and faulty signature.
Prove recovery by signing a **fresh, unpredictable `mu2` issued afterward** by the server.

## 3. Provided Materials

- [starter/attack.py](../../../../labs/lab03/part08/starter/attack.py): TODOs for private-exponent recovery, fresh signing, and requests.
- [data/protocol.json](../../../../labs/lab03/part08/data/protocol.json): public protocol and limits.
- [tests/check.py](../../../../labs/lab03/part08/tests/check.py): checks actual server completion state.
- [Shared HTTP client](../../../../labs/lab03/common/service_client.py): `TargetClient.request(method, path, payload=None)`.
- `GET /part08/challenge`: a fresh session, RSA-2048 public key, and `mu`.

No private key or factors are provided. Public integers are canonical decimal strings without
leading zeroes, satisfying `0 <= value < n`. Sessions are 32 lowercase hexadecimal characters,
valid for 30 minutes. The request limit is 16 KiB; the server socket timeout is 5 seconds.

## 4. Tasks

1. Obtain a fresh session, then request its faulty signature and fresh `mu2` at `/part08/sign`.
   Only one CRT branch is faulty; the other residue remains correct.
2. Analyze `v = faulty_signature^e mod n` and `gcd(v - mu, n)`. Complete
   `recover_private_exponent()` and verify that the recovered factor is nontrivial.
3. Sign `mu2` with the recovered exponent and submit to `/part08/verify`. A correct signature
   of the original `mu` does not satisfy the fresh proof.
4. Request `/part08/secure-sign` with `fault:true`; confirm rejection and the complete absence
   of a signature field. With `fault:false`, obtain a normal signature and verify it with the
   public key. This endpoint signs only the original `mu`, never arbitrary inputs or `mu2`.
5. Complete all three objectives, then fetch the flag from `/part08/result`.

Field sets must match exactly; extra JSON fields are rejected. The common response field
`ok` describes request processing; `accepted` describes application acceptance.

| Method / path | Request | Successful or application result |
|---|---|---|
| `GET /part08/challenge` | None | `session`, `public_key:{n,e}`, `mu`, `primitive`, `expires_in` |
| `POST /part08/sign` | `{session}` | `faulty_signature`, `mu2`; once per session |
| `POST /part08/verify` | `{session,signature}` | `accepted`, `status:FRESH_SIGNATURE_ACCEPTED` or `INVALID_FRESH_SIGNATURE` |
| `POST /part08/secure-sign` | `{session,fault:true}` | `accepted:false`, `status:FAULT_DETECTED`; **no signature field** |
| `POST /part08/secure-sign` | `{session,fault:false}` | `accepted:true`, `status:SIGNATURE_VERIFIED`, `signature` |
| `GET /part08/result?session=...` | This session | `complete`, `checks:{fresh_signature_valid,fault_blocked,normal_signature_valid}`; `flag` only when complete |

`fault` must be a JSON boolean, not a string. HTTP errors have `{ok:false,error:...}`.
Invalid input returns 400, unknown or expired sessions 404, completed-step replay or incorrect
ordering 409, and oversized requests 413. New sessions use fresh `mu` and `mu2` values.

## 5. How to Run

Follow the [Lab03 setup](../README.md) first. The instructor must build or publish the local
image; do not assume the GHCR tag is already published. From the repository root on the host:

```console
docker compose -f docker/compose.yml --profile lab03 up -d --wait course lab03-target
docker compose -f docker/compose.yml --profile lab03 ps
docker compose -f docker/compose.yml exec course bash
```

The expected target state is `healthy`. Inside the course container:

```console
cd /workspace
python3 -c 'from labs.lab03.common.service_client import TargetClient; print(TargetClient().request("GET", "/health"))'
```

Response verified in an actual HTTP test:

```text
{'ok': True, 'service': 'lab03-target'}
```

Check the starter:

```console
python3 labs/lab03/part08/tests/check.py
```

Actual incomplete-starter output, exit status 1:

```text
Part08 incomplete: TODO: recover a factor, the second factor, and the private exponent
```

After completing the implementation, repeat the checker or run it directly:

```console
python3 labs/lab03/part08/starter/attack.py
```

The completed checker prints this first line, followed by a runtime server-issued `LAB03{...}`
value. This first line was verified with the instructor reference implementation.

```text
Part08 complete: target verified all objectives
```

Select another implementation with `--solution /workspace/path/attack.py`, or an instructor
server with `--url https://instructor-provided-address` or `LAB03_TARGET_URL`. On connection
errors, check health, execution inside the course container, and the URL. Request a fresh
session if expired. Inspect logs or stop the target from the host:

```console
docker compose -f docker/compose.yml --profile lab03 logs --tail=30 lab03-target
docker compose -f docker/compose.yml --profile lab03 stop lab03-target
```

## 6. Success Conditions

The server returns the flag only after verifying **all three** objectives: a valid signature
of fresh `mu2`, blocked faulty output, and successful normal signing. Merely submitting factors,
reusing the faulty signature, or rejecting every input does not satisfy these conditions.

The local target is for practice. A user controlling Docker can inspect local images and
runtime state. Hidden evaluation uses an instructor-managed target with separate keys and
flags. Container permissions or unavailable source alone cannot protect local secrets.

## 7. Submission Requirements

Submit the completed `attack.py`, an explanation of factor and exponent recovery, public-key
verification of the fresh signature, protected fault/no-fault request and response records,
the flag, and the answers below. Use the instructor's flag channel. Do not publish another
session's private key.

## 8. Analysis Questions

1. Why does the GCD reveal a factor when just one CRT branch is faulty?
2. Why require a signature of fresh `mu2` instead of the original representative?
3. Why must the no-fault path also succeed?
4. Why does output verification stop leakage in this model, and why is that not proof against
   every physical fault attack?
