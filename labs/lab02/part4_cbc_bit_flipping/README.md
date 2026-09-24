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

**Before completing any TODOs, read `main()` in `starter.py` from beginning to end.**
Trace the inputs, function calls, return values, and outputs so you understand
the overall execution flow.

Here, `main()` requests a normal token, verifies it, passes it to
`forge_admin_token()`, and verifies the returned token. Follow how both
verification results are printed, then complete the TODO only after you
understand this flow.

1. Start the supplied Lab02 target on your computer and obtain a normal token.
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

As in Lab01 Part 2, you start a target container on your own computer and run
the client from a course container. Parts 4–6 share this target. The instructor
publishes its prebuilt image on GitHub Container Registry (GHCR); students do
not build the target locally. The server implementation and secret files are
excluded from the student source release, but the image contains them at
runtime and can be inspected locally. See the
[Lab02 setup instructions](../README.md#setup) for the one-time course-image
preparation.

### Step 1: start the target

Compose automatically pulls this public image when needed, without a manual
download or registry login:

```text
ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab02-target:2026-lab02-v1
```

Use the Lab02 files and image from the same **`2026-lab02-v1`** release;
Part 5's supplied ciphertext must match the target image. In a **host
terminal**, from the repository root, start the common course container and
target, then check their status:

```console
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

The first `up` may take longer while Docker downloads the image. The target
should be `healthy`. Docker creates the internal lab network
automatically; you do not need to create a network or configure a server address.

### Step 2: enter the course container

From the same **host terminal**:

```console
docker compose -f docker/compose.yml exec course bash
```

Inside the container, change to the Lab02 directory:

```console
cd /workspace/labs/lab02
```

Run the following Python commands **inside this container**.

Issue and verify a normal token:

```console
python3 part4_cbc_bit_flipping/client.py issue
python3 part4_cbc_bit_flipping/client.py verify TOKEN_VALUE
```

Replace `TOKEN_VALUE` with the token printed by `issue`.  After completing the
TODO, run the full workflow:

```console
python3 part4_cbc_bit_flipping/starter.py
```

### Step 3: finish or continue to Part 5

Keep the target and course shell running if you are continuing to Part 5.
When you are finished, leave the course shell:

```console
exit
```

Exiting the shell leaves both containers running. Stop the Lab02 target from
the **host terminal**:

```console
docker compose -f docker/compose.yml --profile lab02 stop lab02-target
```

The common course container remains available for other labs. To remove the
course container, Lab02 target, and their networks when this session is
finished, run:

```console
docker compose -f docker/compose.yml --profile lab02 down
```

See the [Lab02 session instructions](../README.md#finish-or-restart-a-session)
for cleanup when you have also started the Lab01 target.

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
