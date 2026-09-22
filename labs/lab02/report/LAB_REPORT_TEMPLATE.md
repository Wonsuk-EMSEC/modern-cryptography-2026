# Lab 02 Report: Practical Security of Block Ciphers

Name:
Student ID:
Date:
Environment and image version:

Use this template to document your implementation and analysis. Include enough
terminal output, code excerpts, diagrams, or redacted screenshots to show your
work. Do not include recovered flags, secret keys, full recovered plaintexts,
MAC values, target tokens, or raw target-service traffic in a public report.
If flags are required for grading, provide them only through the private method
specified by the instructor.

## Part 1: DES Brute-Force Attack

### Evidence

- Commands used:
- Reduced key-space parameters:
- Candidates tested:
- Elapsed time and measured keys per second:
- Redacted completion evidence:

### Analysis

1. Explain how your code maps a candidate ID into a DES key and why DES parity
   handling matters.
2. Estimate the work required for a sequential `2**56` search from your
   measured rate. State the assumptions and units.
3. Explain why that timing does not predict the performance of optimized search
   hardware.
4. State the practical security lesson illustrated by the reduced-space result.

## Part 2: Double-DES Meet-in-the-Middle Attack

### Evidence

- Commands used:
- Reduced key-space parameters:
- Number of forward-table entries and approximate memory use:
- Number of intermediate matches before verification:
- Number of verified key pairs:
- Elapsed time:
- Redacted completion evidence:

### Analysis

1. Contrast naive two-key enumeration with MITM computation cost.
2. Explain why the forward table maps an intermediate value to a list of key
   IDs rather than one ID.
3. Explain how the second known pair verifies a possible key pair.
4. Describe the computation-versus-memory tradeoff in this method.

## Part 3: AES-CBC and PKCS#7

### Evidence

- Commands used:
- Padding and CBC test results:
- Brief description of your ECB-block primitive use:
- Redacted completion evidence:

### Analysis

1. Explain why PKCS#7 adds a full block when the plaintext is block aligned.
2. Describe the role of the IV in the first CBC block.
3. State the CBC encryption and decryption equations and identify the value
   that links adjacent blocks.
4. Explain why malformed padding must be rejected only after every required
   padding byte is checked.

## Part 4: CBC Bit-Flipping Attack

### Evidence

- Commands used:
- Original and modified token lengths, with token content redacted:
- Redacted normal-user and administrator verification responses:
- Redacted completion evidence:

### Analysis

1. Identify the ciphertext or IV position that influenced the target plaintext
   byte and explain why.
2. Show the XOR difference calculation using symbolic or redacted values.
3. Explain why the result is a missing-integrity problem rather than a break of
   the AES block cipher.

## Part 5: Padding Oracle Attack

### Evidence

- Commands used:
- Number of oracle queries used:
- One redacted checkpoint showing a recovered byte or block:
- Redacted completion evidence:

### Analysis

1. What single bit of information does the oracle reveal for each query?
2. Explain how a modification to a preceding block controls a byte in the next
   plaintext block after decryption.
3. Explain why a valid-padding observation can reveal an intermediate byte.
4. Describe one edge case your implementation handles when a padding response
   has more than one possible explanation.

## Part 6: MAC-then-Encrypt and Encrypt-then-MAC

### Evidence

- Commands used:
- Redacted modified-packet response from Service A:
- Redacted modified-packet response from Service B:
- Observed behavior for a modified IV and for a modified ciphertext block:

### Analysis

1. Which service lets padding-related behavior reach the caller, and what
   observation supports your conclusion?
2. Why does authenticating after decryption allow that behavior to matter?
3. Explain why authenticating `IV || ciphertext` before decryption prevents
   the corresponding alteration from reaching padding validation.
4. Why is authenticating only the ciphertext insufficient when the IV affects
   the first plaintext block?

## Part 7: CPA Against AES

### Evidence

- Commands used:
- Trace-set dimensions and selected byte position:
- Best key-guess rank and maximum correlation for one byte:
- Full-key recovery or verification result, with secret values redacted:
- Plots included: example traces, key-guess score, and winning-candidate
  correlation by sample position:
- Redacted completion evidence:

### Analysis

1. State the leakage hypothesis used for one AES key byte.
2. Explain why bytes can be ranked independently in the supplied first-round
   leakage model.
3. Explain why more traces can improve the ranking of the correct key guess.
4. Explain why this experiment does not constitute a mathematical break of AES.
5. Give one implementation-level countermeasure and explain how it reduces the
   relevant leakage.

## Lab-Wide Reflection

1. Relate one lesson from each part to key size, composition, mode of
   operation, integrity, error handling, or implementation behavior.
2. Explain the following statement in your own words:

   > Cryptographic security depends not only on the cipher itself, but also on
   > key size, composition, mode of operation, authentication, error handling,
   > and implementation.

3. Give two concrete design recommendations for a system that encrypts and
   authenticates confidential application data.
