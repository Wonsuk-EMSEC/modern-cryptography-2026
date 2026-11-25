# Part 05: Find an MD5 Collision Pair

[한국어](../../../../labs/lab04/part05/README.md) | **English**

Can two different certificate bodies have the same MD5 hash? Find a genuine collision pair among the supplied binary samples and compare them. You do not need to compute a new collision. The next Part examines what this collision means for a certificate signature.

## Learning Objectives

1. Explain why matching MD5 hashes do not prove that two byte strings have identical contents.
2. Compare the SHA-256 hashes of the same two byte strings.
3. Distinguish a certificate's signed `TBSCertificate` from the complete certificate.

## Provided Materials

| Path | Contents |
| --- | --- |
| [find_collision.py](../../../../labs/lab04/part05/find_collision.py) | `find_collision(samples)` TODO and executable code |
| [data/](../../../../labs/lab04/part05/data/) | Twelve binary samples. One pair consists of different `TBSCertificate` bodies from historical X.509 certificates. |
| [test_part05_materials.py](../../../../labs/lab04/part05/test_part05_materials.py) | Public check of the sample set only |

## Tasks

1. You must complete the `find_collision(samples)` TODO in `find_collision.py` yourself. Read each file from its `Path`, and return two paths whose **contents differ but MD5 hashes match**. Do not hardcode file names or depend on the input order.
2. Run the completed program and compare the two files' MD5 and SHA-256 hashes. The printed `LAB04{...}` is this Part's completion marker.
3. Note that these binary samples are signed certificate bodies, not complete certificates, and record why a collision matters to signature verification.

## How to Run

Start the [shared Lab04 Docker environment](../README.md), then run these commands in the **course container at `/workspace`**. No additional packages or server are needed.

```console
cd /workspace
python3 labs/lab04/part05/find_collision.py
python3 labs/lab04/part05/test_part05_materials.py
```

The first command raises `NotImplementedError` while the TODO remains. The public test checks **only the supplied materials**, so it can pass before you implement the TODO.

## What to Check After Completing the TODO

Run `find_collision.py` again. It prints these items in order; read the actual file names and digests from your own run.

```text
files: <first file name> <second file name>
MD5: <hash shared by both files>
SHA-256 #1: <first file's hash>
SHA-256 #2: <second file's hash>
LAB04{...}
```

`files:` must name **two files with different contents**. `MD5:` is shared by the pair, while `SHA-256 #1` and `SHA-256 #2` must differ. If those conditions fail, the program raises an error before printing the completion marker. An `OK` from `test_part05_materials.py` confirms the sample files, not whether your collision-finding TODO is correct.

## Checkpoint Questions

1. What do matching MD5 hashes and different SHA-256 hashes tell you about the two files?
2. Which part of a certificate is covered by its signature?
3. How does finding a collision between arbitrary files differ from colliding two files whose distinct contents were chosen in advance?

## Source

The colliding certificate bodies were extracted from certificates published by Marc Stevens and colleagues for their [historical rogue CA experiment](https://marc-stevens.nl/research/hashclash/rogue-ca/index.html). The remaining samples were generated for this exercise. Continue to [Part 06](../part06/README.md) to compare the legitimate and rogue CA roles.
