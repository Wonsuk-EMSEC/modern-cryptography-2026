# Part 7: CPA against AES

## Scenario

An AES-128 implementation protects a final record, but its first encryption
round leaks a small amount of synthetic power information.  You have captured
known plaintexts and matching traces from that implementation.  Recover the
AES key from the leakage, then decrypt the final record.

## Objective

Use correlation power analysis (CPA) to recover all 16 bytes of the AES-128
key and obtain the Part 7 flag.

## Provided Files

- `plaintexts.npy`: one known AES plaintext per trace, shaped `(N, 16)`.
- `traces.npy`: the corresponding synthetic power traces, shaped `(N, S)`.
- `secret_ciphertext.bin`: a packet containing `IV || AES-CBC ciphertext`.
- `starter.py` / `cpa.py`: incomplete CPA code and a plotting helper.
- `model.py`: the public AES S-box, Hamming-weight helper, and generic trace
  generator used for local experiments.

No physical hardware is required.  The traces are deterministic synthetic
measurements generated for this course.

## Your Task

**Before completing any TODOs, read `main()` in `starter.py` from beginning to end.**
Trace the inputs, function calls, return values, and outputs so you understand
the overall execution flow.

Here, `main()` parses the command-line options and loads the plaintexts,
traces, and encrypted packet. With `--all`, it recovers the full key, prints
the key and decrypted message, and returns. Otherwise, it analyzes the selected
byte, prints its result, and optionally saves plots. Complete the TODOs in
`starter.py` only after you understand both branches.

For plaintext row `i`, target byte position `j`, and a candidate byte `k`, use
the first-round leakage model

\[
H_{k,i}=HW(SBox(P_{i,j}\oplus k)).
\]

For every candidate `k` and trace sample `t`, calculate Pearson correlation
between the predicted vector `H[k]` and `traces[:, t]`.  Score each candidate
by its largest absolute correlation.  Begin with byte 0, generalize to each
byte position, recover the full key, then decrypt `secret_ciphertext.bin`.

## How to Run

Part 7 needs only the common course container. Follow the one-time
[Lab02 image preparation](../README.md#setup), then start it from the
repository root in a **host terminal**:

```console
docker compose -f docker/compose.yml up -d course
```

The following commands also run from the **host terminal** at the repository
root. `exec` runs Python inside the existing course container, and `-w` sets
the lab directory for that command:

```console
docker compose -f docker/compose.yml exec -w /workspace/labs/lab02 course \
  python3 part7_aes_cpa/starter.py --byte 0 --plots part7_aes_cpa/plots
```

After completing full-key recovery:

```console
docker compose -f docker/compose.yml exec -w /workspace/labs/lab02 course \
  python3 part7_aes_cpa/starter.py --all
```

The byte-0 command should produce three plots: example traces, the score for
each candidate key byte, and correlation over sample position for the winning
candidate. The repository is mounted at `/workspace`, so the plots are saved
in `labs/lab02/part7_aes_cpa/plots` in your host repository.

As an optional experiment, compare the byte-0 result at several trace counts:

```console
docker compose -f docker/compose.yml exec -w /workspace/labs/lab02 course \
  python3 part7_aes_cpa/trace_count_experiment.py
```

Small subsets may give unstable guesses. Record how the result changes as the
number of traces grows.

## Flag Format

The decrypted record has the form:

```text
FLAG{...}
```

## Optional Hints

1. Center a predicted leakage vector and each trace-sample column before
   calculating their dot product.
2. Treat all 256 guesses at once with NumPy broadcasting.  The hypotheses can
   have shape `(256, N)` while traces have shape `(N, S)`.
3. AES-CBC decryption needs the IV stored in the first 16 packet bytes, then
   PKCS#7 padding must be validated and removed.

## Analysis Questions

1. Why can each AES key byte be attacked independently in this leakage model?
2. Why do more traces generally improve the distinction between the correct
   key-byte hypothesis and incorrect hypotheses?
3. Why does this experiment attack an implementation rather than breaking the
   AES algorithm itself?
