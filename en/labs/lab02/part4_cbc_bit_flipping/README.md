# Part 4: CBC Bit-Flipping Attack

[한국어](../../../../labs/lab02/part4_cbc_bit_flipping/README.md) | **English**

**Environment:** course Docker container. Use only the supplied local target.

CBC encryption does not authenticate a packet. In this Part, write a program
that changes the meaning of a course token and compares the original and
modified verification results. The final successful response contains a flag.

The provided `cbc_bit_flipping.py` is empty. Write its imports, function,
`main()`, and execution guard yourself. The functions must be importable
without making network requests.

## 1. Run the offline Sample

Prepare the [course container](../README.md#setup), then run inside it:

```console
cd /workspace/labs/lab02/part4_cbc_bit_flipping
python3 samples/cbc_token_demo.py
```

Read the Sample's input, encryption, packet encoding, decoding, and output.
It uses public demonstration values independent of the course target.

```text
message: b'Sample token'
packet: 32 bytes = 16 IV + 16 ciphertext
base64 round-trip: True
recovered: b'Sample token'
CBC round-trip: OK
```

Confirm that the binary packet contains the 16-byte IV followed by complete
ciphertext blocks. Base64 is a representation of those bytes. The recovered
message matches the original after padding removal.

## 2. Implement and immediately check token modification

Implement this interface in `cbc_bit_flipping.py`:

```python
forge_admin_token(normal_token: str) -> str
```

The input and return value are Base64 strings encoding `IV || ciphertext`.
The course token contains the ASCII field `admin=0;` in its first plaintext
block. Return a modified packet whose decrypted field is `admin=1;`.
Preserve the packet's encoding and block layout. Use the CBC relation:

```text
P_i = D_K(C_i) XOR C_(i-1)
C_0 = IV
```

Determine how changing the preceding block changes a selected plaintext
byte. The service's encryption key is unavailable to your function. Your
method must work on newly issued tokens with different IVs.

Before adding service calls, run this public local fixture. The fixture's
key is used only by the test to create and inspect a packet:

```console
python3 - <<'PY'
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from cbc_bit_flipping import forge_admin_token

key = bytes(range(16))
for iv in (bytes(range(16, 32)), bytes([7]) * 16):
    message = b"admin=0;userid=1042"
    packet = iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad(message, 16))
    original = base64.b64encode(packet).decode("ascii")
    modified = base64.b64decode(forge_admin_token(original), validate=True)
    recovered = unpad(AES.new(key, AES.MODE_CBC, modified[:16]).decrypt(modified[16:]), 16)
    assert len(modified) == len(packet)
    assert b"admin=1;" in recovered
    assert b"userid=1042" in recovered
print("Local token check: OK")
PY
```

Proceed only when `Local token check: OK` appears for the two IVs.

## 3. Observe the target client

From a **host terminal** at the repository root, start the local target:

```console
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

The target must be healthy. Back in the Part directory inside the course
container, run:

```console
python3 samples/cbc_token_demo.py --target
```

In addition to the offline output, the Sample reports a block-aligned target
packet and the normal verification response. An ordinary token should not
grant administrator privileges. Observe the response without modifying
`client.py`.

Read the Sample's target branch. The provided `client.issue()` returns a
Base64 token; `client.verify(token)` returns the service's response string.
Both functions manage their connections.

## 4. Write the program entry point

Now write `main()` and the execution guard in `cbc_bit_flipping.py`:

1. Request a fresh normal token with the provided client.
2. Verify that original token and print its response.
3. Call your tested `forge_admin_token()` function.
4. Verify the returned token and print its response.

Keep network requests inside the entry point. Derive the modified packet
from the issued token on every run.

## 5. Run the complete exercise

```console
python3 cbc_bit_flipping.py
```

Record the original response and the modified response. Successful modified
verification grants administrator privileges and includes `FLAG{...}`.
Random IVs and token strings may differ between runs.

## Example Output

A successful run has the following output format. Values are hidden in this
example. Include your actual results in your report. Run from
`/workspace/labs/lab02` inside the course container.

```console
python3 part4_cbc_bit_flipping/cbc_bit_flipping.py
normal: <original token response>
modified: <administrator response> FLAG{<recovered value>}
```

Run only this Part's implementation checks:

```console
cd /workspace/labs/lab02
make grade PART=4
```

## 6. Completion and report

- [ ] The local fixture passes with both IVs.
- [ ] The program requests and verifies a fresh normal token.
- [ ] Modified verification grants administrator privileges and returns a flag.
- [ ] Part 4 implementation checks pass.
- [ ] The report explains how CBC's preceding block affects the plaintext.
- [ ] The report explains why encryption alone did not detect the modification.

Submit your program, verification observations, and explanation. Submit the
flag through the instructor's designated channel. Keep the target running
if continuing to Part 5. When finished with the target, run from the host:

```console
docker compose -f docker/compose.yml --profile lab02 stop lab02-target
```

The shared course container remains available. See the
[session instructions](../README.md#finish-or-restart-a-session) for cleanup.

## Checkpoint Questions

1. Why can an attacker change a selected plaintext byte without knowing the
   AES key?
2. What effect does a bit change have on the plaintext block associated with
   the changed ciphertext block itself?
3. Why does this demonstrate a missing integrity property rather than a flaw
   in AES?
4. Which authenticated-encryption property would prevent this modification?

## Report Checklist

- [ ] Answers to the Checkpoint Questions
- [ ] Main code changes and an explanation of how they work
- [ ] Execution screenshots and the recovered FLAG
- [ ] Original and modified token verification responses (visible in the screenshot)
