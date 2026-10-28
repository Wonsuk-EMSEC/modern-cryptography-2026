"""Public feedback; the local receipt is nonsecret and is not a grading flag."""
import argparse
import hashlib
import json
import math
import signal
import subprocess
import sys
from pathlib import Path

PART = Path(__file__).resolve().parents[1]


def grade(solution_path, data_path=None, fresh=False):
    challenge = json.loads(Path(data_path or PART/'data/challenge.json').read_text())
    # Submitted code runs in a child. Success is decided here from mathematical
    # evidence, so printing a receipt and exiting zero cannot pass this checker.
    worker = """import importlib.util,json,sys
spec=importlib.util.spec_from_file_location('student_factor',sys.argv[1])
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
answer=m.solve(json.load(sys.stdin))
print(json.dumps(answer))
"""
    proc=subprocess.run([sys.executable,'-c',worker,str(Path(solution_path).resolve())],
                        input=json.dumps(challenge),capture_output=True,text=True,timeout=8)
    assert proc.returncode==0, 'submission failed: '+(proc.stderr.strip().splitlines() or ['no diagnostic'])[-1]
    answer=json.loads(proc.stdout)
    p,q,d = (answer[k] for k in ('p','q','d'))
    n,e,c = (int(challenge[k]) for k in ('n','e','c'))
    assert all(type(x) is int for x in (p,q,d))
    assert p > 1 and q > 1 and p != q and p*q == n
    assert min(p,q) <= challenge['factor_bound']
    phi = (p-1)*(q-1)
    assert math.gcd(e,phi) == 1 and 0 < d < phi and e*d % phi == 1
    message = bytes.fromhex(answer['message_hex'])
    assert len(message) == challenge['message_bytes']
    assert int.from_bytes(message,'big') == pow(c,d,n)
    assert pow(int.from_bytes(message,'big'),e,n) == c
    assert hashlib.sha256(message).hexdigest() == challenge['plaintext_sha256']
    return {'status':'PASS', 'receipt':'LAB03{part04_local_checks_passed}', 'proof':answer}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--solution', type=Path, default=PART/'starter/recover.py')
    ap.add_argument('--data', type=Path)
    args = ap.parse_args()
    signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('10-second budget exceeded')))
    signal.alarm(10)
    try:
        print(json.dumps(grade(args.solution,args.data)))
    except (Exception,SystemExit) as exc:
        print(f'FAIL: {type(exc).__name__}: {exc}', file=sys.stderr)
        return 1
    finally:
        signal.alarm(0)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
