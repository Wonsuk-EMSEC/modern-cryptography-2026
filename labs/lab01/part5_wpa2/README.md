# Part 5: WPA2 offline candidate verification

**Estimated time:** 40 minutes.

**Ethical and authorized use:** use only the supplied course PCAP and synthetic
metadata. Do not capture traffic, deauthenticate clients, disrupt networks, use
a wireless interface, or test third-party credentials. This exercise begins
after an authorized capture has already been provided.

In this part, packet observations are deliberately **not extracted by a Python
script**. You must inspect the saved PCAP with Wireshark or TShark, find the
relevant fields in the decoded protocol tree, and record your own observations.
You will then implement the WPA2 candidate-verification calculations in Python.

## Learning objectives

After completing this part, you should be able to:

- locate the SSID and BSSID in an 802.11 management frame;
- identify the AP and station addresses in EAPOL-Key frames;
- distinguish M1, M2, M3, and M4 using direction, flags, and replay counters;
- locate nonces and a MIC in the Wireshark protocol tree;
- implement WPA2-Personal PMK, PTK, KCK, and MIC calculations;
- explain why a recorded handshake permits offline candidate verification; and
- state the authorization boundary for wireless-security experiments.

## Files used

| File | Purpose |
| --- | --- |
| `data/wpa2/lab01-handshake.pcap` | Instructor-provided classroom capture |
| `data/wpa2/lab01-pcap-wordlist.txt` | Small candidate list for that PCAP only |
| `data/wpa2_passwords.txt` | Bounded candidates for the separate synthetic Python record |
| `CAPTURE_WORKSHEET.md` | Blank table for your manual packet observations |
| `data/wpa2_capture.json` | Separate synthetic Python calculation fixture |
| `samples/explain_handshake.py` | Prints fields from the separate synthetic JSON fixture |
| `samples/bytes_hmac_demo.py` | Complete public byte/KDF/HMAC API example |
| `verify_candidate.py` | Empty file for the complete student verification program |
| `test_wpa2_workflow.py` | Baseline and opt-in implementation tests |
| `samples/flag_unlock_demo.py` | Public helper-usage example; no Part answer |
| `data/flag_challenge.json` | Encrypted completion flag, opened by the experiment result |

The PCAP and `wpa2_capture.json` are two separate, intentionally created
classroom datasets. Do not expect their SSIDs, addresses, nonces, or MICs to be
the same. The PCAP is for manual protocol inspection and the bounded
aircrack-ng comparison. The JSON fixture gives your Python functions a compact,
reproducible input after you have learned where those values appear in a real
packet trace.

The SSID and endpoint MAC addresses embedded in the distributed PCAP are
fictional course identifiers. They are intentionally left out of this guide so
that finding them remains part of Exercise A.

## 1. Run and inspect the public byte/API sample

Inside the course container:

```console
cd /workspace/labs/lab01/part5_wpa2
python3 samples/bytes_hmac_demo.py
python3 -m unittest test_wpa2_workflow.py -v
```

The sample uses public values unrelated to either classroom capture. It prints:

```text
Ordered public bytes: 01020201
Cleared first two bytes: 0000626c69632d64617461
Toy KDF bytes: 16
SHA-256 HMAC bytes: 32
Truncated example bytes: 8
Same message verifies: True
Changed message verifies: False
```

Inspect JSON loading, hex decoding, byte sorting, `bytearray` editing, KDF
output lengths, HMAC, slicing, and constant-time comparison. This sample uses
SHA-256 and 1,000 KDF iterations; the WPA2 exercise uses different parameters.
No file is created. Before implementation, two fixture checks pass and seven
implementation checks are skipped.

## Prepare the analysis tool

TShark, Wireshark's command-line packet analyzer, is installed in the course
image. If your image was built before this Part 5 update, leave the container
and rebuild the image from a **host terminal at the repository root**:

```console
docker compose -f docker/compose.yml build
docker compose -f docker/compose.yml run --rm course bash
```

After the `run` command opens a new course container shell, verify the tool
and move to Part 5:

```console
tshark --version
cd /workspace/labs/lab01/part5_wpa2
```

The Compose configuration does not forward a graphical desktop from the
container. You may optionally open the same repository PCAP with a Wireshark
GUI installed on the host. TShark is the supported container-only path, so a
host Wireshark installation is not required.

### Public flag utility sample

```console
python3 samples/flag_unlock_demo.py
```

Expected output:

```text
Wrong proof rejected: OK
FLAG{public_demo_only}
This public demo flag is not a Part completion flag.
```

The sample leaves no file behind. Inspect how the shared utility is imported,
how authentication failure is handled, and how a successful return value is
printed. Your final program will use its own experiment result, not this public
demo proof.

## 2. Inspect the PCAP manually

Do not write or use a Python parser for this exercise. Do not use a TShark
`-T fields` command that prints a ready-made answer table. Read the decoded
packet tree and enter your findings in `CAPTURE_WORKSHEET.md`.

### Option 1: Wireshark GUI on the host

1. Choose **File > Open** and select
   `labs/lab01/part5_wpa2/data/wpa2/lab01-handshake.pcap` from this repository.
2. Enter the following display filter to show the authentication key exchange:

   ```text
   eapol
   ```

3. Inspect the four displayed frames. In the 802.11 header, find the BSSID that
   is common to the exchange, then distinguish the AP from the other
   station/client address using frame direction and the Key ACK flag.
4. Replace `RECORDED_BSSID` below with the BSSID you just observed. This limits
   the many beacon frames in the PCAP to the relevant access point:

   ```text
   wlan.fc.type_subtype == 0x0008 && wlan.bssid == RECORDED_BSSID
   ```

5. Select the resulting beacon and expand **IEEE 802.11 wireless LAN management
   frame**. Confirm the BSSID in the 802.11 header. Expand **Tagged parameters**
   and the **SSID parameter set** to find the network name.
6. Return to the `eapol` filter. In each frame, record the receiver,
   transmitter, and BSSID. Under **802.1X Authentication** and **WPA Key Data**
   (wording can vary by Wireshark version), locate the replay counter, nonce,
   key MIC, and Key Information flags.
7. Use the message-identification table below to label each frame M1-M4. Record
   frame numbers rather than relying only on their displayed order.

### Option 2: TShark inside the course container

First view the packet list so you understand the trace layout:

```console
tshark -r data/wpa2/lab01-handshake.pcap
```

Display the full decoded protocol tree for the EAPOL-Key frames first:

```console
tshark \
  -r data/wpa2/lab01-handshake.pcap \
  -Y 'eapol' \
  -V
```

Read the receiver, transmitter, BSSID, replay counter, nonce, key MIC, and Key
Information flags. Identify the BSSID shared by the four frames. Then replace
`RECORDED_BSSID` below with that value to inspect only the relevant beacon:

```console
tshark \
  -r data/wpa2/lab01-handshake.pcap \
  -Y 'wlan.fc.type_subtype == 0x0008 && wlan.bssid == RECORDED_BSSID' \
  -V
```

Read the 802.11 header and tagged parameters to locate the SSID. The verbose
output is long by design: locating fields in a protocol tree is part of the
exercise.

### Identify M1-M4

Use the AP/STA direction and these EAPOL-Key flags. A set bit is shown as `1`.

| Message | Direction | Key ACK | Key MIC | Secure | Main observation |
| --- | --- | ---: | ---: | ---: | --- |
| M1 | AP -> STA | 1 | 0 | 0 | AP supplies ANonce |
| M2 | STA -> AP | 0 | 1 | 0 | STA supplies SNonce and MIC |
| M3 | AP -> STA | 1 | 1 | 1 | AP authenticates key installation |
| M4 | STA -> AP | 0 | 1 | 1 | STA acknowledges installation |

Wireshark may display additional Key Information bits. Use only the direction,
three bits above, replay counter, and nonce behavior for this simplified
classification. If your four rows do not form a coherent exchange, recheck the
addresses and frame numbers before continuing.

### Manual observation questions

Complete the worksheet without consulting an automated parser:

1. Which beacon-frame field contains the SSID? Which header field contains the
   BSSID?
2. Which address belongs to the AP, and which belongs to the station?
3. Which frames are M1, M2, M3, and M4? Give evidence from direction and flags.
4. In which messages do ANonce and SNonce first appear?
5. How do the replay counters group the request/response pairs?
6. Which messages contain a nonzero MIC, and why does M1 differ?

Do not put the recovered passphrase in the worksheet, report, or screenshots.

## 3. Inspect the synthetic fixture and understand the pipeline

After completing the manual worksheet, run:

```console
python3 samples/explain_handshake.py data/wpa2_capture.json
```

This sample prints the JSON field names and values, then explains the key
derivation sequence. Compare each field name with the packet-tree fields you
located manually. It reads only the separate JSON fixture; it does not parse
the PCAP. No file is generated.

### PMK, PTK, KCK, and MIC

The password is not transmitted in the four-way handshake. For WPA2-Personal,
a candidate and SSID produce the **Pairwise Master Key (PMK)**:

```text
PMK = PBKDF2-HMAC-SHA1(
    password = UTF-8(passphrase),
    salt = UTF-8(SSID),
    iterations = 4096,
    output length = 32 bytes
)
```

The two peers order their raw address and nonce byte strings identically:

```text
context = min(AP_MAC, STA_MAC) || max(AP_MAC, STA_MAC)
        || min(ANonce, SNonce) || max(ANonce, SNonce)
```

Two 6-byte MAC addresses and two 32-byte nonces produce a 76-byte context. The
PMK and context are expanded into a 64-byte **Pairwise Transient Key (PTK)**:

```text
block[i] = HMAC-SHA1(
    key = PMK,
    data = "Pairwise key expansion" || 0x00 || context || BYTE(i)
)

PTK = first 64 bytes of (block[0] || block[1] || ...)
```

Start the one-byte counter at zero. The first 16 PTK bytes are the **Key
Confirmation Key (KCK)** used to authenticate EAPOL-Key data with a MIC. Other
PTK sections include the KEK and TK, which are not calculated separately here.

For candidate verification, the captured MIC field in the EAPOL bytes is first
replaced with zeros. A candidate MIC is then computed with HMAC-SHA1 and
truncated to 16 bytes:

```text
candidate + SSID -> PMK
PMK + ordered addresses/nonces -> PTK -> first 16 bytes -> KCK
KCK + normalized EAPOL -> candidate MIC -> constant-time comparison
```

A matching MIC is evidence that the candidate generated the same key material.
All inputs needed to test another candidate are already local, so no guess is
sent to the access point and server-side rate limiting cannot observe it.

## 4. Write derive_pmk(), then check it

The provided `verify_candidate.py` is empty. Write all imports, functions,
constants, CLI parsing, and the execution guard yourself. Define:

| Constant | Value |
| --- | --- |
| `PRF_LABEL` | `b"Pairwise key expansion"` |
| `PMK_ITERATIONS`, `PMK_LENGTH` | 4096, 32 |
| `PTK_LENGTH`, `KCK_LENGTH`, `MIC_LENGTH` | 64, 16, 16 |
| `EAPOL_MIC_OFFSET` | 81 |

Implement `derive_pmk(candidate: str, ssid: str) -> bytes` using UTF-8,
PBKDF2-HMAC-SHA1, and the WPA2 parameters above.

```console
python3 - <<'PY'
import hashlib
from verify_candidate import derive_pmk
candidate, ssid = "public-example", "PublicSampleSSID"
pmk = derive_pmk(candidate, ssid)
assert pmk == hashlib.pbkdf2_hmac("sha1", candidate.encode("utf-8"), ssid.encode("utf-8"), 4096, 32)
assert len(pmk) == 32
assert pmk != derive_pmk(candidate, "OtherSampleSSID")
print("PMK check: OK")
PY
```

Proceed after `PMK check: OK`. This check uses no classroom passphrase.

## 5. Write build_context(), then check ordering

Implement `build_context(record: dict[str, str]) -> bytes`. Decode
`ap_mac`, `client_mac`, `anonce`, and `snonce` from hex. Sort the two MAC
byte strings independently of the two nonce byte strings, then concatenate
MACs followed by nonces. The result must be 76 bytes.

```console
python3 - <<'PY'
from verify_candidate import build_context
record = {"ap_mac": "020000000001", "client_mac": "010000000001",
          "anonce": "22" * 32, "snonce": "11" * 32}
expected = bytes.fromhex("010000000001020000000001" + "11" * 32 + "22" * 32)
assert build_context(record) == expected
record["ap_mac"], record["client_mac"] = record["client_mac"], record["ap_mac"]
record["anonce"], record["snonce"] = record["snonce"], record["anonce"]
assert build_context(record) == expected
assert len(expected) == 76
print("Context ordering check: OK")
PY
```

Proceed after `Context ordering check: OK`.

## 6. Write derive_ptk(), then check expansion

Implement `derive_ptk(pmk: bytes, context: bytes) -> bytes`. Compute successive
HMAC-SHA1 blocks over `PRF_LABEL || 0x00 || context || BYTE(counter)`,
starting the counter at zero. Concatenate enough blocks, then retain the first
64 bytes. Use raw byte strings throughout.

```console
python3 - <<'PY'
import hashlib
import hmac
from verify_candidate import derive_ptk
pmk, context = bytes(range(32)), bytes(range(76))
expected = b"".join(hmac.new(pmk, b"Pairwise key expansion\x00" + context + bytes([i]),
                             hashlib.sha1).digest() for i in range(4))[:64]
assert derive_ptk(pmk, context) == expected
assert derive_ptk(pmk, context + b"x") != expected
print("PTK expansion check: OK")
PY
```

Proceed after `PTK expansion check: OK`.

## 7. Write derive_kck(), then check the slice

Implement `derive_kck(ptk: bytes) -> bytes`: return the first 16 PTK bytes.

```console
python3 - <<'PY'
from verify_candidate import derive_kck
ptk = bytes(range(64))
assert derive_kck(ptk) == bytes(range(16))
print("KCK check: OK")
PY
```

Proceed after `KCK check: OK`.

## 8. Write normalized_eapol(), then check byte preservation

Implement `normalized_eapol(record: dict[str, str]) -> bytes`. Decode
`record["eapol"]`, reject inputs shorter than 97 bytes with `ValueError`,
and clear exactly the 16-byte MIC field at slice `81:97`. Preserve all
remaining bytes, and return immutable `bytes`.

```console
python3 - <<'PY'
from verify_candidate import normalized_eapol
raw = bytes(range(100))
normalized = normalized_eapol({"eapol": raw.hex()})
assert len(normalized) == len(raw)
assert normalized[:81] == raw[:81] and normalized[97:] == raw[97:]
assert normalized[81:97] == bytes(16)
try:
    normalized_eapol({"eapol": bytes(96).hex()})
except ValueError:
    pass
else:
    raise AssertionError("truncated EAPOL was accepted")
print("EAPOL normalization check: OK")
PY
```

Proceed after `EAPOL normalization check: OK`.

## 9. Write compute_mic(), then check a public message

Implement `compute_mic(kck: bytes, eapol: bytes) -> bytes`: use HMAC-SHA1
over already normalized EAPOL bytes, retaining the first 16 digest bytes.

```console
python3 - <<'PY'
import hashlib
import hmac
from verify_candidate import compute_mic
key, message = bytes(range(16)), b"public-EAPOL-example"
expected = hmac.new(key, message, hashlib.sha1).digest()[:16]
assert compute_mic(key, message) == expected
assert compute_mic(key, message + b"x") != expected
print("MIC check: OK")
PY
```

Proceed after `MIC check: OK`.

## 10. Write verify(), then check the public pipeline

Implement `verify(candidate: str, record: dict[str, str]) -> bool`.
Connect the implemented PMK, context, PTK, KCK, normalized EAPOL, and MIC
functions; decode the captured `record["mic"]` and compare it with the
computed MIC using `hmac.compare_digest()`. Return only a boolean; do not
print a candidate or derived key material.

This check builds a separate public toy record with your completed primitives:

```console
python3 - <<'PY'
from verify_candidate import (
    derive_pmk, build_context, derive_ptk, derive_kck,
    normalized_eapol, compute_mic, verify,
)
record = {"ssid": "PublicSampleSSID",
          "ap_mac": "020000000001", "client_mac": "010000000001",
          "anonce": "22" * 32, "snonce": "11" * 32, "eapol": bytes(range(100)).hex()}
public = "public-example"
pmk = derive_pmk(public, record["ssid"])
kck = derive_kck(derive_ptk(pmk, build_context(record)))
record["mic"] = compute_mic(kck, normalized_eapol(record)).hex()
assert verify(public, record) is True
assert verify("different-public-example", record) is False
print("Public pipeline check: OK")
PY
```

Proceed after `Public pipeline check: OK`. The earlier individual checks
matter: a round trip alone can conceal the same mistake on both sides.

## 11. Write main() and run the synthetic exercise

Write `main()` using `argparse` for one local metadata JSON path and
`getpass.getpass("Candidate: ")` for interactive input. Load JSON and call
`verify()`; report `match` or `no match`, then follow the completion-flag
requirements below. Add the execution guard;
importing the module must not prompt or run a search.

```console
python3 -c "import verify_candidate; print('Import check: OK')"
LAB01_GRADE=1 python3 -m unittest test_wpa2_workflow.py -v
python3 verify_candidate.py data/wpa2_capture.json
```

All nine enabled tests should pass. They check the data, byte lengths,
ordering, sensitivity, truncation rejection, and that exactly one candidate
from the provided synthetic wordlist matches. They do not print that candidate.

For interactive verification, choose a candidate from
`data/wpa2_passwords.txt` and enter it at the prompt. A consistent candidate
prints `match` followed by the flag; other input prints `no match`. No access
point is contacted.

### Shared completion utility

The whole main program is still yours to write. Resolve the envelope relative
to your exercise file, rather than the shell's current directory. To import
the provided shared utility from a numbered Part exercise file, use:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from labs.lab01.common.flags import unlock_flag, canonical_account_proof
```

`unlock_flag(path, proof)` returns a `FLAG{...}` string after authenticating
the encrypted envelope. An incorrect proof raises `ValueError`; inspect your
implementation and proof format rather than changing the envelope.
The public demo proof opens only the demo artifact and cannot open this Part's
flag. Submit the computed Part flag through the instructor's designated channel.

### Add a bounded synthetic search and flag output

Support an optional `--wordlist` argument in your main for the supplied
`data/wpa2_passwords.txt`. When present, read its nonempty stripped UTF-8
lines and test every candidate through your completed `verify()`. Count the
candidates, measure elapsed time with `time.perf_counter()`, and require
exactly one match. Report only the candidate count, match count, and time;
keep the matching candidate and all derived key material private.

Use that verified candidate string as the proof for
`data/flag_challenge.json`, call `unlock_flag(flag_path, candidate)`, and
print its returned `FLAG{...}` as the final line. In interactive mode, print
the flag only after `verify()` returns `True`; an incorrect input prints
`no match` without a flag.

The completion proof comes from the synthetic JSON dataset. The separate
PCAP inspection, worksheet, and aircrack-ng comparison remain required.

### Run the full synthetic flag exercise

```console
python3 verify_candidate.py data/wpa2_capture.json --wordlist data/wpa2_passwords.txt
```

Expected output shape:

```text
Candidates tested: <count>
Matches: 1
Elapsed: <seconds> seconds
FLAG{...}
```

The count must equal the number of nonempty supplied candidate lines; timing
varies by host. Authentication of the envelope confirms the recovered candidate
is consistent with the intended synthetic experiment.

## 12. Complete the bounded PCAP comparison

Use the BSSID you recorded manually in `CAPTURE_WORKSHEET.md`.
Replace `AP_BSSID_FROM_WORKSHEET` before running:

```console
aircrack-ng \
  -w data/wpa2/lab01-pcap-wordlist.txt \
  -b AP_BSSID_FROM_WORKSHEET \
  data/wpa2/lab01-handshake.pcap
```

Use only these two supplied course files. Record tested-key count and elapsed
time, and redact the key from screenshots and reports. The tool should find
a matching candidate in the bounded PCAP wordlist. Do not substitute a
downloaded wordlist or another capture.

The PCAP and synthetic JSON are distinct datasets: their passphrases and
metadata need not match. Compare the two offline workflows. Both derive key
material locally and reproduce authentication data; neither submits a guess
to an access point.

## 13. Completion and report

- [ ] `CAPTURE_WORKSHEET.md` contains manually observed fields and evidence for M1-M4.
- [ ] The initially empty `verify_candidate.py` is a complete executable program.
- [ ] Every staged public check and all nine enabled tests pass.
- [ ] Exactly one synthetic dictionary candidate verifies.
- [ ] The bounded PCAP comparison succeeds.
- [ ] Reports and screenshots omit passphrases and derived secret key material.
- [ ] The final program authenticates its own `data/flag_challenge.json` and prints the Part flag.

Submit your Python file, completed worksheet, check results, counts/timings, and
a short explanation of the PMK-to-MIC pipeline. Explain where the SSID,
BSSID, station address, nonces, and MIC occur; how direction and flags identify
messages; why the SSID and sorted context matter; why the captured MIC must be
cleared; and why server rate limiting cannot observe offline computation.
Explain why this simplified WPA2-Personal experiment does not apply directly
to WPA2-Enterprise or WPA3-SAE.
