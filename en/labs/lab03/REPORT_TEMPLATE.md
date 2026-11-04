# Lab03 Submission Report

[한국어](../../../labs/lab03/REPORT_TEMPLATE.md) | **English**

This template summarizes the required contents of the report for each Part.
In addition to the items listed below, include **answers to every Checkpoint Question
in each Part's README** in the corresponding Part of your report. Filling in only
these summary fields does not complete the submission requirements.

Submit the implementation source files, execution evidence, and other artifacts
required by each Part's README together with the report.

- Name / student ID:
- Submitted source paths and version:
- Environment: CPU, Docker image, Python, GCC, OpenSSL versions
- Reproduction commands:

## Part01: Modular Exponentiation and Primality Testing

- Answers to all Checkpoint Questions in the [Part01 README](part01/README.md):
- Correctness and edge-case results, with execution logs:
- Exponent bit lengths and modular multiplication counts for your two implementations:
- Warm-up / repetitions / median runtime (your naive implementation, Square-and-Multiply, built-in `pow`):
- Both primality tests' return values and timings by input type for 16/20/24/28/32-bit inputs:
- Exact primality testing versus screening prime candidates, and why passing Fermat does not prove primality:
- t, three prime factors, 128-bit composite n, and condition checks for each of the four search intervals:

## Part02: Predictable Key Recovery and Secure Random Generation

- Answers to all Checkpoint Questions in the [Part02 README](part02/README.md):
- Time zone / search interval / recovery method:
- Recovered PDF, SHA-256, completion evidence:
- Corrected RNG calls and return-value handling:
- Normal encryption/decryption and each injected RNG failure:
- Results and interpretation of repeating the original bounded attack:

## Part03: RSA Key Generation, Encryption, and CRT

- Answers to all Checkpoint Questions in the [Part03 README](part03/README.md):
- Key calculation, encryption, direct and CRT decryption checks:
- RSA size / repetitions / direct and CRT medians / relative speed:
- Excluded work and reference calibration record:

## Part04: RSA Factorization Attack

- Answers to all Checkpoint Questions in the [Part04 README](part04/README.md):
- Factorization, private exponent recovery, and decryption evidence:
- Recovered value and re-encryption verification:

## Part05: RSA Low Public Exponent Attack

- Answers to all Checkpoint Questions in the [Part05 README](part05/README.md):
- Integer-root algorithm and exactness decision:
- Recovery and re-encryption evidence:
- Handling input where the direct root attack does not apply:

## Part06: Textbook RSA Malleability and RSA-OAEP

- Answers to all Checkpoint Questions in the [Part06 README](part06/README.md):
- Target URL / session / multiplicative modification requests and results:
- Valid OAEP processing and rejection of modification:
- Completion result / distinction between OAEP, sender authentication, authorization:

## Part07: RSA-PSS Signatures and Secure Verification

- Answers to all Checkpoint Questions in the [Part07 README](part07/README.md):
- Signing/verification implementation and PSS parameters:
- Valid, modified-message, modified-signature, and wrong-key results:
- Malformed input, API errors, and verification return-value handling:

## Part08: RSA-CRT Fault Attack

- Answers to all Checkpoint Questions in the [Part08 README](part08/README.md):
- Verification of recovered factors and private exponent:
- Server verification of a fresh-message signature:
- Protected-path rejection of faults and valid normal signature:
- Completion result / fault model addressed by the countermeasure:

## Analysis and Limitations

Answer each Part's Checkpoint Questions. Record failed checks and unverified items.
Local receipts are nonsecret; distinguish them from instructor-hosted grading results.
