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
| `des_demo.py` | Runnable single-block DES encryption/decryption with public example values |
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

### Try DES encryption and decryption first

Start the course container as described in the Lab02 overview. Inside the
container, run the demonstration before implementing the search:

```console
cd /workspace/labs/lab02/part1_des_bruteforce
python3 des_demo.py
```

The sample runs immediately, without completing any TODOs. It shows two
single-block examples:

1. Call `DES.new(key, DES.MODE_ECB)`, then `encrypt()` and `decrypt()` using
   public example bytes. It checks both the expected ciphertext and recovery
   of the original plaintext.
2. Convert the public example ID `17` in an **8-bit example space** with
   `make_des_key()`, then use `encrypt_block()` and `decrypt_block()`. This
   shows how the same DES operations are accessed through the lab helpers.

For the first example, the output includes:

```text
Key:        133457799bbcdff1
Plaintext:  0123456789abcdef
Ciphertext: 85e813540f0ab405
Recovered:  0123456789abcdef
Known-answer and round-trip checks: OK
```

The helper example recovers `b'CRYPTO26'` and prints
`Helper round-trip check: OK`. The script reads no task data and uses only
public demonstration keys. It does not search for the task's key or decrypt
its encrypted record.

DES processes **8-byte blocks** and accepts an **8-byte encoded key** with
56 effective key bits and 8 parity bits. `bytes.fromhex()` converts the
displayed hexadecimal values to bytes; `.hex()` displays binary ciphertext
without treating it as text. The example uses ECB to demonstrate one block,
so it needs no IV or padding. Keep the distinction between this 8-bit example
space and the task's 24-bit space. DES is included for historical study.

Try changing the example plaintext while keeping it exactly eight bytes;
the recovered plaintext should still match. The first example's fixed
expected ciphertext applies only to its original key/plaintext pair, so use
the helper example for these changes.

### Run your brute-force implementation

After completing the TODOs, run from the same Part directory:

```console
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
