# Part08: Reject a Revoked Server Certificate with a CRL

[한국어](../../../../labs/lab04/part08/README.md) | **English**

Use the certificate signing request (CSR) from [Part02](../part02/README.md) to obtain a new server certificate. Revoking a certificate need not change its signature or validity period. In this Part, fetch a certificate revocation list (CRL) explicitly and observe how applying it changes verification.

## Learning objectives

- Explain why validating a certificate chain and checking revocation are separate steps.
- Use a CRL signed by the intermediate CA to reject a revoked server certificate.
- Confirm that reissuing from the same CSR gives a new serial number and a certificate that passes verification with the current CRL.

## Prerequisites and materials

Start `course` and `lab04-ca` using the [shared Lab04 Docker environment](../README.md), and **complete Part02 first**. You need `labs/lab04/part02/output/request.csr`. Restarting the CA generates new CA keys and clears its revocation records. You may reuse the CSR, but start this Part's comparison again and do not mix earlier certificates or CRLs with the new CA's materials.

| Path | Contents |
|---|---|
| [revoke.py](../../../../labs/lab04/part08/revoke.py) | Runnable lab code with a `verify_with_crl()` TODO |
| [data/](../../../../labs/lab04/part08/data/) | No static secrets; certificates and CRLs come from the practice CA at runtime |
| [check.py](../../../../labs/lab04/part08/check.py) | Public check of the implementation |

**To complete this Part, you must implement the `verify_with_crl()` TODO in `revoke.py` yourself.** The provided `main()` uses the Part02 CSR to obtain a fresh certificate on every run and performs the verification steps before and after revocation. Starting with a fresh certificate keeps a previous run's revoked certificate from becoming the next run's starting point.

## Tasks

`verify_with_crl(root, intermediate, leaf, crl, hostname)` must return a `subprocess.CompletedProcess` from OpenSSL verification. Use the Root CA certificate as the trust anchor and the intermediate CA certificate as chain material, and check TLS server purpose and `hostname`. Omit revocation checking when `crl` is absent; apply that CRL when it is present. `-CRLfile` supplies the downloaded CRL; `-crl_check` requests a revocation check for the end-entity server certificate. **Supplying a CRL file alone does not enable revocation checking.** The intermediate CA that issued the server certificate signs this exercise's CRL. [OpenSSL `verify` documentation](https://docs.openssl.org/3.0/man1/openssl-verify/)

Observe these four outcomes when the program runs:

| Step | Certificate and verification condition | Expected result |
|---|---|---|
| 1 | New certificate, CRL before revocation | `before revocation with CRL: ACCEPT` |
| 2 | Same certificate after revocation, without a CRL check | `after revocation without CRL: ACCEPT` |
| 3 | Revoked certificate, updated CRL applied | `after revocation with CRL: REJECT` |
| 4 | Newly issued certificate from the same CSR, updated CRL applied | `new certificate with CRL: ACCEPT` |

The practice CA API uses `POST /revoke` with `certificate_pem` in the request body to revoke a certificate, and `GET /crl` returns the current CRL as PEM. The provided `main()` handles these requests. Fetch the CRL **explicitly within Docker** using `GET /crl`; this exercise does not use automatic CRL downloading. Step 2 does not prove that the certificate is unrevoked: it shows what happens when revocation information is omitted from verification.

This exercise reuses the CSR to compare revocation by serial number. **If a certificate is revoked because its private key was exposed, a real service must generate a new private key and CSR.**

## Run and finish

Run these commands in the **course container at `/workspace`**. No change to your personal computer's browser or operating-system trust store is needed.

```console
cd /workspace
python3 labs/lab04/part08/revoke.py
python3 labs/lab04/part08/check.py
```

The unfinished TODO raises `NotImplementedError`. Run the public check after
`revoke.py` creates the required files.

## What to check after completing the TODO

When `revoke.py` succeeds, the four results in the table appear in order:
`ACCEPT`, `ACCEPT`, `REJECT`, `ACCEPT`. The last line is a `LAB04{...}` completion
marker. The third `REJECT` must be caused by the updated CRL rejecting the
revoked certificate.

`part08/output/` contains `root.pem`, `intermediate.pem`, `old.pem`, `new.pem`,
`before.crl`, and `after.crl`. The old and new certificates have the same CSR
public key but different serial numbers. Compare the serial numbers directly:

```console
openssl x509 -in labs/lab04/part08/output/old.pem -noout -serial
openssl x509 -in labs/lab04/part08/output/new.pem -noout -serial
```

When `check.py` passes, it prints
`Part08: CRL, serial numbers, and hostname decisions: OK`. It also checks CRL
signatures, the revoked serial number, the reissued certificate, and rejection
of an incorrect hostname. The marker confirms the practice flow; it does not
certify the revocation state of any real service.

Inspect the updated CRL's issuer and revoked serial number directly:

```console
openssl crl -in labs/lab04/part08/output/after.crl -noout -issuer -text
```

## Checkpoint questions

1. Why should a revoked certificate be rejected even if its signature and validity period are still valid?
2. What are the separate roles of `-CRLfile` and `-crl_check`?
3. Why does verification without the CRL continue to accept the certificate after revocation?
4. Why does a newly issued certificate from the same CSR pass verification with the updated CRL?
5. If you used OCSP instead of a CRL, how would the freshness of the status and the way it is retrieved differ?
