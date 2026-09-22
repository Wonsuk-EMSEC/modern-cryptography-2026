# Part 4: CBC Bit-Flipping Attack

**Estimated time:** 25 minutes. **Environment:** the Lab02 Docker services.

## Scenario

A local application issues encrypted session tokens for ordinary users.  The
application can later verify a submitted token, but its encryption key and
internal implementation remain outside the student workspace.  Your account
is issued as a normal user; find out whether the encrypted token can be
altered so that the application treats it as an administrator.

## Objective

Demonstrate that AES-CBC encryption alone does not protect a token from
modification.  Produce a modified token that is accepted with administrator
privileges and recover the displayed flag.

CBC decryption relates adjacent packet blocks as follows:

```text
P_i = D_K(C_i) XOR C_(i-1)
```

For the first plaintext block, the IV fills the role of `C_(i-1)`.

## Provided Files

| File | Purpose |
| --- | --- |
| `client.py` | Command-line interface for issuing and verifying tokens. |
| `starter.py` | A function to complete and a small verification workflow. |
| `../common/service_client.py` | Shared connection helper for the local lab service. |

The token is encoded for transport.  Treat it as a sequence of bytes after
decoding it; do not attempt to guess the encryption key.

## Your Task

1. Obtain a normal token from the course-operated Lab02 service.
2. Inspect the starter and determine how a controlled change to a preceding
   CBC input affects the decrypted token fields.
3. Complete `forge_admin_token()` in `starter.py` so that it returns an
   encoded modified token.
4. Verify the original and modified tokens through `client.py`.
5. Record the flag only after the modified token is accepted as an
   administrator.

Do not modify the shared client or attempt to access the implementation of the
local service.  Your method should work on a newly issued token, whose IV may
change between runs.

## How to Run

Run these commands from the repository root after course staff confirm that
the isolated `lab02-target` service is available. The target implementation
and its secrets are not installed in the student workspace.

Issue and verify a normal token:

```console
docker compose -f docker/compose.lab02.student.yml run --rm lab02-course \
  python3 part4_cbc_bit_flipping/client.py issue

docker compose -f docker/compose.lab02.student.yml run --rm lab02-course \
  python3 part4_cbc_bit_flipping/client.py verify TOKEN_VALUE
```

Replace `TOKEN_VALUE` with the token printed by `issue`.  After completing the
TODO, run the full workflow:

```console
docker compose -f docker/compose.lab02.student.yml run --rm lab02-course \
  python3 part4_cbc_bit_flipping/starter.py
```


## Flag Format

The accepted administrator response contains one flag in this format:

```text
FLAG{...}
```

## Optional Hints

1. CBC supplies the previous ciphertext block as an XOR input during
   decryption.
2. The difference between two known byte values can be expressed with XOR.
3. Preserve the packet's encoding when returning it from your function.

## Analysis Questions

1. Why can an attacker change a selected plaintext byte without knowing the
   AES key?
2. What effect does a bit change have on the plaintext block associated with
   the changed ciphertext block itself?
3. Why does this demonstrate a missing integrity property rather than a flaw
   in AES?
4. Which authenticated-encryption property would prevent this modification?
