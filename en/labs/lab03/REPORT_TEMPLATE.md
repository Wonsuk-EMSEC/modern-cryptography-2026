# Lab03 Submission Report

[한국어](../../../labs/lab03/REPORT_TEMPLATE.md) | **English**

- Name / student ID:
- Submitted source paths and version:
- Environment: CPU, Docker image, Python, GCC, OpenSSL versions
- Reproduction commands:

## Part01: Modular Exponentiation and Primality Testing

- Correctness and edge-case results:
- Exponent bit lengths and modular multiplication counts:
- Warm-up / repetitions / median (naive, square-and-multiply, built-in):
- Measurements for 16/20/24/28/32-bit primes and composites with small/large factors:
- Generated 128-bit composite, t, three prime factors, verification evidence:
- Why passing Fermat does not prove primality:

## Part02: Predictable Key Recovery and Secure Random Generation

- Time zone / search interval / recovery method:
- Recovered PDF, SHA-256, completion evidence:
- Corrected RNG calls and return-value handling:
- Normal encryption/decryption and each injected RNG failure:
- Results and interpretation of repeating the original bounded attack:

## Part03: RSA Key Generation, Encryption, and CRT

- Key calculation, encryption, direct and CRT decryption checks:
- RSA size / repetitions / direct and CRT medians / relative speed:
- Excluded work and reference calibration record:

## Part04: RSA Factorization Attack

- Factorization, private exponent recovery, and decryption evidence:
- Recovered value and re-encryption verification:

## Part05: RSA Low Public Exponent Attack

- Integer-root algorithm and exactness decision:
- Recovery and re-encryption evidence:
- Handling input where the direct root attack does not apply:

## Part06: Textbook RSA Malleability and RSA-OAEP

- Target URL / session / multiplicative modification requests and results:
- Valid OAEP processing and rejection of modification:
- Completion result / distinction between OAEP, sender authentication, authorization:

## Part07: RSA-PSS Signatures and Secure Verification

- Signing/verification implementation and PSS parameters:
- Valid, modified-message, modified-signature, and wrong-key results:
- Malformed input, API errors, and verification return-value handling:

## Part08: RSA-CRT Fault Attack

- Verification of recovered factors and private exponent:
- Server verification of a fresh-message signature:
- Protected-path rejection of faults and valid normal signature:
- Completion result / fault model addressed by the countermeasure:

## Analysis and Limitations

Answer each Part's analysis questions. Record failed checks and unverified items.
Local receipts are nonsecret; distinguish them from instructor-hosted grading results.
