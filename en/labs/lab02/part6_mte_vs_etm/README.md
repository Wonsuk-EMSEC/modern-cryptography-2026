# Part 6: MAC-then-Encrypt vs. Encrypt-then-MAC

[한국어](../../../../labs/lab02/part6_mte_vs_etm/README.md) | **English**

**Estimated time:** 40 minutes. **Environment:** course Docker container;
the local Lab02 target is needed for the final runs.

Compare two services, named A and B, whose names do not disclose how
authentication and encryption are ordered. Design controlled modifications,
identify useful padding leakage, and adapt your completed Part 5 attack to
recover the vulnerable service's protected message.

`mte_vs_etm.py` is provided as a **zero-byte file**. Write imports, functions,
service calls, output, and the entry point there. Keep functions importable
without connecting to a target. Finish Part 5's `recover_plaintext()` in
`../part5_padding_oracle/padding_oracle.py` before implementing
message recovery here.

## 1. Run and understand the offline sample

Prepare the [course container](../README.md#setup). Run inside it:

```console
cd /workspace/labs/lab02/part6_mte_vs_etm
python3 samples/service_demo.py
```

Read `local_example()` and `main()`. The offline sample computes
HMAC-SHA-256 on a public message, appends the tag, encodes the result in
Base64, decodes it, and separates message from tag. Expected output:

```text
message: b'Sample record'
HMAC-SHA-256 tag: 32 bytes
public packet: 45 bytes
tag verification: True
```

The message has 13 bytes and SHA-256 contributes a fixed 32-byte tag, making
45 bytes before Base64 encoding. Encoding changes representation; it does
not encrypt or authenticate anything. `hmac.compare_digest()` checks the
sample tag against a freshly computed tag. This sample uses a public demo
key and contains no course secret or recovery algorithm.

The final exercise uses the supplied `client.py`: `ServiceClient(name)`
accepts `"A"` or `"B"`, `item()` returns an already-decoded binary
packet, and `query(packet)` returns a public response string. You do not
need to encode that packet yourself. The client also counts queries and
supports a `with` block for closing connections.

## 2. Write and check `probe()`

Implement in `mte_vs_etm.py`:

```python
probe(service: ServiceClient, packet: bytes) -> tuple[str, str]
```

Create two independent mutable copies of the original packet. In the first,
XOR byte index `0` with `1` to modify an IV byte. In the second, XOR byte
index `20` with `1` to modify a ciphertext byte. Submit each as bytes
through `service.query()`, in that order, and return
`(iv_response, ciphertext_response)`.

Do not accumulate both modifications in one packet, modify the original,
or infer service behavior inside this helper. It records observations for
you to interpret later. The course packets are long enough for both probes.

Check packet construction **without a running target**:

```console
python3 - <<'PY'
from mte_vs_etm import probe
packet = bytes(range(48))
class StubService:
    def __init__(self):
        self.calls = []
    def query(self, candidate):
        assert isinstance(candidate, bytes)
        self.calls.append(candidate)
        return ("IV_RESPONSE", "CIPHERTEXT_RESPONSE")[len(self.calls) - 1]
service = StubService()
assert probe(service, packet) == ("IV_RESPONSE", "CIPHERTEXT_RESPONSE")
expected_iv = bytearray(packet)
expected_iv[0] ^= 1
expected_ciphertext = bytearray(packet)
expected_ciphertext[20] ^= 1
assert service.calls == [bytes(expected_iv), bytes(expected_ciphertext)]
assert packet == bytes(range(48))
print("Independent probe check: OK")
PY
```

Expected: `Independent probe check: OK`. These response strings are
fixture labels, not actual observations from either course service.

## 3. Write and check `recover_vulnerable_message()`

Implement:

```python
recover_vulnerable_message(packet: bytes, padding_query: Callable[[bytes], bool]) -> bytes
```

Reuse or adapt your completed Part 5 `recover_plaintext(packet, query)`.
Make that implementation importable from the sibling Part directory; do
not import a nonexistent starter or an instructor solution.

The supplied `padding_query` callback returns a Boolean padding result.
Recover and unpad the entire CBC plaintext first. For the vulnerable
construction it contains `message || HMAC-SHA-256 tag`, so separate the
last **32 bytes** after padding removal and return the message bytes.
If the recovered content is shorter than 32 bytes, raise `RuntimeError`
rather than silently treating it as a valid protected record.
The exercise does not give you a MAC key for independently verifying the
recovered production tag.

Verify this wrapper with a public known-key toy oracle. The fixture builds
a protected message and answers only whether decrypted padding is valid;
it does not implement the recovery attack:

```console
python3 - <<'PY'
import hashlib
import hmac
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from mte_vs_etm import recover_vulnerable_message
key, iv, message = bytes(range(16)), bytes(range(16, 32)), b"public demo"
tag = hmac.new(b"public-demo-key", message, hashlib.sha256).digest()
packet = iv + AES.new(key, AES.MODE_CBC, iv).encrypt(pad(message + tag, 16))
counts = {"queries": 0}
def padding_query(candidate):
    counts["queries"] += 1
    if len(candidate) < 32 or len(candidate) % 16:
        return False
    try:
        padded = AES.new(key, AES.MODE_CBC, candidate[:16]).decrypt(candidate[16:])
        unpad(padded, 16)
        return True
    except ValueError:
        return False
assert recover_vulnerable_message(packet, padding_query) == message
assert counts["queries"] > 0
print("Oracle recovery and MAC separation check: OK")
PY
```

Expected: `Oracle recovery and MAC separation check: OK`. A failure may
come from your Part 5 recovery, padding removal, or incorrect tag separation.
Resolve it before querying either course service.

## 4. Write `main()` and connect the client

Implement `main() -> None` and a guarded entry point. Importing your
module must define functions without constructing service clients.

Use `argparse` to accept optional `--recover-service` with choices
`A` and `B`. With no choice, obtain an item from each service, submit
it unchanged for a baseline, call `probe()`, and print original, IV-change,
and ciphertext-change responses. Stop after these observations so you can
interpret them.

When a service is selected, also open that service, request its item, and
pass the packet and `service.padding_valid` callback to
`recover_vulnerable_message()`. Print the ASCII message and that
connection's `service.queries`. Use context managers to close connections.

`padding_valid()` maps `PADDING_OK` and `ACCEPTED` to `True`.
Use it for recovery only after your observations establish that a service's
responses disclose useful padding information. A uniform rejection response
does not provide a useful Boolean oracle merely because this method exists.

```console
python3 -c 'import mte_vs_etm; print("Import check: OK")'
python3 mte_vs_etm.py --help
```

Expected: only `Import check: OK` on import; `--help` documents
`--recover-service` and its two choices without connecting.

## 5. Start the target and compare live responses

If the target is still running from Part 5, continue with it. Otherwise,
from a **host terminal** at the repository root:

```console
docker compose -f docker/compose.yml --profile lab02 up -d --wait course lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

Wait for `lab02-target` to be `healthy`. Its pinned GHCR image supplies
both services, and the clients already know its internal service name.
For a terminal-only workflow, enter `course` using
`docker compose -f docker/compose.yml exec course bash`.

Inside the course container:

```console
cd /workspace/labs/lab02/part6_mte_vs_etm
python3 samples/service_demo.py --target
python3 mte_vs_etm.py
```

The Sample repeats its offline output, obtains items, and submits them
unchanged. Both original responses should be `ACCEPTED`; each baseline
context reports one query. Acceptance shows the service can process its own
unaltered item, not its authentication order.

Your program then supplies the controlled modifications. Record the response
pattern for each service. Look for responses distinguishing invalid padding
from a later authentication failure, versus rejection before padding can
provide useful information. Determine the service choice from those
observations; the correct letter is intentionally not provided here.

## 6. Run selected recovery and finish

After identifying the service with a useful padding oracle:

```console
python3 mte_vs_etm.py --recover-service SERVICE_LETTER
cd /workspace/labs/lab02
make grade PART=6
```

Replace `SERVICE_LETTER` with your observed choice of `A` or `B`.
Successful recovery prints a message containing `FLAG{...}` and an oracle
query count. It does not print the appended binary MAC as part of the message.
Do not hard-code the selected letter, recovered message, or flag.

## Example Output

A successful run has the following output format. Values are hidden in this
example. Include your actual results in your report. Run from
`/workspace/labs/lab02` inside the course container. Replace `SERVICE_LETTER`
with your observed choice of `A` or `B`.

```console
python3 part6_mte_vs_etm/mte_vs_etm.py --recover-service SERVICE_LETTER
Service A: original=<response>, modified=('<IV modification response>', '<ciphertext modification response>')
Service B: original=<response>, modified=('<IV modification response>', '<ciphertext modification response>')
FLAG{<recovered value>}
oracle queries: <query count>
```

Completion means the two small checks pass, import and CLI checks work,
both services have recorded baseline/probe responses, you justify your
selected service, its message is recovered, and selected-Part grading passes.
After completing all Parts, run `make grade` without `PART`.

If a service query limit is reached, inspect your loop before resetting the
target in a **host terminal**:

```console
docker compose -f docker/compose.yml --profile lab02 restart lab02-target
docker compose -f docker/compose.yml --profile lab02 ps
```

Wait for `healthy`, obtain new items, and repeat probes before recovery.
Restarting resets query counts for both Parts 5 and 6. When finished, leave
the course shell and stop the Lab02 target from the host:

```console
docker compose -f docker/compose.yml --profile lab02 stop lab02-target
```

The common course container remains available; see
[session cleanup](../README.md#finish-or-restart-a-session) for other options.

## Checkpoint Questions

In your report, include both services' original and modified response
patterns, the reason for your choice, and recovery query count. Explain:

1. Which observed response pattern identifies useful padding information?
2. Why can an encrypted MAC still leave padding behavior observable?
3. Why does authenticating before decryption prevent the same oracle?
4. Why must authentication cover the IV as well as ciphertext?

Treat both services as black boxes; do not inspect their implementation or
keys. Submit the recovered flag through the designated course channel and
keep it out of public source code and sample output.

## Report Checklist

- [ ] Answers to the Checkpoint Questions
- [ ] Main code changes and an explanation of how they work
- [ ] Execution screenshots and the recovered FLAG
- [ ] Original, IV-modified, and ciphertext-modified responses from both services
- [ ] Selected service and recovery query count (visible in the screenshot)
