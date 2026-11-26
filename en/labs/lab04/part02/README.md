# Part02: Request a Certificate from the CA Container

[한국어](../../../../labs/lab04/part02/README.md) | **English**

Open the private key protected in [Part01](../part01/README.md) and create a
certificate signing request (CSR). Send the CSR to the practice `lab04-ca`
container and confirm that the issued certificate contains your public key and
requested name. Follow the [Lab04 guide](../README.md) to start and stop the CA.

## Learning objectives

- Put a public key and requested DNS name in a CSR and sign it with your private key.
- Observe how the CA checks the CSR and issues a server certificate.
- Keep the private key with the client while sending a CSR and receiving public certificates.

## Materials and task

- [enroll.py](../../../../labs/lab04/part02/enroll.py): runnable lab code that opens the key, submits the CSR, checks the response, and saves files; **you must complete its `make_csr()` TODO yourself.**
- [check.py](../../../../labs/lab04/part02/check.py): optional check of the issued certificate's public key, purpose, and chain.

`make_csr(private_key, hostname)` must return a PEM CSR. The requested server name is
`lab04.local.test`; put it in a DNS `subjectAltName`. Sign the CSR with SHA-256.
The CA issues a server certificate for this name and rejects requests for
`CA:TRUE`. Provided code handles the `POST /issue` request and response. The
response contains public certificates for the server, intermediate CA, and Root CA.

## 1. Prepare the Part01 private key and environment

Complete Part01 first. If you finished the [shared Lab04 setup](../README.md)
and have not stopped the services, the CA is already running. Continue at
**`/workspace` in your existing course terminal**. The code sends requests to
the CA; you do not need to open a shell in the CA container.

Use `part01/output/private_encrypted.pem` from Part01 and its password.
You do not need to generate another private key or copy it to the CA.

## 2. Create a CSR and request a certificate in code

Complete the `make_csr()` TODO in `enroll.py`, then run it.
Wait for the first command to save the certificate files successfully before
running the second command to check them.

```console
python3 labs/lab04/part02/enroll.py
python3 labs/lab04/part02/check.py
```

The first command prompts for the Part01 key password. After you implement the TODO,
it sends the CSR to the CA's `/issue` endpoint and saves `request.csr`, `server.pem`,
`intermediate.pem`, and `root.pem` under `part02/output/`. It then checks the
public key and DNS name and prints a `LAB04{...}` completion marker. With the TODO
unfinished, it raises `NotImplementedError`.

The CA creates new keys and certificates when its container restarts. After a
restart, rerun this command to get a new CSR and certificate. [Part03](../part03/README.md)
uses the files in `part02/output/`.

### What to check after completing the TODO

- `enroll.py` checks that the issued server certificate's public key matches the
  CSR/private key and that the certificate contains the requested DNS name,
  then prints the output path and completion marker.

  ```text
  Certificate files: /workspace/labs/lab04/part02/output
  Issued name: lab04.local.test; CSR and certificate public key match: OK
  LAB04{...}
  ```

  `part02/output/` contains four files: `request.csr`, `server.pem`,
  `intermediate.pem`, and `root.pem`. The private-key file is not copied there.

- `check.py` rechecks the CSR signature, public-key match, server purpose,
  and chain to the Root, then prints:

  ```text
  Part02: CSR, public key, extensions, and trusted chain: OK
  ```

## Checkpoint Questions

1. Which information comes from a CSR, and which fields does the CA choose at issuance?
2. Why must the issued certificate's public key match the CSR's public key?
3. Why does the CA not need the applicant's private key when it receives only the CSR?
