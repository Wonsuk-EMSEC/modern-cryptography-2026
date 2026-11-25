"""Lab04-only HTTPS site and explicit interception proxy.

The proxy accepts one classroom hostname. It generates fresh, separate target
and interception roots at startup; neither key is distributed or trusted by
the host automatically. The upstream TLS connection is verified normally.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from http import HTTPStatus
from http.client import HTTPResponse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from pathlib import Path
import secrets
import socket
import ssl
import tempfile
import threading

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


HOSTNAME = "lab04.local.test"
FLAG = "LAB04{mitm_" + secrets.token_hex(16) + "}"
LIMIT = 8192
TMP = Path(tempfile.mkdtemp(prefix="lab04-proxy-"))


def make_root(common_name: str):
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, common_name)])
    now = datetime.now(timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5))
            .not_valid_after(now + timedelta(days=30))
            .add_extension(x509.BasicConstraints(ca=True, path_length=0), critical=True)
            .add_extension(x509.KeyUsage(digital_signature=False, content_commitment=False,
                                         key_encipherment=False, data_encipherment=False,
                                         key_agreement=False, key_cert_sign=True, crl_sign=True,
                                         encipher_only=False, decipher_only=False), critical=True)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(key.public_key()),
                           critical=False)
            .sign(key, hashes.SHA256()))
    return key, cert


def make_leaf(root_key, root_cert):
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, HOSTNAME)])
    now = datetime.now(timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(root_cert.subject)
            .public_key(key.public_key()).serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5))
            .not_valid_after(now + timedelta(days=1))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName(HOSTNAME)]), critical=False)
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(x509.KeyUsage(digital_signature=True, content_commitment=False,
                                         key_encipherment=False, data_encipherment=False,
                                         key_agreement=False, key_cert_sign=False, crl_sign=False,
                                         encipher_only=False, decipher_only=False), critical=True)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(key.public_key()), critical=False)
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(root_key.public_key()),
                           critical=False)
            .sign(root_key, hashes.SHA256()))
    return key, cert


def write_certificates(label: str, key, cert, root_cert):
    private_path = TMP / f"{label}.key"
    cert_path = TMP / f"{label}.pem"
    root_path = TMP / f"{label}-root.pem"
    private_path.write_bytes(key.private_bytes(serialization.Encoding.PEM,
                                               serialization.PrivateFormat.PKCS8,
                                               serialization.NoEncryption()))
    private_path.chmod(0o600)
    cert_path.write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    root_path.write_bytes(root_cert.public_bytes(serialization.Encoding.PEM))
    return private_path, cert_path, root_path


target_root_key, target_root = make_root("Lab04 HTTPS Target Root")
target_key, target_cert = make_leaf(target_root_key, target_root)
target_key_path, target_cert_path, target_root_path = write_certificates(
    "target", target_key, target_cert, target_root)
proxy_root_key, proxy_root = make_root("Lab04 MITM Practice Root")
proxy_key, proxy_cert = make_leaf(proxy_root_key, proxy_root)
proxy_key_path, proxy_cert_path, proxy_root_path = write_certificates(
    "mitm", proxy_key, proxy_cert, proxy_root)


def send_body(handler: BaseHTTPRequestHandler, status: int, data: bytes, content_type: str):
    handler.send_response(status)
    handler.send_header("Content-Type", content_type)
    handler.send_header("Content-Length", str(len(data)))
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Connection", "close")
    handler.end_headers()
    handler.wfile.write(data)


class TargetHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            page = b'''<!doctype html><meta charset="utf-8"><title>Original Lab04 Site</title>
<h1>Original Lab04 Site</h1><p>This is a synthetic classroom service.</p>
<button id="send">Send practice token</button><p id="result"></p>
<script>
document.querySelector('#send').onclick = async () => {
  const value = await (await fetch('/api/token')).json();
  const answer = await fetch('/submit', {method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({token: value.token})});
  document.querySelector('#result').textContent = answer.ok ? 'Token sent.' : 'Request failed.';
};
</script>'''
            send_body(self, 200, page, "text/html; charset=utf-8")
        elif self.path == "/api/token":
            send_body(self, 200, json.dumps({"token": FLAG}).encode(), "application/json")
        else:
            send_body(self, 404, b"Not found", "text/plain")

    def do_POST(self):
        if self.path != "/submit":
            send_body(self, 404, b"Not found", "text/plain")
            return
        try:
            size = int(self.headers.get("Content-Length", "0"))
            if not 1 <= size <= LIMIT:
                raise ValueError
            token = json.loads(self.rfile.read(size))["token"]
        except (ValueError, KeyError, TypeError):
            send_body(self, 400, b"Bad request", "text/plain")
            return
        if token == FLAG:
            send_body(self, 200, b"Practice token received", "text/plain")
        else:
            send_body(self, 403, b"Wrong token", "text/plain")


class ProxyHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        if self.path == "/health":
            send_body(self, 200, b'{"ok":true,"service":"lab04-proxy"}', "application/json")
        elif self.path == "/lab04-proxy-ca.pem":
            send_body(self, 200, proxy_root_path.read_bytes(), "application/x-pem-file")
        elif self.path == "/lab04-target-cert.pem":
            send_body(self, 200, target_cert_path.read_bytes(), "application/x-pem-file")
        elif self.path == "/lab04-intercept-cert.pem":
            send_body(self, 200, proxy_cert_path.read_bytes(), "application/x-pem-file")
        else:
            send_body(self, 404, b"Only the Lab04 practice certificate is available", "text/plain")
        self.close_connection = True

    def do_CONNECT(self):
        if self.path != HOSTNAME + ":443":
            send_body(self, 403, b"Proxy permits only lab04.local.test:443", "text/plain")
            self.close_connection = True
            return
        self.send_response(200, "Connection Established")
        self.end_headers()
        self.wfile.flush()
        server_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        server_context.load_cert_chain(str(proxy_cert_path), str(proxy_key_path))
        try:
            with server_context.wrap_socket(self.connection, server_side=True) as client_tls:
                self.connection = client_tls
                self.rfile = client_tls.makefile("rb")
                self.wfile = client_tls.makefile("wb", 0)
                request_line = self.rfile.readline(LIMIT + 1)
                if len(request_line) > LIMIT:
                    return
                parts = request_line.decode("ascii").strip().split(" ")
                if len(parts) != 3 or parts[0] not in {"GET", "POST"} or not parts[1].startswith("/"):
                    return
                method, path, _version = parts
                headers = {}
                for _ in range(50):
                    line = self.rfile.readline(LIMIT + 1)
                    if not line or len(line) > LIMIT:
                        return
                    if line == b"\r\n":
                        break
                    key, _, value = line.decode("ascii").partition(":")
                    headers[key.lower()] = value.strip()
                else:
                    return
                size = int(headers.get("content-length", "0"))
                if size < 0 or size > LIMIT:
                    return
                body = self.rfile.read(size) if size else b""
                upstream_context = ssl.create_default_context(cafile=str(target_root_path))
                with socket.create_connection(("127.0.0.1", 8443), timeout=5) as raw:
                    with upstream_context.wrap_socket(raw, server_hostname=HOSTNAME) as upstream:
                        upstream.settimeout(5)
                        outbound = (f"{method} {path} HTTP/1.1\r\nHost: {HOSTNAME}\r\n"
                                    f"Connection: close\r\nContent-Length: {size}\r\n"
                                    f"Content-Type: {headers.get('content-type', 'application/octet-stream')}\r\n\r\n")
                        upstream.sendall(outbound.encode("ascii") + body)
                        response = HTTPResponse(upstream)
                        response.begin()
                        data = response.read(LIMIT * 8)
                        content_type = response.getheader("Content-Type", "text/plain")
                        status = response.status
                if path == "/" and status == 200:
                    data = data.replace(b"Original Lab04 Site", b"Observed Through Proxy")
                if path == "/api/token" and status == 200:
                    print("Lab04 proxy observed token response: " + data.decode("ascii"), flush=True)
                if path == "/submit":
                    print("Lab04 proxy observed submitted body: " + body.decode("utf-8", "replace"), flush=True)
                outgoing = (f"HTTP/1.1 {status} {HTTPStatus(status).phrase}\r\n"
                            f"Content-Type: {content_type}\r\nContent-Length: {len(data)}\r\n"
                            "Cache-Control: no-store\r\nConnection: close\r\n\r\n")
                client_tls.sendall(outgoing.encode("ascii") + data)
        except (OSError, ssl.SSLError, ValueError, UnicodeError) as error:
            print(f"Lab04 proxy connection ended: {type(error).__name__}: {error}", flush=True)
        finally:
            self.close_connection = True


def serve_target():
    server = ThreadingHTTPServer(("127.0.0.1", 8443), TargetHandler)
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(str(target_cert_path), str(target_key_path))
    server.socket = context.wrap_socket(server.socket, server_side=True)
    server.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=serve_target, daemon=True).start()
    ThreadingHTTPServer(("0.0.0.0", 8080), ProxyHandler).serve_forever()
