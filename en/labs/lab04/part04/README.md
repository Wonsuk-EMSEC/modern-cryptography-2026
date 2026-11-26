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

First complete the [shared Lab04 Docker setup](../README.md). If you have not
stopped the services, the proxy is already running; you do not need to open a
shell in the proxy container. Use **the browser on your PC** for this Part and
run the certificate comparison code in **your existing course terminal**.

Check the service status in a **host terminal at the repository root**:

```console
docker compose -f docker/compose.yml --profile lab04 ps
```

If you stopped the services, restart them in the same host terminal:

```console
docker compose -f docker/compose.yml --profile lab04 up -d --wait course lab04-proxy
```

Confirm that `lab04-proxy` is `healthy`. The proxy is available only on the
host's `127.0.0.1:18080`. The practice name `lab04.local.test` is sent by the
browser to the proxy; you need not change the PC's DNS or hosts file.

### Configure the Chrome proxy

Chrome uses the operating system's proxy settings by default.
Expand the instructions for the operating system **on your PC**. Note your
existing settings so you can restore them afterward.

<details>
<summary>macOS · Chrome</summary>

1. Open **System Settings → Network → your connected Wi-Fi → Details → Proxies**.
   For a wired connection, select the network you are using instead of Wi-Fi.
2. Turn on **Secure web proxy (HTTPS)**.
3. Enter `127.0.0.1` for the server and `18080` for the port.
   Turn off **Proxy server requires password**. You do not need to enable
   the HTTP or SOCKS proxy for this lab.
4. Click **OK** to apply.

[Apple: Change proxy settings](https://support.apple.com/en-euro/guide/mac-help/-mchlp2591/mac)

</details>

<details>
<summary>Windows · Chrome</summary>

1. Open **Settings → Network & internet → Proxy** in Windows, not WSL or the container.
2. Under **Manual proxy setup → Use a proxy server**, select **Set up** and turn
   on **Use a proxy server**. In Windows 10, you can turn on the switch directly
   on that screen.
3. Enter `127.0.0.1` for **Proxy IP address** and `18080` for **Port**.
   Do not add `lab04.local.test` to the proxy exception list.
4. Click **Save** to apply.

[Microsoft: Use a proxy server in Windows](https://support.microsoft.com/en-us/windows/experience/connectivity-networking/use-a-proxy-server-in-windows)

</details>

After configuring the proxy, proceed to the connection before trusting the
certificate below. This setting can affect other web connections. The practice
proxy handles only the practice site, so restore your previous proxy settings
after the lab. For Chrome's default behavior, see the
[Chromium network settings documentation](https://www.chromium.org/developers/design-documents/network-settings/).

### 1. Connect before trusting the certificate

With the proxy configured, open `https://lab04.local.test/` in **Chrome on your PC**.
Expect a certificate trust warning. Do not bypass it to continue.

### 2. Download and trust the practice CA

Open this URL in Chrome to download the CA's **public certificate**:

```text
http://127.0.0.1:18080/lab04-proxy-ca.pem
```

This URL connects directly to the server and works without proxy configuration.
**Downloading the certificate, trusting the CA, and configuring the proxy are
separate tasks.** You do not need to copy a private key to your PC.
After downloading, follow the instructions for your operating system below.

<details>
<summary>macOS · Import with Keychain Access</summary>

1. Press **⌘ + Space**, search for `Keychain Access`, and open it. This is
   different from the **Passwords** app.
2. Select the **login** keychain. If the keychain list is hidden, open it with
   **Window → Keychain Viewer** or **⌘ + 1**.
3. Drag the downloaded `lab04-proxy-ca.pem` into the Keychain Access window to import it.
4. Double-click the imported **Lab04 MITM Practice Root** and expand **Trust**.
5. Set **Secure Sockets Layer (SSL)** to **Always Trust** and close the window.
   Authenticate with your Mac user credentials if prompted.

[Apple: Add certificates](https://support.apple.com/en-ca/guide/keychain-access/kyca2431/mac) ·
[Show keychains](https://support.apple.com/en-ca/guide/keychain-access/kyca1085/mac) ·
[Change trust settings](https://support.apple.com/en-ca/guide/keychain-access/kyca11871/mac)

</details>

<details>
<summary>Windows · Import into the current user's certificate store</summary>

1. Press **Win + R** and enter `certmgr.msc` to open the **current user** certificate manager.
2. Select **Trusted Root Certification Authorities → Certificates**.
3. Right-click and select **All Tasks → Import**.
4. Select the downloaded `lab04-proxy-ca.pem`. If it is not visible, change
   the file type filter to **All Files**.
5. Confirm that the store is **Trusted Root Certification Authorities** and
   finish importing. Check that the certificate name is **Lab04 MITM Practice Root**.

[Microsoft: Manage certificate stores](https://learn.microsoft.com/en-us/windows-server/identity/ad-cs/inspect-certificates-manage-certificate-stores)

</details>

### 3. Reconnect and find the Flag

Completely quit and reopen Chrome, then visit `https://lab04.local.test/`.
After a successful connection, the page title is **Observed Through Proxy**.
Inspect the issuer and target name in the browser's certificate viewer.

Click **Send practice token** on the page, then read the logs in a
**host terminal at the repository root**:

```console
docker compose -f docker/compose.yml --profile lab04 logs --tail 50 lab04-proxy
```

Find the practice `LAB04{...}` value in a line containing
`Lab04 proxy observed token response` or `Lab04 proxy observed submitted body`.
This value is generated at runtime. Trusting the CA without configuring the
proxy does not route traffic through this lab's proxy.

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

### What to check after completing the TODO

- `compare_certificates.py` prints JSON with `original` and `intercepted`.
  Each has `subject`, `issuer`, `fingerprint`, and `dns_names` fields. Both
  `dns_names` lists contain `lab04.local.test`, and each `fingerprint` is
  64 hexadecimal characters.
- The original and proxy certificates have different `issuer` and
  `fingerprint` values. When `check.py` confirms this, it prints
  `Part04: original and intercepted certificate identities: OK`.
- The JSON does not contain a Flag. After sending the practice token in the
  browser step above, find `LAB04{...}` in the **proxy logs**.

## Cleanup

On the **host PC**, remove `Lab04 MITM Practice Root` from the browser's or
user's trust list and restore the HTTPS proxy setting to its previous value.
Restart the browser if needed.

- **macOS:** Delete the certificate you added from the **login** keychain in Keychain Access.
- **Windows:** Delete the certificate you added from **Trusted Root Certification Authorities → Certificates** in `certmgr.msc`.

Then stop the proxy in a **host terminal at the repository root**:

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

## Checkpoint Questions

1. Why did the browser accept the proxy's certificate instead of the original
   server's certificate?
2. How do the issuers and fingerprints of the two certificates for the same
   DNS name differ?
3. Why could the proxy see the response text and transmitted token?
4. Why does a new connection fail after you remove the CA from the trust list?
