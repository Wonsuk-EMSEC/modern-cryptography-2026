# Lab04: TLS Certificates and Trust

[한국어](../../../labs/lab04/README.md) | **English**

## Learning objectives

Generate an RSA key pair with OpenSSL, inspect the encryption OIDs, and write
code to open its PBKDF2-protected private-key file. Then run the path from
certificate signing request to server-certificate verification. Connect a
browser on your PC to the practice HTTPS proxy, then compare the certificate
warning before trusting the proxy CA with the accepted connection afterward.
Explain why the proxy can read and change requests and responses from the
practice site, and analyze the effect of a historical MD5 certificate
collision. Recover a private key protected by a weak password using an offline
dictionary, then check revocation with a CRL.

| Part | Topic | Starting file | Result to check after completion |
|---|---|---|---|
| [01](part01/README.md) | Generate a key pair, inspect OIDs, and open the encrypted private key | `part01/decrypt_key.py` | Private/public key match and completion marker |
| [02](part02/README.md) | Submit a CSR to the CA container | `part02/enroll.py` | Issued certificate files and matching CSR/certificate public keys |
| [03](part03/README.md) | Verify a chain and DNS name | `part03/verify_chain.py` | Valid chain and name accepted; invalid cases rejected |
| [04](part04/README.md) | PC trust settings and a local HTTPS proxy | `part04/compare_certificates.py` | Original/proxy certificate comparison and Flag in proxy logs |
| [05](part05/README.md) | Find an MD5 collision in supplied files | `part05/find_collision.py` | Different files with matching MD5 and different SHA-256 |
| [06](part06/README.md) | Reconstruct a historical rogue intermediate CA | `part06/investigate.py` | Reconstructed file, legacy acceptance and modern rejection |
| [07](part07/README.md) | Dictionary attack on an encrypted private key | `part07/attack.py` | Attempt count, elapsed time, and decrypted Flag |
| [08](part08/README.md) | Check certificate revocation with a CRL | `part08/revoke.py` | Acceptance before revocation, rejection with the updated CRL, and acceptance of the new certificate |

Each Part keeps its task script and optional public check beside its README.
To complete a Part, fill in the task script's TODOs yourself and run its
provided `main()` to check the input and output flow. Completion markers in the
form `LAB04{...}` let you check your progress in each Part. Find Part04's Flag
in synthetic HTTPS traffic and recover
Part07's Flag from ciphertext after unlocking the private key. In Part04, you
must both observe the Flag and complete `compare_certificates.py`.
Each Part README lists specific output and behavior to check after running the task.

## Required Docker images

| Image (Compose service) | How to prepare it | Used by |
|---|---|---|
| `modern-cryptography-2026` (`course`) | Build locally from `docker/Dockerfile` | Every Part |
| `modern-cryptography-2026-lab04-ca` (`lab04-ca`) | Build locally from `docker/lab04-ca/Dockerfile` on top of the course image | Parts 02 and 08; issuance of Part03's input certificate |
| `modern-cryptography-2026-lab04-proxy` (`lab04-proxy`) | Build locally from `docker/lab04-proxy/Dockerfile` on top of the course image | Part04 |

Parts 01, 05, 06, and 07 use only the `course` image. Part03 also verifies in
`course`, but first needs the certificate files produced in Part02. No Lab04
target image needs to be pulled separately from an external registry.

## Start the environment

Run these commands from the repository root on the host **for the complete
Lab04**. Build the shared course image before the two service images.

```console
docker compose -f docker/compose.yml build course
docker compose -f docker/compose.yml --profile lab04 build lab04-ca lab04-proxy
docker compose -f docker/compose.yml --profile lab04 up -d --wait course lab04-ca lab04-proxy
docker compose -f docker/compose.yml exec course bash
```

In the **course container**, follow each Part's README from `/workspace`.
Part02 uses the key made in Part01, so remember its password. Generated keys
are in `part01/output/` and issued certificates in `part02/output/`; Git ignores
both directories. Restarting the CA container regenerates its practice CA keys,
so reissue the Part02 certificate after a restart.
Part08 uses the Part02 CSR to issue a fresh certificate and check its revocation status.

Part04 also uses the browser on your own PC. The proxy is bound to
`127.0.0.1:18080` on that PC. Follow Part04's instructions to add its practice
CA, and remove both the CA and browser proxy setting at the end. Use only the
synthetic data and local services provided for this lab.

After the lab, exit the container shell and run this command on the host:

```console
docker compose -f docker/compose.yml --profile lab04 down
```

## Scope of the MD5 exercise

Part05 finds a genuine chosen-prefix MD5 collision among the supplied files.
Part06 uses genuine published 2008 certificate material: transplant the
legitimate certificate's signature into the rogue intermediate CA certificate
and verify the chain of the **previously issued** historical server certificate.
The researchers did not release the rogue CA's private key, so these materials
cannot issue a new server certificate. The reconstruction uses a fixed past
time and an explicit legacy verification policy; compare it with modern
rejection. Do not import the historical Root certificate into your personal
PC's trust store. [Original research material](https://marc-stevens.nl/research/hashclash/rogue-ca/index.html)
