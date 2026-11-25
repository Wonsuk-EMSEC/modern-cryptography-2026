# Part 06: Reconstruct an MD5 Rogue Intermediate CA

[한국어](../../../../labs/lab04/part06/README.md) | **English**

In 2008, researchers made the signed bodies of a legitimate server certificate and a rogue intermediate CA certificate differ while giving them the same MD5 hash. In this Part, transfer the signature from the published legitimate certificate into a rogue CA template, then examine whether a server certificate they issued at the time verifies through that CA.

The researchers **did not release the rogue CA's private key**. You therefore cannot issue a new server certificate with these materials. The supplied `historical_server.der` is a certificate that the researchers had already issued.

## Learning Objectives

1. Check that the two `TBSCertificate` bodies differ but share an MD5 hash.
2. Explain how the same signature can validate certificates with `CA:FALSE` and `CA:TRUE` roles.
3. Compare verification at a historical time under a policy allowing weak signatures with a stronger current policy.
4. Explain the different roles of a rogue CA certificate and its private key.

## Provided Materials

| Path | Contents |
| --- | --- |
| [investigate.py](../../../../labs/lab04/part06/investigate.py) | `collision_evidence()` and `transplant_signature()` TODOs, plus chain checking code |
| [data/legitimate.der](../../../../labs/lab04/part06/data/legitimate.der) | Legitimate certificate actually signed by the CA |
| [data/rogue_template.der](../../../../labs/lab04/part06/data/rogue_template.der) | Rogue intermediate CA template with blank signature bytes |
| [data/template.json](../../../../labs/lab04/part06/data/template.json) | Location and length of the template's signature bytes |
| [data/historical_server.der](../../../../labs/lab04/part06/data/historical_server.der) | Server certificate issued by the rogue CA at the time |
| [data/historical_root.crt](../../../../labs/lab04/part06/data/historical_root.crt) | Historical root certificate for offline verification |
| [test_part06_materials.py](../../../../labs/lab04/part06/test_part06_materials.py) | Public check of file formats and template metadata |

## Tasks

You must complete both TODO functions in `investigate.py` yourself; the
steps below specify their required behavior.

1. In `collision_evidence()`, parse the two DER certificates and compare their `TBSCertificate` bodies. Return `True` only when the bodies and SHA-256 hashes differ but the MD5 hashes match.
2. In `transplant_signature()`, read the legitimate certificate's signature and return DER bytes with only the blank signature bytes at the position in `template.json` replaced. Keep all other certificate fields unchanged.
3. Run the completed program. Inspect `CA:FALSE` on the legitimate certificate and `CA:TRUE` on the reconstructed one, and compare the results of the two verification policies.

`investigate.py` saves the reconstructed certificate at `/tmp/lab04-rogue-reconstructed.der`. OpenSSL uses `historical_root.crt` **only as the `-CAfile` input for an individual offline command**. Do not install this historical root in your computer's operating system or browser trust store.

## How to Run

Start the [shared Lab04 Docker environment](../README.md), then run these commands in the **course container at `/workspace`**. No network server or additional packages are needed.

```console
cd /workspace
python3 labs/lab04/part06/investigate.py
python3 labs/lab04/part06/test_part06_materials.py
```

The first command raises `NotImplementedError` while the TODOs remain. The public test checks **only the supplied materials**, so it can pass before implementation.

## What to Check After Completing the TODOs

Run `investigate.py` again after completing both TODOs. It prints these items in order; read the MD5 value and completion marker from your own run.

```text
legitimate CA role: False
rogue CA role: True
TBS MD5: <hash shared by the two signed bodies>
legacy chain: accepted
modern chain: rejected
LAB04{...}
reconstructed certificate: /tmp/lab04-rogue-reconstructed.der
```

`legitimate CA role` and `rogue CA role` show a server certificate and an intermediate CA certificate, respectively. `legacy chain` must be accepted and `modern chain` rejected; otherwise the program raises an error. The last path holds the reconstructed **certificate**, not a private key. An `OK` from `test_part06_materials.py` confirms only the format of the supplied files, not your two TODO implementations.

Verification time is fixed at **2004-08-05 00:00 UTC**, inside the certificates' validity periods. `legacy chain` is an offline reproduction using OpenSSL `-auth_level 0` to allow weak signatures; `modern chain` uses `-auth_level 1` and rejects the weak MD5 signature. This command checks **only the certificate chain**; it does not check a hostname, establish a TLS connection, or show that a current browser trusts the chain.

## Checkpoint Questions

1. How can the same signature bytes validate certificates with different CA roles?
2. Why must the `TBSCertificate` remain unchanged when moving the signature into the rogue template?
3. Why can you not issue a new server certificate with only the reconstructed CA certificate and without its matching private key?
4. Why do verification time and `-auth_level` affect the result?

## Sources and Scope

The legitimate and rogue CA certificates and the previously issued server certificate are public materials from Marc Stevens and colleagues' [MD5 considered harmful today](https://marc-stevens.nl/research/hashclash/rogue-ca/index.html) experiment. The historical root certificate comes from the [Android certificate store archive](https://android.googlesource.com/platform/system/ca-certificates/+/a0de1e8ae3654572ec4f87074bb13b8ff3a04670/files/74c26bd0.0). This Part analyzes published certificates offline; it does not compute a new MD5 collision or issue a new server certificate.
