# Part04: Trusting a Practice CA and Intercepting HTTPS

[한국어](../../../../labs/lab04/part04/README.md) | **English**

Observe how a PC browser's trusted CAs change its decision about the same HTTPS
connection. The Docker practice proxy accepts connections only for
`lab04.local.test`. It creates separate TLS connections from the browser to the
proxy and from the proxy to the original server.

## Learning Objectives

1. Explain a certificate warning using the trust list and certificate issuer.
2. Add a practice CA to the browser and observe an HTTPS request through the proxy.
3. Compare the original server certificate with the certificate shown to the
   browser, then restore the browser's trust settings.

The target in this Part is a **synthetic site in Docker**. Do not use real
website accounts or data. Trust the practice CA on this PC only temporarily.
If possible, import the certificate into a dedicated browser profile. If the
browser uses the operating system's trust store, use the current user's store
and remove the certificate from that same location when finished.

## Provided Materials

- [compare_certificates.py](../../../../labs/lab04/part04/compare_certificates.py): TODOs
  for reading Subject, Issuer, SHA-256 fingerprint, and DNS SAN from two
  certificates, with a directly runnable `main()`.
- [check.py](../../../../labs/lab04/part04/check.py): optional public check of
  the completed `describe()` function against the running practice proxy.
- [data/protocol.json](../../../../labs/lab04/part04/data/protocol.json): the
  practice hostname and proxy address.
- The `lab04-proxy` container: a practice site and interception proxy. It
  generates a new practice CA on each start.

You must complete the `describe()` TODO in `compare_certificates.py` yourself; observing
the Flag in proxy logs alone does not complete this Part. The environment
provides the proxy; inspect browser requests and container logs to understand
its behavior.

## How to Run

First complete the [shared Lab04 Docker setup](../README.md). Run Docker commands
below in a **host terminal at the repository root**. Open the browser on your PC.

```console
docker compose -f docker/compose.yml --profile lab04 up -d --wait course lab04-proxy
docker compose -f docker/compose.yml --profile lab04 ps
```

Confirm that `lab04-proxy` is `healthy`. The proxy is available only on the
host's `127.0.0.1:18080`. The practice name `lab04.local.test` is sent by the
browser to the proxy; you need not change the PC's DNS or hosts file.

1. **Before trusting the certificate:** Set the browser's HTTPS proxy to
   `127.0.0.1`, port `18080`, and open `https://lab04.local.test/`. Expect a
   certificate trust warning. Do not bypass the warning.
2. **Import the practice CA:** In the host browser, open
   `http://127.0.0.1:18080/lab04-proxy-ca.pem` and download only the CA's
   **public certificate**. In the browser's certificate-authority settings,
   import it as trusted for identifying websites. Its displayed name is
   `Lab04 MITM Practice Root`. There is no need to copy the private key to the
   PC. Browser menus vary; restart the browser if necessary after the import.
3. **Connect again:** Open the same practice URL in a new tab. The page title
   now reads `Observed Through Proxy`. Inspect the certificate shown by the
   browser and note its issuer and target name.
4. **Observe the Flag:** Click **Send practice token** on the page, then read
   the logs in a **host terminal**:

   ```console
   docker compose -f docker/compose.yml --profile lab04 logs --tail 50 lab04-proxy
   ```

   Find the practice `LAB04{...}` value in a `Lab04 proxy observed token response`
   or `Lab04 proxy observed submitted body` line. The value is generated at
   runtime.

Setting the browser proxy and trusting its CA are separate actions. Importing
the CA alone does not route traffic through the proxy.

## Compare the Certificates in Code

Run these commands in the **course container terminal**. Both PEM files are
public certificates, not private keys.

```console
cd /workspace/labs/lab04/part04
curl -fsS http://lab04-proxy:8080/lab04-target-cert.pem -o /tmp/lab04-target-cert.pem
curl -fsS http://lab04-proxy:8080/lab04-intercept-cert.pem -o /tmp/lab04-intercept-cert.pem
openssl x509 -in /tmp/lab04-target-cert.pem -noout -subject -issuer -ext subjectAltName -sha256 -fingerprint
openssl x509 -in /tmp/lab04-intercept-cert.pem -noout -subject -issuer -ext subjectAltName -sha256 -fingerprint
python3 compare_certificates.py /tmp/lab04-target-cert.pem /tmp/lab04-intercept-cert.pem
python3 check.py
```

The comparison script raises `NotImplementedError` until you complete `describe()`.
Afterward it should print each certificate's Subject, Issuer, SHA-256
fingerprint, and DNS SAN side by side. Confirm that the intercepted
certificate's issuer matches the certificate shown in the browser. Run the
optional check after completing the TODO while `lab04-proxy` is running.

## Cleanup

On the **host PC**, remove `Lab04 MITM Practice Root` from the browser's or
user's trust list and restore the HTTPS proxy setting to its previous value.
Restart the browser if needed. Then stop the proxy in a **host terminal at the
repository root**:

```console
docker compose -f docker/compose.yml --profile lab04 stop lab04-proxy
```

Restarting the proxy creates a new CA, so a previously downloaded root will
not trust the new interception certificate. Confirm that the old practice CA
is no longer trusted by the PC.

## Completion and Notes

Record the initial trust error, successful connection after import, the two
certificates' differing issuers and fingerprints, and the Flag seen in proxy
logs. Do not submit a practice CA private key or real account information.

1. Why did the browser accept the proxy's certificate instead of the original
   server's certificate?
2. How do the issuers and fingerprints of the two certificates for the same
   DNS name differ?
3. Why could the proxy see the response text and transmitted token?
4. Why does a new connection fail after you remove the CA from the trust list?
