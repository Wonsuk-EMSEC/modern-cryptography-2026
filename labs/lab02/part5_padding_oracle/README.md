# Part 5: Padding Oracle Attack

**Estimated time:** 50 minutes. **Environment:** the Lab02 Docker services.

## Scenario

A local application holds an encrypted record.  It will accept modified
packets and reveal only whether the resulting CBC plaintext has valid PKCS#7
padding.  It never returns the decrypted record.  Treat this one-bit response
as the only information available to your program.

## Objective

Recover the hidden plaintext one byte at a time by using CBC packet
modifications and the padding-validity response.  The recovered plaintext
contains the flag.

## Provided Files

| File | Purpose |
| --- | --- |
| `data/ciphertext.hex` | The supplied IV-and-ciphertext packet in hexadecimal form. |
| `oracle_client.py` | Boolean-only query interface for the local lab service. |
| `starter.py` | Block and full-packet recovery functions to complete. |
| `../common/service_client.py` | Shared connection helper for the local lab service. |

`OracleClient.query(ciphertext)` returns `True` for valid padding and `False`
for invalid padding.  It does not return plaintext or padding bytes.  The
service enforces a per-run query limit to help you detect an unintended loop.

## Your Task

1. Read the supplied packet as `IV || C_1 || C_2 || ...`, using AES's
   16-byte block size.
2. Complete `recover_block()` so it uses only the Boolean query result to
   recover one plaintext block.  Work from the rightmost byte toward the
   leftmost byte.
3. Handle the ambiguity that can occur when testing padding length one.
4. Complete `recover_plaintext()` to recover every plaintext block and remove
   validated PKCS#7 padding.
5. Run your program and retain the recovered flag.

Do not decode or inspect a local implementation of the oracle.  Your recovery
code must derive every plaintext byte from packet modifications and the
provided query interface.

## How to Run

Use the same local target as Part 4. If you have not loaded the
instructor-provided target image yet, follow the one-time
[Lab02 setup instructions](../README.md#setup). The oracle source and keys are
not supplied as files in your workspace.

### Step 1: start the target and enter the course container

In a **host terminal**, from the repository root:

```console
docker compose -f docker/compose.lab02.student.yml --profile lab02 up -d --wait lab02-target
docker compose -f docker/compose.lab02.student.yml --profile lab02 ps
docker compose -f docker/compose.lab02.student.yml run --rm lab02-course bash
```

The target should be `healthy`. The last command opens a shell in
`/workspace/labs/lab02`. If your target and course shell are still running from
Part 4, continue in that shell without starting another one.

### Step 2: run your recovery code

Run the starter **inside the course container** after completing its TODOs:

```console
python3 part5_padding_oracle/starter.py
```

To try a small query while developing, start Python from the Part 5 directory
in the same course shell and use `OracleClient` from there:

```console
cd /workspace/labs/lab02/part5_padding_oracle
python3
```

Use `exit()` to leave Python, then `cd /workspace/labs/lab02` to return to the
lab directory.

### Step 3: reset or stop the target

If you reach the query limit while debugging, check your loop, then reset your
local target from a **second host terminal** at the repository root:

```console
docker compose -f docker/compose.lab02.student.yml --profile lab02 restart lab02-target
docker compose -f docker/compose.lab02.student.yml --profile lab02 ps
```

Wait until the target is `healthy`, then rerun your program. Restarting the
target resets query counts for Parts 5 and 6.

Keep the target running if you are continuing to Part 6. When finished, run
`exit` in the course shell, then remove the Lab02 containers from the
**host terminal**:

```console
docker compose -f docker/compose.lab02.student.yml --profile lab02 down
```

## Flag Format

The recovered plaintext includes one flag in this format:

```text
FLAG{...}
```

## Optional Hints

1. To recover `P_i`, preserve `C_i` and construct variants of the preceding
   block.
2. First force a valid one-byte padding value, then extend the forced suffix
   one byte at a time.
3. A second perturbation can distinguish a genuine one-byte result from a
   longer valid padding suffix.

## Analysis Questions

1. What information does the Boolean oracle reveal about a modified packet?
2. Why can this small amount of information reveal an entire plaintext block?
3. Why should a receiver avoid distinguishable padding errors for unauthenticated input?
4. How does this part connect CBC's XOR relationship to the attack in Part 4?
