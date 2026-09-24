# Part 1: DES Brute-Force Attack

**Estimated time:** 25 minutes. **Environment:** course Docker container.

## Scenario

An archival service encrypted a short record with DES, but its designers chose
a deliberately small teaching key space. You have one known plaintext block,
the corresponding ciphertext block, and a separate encrypted record. Your
work stays entirely within the supplied local files.

## Objective

Recover the reduced-space DES key identifier, use the recovered key to decrypt
the encrypted record, and measure the cost of the search. This part shows why a
small key space can make a sound block cipher impractical to use securely.

The known relation is:

```text
C = E_K(P)
```

The exercise uses real DES, but only a bounded key-ID space. Do not attempt to
search DES's full 56-bit effective key space.

The supplied instance uses **24 key-ID bits**, giving **16,777,216 candidates**.
This is 256 times the search space of a 16-bit instance. Budget roughly
**1–3 minutes for one sequential Python search** in the course container;
the time varies with your CPU, Docker resources, and implementation. The
program stops at the first match, so it need not test the entire space.

## Provided Files

| File | Purpose |
| --- | --- |
| `starter.py` | Functions to complete for search, measurement, and decryption |
| `data/parameters.json` | Public reduced-space parameters, including `key_bits` |
| `data/known_plaintext.bin` | One known DES plaintext block |
| `data/known_ciphertext.bin` | Ciphertext for that known block |
| `data/encrypted_flag.bin` | A separately encrypted, padded record |
| `../common/des.py` | Bounded DES helpers, including `make_des_key()` |

`make_des_key(key_id, key_bits)` is the required deterministic mapping from a
candidate ID to an eight-byte DES key. It encodes DES parity bits so that the
bounded candidate IDs remain distinct effective DES keys. Use this helper;
do not invent a second key mapping.

## Your Task

1. Complete `brute_force()` in `starter.py`.
2. Enumerate candidate IDs from `0` through `2**key_bits - 1`.
3. For each ID, create its DES key with `make_des_key()` and encrypt the known
   plaintext with `encrypt_block()`.
4. Stop when the result equals the known ciphertext. Return the recovered ID,
   the number of candidates tested, and elapsed time measured with
   `time.perf_counter()`.
5. Complete `decrypt_flag()` by reconstructing the recovered key, decrypting
   all eight-byte blocks, and removing the supplied padding with `unpad8()`.
6. Run the program and record the candidate count, elapsed time, and keys per
   second for your report.

Do not special-case a candidate ID or hard-code decrypted output. Your code
must work from the public parameters and the supplied known pair.

## How to Run

Start the course container as described in the Lab02 overview, then run:

```console
cd /workspace/labs/lab02/part1_des_bruteforce
python3 starter.py
```

The starter prints its result after the search finishes. A completed search
loop may therefore run for a while without terminal output. Check your code
first with the small, synthetic fixtures in the tests before running the
supplied 24-bit instance. Do not insert delays or repeat matching candidates
to increase the measured time; measure the actual candidate search.

After completing this part, run the Lab02 checks from the lab root:

```console
cd /workspace/labs/lab02
make grade
```

The search is intentionally bounded. Keep `parameters.json` and both
ciphertext files from the same release. Increasing `key_bits` alone leaves
the old key and ciphertext unchanged, so it does not necessarily make the
search take longer. Use the supplied 24-bit data for your final measurement.

## Flag Format

Successful decryption prints a value in this format:

```text
FLAG{...}
```

Treat the recovered value as course-completion evidence. Follow your
instructor's submission policy and do not place it in public source code or a
public report.

## Optional Hints

1. The candidate ID is not itself the DES key bytes. Pass it through
   `make_des_key()` before each block encryption.
2. Test a candidate against the known block before attempting to decrypt the
   larger file.
3. The encrypted record contains complete DES blocks. Remove padding only
   after every block has been decrypted.

## Analysis Questions

1. Why does this exercise use a reduced key space instead of searching all of
   DES's effective 56-bit key space?
2. Based on your measured rate, estimate how long a sequential Python search
   of `2**56` candidates would take. State the assumptions in your estimate.
3. Why is a Python timing result not a realistic estimate for an optimized GPU,
   FPGA, or ASIC search?
4. What role do DES parity bits play in the mapping from candidate IDs to DES
   keys, and why must different candidate IDs avoid collapsing to the same
   effective key?
5. Does this result show a mathematical weakness in every DES round function,
   or a practical limitation of its key-space size? Explain.
