# Part 3: AES-CBC and PKCS#7

**Estimated time:** 35 minutes. **Environment:** course Docker container.

## Scenario

The next records use AES rather than DES. Before examining failures in how CBC
is deployed later in this lab, you must build the mode and its padding rules
from the AES block primitive. The supplied key and IV are test material for
this implementation exercise; recovering an AES key is not the goal here.

## Objective

Implement PKCS#7 padding, PKCS#7 validation and removal, CBC encryption, and
CBC decryption. Use AES-ECB only as the one-block AES primitive. Then decrypt
the supplied encrypted record using your own CBC implementation.

For a block size of 16 bytes, CBC uses:

```text
C_i = E_K(P_i XOR C_(i-1))
P_i = D_K(C_i) XOR C_(i-1)
```

For the first block, `C_(i-1)` is the IV.

## Provided Files

| File | Purpose |
| --- | --- |
| `starter.py` | Functions to complete for padding and manual CBC processing |
| `data/key.bin` | AES test key for this construction exercise |
| `data/iv.bin` | AES-CBC initialization vector |
| `data/encrypted_flag.bin` | CBC-encrypted record to decrypt after implementation |
| `data/nist_cbc_vector.json` | Public AES-CBC known-answer vector for block-level checks |

The course image includes PyCryptodome. You may create an AES primitive with
`AES.new(key, AES.MODE_ECB)`, but you must not use `AES.MODE_CBC` or a library
PKCS#7 padding helper for the required functions.

## Your Task

**Before completing any TODOs, read `main()` in `starter.py` from beginning
to end.** Trace the inputs, function calls, return values, and outputs so you
understand the overall execution flow.

Follow how `main()` reads the key, IV, and ciphertext, passes them to
`cbc_decrypt()`, and displays the recovered plaintext. Also inspect the tests
to see how the padding and encryption functions are used beyond this entry
point. Complete the TODOs below only after you understand how these steps
fit together.

1. Complete `pkcs7_pad()`.
   - Append between 1 and 16 bytes for AES.
   - Append a complete padding block when the input length is already block
     aligned, including for an empty input.
2. Complete `pkcs7_unpad()`.
   - Reject empty input and input whose length is not a block multiple.
   - Reject a padding length outside the permitted range.
   - Verify every claimed padding byte before removing it.
3. Complete `cbc_encrypt()`.
   - Pad the plaintext first.
   - XOR each plaintext block with the IV or preceding ciphertext block.
   - Encrypt that XOR result with an AES-ECB block primitive.
4. Complete `cbc_decrypt()`.
   - Reject malformed ciphertext lengths.
   - AES-decrypt each block, XOR it with the IV or preceding ciphertext block,
     then validate and remove padding after all blocks are assembled.
5. Run `starter.py` to decrypt the supplied record and obtain the completion
   value.

Do not hard-code the decrypted output or substitute a library CBC mode. The
tests exercise empty, short, aligned, multi-block, and malformed-padding cases.

## How to Run

From inside the running course container:

```console
cd /workspace/labs/lab02/part3_aes_cbc_pkcs7
python3 starter.py
```

Run the Lab02 checks after completing the required functions:

```console
cd /workspace/labs/lab02
make grade
```

## Flag Format

Successful decryption prints a value in this format:

```text
FLAG{...}
```

Use the recovered value only as directed by your course submission policy. Do
not add it to public code, a public report, or a reusable test fixture.

## Optional Hints

1. With PKCS#7, the final byte states how many padding bytes were appended;
   all of those bytes must have the same value.
2. In CBC encryption, update the previous-block variable to the ciphertext you
   just produced. In CBC decryption, preserve the current ciphertext block
   before moving to the next one.
3. Decryption produces padded plaintext first. Validate and remove the padding
   only after all blocks have been processed.

## Analysis Questions

1. Why must PKCS#7 add a full block of padding when plaintext is already a
   multiple of the AES block size?
2. What information does the IV provide for the first CBC block, and why must
   it be available for decryption?
3. If one ciphertext block is modified, which plaintext blocks can be affected
   after CBC decryption? Explain with the CBC equation.
4. Why must an implementation validate every padding byte rather than only the
   final byte?
5. Why is AES-ECB acceptable here only as an underlying one-block primitive,
   while an ECB mode applied directly to a multi-block message has different
   security properties?
