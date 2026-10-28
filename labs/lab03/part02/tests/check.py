"""Student feedback. Receipts are public feedback, never hidden grading flags."""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile

PART = Path(__file__).resolve().parents[1]


def run(command, **kwargs):
    return subprocess.run([str(x) for x in command], capture_output=True,
                          timeout=20, **kwargs)


def valid_pdf(pdf: bytes) -> bool:
    match = re.search(rb"startxref\n(\d+)\n%%EOF\s*$", pdf)
    if not pdf.startswith(b"%PDF-1.4\n") or not match:
        return False
    xref = int(match[1])
    lines = pdf[xref:].splitlines()
    if len(lines) < 8 or lines[:2] != [b"xref", b"0 6"]:
        return False
    for number, entry in enumerate(lines[3:8], 1):
        offset = int(entry[:10])
        if not pdf[offset:].startswith(f"{number} 0 obj\n".encode()):
            return False
    return b"/Type /Page " in pdf and b"/Contents 5 0 R" in pdf


def check(recovery: Path, secure: Path, data_dir: Path | None = None) -> None:
    data = data_dir or PART / "data"
    info = json.loads((data / "challenge.json").read_text())
    with tempfile.TemporaryDirectory(prefix="lab03-part02-check-") as scratch:
        tmp = Path(scratch)
        worker = """import importlib.util, pathlib, sys
try:
    s = importlib.util.spec_from_file_location('submission', sys.argv[1])
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    p = m.recover(pathlib.Path(sys.argv[2]).read_bytes(), int(sys.argv[3]), int(sys.argv[4]))
    pathlib.Path(sys.argv[5]).write_bytes(p)
except SystemExit as error:
    raise RuntimeError('submission exited before completing recovery') from error
"""
        result = run([sys.executable, "-I", "-c", worker, recovery.resolve(),
                      (data / "confidential_report.enc").resolve(), info["start_epoch"],
                      info["end_epoch"], tmp / "recovered.pdf"], cwd=tmp)
        assert result.returncode == 0 and (tmp / "recovered.pdf").is_file(), "PDF recovery failed: " + result.stderr.decode(errors="replace")[-400:]
        pdf = (tmp / "recovered.pdf").read_bytes()
        assert hashlib.sha256(pdf).hexdigest() == info["sha256"], "recovered PDF SHA-256 mismatch"
        assert valid_pdf(pdf), "PDF structure/xref invalid"
        # Fresh caller input is deliberately unrelated to the original PDF.
        message = pdf + b"\n% independent round-trip input\n"
        (tmp / "input.pdf").write_bytes(message)
        source = re.sub(r"/\*.*?\*/|//[^\n]*", "", secure.read_text(), flags=re.S)
        assert not re.search(r"\b(srand|rand|time)\s*\(", source), "remove timestamp/C-PRNG path"
        compiled = run(["gcc", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror",
                        secure.resolve(), PART / "tests/rng_driver.c", "-lcrypto",
                        "-Wl,--wrap=RAND_priv_bytes", "-Wl,--wrap=RAND_bytes", "-o", tmp / "rng"])
        assert compiled.returncode == 0, compiled.stderr.decode(errors="replace")
        seen = []
        for _ in range(2):
            result = run([tmp / "rng", "0", tmp / "input.pdf"], cwd=tmp)
            assert result.returncode == 0, "secure RNG/round-trip failed: " + result.stdout.decode(errors="replace")
            fields = dict(line.split() for line in result.stdout.decode().splitlines())
            assert set(fields) == {"KEY", "IV", "CIPHER"}, "unexpected RNG harness output"
            key, iv, cipher = (bytes.fromhex(fields[k]) for k in ("KEY", "IV", "CIPHER"))
            assert len(key) == len(iv) == 16
            decrypted = run(["openssl", "enc", "-d", "-aes-128-cbc", "-K", key.hex(), "-iv", iv.hex()], input=cipher)
            assert decrypted.returncode == 0 and decrypted.stdout == message, "AES round-trip mismatch"
            seen.append((key, iv))
        assert seen[0] != seen[1], "reused fixed key/IV"
        for failure in (1, 2, 3, 4):
            result = run([tmp / "rng", failure, tmp / "input.pdf"], cwd=tmp)
            assert result.returncode == 1 and result.stdout == b"RNG_REJECTED\n", "RNG failure must abort before encryption"
        libc = ctypes.CDLL("libc.so.6")
        libc.srand.argtypes = [ctypes.c_uint]
        libc.rand.restype = ctypes.c_int
        candidates = set()
        for seed in range(info["start_epoch"], info["end_epoch"]+1):
            libc.srand(seed)
            candidates.add(bytes(libc.rand() % 256 for _ in range(32)))
        assert all(key+iv not in candidates for key, iv in seen), "bounded timestamp attack recovered secure key"
    print("Part02: PDF SHA-256, glibc recovery, secure round-trip, RNG failures, bounded attack: OK")
    print("LAB03{part02_local_checks_passed}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--recovery", type=Path, default=PART / "starter/recover.py")
    parser.add_argument("--secure", type=Path, default=PART / "starter/secure_random.c")
    parser.add_argument("--data-dir", type=Path)
    args = parser.parse_args()
    check(args.recovery, args.secure, args.data_dir)
