# Part03: Validate a Certificate Chain and Server Name

[한국어](../../../../labs/lab04/part03/README.md) | **English**

Determine when the server certificate issued in [Part02](../part02/README.md)
should be trusted. The trusted Root CA, intermediate CA, and intended server name
play different roles. Follow the [Lab04 guide](../README.md) for the environment.

## Learning objectives

- Use the Root CA as the trust anchor and the intermediate CA as chain material.
- Check both the certificate chain and the server name.
- Change only the intermediate or requested name to distinguish failure causes.

## Materials and task

- [verify_chain.py](../../../../labs/lab04/part03/verify_chain.py): runnable lab code showing three verification cases; **you must complete its `verify_certificate()` TODO yourself.**
- [check.py](../../../../labs/lab04/part03/check.py): optional check of acceptance and rejection outcomes.
- `part02/output/root.pem`, `intermediate.pem`, and `server.pem` produced in Part02.

In `verify_certificate(root, intermediate, leaf, hostname)`, run `openssl verify`
and return a `subprocess.CompletedProcess`. Use only `root.pem` as a trusted
certificate and use `intermediate.pem` as chain material only when it is supplied.
Check the TLS server purpose and the requested `hostname` as well. Specify the
trust store so other CAs installed on the system cannot change the result.
Use `openssl verify -help` to inspect available options.

## Run and expected behavior

Prepare the Part02 output first. Run these commands **inside the course container
at `/workspace`**:

```console
python3 labs/lab04/part03/verify_chain.py
python3 labs/lab04/part03/check.py
```

The completed program displays the three outcomes below and a `LAB04{...}`
completion marker. An unfinished TODO raises `NotImplementedError`.

| Case | Expected result | Cause to observe |
|---|---|---|
| Trusted chain and correct name | ACCEPT | The chain reaches the Root and the SAN name matches |
| Valid chain and different name | REJECT | The SAN name does not match |
| Missing intermediate CA | REJECT | Chain material needed to reach the Root is missing |

Use the same server certificate and change one condition at a time. Do not add
the intermediate CA directly as a trust anchor. Regenerate `part02/output/`
after the CA restarts.

## Checkpoint questions

1. When should a connection be rejected even though its certificate signature is valid?
2. What are the Root and intermediate CAs' different roles during verification?
3. What decision is missing if you check the chain but omit the expected DNS name?
