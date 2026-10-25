# Part 5: Padding Oracle Attack

[한국어](../../../../labs/lab02/part5_padding_oracle/README.md) | **English**

**Environment:** course Docker container and the supplied local Lab02 target.

The local oracle reports only whether a modified AES-CBC packet has valid
PKCS#7 padding. Recover the protected plaintext by using that Boolean
response. The recovered message contains `FLAG{...}`.

The provided `padding_oracle.py` is a zero-byte student file. Write its
imports, functions, `main()`, and execution guard. Keep recovery functions
importable without connecting to the target. The provided
`oracle_client.py` handles the local protocol and counts requests.

## 1. Run and understand the Sample

Follow the [Lab02 setup](../README.md#setup), enter the course container,
then run:

```console
cd /workspace/labs/lab02/part5_padding_oracle
python3 samples/padding_demo.py
```

The Sample uses a public message and standard PKCS#7 functions. It prints:

```text
message: b'Sample record'
padded: b'Sample record\x03\x03\x03'
length: 13 -> 16 bytes
valid suffix: True
damaged suffix: rejected
```

Observe that the padding suffix must agree with the final padding byte.
Changing a byte inside that suffix makes padding invalid even if the final
byte remains unchanged. Read the Sample's `local_example()` and `main()` to
follow bytes, exception handling, and output.

The course packet is `IV || C_1 || C_2 || ...`, with 16-byte blocks.
`OracleClient.query(packet)` returns `True` or `False`. It reveals no
plaintext. Keep the target's per-run query limit in mind while developing.

## 2. Implement one-block recovery and check it

Implement in `padding_oracle.py`:

```python
recover_block(previous: bytes, target: bytes, query: Callable[[bytes], bool]) -> bytes
```

`previous` is the IV or the preceding ciphertext block; `target` is the
ciphertext block being recovered. Both are 16 bytes. Return the 16-byte
plaintext block, including any padding bytes. Use only the Boolean result
from `query`. Recover from right to left, and resolve the possible
one-byte-padding ambiguity before accepting a candidate.

Check against a small in-memory oracle that uses only public test values.
Your recovery function receives only the callback, blocks, and Boolean
responses; the key exists in this test fixture to create responses:

```console
python3 - <<'PY'
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from padding_oracle import recover_block

key, iv = bytes(range(16)), bytes(range(16, 32))
message = b"Sample record"
padded = pad(message, 16)
target = AES.new(key, AES.MODE_CBC, iv).encrypt(padded)

def query(packet: bytes) -> bool:
    if len(packet) < 32 or len(packet) % 16:
        return False
    candidate_iv, candidate_ciphertext = packet[:16], packet[16:]
    clear = AES.new(key, AES.MODE_CBC, candidate_iv).decrypt(candidate_ciphertext)
    try:
        unpad(clear, 16)
        return True
    except ValueError:
        return False

assert recover_block(iv, target, query) == padded
print("One-block recovery: OK")
PY
```

Proceed when the recovered block matches the public padded message.

## 3. Implement full-packet recovery and check it

Implement:

```python
recover_plaintext(packet: bytes, query: Callable[[bytes], bool]) -> bytes
```

Split the packet into its IV and ciphertext blocks. Reuse your tested
`recover_block()` for each block, concatenate the recovered blocks, validate
the final PKCS#7 suffix, and return the plaintext without padding. Handle
packets that contain multiple ciphertext blocks.

Use this public two-block fixture. The callback has the same Boolean-only
interface as the local target:

```console
python3 - <<'PY'
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from padding_oracle import recover_plaintext

key, iv = bytes(range(16)), bytes(range(16, 32))
message = b"Sample message across two blocks"
packet = iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad(message, 16))

def query(candidate: bytes) -> bool:
    if len(candidate) < 32 or len(candidate) % 16:
        return False
    clear = AES.new(key, AES.MODE_CBC, candidate[:16]).decrypt(candidate[16:])
    try:
        unpad(clear, 16)
        return True
    except ValueError:
        return False

assert recover_plaintext(packet, query) == message
print("Full-packet recovery: OK")
PY
```

Proceed only when `Full-packet recovery: OK` appears.

## 4. Observe the supplied target interface

Start the local target in a **host terminal** at the repository root:

```console
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

When it is healthy, run from the Part directory inside the course container:

```console
python3 samples/padding_demo.py --target
```

The offline output is followed by the number of ciphertext blocks, the
original packet's padding-valid result, and a query count of `1`. The normal
packet should be valid. The Sample reads `data/ciphertext.hex` and submits
that packet unchanged. It performs no recovery.

## 5. Write the program entry point

Write `main()` and the execution guard in `padding_oracle.py`:

1. Read `data/ciphertext.hex` and convert its hexadecimal text to bytes.
2. Open `OracleClient()` with a `with` block.
3. Pass the packet and `oracle.query` to `recover_plaintext()`.
4. Print the recovered message and `oracle.queries`.

Follow the Sample's path handling so the program can run from the Part
directory. Keep the recovery functions independent of the client and data
file.

## 6. Run the complete exercise

```console
python3 padding_oracle.py
```

The output should contain the recovered message in the form `FLAG{...}`
and the number of oracle queries. Query counts may vary with your
implementation. Each plaintext byte must come from packet modifications
and the Boolean query interface.

## Example Output

A successful run has the following output format. Values are hidden in this
example. Include your actual results in your report. Run from
`/workspace/labs/lab02` inside the course container.

```console
python3 part5_padding_oracle/padding_oracle.py
FLAG{<recovered value>}
oracle queries: <query count>
```

Run the Part-specific implementation checks from the Lab02 directory:

```console
cd /workspace/labs/lab02
make grade PART=5
```

If you reach the target's query limit, inspect the loop, then reset the
target in the host terminal and wait until it is healthy:

```console
docker compose -f docker/compose.yml --profile lab02 restart lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

## 7. Completion and report

- [ ] One-block and full-packet public checks pass.
- [ ] The final program reads the supplied packet and uses only oracle responses.
- [ ] It recovers every plaintext block, validates padding, and prints `FLAG{...}`.
- [ ] It prints the number of queries; the Part 5 implementation checks pass.
- [ ] The report explains what the Boolean response reveals and how the
      previous block affects a target plaintext block.

Submit the student program, query count, and explanation. Submit the flag
through the instructor's designated channel. Keep the target running for
Part 6, or stop it from the host terminal:

```console
docker compose -f docker/compose.yml --profile lab02 stop lab02-target
```

## Checkpoint Questions

1. What information does the Boolean oracle reveal about a modified packet?
2. Why can this small amount of information reveal an entire plaintext block?
3. Why should a receiver avoid distinguishable padding errors for unauthenticated input?
4. How does this part connect CBC's XOR relationship to the attack in Part 4?

## Report Checklist

- [ ] Answers to the Checkpoint Questions
- [ ] Main code changes and an explanation of how they work
- [ ] Execution screenshots and the recovered FLAG
- [ ] Oracle query count (visible in the screenshot)
