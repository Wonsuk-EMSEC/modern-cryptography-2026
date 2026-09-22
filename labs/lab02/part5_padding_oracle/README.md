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

Run these commands from the repository root after course staff confirm that
the isolated `lab02-target` service is available. The student release contains
only the Boolean client interface, never the oracle implementation or keys.

Run the starter after completing its TODOs:

```console
docker compose -f docker/compose.lab02.student.yml run --rm lab02-course \
  python3 part5_padding_oracle/starter.py
```

To try a small query while developing, run an interactive shell in the student
workspace and use `OracleClient` from there:

```console
docker compose -f docker/compose.lab02.student.yml run --rm -it lab02-course bash
cd /workspace/labs/lab02/part5_padding_oracle
python3
```

If you reach the query limit while debugging, ask course staff to reset the
course target after checking your loop.

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
