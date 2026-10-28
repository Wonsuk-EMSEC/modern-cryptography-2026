"""Fresh positive/negative verification checks; no hidden flag is in this file."""
import argparse
import os
from pathlib import Path
import subprocess
import tempfile

PART = Path(__file__).resolve().parents[1]


def run(command, **kwargs):
    return subprocess.run([str(x) for x in command], capture_output=True, timeout=20, **kwargs)


def openssl(*args):
    result = run(["openssl", *args])
    assert result.returncode == 0, result.stderr.decode(errors="replace")
    return result


def check(pss: Path, update: Path, data_dir: Path | None = None) -> None:
    with tempfile.TemporaryDirectory(prefix="lab03-part07-check-") as scratch:
        tmp = Path(scratch)
        compiled = run(["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror", "-I", PART / "starter",
                        pss.resolve(), update.resolve(), PART / "tests/driver.c", "-lcrypto",
                        "-Wl,--wrap=EVP_DigestVerifyFinal", "-o", tmp / "pss"])
        assert compiled.returncode == 0, compiled.stderr.decode(errors="replace")
        for name in ("trusted", "wrong"):
            openssl("genpkey", "-algorithm", "RSA", "-pkeyopt", "rsa_keygen_bits:2048", "-out", tmp / f"{name}.key")
            openssl("pkey", "-in", tmp / f"{name}.key", "-pubout", "-out", tmp / f"{name}.pem")
        message = b"Lab03 fresh inert update\n" + os.urandom(47)
        (tmp / "message").write_bytes(message)
        (tmp / "modified").write_bytes(message + b"modified")
        signed = run([tmp / "pss", "sign", tmp / "trusted.key", tmp / "message", tmp / "student.sig"], cwd=tmp)
        assert signed.returncode == 0 and (tmp / "student.sig").is_file(), "signature generation failed"
        # Independent CLI enforces exact digest/MGF/salt settings for student signatures.
        openssl("dgst", "-sha256", "-verify", tmp / "trusted.pem", "-signature", tmp / "student.sig",
                "-sigopt", "rsa_padding_mode:pss", "-sigopt", "rsa_pss_saltlen:32",
                "-sigopt", "rsa_mgf1_md:sha256", tmp / "message")
        openssl("dgst", "-sha256", "-sign", tmp / "trusted.key", "-out", tmp / "trusted.sig",
                "-sigopt", "rsa_padding_mode:pss", "-sigopt", "rsa_pss_saltlen:32",
                "-sigopt", "rsa_mgf1_md:sha256", tmp / "message")
        sig = bytearray((tmp / "trusted.sig").read_bytes()); sig[13] ^= 1
        (tmp / "changed.sig").write_bytes(sig)
        (tmp / "short.sig").write_bytes(b"malformed")
        (tmp / "empty.sig").write_bytes(b"")
        (tmp / "broken.pem").write_bytes(b"not a key")
        for name, options in (("salt20", ["rsa_padding_mode:pss", "rsa_pss_saltlen:20", "rsa_mgf1_md:sha256"]),
                              ("mgf384", ["rsa_padding_mode:pss", "rsa_pss_saltlen:32", "rsa_mgf1_md:sha384"]),
                              ("pkcs1", ["rsa_padding_mode:pkcs1"])):
            extra = [item for option in options for item in ("-sigopt", option)]
            openssl("dgst", "-sha256", "-sign", tmp / "trusted.key", "-out", tmp / f"{name}.sig", *extra, tmp / "message")
        cases = [("trusted.pem", "message", "trusted.sig", True),
                 ("trusted.pem", "message", "student.sig", True),
                 ("trusted.pem", "modified", "trusted.sig", False),
                 ("trusted.pem", "message", "changed.sig", False),
                 ("wrong.pem", "message", "trusted.sig", False),
                 ("trusted.pem", "message", "short.sig", False),
                 ("trusted.pem", "message", "empty.sig", False),
                 ("trusted.pem", "message", "salt20.sig", False),
                 ("trusted.pem", "message", "mgf384.sig", False),
                 ("trusted.pem", "message", "pkcs1.sig", False)]
        for key, msg, signature, valid in cases:
            verified = run([tmp / "pss", "verify", tmp / key, tmp / msg, tmp / signature], cwd=tmp)
            assert verified.returncode == 0 and verified.stdout.strip() in (b"-1", b"0", b"1"), "invalid verifier protocol"
            assert (verified.stdout.strip() == b"1") == valid, f"incorrect verification: {key}/{msg}/{signature}"
            processed = run([tmp / "pss", "update", tmp / key, tmp / msg, tmp / signature], cwd=tmp)
            assert processed.returncode == 0 and processed.stdout == (b"ACCEPT\n" if valid else b"REJECT\n"), f"fail-open or reject-all update: {key}/{msg}/{signature}"
        for mode in ("verify-error", "update-error"):
            result = run([tmp / "pss", mode, tmp / "trusted.pem", tmp / "message", tmp / "trusted.sig"], cwd=tmp)
            expected = b"-1\n" if mode == "verify-error" else b"REJECT\n"
            assert result.returncode == 0 and result.stdout == expected, "EVP error must fail closed"
        broken = run([tmp / "pss", "update", tmp / "broken.pem", tmp / "message", tmp / "trusted.sig"], cwd=tmp)
        assert broken.returncode != 0 and broken.stdout == b"REJECT\n", "malformed key must reject"
        # The distributed key is an explicit trust input, not a replacement supplied by a package.
        fixture = data_dir or PART / "data"
        actual = run([tmp / "pss", "update", fixture / "trusted_public.pem", fixture / "update.bin", fixture / "update.sig"], cwd=tmp)
        assert actual.returncode == 0 and actual.stdout == b"ACCEPT\n", "provided signed update failed"
    print("Part07: fresh RSA-PSS signing, trusted verification, tampering, wrong key, malformed input, EVP error: OK")
    print("LAB03{part07_local_checks_passed}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pss", type=Path, default=PART / "starter/pss.c")
    parser.add_argument("--update", type=Path, default=PART / "starter/update.c")
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()
    check(args.pss, args.update, args.data_dir)
