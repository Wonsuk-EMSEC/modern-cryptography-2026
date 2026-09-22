# Part 2: Double-DES Meet-in-the-Middle Attack

**Estimated time:** 35 minutes. **Environment:** course Docker container.

## Scenario

After seeing that one short DES key space is weak, an archival system added a
second DES encryption layer. Both layer keys come from independent, deliberately
bounded teaching spaces. Two known plaintext/ciphertext pairs are available,
along with a separately encrypted record.

## Objective

Recover both reduced-space DES key identifiers with a meet-in-the-middle (MITM)
search, verify the result with an independent known pair, and decrypt the
encrypted record. Compare the method with the cost of a naive two-key search.

The construction is:

```text
C = E_K2(E_K1(P))
```

For the first known pair, a correct key pair has the same intermediate value on
both sides:

```text
E_K1(P1) = D_K2(C1)
```

## Provided Files

| File | Purpose |
| --- | --- |
| `starter.py` | Functions to complete for MITM recovery and decryption |
| `data/known_pairs.json` | Two public known plaintext/ciphertext pairs and `key_bits` |
| `data/encrypted_flag.bin` | A separately encrypted, padded record |
| `../common/des.py` | Bounded DES block, padding, and key-mapping helpers |

The two known pairs have different roles. Use the first to find possible
intermediate-value matches, and use the second to reject accidental matches.

## Your Task

1. Read the two pairs and the bounded `key_bits` value in `known_pairs.json`.
2. Complete `recover_keys()` in `starter.py`.
3. For every possible `K1` ID, compute `E_K1(P1)` and store the result in a
   table that maps each intermediate value to a **list** of candidate IDs.
4. For every possible `K2` ID, compute `D_K2(C1)` and look for that value in
   the table.
5. For every matched pair, encrypt `P2` through both layers and compare it to
   `C2`. Return only the verified candidate pairs.
6. Complete `decrypt_flag()` by reversing the two DES layers for each block,
   then removing the final padding.
7. Run the program and record runtime, the expected forward-table size
   (`2**key_bits` entries before collisions), and the number of verified pairs.

Do not implement the default search as a nested loop over every possible `K1`
and `K2` pair. That approach grows approximately as `2**(2 * key_bits)` and is
included here only as a complexity comparison.

## How to Run

From inside the running course container:

```console
cd /workspace/labs/lab02/part2_double_des_mitm
python3 starter.py
```

Run the Lab02 checks after completing the required functions:

```console
cd /workspace/labs/lab02
make grade
```

The public key-space limit is intentional. Keep the supplied parameters for
the required run so that the exercise remains reproducible.

## Flag Format

Successful decryption prints a value in this format:

```text
FLAG{...}
```

Keep the recovered value out of public repositories, screenshots, and source
code unless your instructor explicitly requests it through a private channel.

## Optional Hints

1. Build the forward table from the first plaintext, then walk backward from
   the first ciphertext.
2. One intermediate value can map to more than one `K1` ID. Preserve every ID
   rather than overwriting an earlier entry.
3. An intermediate-value match is only a candidate. The second known pair is
   what verifies it.

## Analysis Questions

1. Why would a naive search over two `n`-bit reduced key spaces require about
   `2**(2*n)` block-cipher operations?
2. How does the MITM search change the expected work, and what memory does it
   require?
3. Why must the forward table retain a list of key IDs for each intermediate
   value?
4. Why does the second known pair matter even if the first pair gives one
   apparent match in a particular run?
5. Why does adding a second cipher invocation not automatically provide the
   security one might expect from simply doubling a key length?
