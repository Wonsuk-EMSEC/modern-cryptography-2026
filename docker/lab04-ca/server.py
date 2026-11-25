"""Small local CA for Lab04. Keys are generated in memory at container start."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from threading import Lock

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec, rsa
from cryptography.x509.oid import ExtendedKeyUsageOID, NameOID


HOSTNAME = "lab04.local.test"
CRL_URL = "http://lab04-ca:8080/crl"
MAX_BODY = 65_536


def pem(certificate: x509.Certificate) -> str:
    return certificate.public_bytes(serialization.Encoding.PEM).decode("ascii")


def name(common_name: str) -> x509.Name:
    return x509.Name([x509.NameAttribute(NameOID.ORGANIZATION_NAME, "Lab04 Practice"),
                      x509.NameAttribute(NameOID.COMMON_NAME, common_name)])


def ca_certificate(subject: x509.Name, issuer: x509.Name, public_key, signing_key,
                   *, path_length: int, days: int) -> x509.Certificate:
    now = datetime.now(timezone.utc)
    return (x509.CertificateBuilder()
            .subject_name(subject).issuer_name(issuer).public_key(public_key)
            .serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5))
            .not_valid_after(now + timedelta(days=days))
            .add_extension(x509.BasicConstraints(ca=True, path_length=path_length), critical=True)
            .add_extension(x509.KeyUsage(digital_signature=False, content_commitment=False,
                                         key_encipherment=False, data_encipherment=False,
                                         key_agreement=False, key_cert_sign=True, crl_sign=True,
                                         encipher_only=False, decipher_only=False), critical=True)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(public_key), critical=False)
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(signing_key.public_key()),
                           critical=False)
            .sign(signing_key, hashes.SHA256()))


ROOT_KEY = ec.generate_private_key(ec.SECP256R1())
ROOT_NAME = name("Lab04 Course Root CA")
ROOT = ca_certificate(ROOT_NAME, ROOT_NAME, ROOT_KEY.public_key(), ROOT_KEY,
                      path_length=1, days=365)
INTERMEDIATE_KEY = ec.generate_private_key(ec.SECP256R1())
INTERMEDIATE_NAME = name("Lab04 Course Intermediate CA")
INTERMEDIATE = ca_certificate(INTERMEDIATE_NAME, ROOT_NAME,
                              INTERMEDIATE_KEY.public_key(), ROOT_KEY,
                              path_length=0, days=180)


def issue(csr_pem: str) -> x509.Certificate:
    csr = x509.load_pem_x509_csr(csr_pem.encode("ascii"))
    if not csr.is_signature_valid:
        raise ValueError("CSR signature is invalid")
    public_key = csr.public_key()
    if isinstance(public_key, rsa.RSAPublicKey):
        if public_key.key_size < 2048:
            raise ValueError("RSA key must have at least 2048 bits")
    elif not (isinstance(public_key, ec.EllipticCurvePublicKey) and
              isinstance(public_key.curve, ec.SECP256R1)):
        raise ValueError("use RSA-2048 or P-256")
    try:
        san = csr.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
    except x509.ExtensionNotFound as error:
        raise ValueError("CSR must contain a DNS Subject Alternative Name") from error
    if san.get_values_for_type(x509.DNSName) != [HOSTNAME] or len(san) != 1:
        raise ValueError(f"CSR SAN must be exactly DNS:{HOSTNAME}")
    for extension in csr.extensions:
        if isinstance(extension.value, x509.BasicConstraints) and extension.value.ca:
            raise ValueError("CA certificates cannot be requested")
        if isinstance(extension.value, x509.KeyUsage) and extension.value.key_cert_sign:
            raise ValueError("certificate-signing key usage cannot be requested")
    now = datetime.now(timezone.utc)
    return (x509.CertificateBuilder()
            .subject_name(name(HOSTNAME)).issuer_name(INTERMEDIATE.subject)
            .public_key(public_key).serial_number(x509.random_serial_number())
            .not_valid_before(now - timedelta(minutes=5))
            .not_valid_after(now + timedelta(days=30))
            .add_extension(x509.SubjectAlternativeName([x509.DNSName(HOSTNAME)]), critical=False)
            .add_extension(x509.BasicConstraints(ca=False, path_length=None), critical=True)
            .add_extension(x509.KeyUsage(digital_signature=True, content_commitment=False,
                                         key_encipherment=isinstance(public_key, rsa.RSAPublicKey),
                                         data_encipherment=False, key_agreement=False,
                                         key_cert_sign=False, crl_sign=False,
                                         encipher_only=False, decipher_only=False), critical=True)
            .add_extension(x509.ExtendedKeyUsage([ExtendedKeyUsageOID.SERVER_AUTH]), critical=False)
            .add_extension(x509.SubjectKeyIdentifier.from_public_key(public_key), critical=False)
            .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(
                INTERMEDIATE_KEY.public_key()), critical=False)
            .add_extension(x509.CRLDistributionPoints([
                x509.DistributionPoint(
                    full_name=[x509.UniformResourceIdentifier(CRL_URL)],
                    relative_name=None, reasons=None, crl_issuer=None)
            ]), critical=False)
            .sign(INTERMEDIATE_KEY, hashes.SHA256()))


class AlreadyRevoked(ValueError):
    pass


class CAState:
    """Issued certificates and the current CRL live only in this process."""

    def __init__(self) -> None:
        self.lock = Lock()
        self.issued: dict[int, bytes] = {}
        self.revoked: dict[int, datetime] = {}
        self.crl_number = 1
        self.crl_pem = self._build_crl(self.revoked, self.crl_number)

    @staticmethod
    def _build_crl(revoked: dict[int, datetime], number: int) -> bytes:
        now = datetime.now(timezone.utc)
        builder = (x509.CertificateRevocationListBuilder()
                   .issuer_name(INTERMEDIATE.subject)
                   .last_update(now - timedelta(minutes=5))
                   .next_update(now + timedelta(days=7))
                   .add_extension(x509.AuthorityKeyIdentifier.from_issuer_public_key(
                       INTERMEDIATE_KEY.public_key()), critical=False)
                   .add_extension(x509.CRLNumber(number), critical=False))
        for serial_number, revoked_at in sorted(revoked.items()):
            entry = (x509.RevokedCertificateBuilder()
                     .serial_number(serial_number)
                     .revocation_date(revoked_at)
                     .build())
            builder = builder.add_revoked_certificate(entry)
        return builder.sign(INTERMEDIATE_KEY, hashes.SHA256()).public_bytes(
            serialization.Encoding.PEM)

    def issue(self, csr_pem: str) -> x509.Certificate:
        with self.lock:
            certificate = issue(csr_pem)
            while certificate.serial_number in self.issued:
                certificate = issue(csr_pem)
            self.issued[certificate.serial_number] = certificate.public_bytes(
                serialization.Encoding.DER)
            return certificate

    def revoke(self, certificate_pem: str) -> int:
        certificate = x509.load_pem_x509_certificate(certificate_pem.encode("ascii"))
        serial_number = certificate.serial_number
        certificate_der = certificate.public_bytes(serialization.Encoding.DER)
        with self.lock:
            if self.issued.get(serial_number) != certificate_der:
                raise ValueError("certificate was not issued by this CA")
            if serial_number in self.revoked:
                raise AlreadyRevoked("certificate already revoked")
            updated = dict(self.revoked)
            updated[serial_number] = datetime.now(timezone.utc)
            new_number = self.crl_number + 1
            new_crl = self._build_crl(updated, new_number)
            self.revoked = updated
            self.crl_number = new_number
            self.crl_pem = new_crl
            return serial_number

    def get_crl(self) -> bytes:
        with self.lock:
            return self.crl_pem


STATE = CAState()


class Handler(BaseHTTPRequestHandler):
    def send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def send_pem(self, body: bytes) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "application/x-pem-file")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def read_json(self, field: str) -> str:
        length = int(self.headers.get("Content-Length", "0"))
        if length < 1 or length > MAX_BODY:
            raise ValueError("invalid request size")
        request = json.loads(self.rfile.read(length))
        if not isinstance(request, dict) or set(request) != {field} or not isinstance(request[field], str):
            raise ValueError(f"request must contain only {field}")
        return request[field]

    def do_GET(self) -> None:
        if self.path == "/health":
            self.send_json(200, {"ok": True, "service": "lab04-ca"})
        elif self.path == "/ca":
            self.send_json(200, {"root_pem": pem(ROOT),
                                 "intermediate_pem": pem(INTERMEDIATE)})
        elif self.path == "/crl":
            self.send_pem(STATE.get_crl())
        else:
            self.send_json(404, {"error": "unknown path"})

    def do_POST(self) -> None:
        if self.path not in ("/issue", "/revoke"):
            self.send_json(404, {"error": "unknown path"})
            return
        try:
            if self.path == "/issue":
                certificate = STATE.issue(self.read_json("csr_pem"))
            else:
                serial_number = STATE.revoke(self.read_json("certificate_pem"))
        except AlreadyRevoked as error:
            self.send_json(409, {"error": str(error)})
            return
        except (ValueError, TypeError, UnicodeError) as error:
            self.send_json(400, {"error": str(error)})
            return
        if self.path == "/issue":
            self.send_json(200, {"certificate_pem": pem(certificate),
                                 "intermediate_pem": pem(INTERMEDIATE),
                                 "root_pem": pem(ROOT)})
        else:
            self.send_json(200, {"revoked": True, "serial_number": str(serial_number)})


if __name__ == "__main__":
    ThreadingHTTPServer(("0.0.0.0", 8080), Handler).serve_forever()
