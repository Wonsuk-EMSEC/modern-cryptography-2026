# Part 6: MAC-then-Encrypt vs. Encrypt-then-MAC

**Estimated time:** 40 minutes. **Environment:** the Lab02 Docker services.

## Scenario

Two local services, named **Service A** and **Service B**, each return an
authenticated encrypted item.  Their names do not disclose how authentication
and encryption are ordered.  You can submit an item or a modified copy and
observe each service's public response.

This part continues the padding-oracle work from Part 5.  Determine which
service permits useful information to reach an attacker before authentication
has succeeded, and which service rejects altered data first.

## Objective

Compare the observed behavior of the two services, recover the message from
the service whose behavior permits the Part 5 technique, and explain why the
other service resists the same packet modifications.

## Provided Files

| File | Purpose |
| --- | --- |
| `client.py` | Client interface for locally named Service A and Service B. |
| `starter.py` | Initial probes and a TODO for the comparison. |
| `../part5_padding_oracle/starter.py` | Your earlier recovery code, available to adapt. |
| `../common/service_client.py` | Shared connection helper for the local lab service. |

`ServiceClient.item()` returns an encoded packet as bytes.  `query(packet)`
returns a public response string.  The helper method `padding_valid(packet)`
maps responses that indicate valid padding to `True`; use it only after you
have determined that the service's responses make that interpretation useful.

## Your Task

1. Obtain an item from each service and submit it unchanged to establish a
   baseline response.
2. Make controlled modifications to an IV byte and to a ciphertext byte, then
   record the responses from both services.
3. Identify the service whose responses still disclose useful padding
   information after a modification.
4. Reuse or adapt your Part 5 recovery code against that service to recover
   the protected message and its flag.
5. Explain why the other service rejects an altered packet before CBC padding
   handling can provide an oracle.

Treat Service A and Service B as black boxes.  Do not infer construction order
from their names, and do not access their implementation or cryptographic
keys.

## How to Run

Service A and Service B both run in the same local target container used in
Parts 4 and 5. If you have not loaded the instructor-provided target image yet,
follow the one-time [Lab02 setup instructions](../README.md#setup). The server
source and keys are not supplied as files in your workspace.

### Step 1: start the target and enter the course container

In a **host terminal**, from the repository root:

```console
docker compose -f docker/compose.lab02.student.yml --profile lab02 up -d --wait lab02-target
docker compose -f docker/compose.lab02.student.yml --profile lab02 ps
docker compose -f docker/compose.lab02.student.yml run --rm lab02-course bash
```

The target should be `healthy`. The last command opens a shell in
`/workspace/labs/lab02`. If your target and course shell are still running from
Part 5, continue in that shell without starting another one.

### Step 2: compare the services

Run the supplied probes **inside the course container**:

```console
python3 part6_mte_vs_etm/starter.py
```

After identifying the service with useful padding responses, run recovery
against the letter you found:

```console
python3 part6_mte_vs_etm/starter.py --recover-service SERVICE_LETTER
```

Replace `SERVICE_LETTER` with your observed choice of `A` or `B`.

To make short, controlled probes with `ServiceClient`, start Python from the
Part 6 directory in the same course shell:

```console
cd /workspace/labs/lab02/part6_mte_vs_etm
python3
```

Use `exit()` to leave Python, then `cd /workspace/labs/lab02` to return to the
lab directory.

### Step 3: reset or stop the target

If you reach a query limit, check your loop, then reset your local target from
a **second host terminal** at the repository root:

```console
docker compose -f docker/compose.lab02.student.yml --profile lab02 restart lab02-target
docker compose -f docker/compose.lab02.student.yml --profile lab02 ps
```

Wait until the target is `healthy`, then rerun your program to obtain fresh
items and repeat your probes. Restarting resets query counts for Parts 5 and 6.

When finished, run `exit` in the course shell. Then remove the Lab02 containers
from the **host terminal**:

```console
docker compose -f docker/compose.lab02.student.yml --profile lab02 down
```

## Flag Format

The recovered protected message includes one flag in this format:

```text
FLAG{...}
```

## Optional Hints

1. Compare an unchanged packet with two modifications of different packet
   components; do not rely on a service name.
2. A response that distinguishes invalid padding from a later authentication
   failure can be converted into the Boolean interface from Part 5.
3. Authentication that covers every transmitted CBC input must be checked
   before decryption to suppress that distinction.

## Analysis Questions

1. Which observed response pattern identifies a useful padding oracle?
2. Why can an encrypted MAC still leave padding behavior observable in one
   ordering?
3. Why does verifying an authentication tag before decryption stop the same
   attack?
4. Why must the authentication calculation cover both the IV and ciphertext?
