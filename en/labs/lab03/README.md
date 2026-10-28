# Lab03: Public-Key Cryptography — CTF Laboratory

[한국어](../../../labs/lab03/README.md) | **English**

## Learning Objectives

Implement the mathematics of public-key cryptography and measure its cost. Investigate
predictable randomness, weak RSA parameters, textbook RSA malleability, signature
verification errors, and CRT faults, then validate secure API usage and countermeasures.
Complete exactly these eight Parts.

| Part | Title | Completion objective |
|---|---|---|
| [Part01](part01/README.md) | Modular Exponentiation and Primality Testing | Implementation, performance, and a 128-bit composite |
| [Part02](part02/README.md) | Predictable Key Recovery and Secure Random Generation | PDF recovery and RNG error handling |
| [Part03](part03/README.md) | RSA Key Generation, Encryption, and CRT | C BIGNUM RSA and CRT optimization |
| [Part04](part04/README.md) | RSA Factorization Attack | Factor a weak modulus and decrypt |
| [Part05](part05/README.md) | RSA Low Public Exponent Attack | Exact integer cube root and attack conditions |
| [Part06](part06/README.md) | Textbook RSA Malleability and RSA-OAEP | Server exploitation and OAEP comparison |
| [Part07](part07/README.md) | RSA-PSS Signatures and Secure Verification | Accept valid signatures and reject errors |
| [Part08](part08/README.md) | RSA-CRT Fault Attack | Fresh-message signing and output verification |

## Challenge Scenario

Each Part audits an independent device or service. Implementation challenges require
the specified operations and performance as well as correct results. Use only the
supplied public data and explicitly authorized laboratory targets for attacks.

## Provided Materials

Each `partNN/` contains `README.md`, `starter/`, `data/`, and `tests/`.
Korean and English documents share the same code and data. Instructor solutions,
generators, and grading materials are excluded from the student release.
Use [REPORT_TEMPLATE.md](REPORT_TEMPLATE.md) for your report.

## Tasks

Implement each Part's TODOs, run its public checks, and answer its analysis questions.
Use Python 3 for experiments and GCC/OpenSSL for C implementations. Submit source,
reproducible measurements, attack evidence, and countermeasure checks. Public checks
provide local feedback; they do not determine the final grade.

<a id="setup"></a>

## How to Run

Follow the [shared environment guide](../../docker/README.md). From the repository
root in a host terminal:

```console
docker compose -f docker/compose.yml build course
docker compose -f docker/compose.yml up -d course
docker compose -f docker/compose.yml exec course bash
```

Inside the container, verify the environment. No extra `pip install` or `apt install`
is needed.

```console
cd /workspace
python3 -c "import Crypto, cryptography; print('Lab03 Python imports: OK')"
gcc --version
openssl version
make -C labs/lab03 test
```

The first command should print `Lab03 Python imports: OK`; tool versions vary.
`make test` checks materials and tools. It does not check challenge completion.

For Parts06 and08, start the additional target from the host:

```console
docker compose -f docker/compose.yml --profile lab03 up -d --wait course lab03-target
docker compose -f docker/compose.yml --profile lab03 ps
docker compose -f docker/compose.yml --profile lab03 logs --tail 30 lab03-target
```

The target should be `healthy` in `ps`. Its image is
`ghcr.io/wonsuk-emsec/modern-cryptography-2026-lab03-target:2026-lab03-v1`.
Staff must build, validate, and publish this version before students can pull it.
Implementing these sources does not publish the image or verify anonymous pulls.
For `manifest unknown`, check the image publication status or hosted target address
provided by your instructor.

For an instructor-hosted service, set the supplied address inside the container:

```console
export LAB03_TARGET_URL=https://INSTRUCTOR-PROVIDED-HOST
```

Replace this example with the actual address. The default is
`http://lab03-target:8080`. The target exposes no host port by default.
Check service health with:

```console
python3 -c "from labs.lab03.common.service_client import TargetClient; print(TargetClient().request('GET', '/health'))"
```

See each Part for exact response schemas and client commands. After implementing
the tasks, run the per-Part checks from the repository root:

```console
python3 -m labs.lab03.check --part 1
python3 -m labs.lab03.check --part 2
python3 -m labs.lab03.check --part 3
python3 -m labs.lab03.check --part 4
python3 -m labs.lab03.check --part 5
python3 -m labs.lab03.check --part 6
python3 -m labs.lab03.check --part 7
python3 -m labs.lab03.check --part 8
```

Incomplete starters must fail. Each Part documents successful output and additional
options. `make -C labs/lab03 grade PART=1` selects the same checker. For timing,
reduce competing load, warm up, repeat measurements in the same container, and use
the median. Exclude Docker startup, key generation, and file I/O from timing.

To stop only the target, or clean up after completing all work, respectively, run
these commands on the host:

```console
docker compose -f docker/compose.yml --profile lab03 stop lab03-target
docker compose -f docker/compose.yml --profile lab03 down
```

For connection errors, check target health, logs, `LAB03_TARGET_URL`, and your
execution location. Inside `course`, `localhost` does not refer to the target.
If `/workspace` is missing, enter the `course` shell rather than running on the host.

## Success Conditions

Completion results use `LAB03{...}`. Local checker receipts are public, nonsecret
feedback. Recovered data in Parts02,04,05 is evidence of exploitation. Final grading
uses independently generated inputs and source review; instructors assess written
analysis. Printing a known string alone cannot pass.

Users controlling local Docker can inspect images and memory. Local practice keys
and flags have no secrecy guarantee. Real grading keys and flags belong on
instructor-hosted targets or in isolated grading infrastructure. OAEP does not
authenticate senders or authorize transfers. The Part08 countermeasure addresses
the laboratory's single-CRT-branch fault model.

## Submission Requirements

Submit each Part's source, commands/output, recovery evidence or server completion
result. Include operation counts, repetitions, medians, relative speed, and execution
environment for Parts01/03. Include the recovered PDF and SHA-256 for Part02 and
positive/error verification results for Part07. Do not submit server keys or
instructor files unless requested by staff.

## Analysis Questions

1. Why do mathematically correct RSA operations alone not make a secure system?
2. Why check both local execution time and operation counts?
3. How should RNG API errors and signature verification API errors be handled?
4. What evidence comes from local receipts, recovered data, and hosted completion flags?
